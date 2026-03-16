"""
TechHive Predictor v22 — Integración del modelo ML en Django.

Arquitectura (idéntica al notebook ModeloPrediccionVentasFinalDjango.ipynb):
  - Ensemble de 3 CatBoostRegressor por tenant (direct, ratio, global)
  - Blend ponderado con pesos optimizados almacenados en metadata_v22.json
  - Calibración por segmento (is_weekend × is_holiday)
  - Forecast recursivo día a día

Mapeo de tenants:
  magic_world → tenant_id=0 → magic_direct_v22 + magic_ratio_v22
  papeleria   → tenant_id=1 → pap_direct_v22   + pap_ratio_v22
  demo        → tenant_id=1 (datos de papelería)
"""

import json
import logging
from datetime import date, datetime
from pathlib import Path

import joblib
import holidays as holidays_lib
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────

QUITO_LAT = -0.1807
QUITO_LON = -78.4678
QUITO_ALT = 2850  # metros sobre el nivel del mar

WEATHER_COLS = [
    "tavg", "tmin", "tmax", "prcp", "snow",
    "wdir", "wspd", "wpgt", "pres", "tsun",
]

# Orden exacto de features según celda 18 del notebook (crítico para CatBoost)
FEATURES_V22 = [
    "tavg", "tmin", "tmax", "prcp", "snow", "wdir", "wspd", "wpgt", "pres", "tsun",
    "is_holiday", "is_pre_holiday", "is_post_holiday",
    "dayofweek", "day", "month", "quarter", "weekofyear", "is_weekend",
    "dow_sin", "dow_cos", "month_sin", "month_cos", "week_sin", "week_cos",
    "t",
    "llovio", "lluvia_fuerte", "calor_alto", "frio_bajo", "llovio_finsemana",
    "prcp_roll_mean_3", "tavg_roll_mean_3", "wspd_roll_mean_3",
    "prcp_roll_mean_7", "tavg_roll_mean_7", "wspd_roll_mean_7",
    "lag1", "lag2", "lag3", "lag7", "lag14", "lag21", "lag28",
    "roll_mean_7", "roll_std_7", "roll_max_7", "roll_min_7", "roll_median_7",
    "roll_mean_14", "roll_std_14", "roll_max_14", "roll_min_14", "roll_median_14",
    "roll_mean_28", "roll_std_28", "roll_max_28", "roll_min_28", "roll_median_28",
    "ema_7", "ema_14",
    "diff1", "diff7", "growth_1", "growth_7",
    "weak_demand_regime", "high_volatility", "shock_recent",
    "tenant_id", "anchor_base", "ratio_to_anchor", "ratio_to_anchor_log",
    "lag1_low", "lag7_low", "low_demand_streak", "days_since_peak",
    "positive_pressure", "positive_pressure_ema",
]

# Mapeo schema_name → tenant_id del modelo
TENANT_ID_MAP = {
    "magic_world": 0,
    "magic": 0,
    "papeleria": 1,
    "pap": 1,
    "demo": 1,  # demo tiene CSV de papelería
}

MIN_HISTORY_DAYS = 28

ML_DIR = Path(__file__).parent / "ml_models"


# ─────────────────────────────────────────────
# FUNCIONES AUXILIARES (idénticas al notebook)
# ─────────────────────────────────────────────

def safe_float(val, default=0.0):
    try:
        return float(val)
    except Exception:
        return default


def safe_get_lag(values, lag):
    values = [safe_float(v, 0.0) for v in values]
    if len(values) >= lag:
        return float(values[-lag])
    return float(values[0]) if len(values) > 0 else 0.0


def safe_roll(values, window, func):
    values = [safe_float(v, 0.0) for v in values]
    if not values:
        return 0.0
    s = pd.Series(values[-window:] if len(values) >= window else values)
    return safe_float(func(s), 0.0)


def compute_ema_from_history(values, span):
    values = [safe_float(v, 0.0) for v in values]
    return float(pd.Series(values).ewm(span=span, adjust=False).mean().iloc[-1])


def build_weather_profile_by_dow(weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Perfil climático mediano por día de la semana.
    Idéntico a build_weather_profile_by_dow() del notebook (celda 28).
    """
    tmp = weather_df.copy()
    tmp["fecha_venta"] = pd.to_datetime(tmp["fecha_venta"])

    for c in WEATHER_COLS:
        if c not in tmp.columns:
            tmp[c] = 0.0
        tmp[c] = pd.to_numeric(tmp[c], errors="coerce").replace([np.inf, -np.inf], np.nan)
        if tmp[c].isna().all():
            tmp[c] = 0.0
        else:
            tmp[c] = tmp[c].interpolate(limit_direction="both").fillna(tmp[c].median()).fillna(0.0)

    tmp["dayofweek"] = tmp["fecha_venta"].dt.dayofweek
    profile = tmp.groupby("dayofweek")[WEATHER_COLS].median().reset_index()
    for c in WEATHER_COLS:
        profile[c] = pd.to_numeric(profile[c], errors="coerce").fillna(0.0)
    return profile


def _get_future_weather_row(future_date, weather_profile_dow: pd.DataFrame) -> dict:
    dow = pd.Timestamp(future_date).dayofweek
    row = weather_profile_dow[weather_profile_dow["dayofweek"] == dow]
    if row.empty:
        return {c: 0.0 for c in WEATHER_COLS}
    return {c: safe_float(row.iloc[0][c], 0.0) for c in WEATHER_COLS}


def build_future_feature_row_v22(
    history_df: pd.DataFrame,
    future_date,
    tenant_id: int,
    weather_profile_dow: pd.DataFrame,
    holiday_dates: set,
    features_v22: list,
) -> pd.DataFrame:
    """
    Construye un vector de features para una fecha futura.
    Idéntico a build_future_feature_row_v22() del notebook (celda 28).
    """
    hist = history_df.copy().sort_values("fecha_venta").reset_index(drop=True)
    sales = hist["ventas"].tolist()
    weather_vals = _get_future_weather_row(future_date, weather_profile_dow)

    row = {}
    row["fecha_venta"] = pd.Timestamp(future_date)
    row["tenant_id"] = tenant_id

    # ── Calendario ──────────────────────────────
    row["dayofweek"] = row["fecha_venta"].dayofweek
    row["day"] = row["fecha_venta"].day
    row["month"] = row["fecha_venta"].month
    row["quarter"] = row["fecha_venta"].quarter
    row["weekofyear"] = int(row["fecha_venta"].isocalendar().week)
    row["is_weekend"] = int(row["dayofweek"] >= 5)

    row["dow_sin"] = np.sin(2 * np.pi * row["dayofweek"] / 7)
    row["dow_cos"] = np.cos(2 * np.pi * row["dayofweek"] / 7)
    row["month_sin"] = np.sin(2 * np.pi * row["month"] / 12)
    row["month_cos"] = np.cos(2 * np.pi * row["month"] / 12)
    row["week_sin"] = np.sin(2 * np.pi * row["weekofyear"] / 52)
    row["week_cos"] = np.cos(2 * np.pi * row["weekofyear"] / 52)
    row["t"] = len(hist)

    # ── Feriados ────────────────────────────────
    row["is_holiday"] = int(row["fecha_venta"].normalize() in holiday_dates)
    row["is_pre_holiday"] = int(
        (row["fecha_venta"] + pd.Timedelta(days=1)).normalize() in holiday_dates
    )
    row["is_post_holiday"] = int(
        (row["fecha_venta"] - pd.Timedelta(days=1)).normalize() in holiday_dates
    )

    # ── Clima ────────────────────────────────────
    for c in WEATHER_COLS:
        row[c] = safe_float(weather_vals.get(c, 0.0), 0.0)

    def safe_hist_col(df, col):
        if col not in df.columns:
            return pd.Series([0.0])
        s = pd.to_numeric(df[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
        if s.isna().all():
            return pd.Series([0.0])
        return s.fillna(s.median()).fillna(0.0)

    hist_prcp = safe_hist_col(hist, "prcp")
    hist_tmax = safe_hist_col(hist, "tmax")
    hist_tmin = safe_hist_col(hist, "tmin")

    row["llovio"] = int(row["prcp"] > 0)
    row["lluvia_fuerte"] = int(row["prcp"] > hist_prcp.quantile(0.75))
    row["calor_alto"] = int(row["tmax"] > hist_tmax.quantile(0.75))
    row["frio_bajo"] = int(row["tmin"] < hist_tmin.quantile(0.25))
    row["llovio_finsemana"] = row["llovio"] * row["is_weekend"]

    # Rolling climático
    for w in [3, 7]:
        for base_col, out_col in [
            ("prcp", f"prcp_roll_mean_{w}"),
            ("tavg", f"tavg_roll_mean_{w}"),
            ("wspd", f"wspd_roll_mean_{w}"),
        ]:
            hist_vals = safe_hist_col(hist, base_col).tolist()
            vals = hist_vals + [row[base_col]]
            row[out_col] = safe_float(pd.Series(vals[-w:]).mean(), 0.0)

    # ── Lags de ventas ───────────────────────────
    for lag in [1, 2, 3, 7, 14, 21, 28]:
        row[f"lag{lag}"] = safe_get_lag(sales, lag)

    # ── Ventanas móviles ─────────────────────────
    for w in [7, 14, 28]:
        row[f"roll_mean_{w}"] = safe_roll(sales, w, pd.Series.mean)
        row[f"roll_std_{w}"] = safe_roll(
            sales, w, lambda s: s.std(ddof=0) if len(s) > 1 else 0.0
        )
        row[f"roll_max_{w}"] = safe_roll(sales, w, pd.Series.max)
        row[f"roll_min_{w}"] = safe_roll(sales, w, pd.Series.min)
        row[f"roll_median_{w}"] = safe_roll(sales, w, pd.Series.median)

    # ── EMA ──────────────────────────────────────
    row["ema_7"] = safe_float(compute_ema_from_history(sales, 7), 0.0)
    row["ema_14"] = safe_float(compute_ema_from_history(sales, 14), 0.0)

    # ── Cambios (solo pasado) ────────────────────
    row["diff1"] = row["lag1"] - row["lag2"]
    row["diff7"] = row["lag1"] - row["lag7"]
    row["growth_1"] = row["lag1"] / (row["lag2"] + 1e-6)
    row["growth_7"] = row["lag1"] / (row["lag7"] + 1e-6)

    # ── Regímenes ────────────────────────────────
    row["weak_demand_regime"] = int(row["lag1"] <= 0.70 * (row["roll_median_14"] + 1e-6))

    hist_roll_std_7 = safe_hist_col(hist, "roll_std_7")
    row["high_volatility"] = int(row["roll_std_7"] > hist_roll_std_7.quantile(0.75))

    hist_diff1_abs = safe_hist_col(hist, "diff1").abs()
    row["shock_recent"] = int(abs(row["diff1"]) > hist_diff1_abs.quantile(0.85))

    # ── Ancla e intermitencia ────────────────────
    row["anchor_base"] = (
        0.50 * row["roll_median_7"]
        + 0.30 * row["roll_median_14"]
        + 0.20 * row["ema_7"]
    )
    if pd.isna(row["anchor_base"]) or row["anchor_base"] <= 0:
        row["anchor_base"] = max(row["lag1"], 1.0)

    row["low_demand_today"] = int(row["lag1"] <= 0.70 * (row["roll_median_14"] + 1e-6))
    row["relevant_demand_today"] = 1 - row["low_demand_today"]
    row["lag1_low"] = int(row["lag1"] <= 0.70 * (row["anchor_base"] + 1e-6))
    row["lag7_low"] = int(row["lag7"] <= 0.70 * (row["anchor_base"] + 1e-6))

    # Streak acumulada (se mantiene entre pasos recursivos vía hist)
    if "low_demand_streak" in hist.columns and len(hist) > 0:
        prev_streak = int(safe_float(hist.iloc[-1]["low_demand_streak"], 0))
    else:
        prev_streak = 0
    row["low_demand_streak"] = prev_streak + 1 if row["lag1_low"] == 1 else 0

    if "days_since_peak" in hist.columns and len(hist) > 0:
        prev_days_since_peak = int(safe_float(hist.iloc[-1]["days_since_peak"], 1))
    else:
        prev_days_since_peak = 1
    peak_threshold = safe_float(hist["ventas"].quantile(0.75), 0.0) if len(hist) > 0 else 0.0
    row["days_since_peak"] = 1 if row["lag1"] >= peak_threshold else prev_days_since_peak + 1

    row["positive_pressure"] = row["lag1"] / (row["anchor_base"] + 1e-6)
    prev_pp = [
        safe_float(v, 0.0)
        for v in (hist["positive_pressure"].tolist() if "positive_pressure" in hist.columns else [])
    ]
    row["positive_pressure_ema"] = float(
        pd.Series(prev_pp[-4:] + [row["positive_pressure"]]).ewm(span=5, adjust=False).mean().iloc[-1]
    )

    # Proxy ratio (nunca usa venta futura real)
    proxy_ratio = float(np.clip(row["lag1"] / (row["anchor_base"] + 1e-6), 0, 10))
    row["ratio_to_anchor"] = proxy_ratio
    row["ratio_to_anchor_log"] = np.log1p(proxy_ratio)

    # Placeholders de targets
    row["ventas"] = np.nan
    row["ventas_log"] = np.nan
    row["ratio_target"] = np.nan
    row["ratio_target_log"] = np.nan

    # Garantizar que todas las features existen
    for c in features_v22:
        if c not in row:
            row[c] = 0.0

    future_df = pd.DataFrame([row])
    for c in future_df.columns:
        if c != "fecha_venta":
            future_df[c] = pd.to_numeric(future_df[c], errors="coerce")
    future_df = future_df.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return future_df


def apply_single_calibration_v22(future_row_df: pd.DataFrame, pred_value: float, calibrator: dict) -> float:
    """
    Calibración por segmento (is_weekend × is_holiday).
    Idéntico a apply_single_calibration_v22() del notebook (celda 28).
    """
    tmp = future_row_df.copy()
    is_weekend = int(tmp.iloc[0].get("is_weekend", 0))
    is_holiday = int(tmp.iloc[0].get("is_holiday", 0))
    seg = f"{is_weekend}_{is_holiday}"
    mult = calibrator["seg_mult"].get(seg, calibrator["global_mult"])
    return max(pred_value * mult, 0.0)


def recursive_forecast_v22(
    history_df: pd.DataFrame,
    direct_model,
    ratio_model,
    global_model,
    blend_info: dict,
    calibrator: dict,
    tenant_id: int,
    weather_profile_dow: pd.DataFrame,
    holiday_dates: set,
    features_v22: list,
    horizon: int = 7,
) -> pd.DataFrame:
    """
    Forecast recursivo día a día.
    Idéntico a recursive_forecast_v22() del notebook (celda 28),
    con weather_profile_dow y holiday_dates como parámetros explícitos.
    """
    hist = history_df.copy().sort_values("fecha_venta").reset_index(drop=True)
    forecasts = []
    last_date = pd.to_datetime(hist["fecha_venta"]).max()

    for h in range(1, horizon + 1):
        future_date = last_date + pd.Timedelta(days=h)
        future_row = build_future_feature_row_v22(
            hist, future_date, tenant_id, weather_profile_dow, holiday_dates, features_v22
        )

        X_future = future_row[features_v22].copy()
        X_future = X_future.replace([np.inf, -np.inf], np.nan).fillna(0.0)

        pred_direct = np.expm1(direct_model.predict(X_future))[0]
        pred_ratio_log = np.expm1(ratio_model.predict(X_future))[0]
        pred_ratio = pred_ratio_log * future_row["anchor_base"].values[0]
        pred_global = np.expm1(global_model.predict(X_future))[0]

        pred_base = (
            blend_info["weights"]["pred_direct"] * pred_direct
            + blend_info["weights"]["pred_ratio"] * pred_ratio
            + blend_info["weights"]["pred_global"] * pred_global
        )

        pred_final = apply_single_calibration_v22(future_row, pred_base, calibrator)

        forecasts.append({
            "fecha_venta": future_date,
            "pred_final": pred_final,
        })

        # Incorporar predicción al historial para el siguiente paso (forecast recursivo)
        row_to_append = future_row.copy()
        row_to_append["ventas"] = pred_final
        row_to_append["ventas_log"] = np.log1p(pred_final)
        row_to_append["ratio_target"] = pred_final / (row_to_append["anchor_base"].values[0] + 1e-6)
        row_to_append["ratio_target_log"] = np.log1p(row_to_append["ratio_target"])
        hist = pd.concat([hist, row_to_append], ignore_index=True)

    return pd.DataFrame(forecasts)


# ─────────────────────────────────────────────
# CLASE PREDICTOR
# ─────────────────────────────────────────────

class TechHivePredictor:
    """
    Singleton que encapsula los modelos v22 y expone el método forecast().
    Los modelos se cargan UNA SOLA VEZ al instanciar (AppConfig.ready() o primer uso).
    """

    def __init__(self):
        self.features = FEATURES_V22
        self._load_models()
        self._init_holidays()
        self._init_weather()

    def _load_models(self):
        """Carga los 5 pkl y metadata_v22.json desde ml_models/."""
        try:
            with open(ML_DIR / "metadata_v22.json", encoding="utf-8") as f:
                metadata = json.load(f)

            # Los pkl contienen el CatBoostRegressor directamente
            self.magic_direct = joblib.load(ML_DIR / "magic_direct_v22.pkl")
            self.magic_ratio = joblib.load(ML_DIR / "magic_ratio_v22.pkl")
            self.pap_direct = joblib.load(ML_DIR / "pap_direct_v22.pkl")
            self.pap_ratio = joblib.load(ML_DIR / "pap_ratio_v22.pkl")
            self.global_model = joblib.load(ML_DIR / "global_model_v22.pkl")

            self.blend_magic = metadata["best_magic_v22"]
            self.blend_pap = metadata["best_pap_v22"]
            self.calibrator_magic = metadata["magic_calibrator_v22"]
            self.calibrator_pap = metadata["pap_calibrator_v22"]

            logger.info("TechHivePredictor: modelos v22 cargados OK")
        except Exception as exc:
            logger.error("TechHivePredictor: error al cargar modelos — %s", exc)
            raise

    def _init_holidays(self):
        hoy = date.today()
        years = list(range(hoy.year - 2, hoy.year + 3))
        ec = holidays_lib.country_holidays("EC", years=years)
        self.holiday_dates = set(pd.to_datetime(list(ec.keys())))
        logger.info("TechHivePredictor: feriados Ecuador cargados (%d fechas)", len(self.holiday_dates))

    def _init_weather(self):
        """
        Descarga el perfil climático histórico de Quito desde meteostat.
        Se usa para calcular los umbrales de lluvia/calor y el perfil por DOW.
        Si falla, usa ceros (el modelo puede funcionar igualmente).
        Compatible con meteostat 1.x (Daily class) y 2.x (daily function).
        """
        try:
            raw = self._fetch_weather_meteostat(datetime(2023, 1, 1), datetime.now())
            if raw is None or raw.empty:
                raise ValueError("meteostat no retornó datos para Quito")

            raw["fecha_venta"] = pd.to_datetime(raw["fecha_venta"]).dt.normalize()
            self._weather_raw = raw
            self.weather_profile_dow = build_weather_profile_by_dow(raw)
            logger.info(
                "TechHivePredictor: perfil climático cargado (%d días)", len(raw)
            )
        except Exception as exc:
            logger.warning(
                "TechHivePredictor: no se pudo cargar clima — %s. Usando ceros como fallback.",
                exc,
            )
            self._weather_raw = pd.DataFrame()
            self.weather_profile_dow = pd.DataFrame(
                {"dayofweek": range(7), **{c: [0.0] * 7 for c in WEATHER_COLS}}
            )

    def _fetch_weather_meteostat(self, start: datetime, end: datetime):
        """Intenta meteostat 1.x (Daily class) y luego 2.x (daily function)."""
        from meteostat import Point
        location = Point(QUITO_LAT, QUITO_LON, QUITO_ALT)

        # meteostat 1.x
        try:
            from meteostat import Daily
            raw = Daily(location, start, end).fetch().reset_index()
            raw = raw.rename(columns={"time": "fecha_venta"})
            return raw
        except ImportError:
            pass

        # meteostat 2.x
        from meteostat import daily as daily_fn
        result = daily_fn(location, start, end)
        df = result.fetch()
        if df is None or df.empty:
            return None
        df = df.reset_index()
        # columna de fecha puede ser 'time' o index de datetime
        if "time" in df.columns:
            df = df.rename(columns={"time": "fecha_venta"})
        elif df.index.name == "time":
            df = df.reset_index().rename(columns={"time": "fecha_venta"})
        else:
            df.columns.values[0] = "fecha_venta"
        return df

    def _get_history(self) -> pd.DataFrame:
        """
        Consulta ventas diarias del tenant activo (schema ya establecido por middleware)
        y fusiona con datos climáticos históricos.
        """
        from django.db import connection

        with connection.cursor() as cur:
            cur.execute(
                "SELECT fecha_venta, SUM(total) AS ventas "
                "FROM ventas_venta "
                "GROUP BY fecha_venta "
                "ORDER BY fecha_venta"
            )
            rows = cur.fetchall()

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows, columns=["fecha_venta", "ventas"])
        df["fecha_venta"] = pd.to_datetime(df["fecha_venta"]).dt.normalize()
        df["ventas"] = df["ventas"].astype(float)

        # Fusionar clima histórico real
        if not self._weather_raw.empty:
            weather = self._weather_raw[["fecha_venta"] + WEATHER_COLS].copy()
            df = df.merge(weather, on="fecha_venta", how="left")
            for c in WEATHER_COLS:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

        for c in WEATHER_COLS:
            if c not in df.columns:
                df[c] = 0.0

        # Pre-computar roll_std_7 y diff1 para que los umbrales sean más precisos
        df = df.sort_values("fecha_venta").reset_index(drop=True)
        df["roll_std_7"] = df["ventas"].rolling(7, min_periods=1).std(ddof=0).fillna(0.0)
        df["diff1"] = df["ventas"].diff(1).fillna(0.0)

        return df

    def forecast(self, tenant_slug: str, horizon: int = 7) -> list:
        """
        Genera predicciones de ventas diarias para los próximos `horizon` días.

        Args:
            tenant_slug: schema_name del tenant activo (ej: 'magic_world', 'papeleria')
            horizon: número de días a predecir (1-90)

        Returns:
            Lista de dicts: [{"fecha": "YYYY-MM-DD", "prediccion": float, "horizonte_dias": int}]

        Raises:
            ValueError: si el tenant no tiene modelo o el historial es insuficiente.
        """
        # Resolver tenant_id
        tenant_id = None
        slug_lower = tenant_slug.lower()
        for key, tid in TENANT_ID_MAP.items():
            if key in slug_lower:
                tenant_id = tid
                break

        if tenant_id is None:
            raise ValueError("Tenant no tiene modelo predictivo configurado")

        # Seleccionar modelos según tenant
        if tenant_id == 0:
            direct_model = self.magic_direct
            ratio_model = self.magic_ratio
            blend_info = self.blend_magic
            calibrator = self.calibrator_magic
        else:
            direct_model = self.pap_direct
            ratio_model = self.pap_ratio
            blend_info = self.blend_pap
            calibrator = self.calibrator_pap

        # Obtener y validar historial
        history_df = self._get_history()

        if history_df.empty:
            raise ValueError("No hay datos de ventas en este tenant")

        unique_days = history_df["fecha_venta"].nunique()
        if unique_days < MIN_HISTORY_DAYS:
            raise ValueError(
                f"Historial insuficiente: se requieren al menos {MIN_HISTORY_DAYS} días "
                f"de ventas para generar predicciones (actuales: {unique_days})"
            )

        # Forecast recursivo
        forecast_df = recursive_forecast_v22(
            history_df=history_df,
            direct_model=direct_model,
            ratio_model=ratio_model,
            global_model=self.global_model,
            blend_info=blend_info,
            calibrator=calibrator,
            tenant_id=tenant_id,
            weather_profile_dow=self.weather_profile_dow,
            holiday_dates=self.holiday_dates,
            features_v22=self.features,
            horizon=horizon,
        )

        return [
            {
                "fecha": row["fecha_venta"].strftime("%Y-%m-%d"),
                "prediccion": round(float(row["pred_final"]), 2),
                "horizonte_dias": i + 1,
            }
            for i, (_, row) in enumerate(forecast_df.iterrows())
        ]


# ─────────────────────────────────────────────
# SINGLETON
# ─────────────────────────────────────────────

_predictor_instance: TechHivePredictor | None = None


def get_predictor() -> TechHivePredictor:
    """Retorna el singleton del predictor. Crea una instancia si no existe."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = TechHivePredictor()
    return _predictor_instance
