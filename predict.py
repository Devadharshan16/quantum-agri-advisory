#!/usr/bin/env python3
"""
Quantum Agricultural Advisory — Inference CLI (TASK 8).

Loads saved QSVC artifacts, accepts raw feature input (CSV or interactive),
computes the quantum kernel vector against saved training states, and
outputs the predicted crop plus top-3 class probabilities.

Probabilities come from SVC.decision_function → softmax (not calibrated;
for proper calibration use CalibratedClassifierCV at training time).
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Sequence

import joblib
import numpy as np
import pandas as pd

log = logging.getLogger("predict")

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
FEATURE_RANGES = {
    "N": (0, 140), "P": (5, 145), "K": (5, 205),
    "temperature": (8, 44), "humidity": (14, 100),
    "ph": (3.5, 9.9), "rainfall": (20, 300),
}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def softmax(x: np.ndarray) -> np.ndarray:
    """Row-wise softmax."""
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


def require(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return path


def validate_input(df: pd.DataFrame) -> pd.DataFrame:
    """Check columns, types, and ranges."""
    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}. Expected: {FEATURES}")
    df = df[FEATURES].copy()
    for col in FEATURES:
        if not np.issubdtype(df[col].dtype, np.number):
            raise ValueError(f"Column '{col}' is not numeric.")
        lo, hi = FEATURE_RANGES[col]
        oob = ((df[col] < lo) | (df[col] > hi)).sum()
        if oob > 0:
            log.warning("Column '%s': %d values outside expected range [%s, %s]", col, oob, lo, hi)
    return df


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #
def load_pipeline(model_dir: Path) -> dict:
    """Load all saved artifacts."""
    svc = joblib.load(require(model_dir / "qsvc_model.joblib"))
    std_scaler = joblib.load(require(model_dir / "standard_scaler.joblib"))
    mm_scaler = joblib.load(require(model_dir / "minmax_scaler.joblib"))
    encoder = joblib.load(require(model_dir / "label_encoder.joblib"))
    train_states = np.load(require(model_dir / "train_states.npy"))
    with open(require(model_dir / "config.json")) as f:
        config = json.load(f)
    with open(require(model_dir / "data_meta.json")) as f:
        meta = json.load(f)

    # Rebuild the quantum kernel components
    from qkernel import build_feature_map, compute_states, fidelity_kernel
    fm = build_feature_map(
        n_qubits=meta["num_qubits"],
        reps=config["hyperparameters"]["reps"],
        entanglement=config["hyperparameters"]["entanglement"],
    )

    return {
        "svc": svc, "std_scaler": std_scaler, "mm_scaler": mm_scaler,
        "encoder": encoder, "train_states": train_states, "config": config,
        "meta": meta, "feature_map": fm,
        "gamma": config["hyperparameters"]["gamma"],
        "compute_states": compute_states, "fidelity_kernel": fidelity_kernel,
    }


# --------------------------------------------------------------------------- #
# Prediction
# --------------------------------------------------------------------------- #
def predict_crops(pipeline: dict, df_raw: pd.DataFrame) -> pd.DataFrame:
    """Run the full inference pipeline. Returns DataFrame with predictions."""
    X_raw = df_raw[FEATURES].values.astype(np.float64)

    # 1. StandardScaler
    X_std = pipeline["std_scaler"].transform(X_raw)
    # 2. MinMaxScaler to [0, pi]
    X_scaled = pipeline["mm_scaler"].transform(X_std)
    # 3. Clip to [0, pi]
    X_scaled = np.clip(X_scaled, 0, np.pi)
    # 4. Apply gamma bandwidth
    X_gamma = X_scaled * pipeline["gamma"]
    # 5. Compute statevectors
    states = pipeline["compute_states"](pipeline["feature_map"], X_gamma, n_jobs=1)
    # 6. Kernel vector against training states
    K = pipeline["fidelity_kernel"](states, pipeline["train_states"])
    # 7. SVM prediction
    y_pred = pipeline["svc"].predict(K)
    crops = pipeline["encoder"].inverse_transform(y_pred)

    # 8. Top-3 probabilities from decision_function -> softmax
    dec = pipeline["svc"].decision_function(K)
    if dec.ndim == 1:
        probs = softmax(dec.reshape(1, -1))
    else:
        probs = softmax(dec)

    results = []
    classes = pipeline["encoder"].classes_
    for i in range(len(X_raw)):
        top3_idx = np.argsort(probs[i])[::-1][:3]
        top3 = [(classes[j], float(probs[i, j])) for j in top3_idx]
        results.append({
            "predicted_crop": crops[i],
            "top1": top3[0][0], "top1_prob": f"{top3[0][1]:.3f}",
            "top2": top3[1][0], "top2_prob": f"{top3[1][1]:.3f}",
            "top3": top3[2][0], "top3_prob": f"{top3[2][1]:.3f}",
        })

    return pd.DataFrame(results)


# --------------------------------------------------------------------------- #
# Interactive mode
# --------------------------------------------------------------------------- #
def interactive_mode(pipeline: dict) -> None:
    """Prompt user for feature values and predict."""
    print("\n" + "=" * 60)
    print("  QUANTUM AGRICULTURAL ADVISORY SYSTEM")
    print("  Powered by QSVC (Quantum Kernel SVM)")
    print("  Course: 23CSE463 Quantum Computing — Amrita Chennai")
    print("=" * 60)

    while True:
        print("\n  -- Enter your farm conditions --")
        values = {}
        for feat in FEATURES:
            lo, hi = FEATURE_RANGES[feat]
            while True:
                try:
                    v = float(input(f"    {feat:15s} [{lo}-{hi}]: "))
                    if lo <= v <= hi:
                        values[feat] = v
                        break
                    print(f"      -> Enter a value between {lo} and {hi}")
                except ValueError:
                    print("      -> Please enter a number")

        df = pd.DataFrame([values])
        result = predict_crops(pipeline, df)
        row = result.iloc[0]

        print("\n" + "=" * 60)
        print(f"  RECOMMENDED CROP: {row['predicted_crop'].upper()}")
        print("=" * 60)
        print(f"  Top 3 predictions:")
        print(f"    1. {row['top1']:15s}  (confidence: {row['top1_prob']})")
        print(f"    2. {row['top2']:15s}  (confidence: {row['top2_prob']})")
        print(f"    3. {row['top3']:15s}  (confidence: {row['top3_prob']})")

        again = input("\n  Try another scenario? [y/n]: ").strip().lower()
        if again != "y":
            break

    print("\nThank you for using the Quantum Agricultural Advisory System!")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--model-dir", default="models", help="Directory with saved artifacts")
    p.add_argument("--input-csv", default=None, help="CSV file with raw features (batch mode)")
    p.add_argument("--output-csv", default=None, help="Output CSV (batch mode)")
    p.add_argument("--interactive", action="store_true", help="Interactive CLI mode")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )

    try:
        model_dir = Path(args.model_dir)
        log.info("Loading pipeline from %s", model_dir)
        pipeline = load_pipeline(model_dir)
        log.info("Pipeline loaded (qubits=%d, gamma=%.3f, reps=%d, C=%g)",
                 pipeline["meta"]["num_qubits"], pipeline["gamma"],
                 pipeline["config"]["hyperparameters"]["reps"],
                 pipeline["config"]["hyperparameters"]["C"])

        if args.input_csv:
            log.info("Batch mode: reading %s", args.input_csv)
            df_in = pd.read_csv(args.input_csv)
            df_in = validate_input(df_in)
            results = predict_crops(pipeline, df_in)
            out_path = args.output_csv or "predictions.csv"
            results.to_csv(out_path, index=False)
            log.info("Predictions saved to %s", out_path)
            print(results.to_string(index=False))
        elif args.interactive:
            interactive_mode(pipeline)
        else:
            # Default: interactive
            interactive_mode(pipeline)

    except FileNotFoundError as exc:
        log.error("%s", exc)
        log.error("Run the training pipeline first: python data_prep.py && python trainv2.py")
        return 1
    except Exception:
        log.exception("Unexpected failure")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
