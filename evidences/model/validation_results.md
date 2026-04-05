# Resultados de Validación — Modelo V22

**Modelo:** CatBoost ensemble `v22_small_data_volatility_model`
**Fecha:** 2026-04-04
**Fuentes:** `metadata_v22.json`, `notebooks/ModeloPrediccionVentasFinalDjango.ipynb`

---

## 1. Métricas finales en test set

Evaluación sobre datos reales de ambos tenants.
Los datos de Papelería provienen del dataset de entrenamiento histórico; los de Magic World del CSV `backend/data/BD_Ventas_Magic.csv`.

| Tenant | RMSE | MAE | MAPE | Acc@MAPE | Acc@±20% | Modelo ganador |
|--------|------|-----|------|----------|---------|----------------|
| Magic World | **55.473** | 13.858 | **16.120%** | 83.880% | **80.00%** | ratio |
| Papelería Alfa & Omega | **10.253** | 7.874 | **14.875%** | 85.125% | **76.47%** | global |

**Fórmulas:**
- `RMSE = sqrt(mean((y_pred - y_real)^2))`
- `MAE = mean(|y_pred - y_real|)`
- `MAPE = mean(|y_pred - y_real| / y_real) × 100`
- `Acc@MAPE = 100 - MAPE`
- `Acc@±20% = fracción de predicciones con error < 20% del valor real`

---

## 2. Validación walk-forward — Modelo directo Papelería (5 folds)

Implementado en `notebooks/ModeloPrediccionVentasFinalDjango.ipynb` (celda walk-forward, antes del bloque de exportación).

**Configuración:**
- Método: `TimeSeriesSplit(n_splits=5)` sobre `pap_feat_v22`
- Variable target: `ventas_log` (log1p de ventas reales)
- Predicción: invertida con `np.expm1()` para evaluar en escala original
- Hiperparámetros del fold: igual a V22 directo (depth=4, l2_leaf_reg=10, iterations=1800, lr=0.01, random_seed=42)
- Métricas calculadas con las funciones `evaluate()` y `tolerance_accuracy()` del notebook

| Fold | N train | N test | RMSE | MAE | MAPE (%) | Acc ±20% |
|------|---------|--------|------|-----|----------|---------|
| 1 | ~520 | ~130 | — | — | — | — |
| 2 | ~650 | ~130 | — | — | — | — |
| 3 | ~780 | ~130 | — | — | — | — |
| 4 | ~910 | ~130 | — | — | — | — |
| 5 | ~1040 | ~130 | — | — | — | — |
| **Media ± Std** | — | — | — | — | — | — |

> **Nota:** Los valores exactos por fold se obtienen ejecutando el notebook.
> Ejecutar: `jupyter nbconvert --to notebook --execute notebooks/ModeloPrediccionVentasFinalDjango.ipynb`
> La celda walk-forward imprime la tabla completa con valores reales.

---

## 3. Evolución del modelo (versiones v1 → v22)

Documentado en `notebooks/MejorasModeloPrediccionVentasA.ipynb`.

| Hito | Mejora introducida | Efecto aproximado |
|------|-------------------|-------------------|
| v1–v5 | Features base: lags, calendario | Baseline funcional |
| v6–v10 | Integración Meteostat (clima Quito) | Reducción MAPE ~5% |
| v11–v15 | Features de régimen (volatilidad, demanda baja) | Mejora en días extremos |
| v16–v19 | Anchor/ratio cross-tenant | Mejor generalización |
| v20–v21 | Intermittency features | Mejor en demanda esporádica |
| **v22** | Tuning final + calibración por segmento | MAPE 16.12% / 14.87% |

> Todos los experimentos están en `notebooks/MejorasModeloPrediccionVentasA.ipynb` (8.3 MB).
> Los valores finales oficiales son los del `metadata_v22.json`, coincidentes con el `notebooks/ModeloPrediccionVentasFinalDjango.ipynb`.

---

## 4. Ensemble y calibración

### Proceso de selección del blend (optimización de pesos)

Para cada tenant, se prueba todas las combinaciones de pesos `(w_direct, w_ratio, w_global)` con suma = 1.0 y paso 0.1:
```
pred_blend = w_direct × pred_direct + w_ratio × pred_ratio + w_global × pred_global
```
Se elige la combinación que minimiza el score combinado `RMSE/10 + MAPE`.

**Resultados:**

| Tenant | w_direct | w_ratio | w_global | Score |
|--------|----------|---------|----------|-------|
| Magic World | 0.0 | **1.0** | 0.0 | 9.869 |
| Papelería | 0.0 | 0.0 | **1.0** | 17.923 |

### Calibración post-predicción

Multiplicador aplicado sobre la predicción blend, segmentado por `(is_weekend × is_holiday)`:

| Tenant | Segmento | Multiplicador |
|--------|----------|---------------|
| Magic World | global | 1.0750 |
| Magic World | día_laborable | 1.0700 |
| Magic World | fin_de_semana | 1.0800 |
| Papelería | global | 0.9126 |
| Papelería | día_laborable | 0.9401 |
| Papelería | día_laborable_feriado | 0.9251 |
| Papelería | fin_de_semana | 0.9200 |
| Papelería | fin_de_semana_feriado | 0.9200 |

---

## 5. Cómo reproducir las métricas

```bash
# Opción 1: leer directamente el metadata
cat backend/apps/prediccion/ml_models/metadata_v22.json | python -m json.tool

# Opción 2: exportar CSV
cd backend
python evidences/model/export_metrics.py
# → genera evidences/model/metrics_summary.csv

# Opción 3: ejecutar notebook completo
pip install jupyter catboost pandas numpy scikit-learn meteostat
jupyter nbconvert --to notebook --execute notebooks/ModeloPrediccionVentasFinalDjango.ipynb --output /tmp/executed.ipynb
```

---

## 6. Archivos del modelo en el repositorio

| Archivo | Tamaño aprox. | Descripción |
|---------|---------------|-------------|
| `backend/apps/prediccion/ml_models/magic_direct_v22.pkl` | ~MB | Magic World — modelo directo |
| `backend/apps/prediccion/ml_models/magic_ratio_v22.pkl` | ~MB | Magic World — modelo ratio |
| `backend/apps/prediccion/ml_models/pap_direct_v22.pkl` | ~MB | Papelería — modelo directo |
| `backend/apps/prediccion/ml_models/pap_ratio_v22.pkl` | ~MB | Papelería — modelo ratio |
| `backend/apps/prediccion/ml_models/global_model_v22.pkl` | ~MB | Modelo global cross-tenant |
| `backend/apps/prediccion/ml_models/metadata_v22.json` | 134 líneas | Configuración, pesos, métricas |
