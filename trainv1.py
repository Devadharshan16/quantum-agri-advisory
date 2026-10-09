#!/usr/bin/env python3
"""
QSVC training: quantum fidelity kernel + classical SVM (22 crops, 7 qubits).

Key design choices
------------------
* Statevectors are simulated ONCE per sample (O(N) circuits) and the fidelity
  kernel K_ij = |<psi_i|psi_j>|^2 is a single matrix product. This is
  numerically identical to the noiseless compute-uncompute kernel but takes
  seconds instead of ~80 minutes, and exploits K_ij = K_ji for free.
* Hyperparameters (reps, bandwidth gamma, SVM C) are selected by stratified
  CV on the training set only. The test set is touched once at the end.
* A classical RBF-SVM baseline is reported for context.

Assumption: the input features were scaled by data_prep.py (e.g. MinMax).
Bandwidth `gamma` multiplies those scaled features before encoding.
"""
from __future__ import annotations

import argparse
import itertools
import json
import logging
import platform
import sys
import time
from pathlib import Path
from typing import Sequence

import joblib
import numpy as np
import qiskit
import sklearn
from joblib import Parallel, delayed
from qiskit.circuit.library import ZZFeatureMap
from qiskit.quantum_info import Statevector
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import StratifiedKFold
from sklearn.svm import SVC

log = logging.getLogger("qsvc")


# --------------------------------------------------------------------------- #
# Quantum kernel
# --------------------------------------------------------------------------- #
def build_feature_map(n_qubits: int, reps: int, entanglement: str) -> ZZFeatureMap:
    return ZZFeatureMap(feature_dimension=n_qubits, reps=reps, entanglement=entanglement)


def _encode_chunk(circuit: ZZFeatureMap, X_chunk: np.ndarray) -> np.ndarray:
    out = np.empty((len(X_chunk), 2 ** circuit.num_qubits), dtype=np.complex128)
    for k, x in enumerate(X_chunk):
        out[k] = Statevector(circuit.assign_parameters(x.tolist())).data
    return out


def compute_states(
    circuit: ZZFeatureMap, X: np.ndarray, n_jobs: int = -1, chunk_size: int = 32
) -> np.ndarray:
    """Simulate |psi(x)> for every row of X. Returns array (N, 2**n_qubits)."""
    chunks = [X[i : i + chunk_size] for i in range(0, len(X), chunk_size)]
    parts = Parallel(n_jobs=n_jobs)(delayed(_encode_chunk)(circuit, c) for c in chunks)
    return np.vstack(parts)


def fidelity_kernel(A: np.ndarray, B: np.ndarray | None = None) -> np.ndarray:
    """K[i, j] = |<A_i|B_j>|^2. If B is None the kernel is symmetrised, diag = 1."""
    symmetric = B is None
    K = np.abs(A.conj() @ (A if symmetric else B).T) ** 2
    if symmetric:
        K = (K + K.T) / 2.0
        np.fill_diagonal(K, 1.0)
    return K


def kernel_diagnostics(K: np.ndarray) -> dict:
    off = K[~np.eye(len(K), dtype=bool)]
    return {
        "offdiag_mean": float(off.mean()),
        "offdiag_std": float(off.std()),
        "min_eigenvalue": float(np.linalg.eigvalsh(K).min()),
    }


# --------------------------------------------------------------------------- #
# Model selection
# --------------------------------------------------------------------------- #
def cv_score(K: np.ndarray, y: np.ndarray, C: float, folds: int, seed: int) -> tuple[float, float]:
    skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    scores = []
    for tr, va in skf.split(K, y):
        clf = SVC(kernel="precomputed", C=C)
        clf.fit(K[np.ix_(tr, tr)], y[tr])
        scores.append(clf.score(K[np.ix_(va, tr)], y[va]))
    return float(np.mean(scores)), float(np.std(scores))


# --------------------------------------------------------------------------- #
# I/O helpers
# --------------------------------------------------------------------------- #
def require(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return path


def load_data(data_dir: Path, model_dir: Path):
    X_train = np.load(require(data_dir / "X_train_scaled.npy"))
    X_test = np.load(require(data_dir / "X_test_scaled.npy"))
    y_train = np.load(require(data_dir / "y_train.npy"))
    y_test = np.load(require(data_dir / "y_test.npy"))
    encoder = joblib.load(require(model_dir / "label_encoder.joblib"))

    if X_train.shape[1] != X_test.shape[1]:
        raise ValueError("Train/test feature dimensions differ.")
    if len(X_train) != len(y_train) or len(X_test) != len(y_test):
        raise ValueError("Feature/label length mismatch.")
    if not (np.isfinite(X_train).all() and np.isfinite(X_test).all()):
        raise ValueError("Non-finite values in features.")
    lo, hi = float(X_train.min()), float(X_train.max())
    log.info("Feature range after scaling: [%.3f, %.3f]", lo, hi)
    if hi - lo > 2 * np.pi:
        log.warning("Features span more than 2*pi; expect a very sharp kernel.")
    return X_train, X_test, y_train, y_test, encoder


def parse_floats(s: str) -> list[float]:
    return [float(v) for v in s.split(",")]


def parse_ints(s: str) -> list[int]:
    return [int(v) for v in s.split(",")]


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def run(args: argparse.Namespace) -> None:
    data_dir, model_dir = Path(args.data_dir), Path(args.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    np.random.seed(args.seed)

    log.info("[1/5] Loading data")
    X_train, X_test, y_train, y_test, encoder = load_data(data_dir, model_dir)
    n_classes, n_qubits = len(encoder.classes_), X_train.shape[1]
    log.info("train=%s test=%s classes=%d qubits=%d", X_train.shape, X_test.shape, n_classes, n_qubits)
    if np.bincount(y_train).min() < args.folds:
        raise ValueError("Smallest class has fewer samples than CV folds.")

    # Classical baseline (context for the quantum result)
    base = SVC(kernel="rbf", C=10.0, gamma="scale").fit(X_train, y_train)
    baseline_acc = accuracy_score(y_test, base.predict(X_test))
    log.info("Classical RBF-SVM baseline test accuracy: %.1f%%", baseline_acc * 100)

    log.info("[2/5] Hyperparameter search (stratified %d-fold CV on train only)", args.folds)
    best: dict = {"cv": -1.0}
    t0 = time.perf_counter()
    for reps, gamma in itertools.product(args.reps, args.gammas):
        fm = build_feature_map(n_qubits, reps, args.entanglement)
        t = time.perf_counter()
        S_train = compute_states(fm, X_train * gamma, n_jobs=args.n_jobs)
        K_train = fidelity_kernel(S_train)
        diag = kernel_diagnostics(K_train)
        log.info(
            "reps=%d gamma=%.2f | kernel %.1fs | offdiag mean=%.4f std=%.4f min_eig=%.2e",
            reps, gamma, time.perf_counter() - t,
            diag["offdiag_mean"], diag["offdiag_std"], diag["min_eigenvalue"],
        )
        for C in args.Cs:
            mean, std = cv_score(K_train, y_train, C, args.folds, args.seed)
            log.info("    C=%-7g CV acc = %.3f +/- %.3f", C, mean, std)
            if mean > best["cv"]:
                best = dict(cv=mean, cv_std=std, reps=reps, gamma=gamma, C=C,
                            fm=fm, S_train=S_train, K_train=K_train, diag=diag)
    log.info("Search done in %.1fs", time.perf_counter() - t0)
    log.info("Best: reps=%d gamma=%.2f C=%g (CV %.3f)", best["reps"], best["gamma"], best["C"], best["cv"])

    log.info("[3/5] Computing test kernel for the selected configuration")
    S_test = compute_states(best["fm"], X_test * best["gamma"], n_jobs=args.n_jobs)
    K_test = fidelity_kernel(S_test, best["S_train"])

    log.info("[4/5] Fitting final SVM on full training set")
    svc = SVC(kernel="precomputed", C=best["C"]).fit(best["K_train"], y_train)
    train_acc = accuracy_score(y_train, svc.predict(best["K_train"]))
    y_pred = svc.predict(K_test)
    test_acc = accuracy_score(y_test, y_pred)
    log.info("Train acc %.1f%% | CV acc %.1f%% | Test acc %.1f%% | baseline %.1f%%",
             train_acc * 100, best["cv"] * 100, test_acc * 100, baseline_acc * 100)
    log.info("\n%s", classification_report(
        y_test, y_pred, labels=list(range(n_classes)),
        target_names=encoder.classes_, digits=2, zero_division=0))

    log.info("[5/5] Saving artifacts to %s", model_dir)
    joblib.dump(svc, model_dir / "qsvc_model.joblib")
    np.save(model_dir / "K_train.npy", best["K_train"])
    np.save(model_dir / "K_test.npy", K_test)
    np.save(model_dir / "train_states.npy", best["S_train"])  # needed for inference
    np.save(model_dir / "X_train_kernel.npy", X_train)

    metrics = {
        "model_type": "QSVC (exact statevector fidelity kernel + SVM)",
        "train_accuracy": float(train_acc),
        "cv_accuracy_mean": best["cv"],
        "cv_accuracy_std": best["cv_std"],
        "test_accuracy": float(test_acc),
        "classical_rbf_baseline_test_accuracy": float(baseline_acc),
        "hyperparameters": {"reps": best["reps"], "gamma": best["gamma"], "C": best["C"],
                            "entanglement": args.entanglement},
        "kernel_diagnostics": best["diag"],
        "num_qubits": n_qubits,
        "num_classes": n_classes,
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "kernel": "|<psi(x)|psi(x')>|^2, noiseless statevector simulation",
        "trainable_quantum_params": 0,
        "seed": args.seed,
        "versions": {"python": platform.python_version(), "qiskit": qiskit.__version__,
                     "sklearn": sklearn.__version__, "numpy": np.__version__},
        "crops": list(encoder.classes_),
    }
    with open(model_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    log.info("Done.")


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data-dir", default="data")
    p.add_argument("--model-dir", default="models")
    p.add_argument("--reps", type=parse_ints, default=[1, 2], help="comma-separated, e.g. 1,2")
    p.add_argument("--gammas", type=parse_floats, default=[0.1, 0.25, 0.5, 1.0],
                   help="feature bandwidth multipliers")
    p.add_argument("--Cs", type=parse_floats, default=[1, 10, 100, 1000])
    p.add_argument("--entanglement", default="full", choices=["full", "linear", "circular"])
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--n-jobs", type=int, default=-1)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )
    try:
        run(args)
    except (FileNotFoundError, ValueError) as exc:
        log.error("%s", exc)
        return 1
    except Exception:
        log.exception("Unexpected failure")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
