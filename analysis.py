"""Clean machine-readable hospital rates and quantify price variation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


def make_demo_rates(seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    hospitals = [f"TN Medical Center {i:02d}" for i in range(16)]
    procedures = {"45378": 2300, "70553": 1850, "27447": 31000, "43239": 2900}
    payers = ["Blue Cross", "Aetna", "Cigna", "Self Pay"]
    rows = []
    for i, hospital in enumerate(hospitals):
        rural = i % 4 == 0
        beds = int(rng.integers(35, 650))
        for code, base in procedures.items():
            for payer in payers:
                multiplier = (0.83 if payer == "Self Pay" else 1.0) * (0.90 if rural else 1.05)
                price = base * multiplier * rng.lognormal(0, 0.23)
                rows.append((hospital, code, payer, f"${price:,.2f}", rural, beds))
    rows += [rows[0], rows[5]]
    rows[9] = (*rows[9][:3], "Not Available", *rows[9][4:])
    return pd.DataFrame(rows, columns=["hospital", "procedure_code", "payer", "negotiated_rate", "rural", "beds"])


def clean_rates(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    required = {"hospital", "procedure_code", "payer", "negotiated_rate", "rural", "beds"}
    missing = required.difference(raw.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    data = raw.copy()
    before = len(data)
    data["rate"] = pd.to_numeric(
        data["negotiated_rate"].astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce"
    )
    invalid = int(data["rate"].isna().sum())
    data["payer"] = data["payer"].str.strip().str.title()
    data = data.dropna(subset=["rate"])
    data = data.loc[data["rate"].between(1, 1_000_000)]
    duplicate_mask = data.duplicated(["hospital", "procedure_code", "payer"], keep="first")
    duplicates = int(duplicate_mask.sum())
    data = data.loc[~duplicate_mask].copy()
    return data, {"input_rows": before, "invalid_rates": invalid, "duplicates_removed": duplicates, "clean_rows": len(data)}


def analyze_variation(clean: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    summary = clean.groupby("procedure_code")["rate"].agg(["count", "median", "min", "max"]).reset_index()
    summary["max_to_min_ratio"] = summary["max"] / summary["min"]
    y = np.log(clean["rate"].to_numpy())
    x = np.column_stack([
        np.ones(len(clean)), clean["rural"].astype(int), np.log1p(clean["beds"]),
        pd.get_dummies(clean["procedure_code"], drop_first=True, dtype=float).to_numpy(),
        pd.get_dummies(clean["payer"], drop_first=True, dtype=float).to_numpy(),
    ])
    beta = np.linalg.pinv(x.T @ x) @ x.T @ y
    drivers = {
        "rural_adjusted_pct": float(100 * (np.exp(beta[1]) - 1)),
        "bed_count_elasticity": float(beta[2]),
        "median_max_to_min_ratio": float(summary["max_to_min_ratio"].median()),
    }
    return summary, drivers


def payer_price_index(clean: pd.DataFrame) -> pd.DataFrame:
    """Compare payer rates after normalizing within procedure."""
    data = clean.copy()
    procedure_median = data.groupby("procedure_code")["rate"].transform("median")
    data["price_index"] = data["rate"] / procedure_median
    return (
        data.groupby("payer", as_index=False)
        .agg(median_price_index=("price_index", "median"), observations=("price_index", "size"))
        .sort_values("median_price_index", ascending=False)
    )


def hospital_outliers(clean: pd.DataFrame, threshold: float = 1.5) -> pd.DataFrame:
    """Identify unusually high prices relative to the procedure/payer median."""
    data = clean.copy()
    benchmark = data.groupby(["procedure_code", "payer"])["rate"].transform("median")
    data["benchmark_rate"] = benchmark
    data["relative_to_benchmark"] = data["rate"] / benchmark
    return data.loc[data["relative_to_benchmark"] >= threshold].sort_values("relative_to_benchmark", ascending=False)


def bootstrap_rural_difference(clean: pd.DataFrame, seed: int = 19, draws: int = 2000) -> dict[str, float]:
    """Bootstrap the rural-versus-urban median log-price difference."""
    data = clean.assign(log_rate=np.log(clean["rate"]))
    rural = data.loc[data["rural"], "log_rate"].to_numpy()
    urban = data.loc[~data["rural"], "log_rate"].to_numpy()
    rng = np.random.default_rng(seed)
    estimates = np.empty(draws)
    for index in range(draws):
        estimates[index] = np.median(rng.choice(rural, len(rural), replace=True)) - np.median(rng.choice(urban, len(urban), replace=True))
    low, high = np.quantile(100 * (np.exp(estimates) - 1), [0.025, 0.975])
    return {"median_difference_pct": float(100 * (np.exp(np.median(rural) - np.median(urban)) - 1)), "ci_low": float(low), "ci_high": float(high)}


def main() -> None:
    out = Path(__file__).parent / "outputs"
    out.mkdir(exist_ok=True)
    clean, quality = clean_rates(make_demo_rates())
    summary, drivers = analyze_variation(clean)
    clean.to_csv(out / "clean_rates.csv", index=False)
    summary.to_csv(out / "procedure_variation.csv", index=False)
    payer_price_index(clean).to_csv(out / "payer_price_index.csv", index=False)
    hospital_outliers(clean).to_csv(out / "high_price_outliers.csv", index=False)
    result = {"data_quality": quality, "modeled_drivers": drivers, "rural_bootstrap": bootstrap_rural_difference(clean)}
    (out / "findings.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
