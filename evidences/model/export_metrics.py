#!/usr/bin/env python3
"""
Script: export_metrics.py
Propósito: Regenerar evidences/model/metrics_summary.csv desde metadata_v22.json

Uso:
    cd backend
    python ../evidences/model/export_metrics.py

Salida:
    ../evidences/model/metrics_summary.csv  (sobreescribe)
    Imprime resumen en consola
"""

import json
import csv
import os
from pathlib import Path

# ── Rutas ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
METADATA_PATH = REPO_ROOT / "backend" / "apps" / "prediccion" / "ml_models" / "metadata_v22.json"
OUTPUT_CSV = SCRIPT_DIR / "metrics_summary.csv"

TENANT_NAMES = {
    "magic": ("Magic World", "magic_world"),
    "pap":   ("Papelería Alfa & Omega", "papeleria"),
}

BLEND_MODELS = {
    "magic": "ratio",   # pred_ratio=1.0
    "pap":   "global",  # pred_global=1.0
}


def main():
    if not METADATA_PATH.exists():
        print(f"ERROR: No se encontró {METADATA_PATH}")
        print("Asegúrate de ejecutar desde la raíz del repo o desde backend/")
        return 1

    with open(METADATA_PATH, encoding="utf-8") as f:
        meta = json.load(f)

    version = meta.get("version", "unknown")
    metrics = meta.get("metrics", {})
    n_features = len(meta.get("features_v22", []))

    rows = []
    for key, (display_name, slug) in TENANT_NAMES.items():
        m = metrics.get(key, {})
        rows.append({
            "tenant":             display_name,
            "tenant_slug":        slug,
            "model_version":      version,
            "rmse":               round(m.get("rmse", 0), 3),
            "mae":                round(m.get("mae", 0), 3),
            "mape_pct":           round(m.get("mape", 0), 3),
            "accuracy_mape_pct":  round(m.get("accuracy_mape", 0), 3),
            "accuracy_20_pct":    round(m.get("accuracy_20", 0), 3),
            "blend_model":        BLEND_MODELS[key],
            "n_features":         n_features,
            "source":             "metadata_v22.json",
        })

    fieldnames = [
        "tenant", "tenant_slug", "model_version",
        "rmse", "mae", "mape_pct", "accuracy_mape_pct", "accuracy_20_pct",
        "blend_model", "n_features", "source",
    ]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n{'='*60}")
    print(f"  Métricas exportadas → {OUTPUT_CSV}")
    print(f"{'='*60}")
    print(f"  Versión del modelo : {version}")
    print(f"  Nº de features     : {n_features}")
    print(f"  Tenants            : {len(rows)}")
    print(f"{'='*60}\n")
    print(f"{'Tenant':<30} {'RMSE':>8} {'MAPE%':>8} {'Acc±20%':>9}")
    print(f"{'-'*60}")
    for r in rows:
        print(f"{r['tenant']:<30} {r['rmse']:>8.3f} {r['mape_pct']:>7.3f}% {r['accuracy_20_pct']:>8.3f}%")
    print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":
    exit(main())
