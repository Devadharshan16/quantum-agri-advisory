import argparse
import json
import logging
from pathlib import Path
from typing import Tuple, List, Dict, Any

import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedShuffleSplit

from qkernel import build_feature_map, compute_states, fidelity_kernel

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("learning_curve")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(ch)
    return logger

logger = setup_logger()

def load_data(data_dir: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    logger.info(f"Loading data from {data_dir}")
    X_train = np.load(data_dir / "X_train.npy")
    X_test = np.load(data_dir / "X_test.npy")
    y_train = np.load(data_dir / "y_train.npy")
    y_test = np.load(data_dir / "y_test.npy")
    return X_train, X_test, y_train, y_test

def load_config(config_path: Path) -> Dict[str, Any]:
    logger.info(f"Loading configuration from {config_path}")
    with open(config_path, "r") as f:
        return json.load(f)

def subsample_data(X: np.ndarray, y: np.ndarray, fraction: float, seed: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    if fraction >= 1.0:
        return X, y
    sss = StratifiedShuffleSplit(n_splits=1, test_size=1.0 - fraction, random_state=seed)
    train_index, _ = next(sss.split(X, y))
    return X[train_index], y[train_index]

def evaluate_quantum_svc(X_tr: np.ndarray, y_tr: np.ndarray, X_te: np.ndarray, y_te: np.ndarray,
                         num_qubits: int, reps: int, entanglement: str, gamma: float, C: float) -> float:
    fm = build_feature_map(num_qubits, reps, entanglement)
    train_states = compute_states(fm, X_tr * gamma)
    test_states = compute_states(fm, X_te * gamma)
    
    K_train = fidelity_kernel(train_states)
    K_test = fidelity_kernel(test_states, train_states)
    
    svc = SVC(kernel="precomputed", C=C, random_state=42)
    svc.fit(K_train, y_tr)
    return float(svc.score(K_test, y_te))

def plot_learning_curve(X_train: np.ndarray, y_train: np.ndarray,
                        X_test: np.ndarray, y_test: np.ndarray,
                        config: Dict[str, Any], assets_dir: Path) -> None:
    fractions = [0.25, 0.50, 0.75, 1.0]
    q_accs = []
    c_accs = []
    
    num_qubits = X_train.shape[1]
    hp = config.get("hyperparameters", config)
    reps = hp.get("reps", 2)
    entanglement = hp.get("entanglement", "full")
    gamma = hp.get("gamma", 0.1)
    C = hp.get("C", 10.0)
    
    logger.info("Starting Plot 1: Accuracy vs training-set size")
    for frac in fractions:
        logger.info(f"Evaluating fraction {frac}")
        X_sub, y_sub = subsample_data(X_train, y_train, frac, seed=42)
        
        # Quantum Model
        q_acc = evaluate_quantum_svc(X_sub, y_sub, X_test, y_test, num_qubits, reps, entanglement, gamma, C)
        q_accs.append(q_acc)
        
        # Classical Model (RBF)
        c_svc = SVC(kernel="rbf", C=C, gamma='scale', random_state=42)
        c_svc.fit(X_sub, y_sub)
        c_acc = float(c_svc.score(X_test, y_test))
        c_accs.append(c_acc)
        
    plt.figure(figsize=(8, 6))
    plt.plot(fractions, q_accs, marker='o', label='Quantum Kernel SVC')
    plt.plot(fractions, c_accs, marker='s', label='Classical RBF SVC')
    plt.xlabel('Fraction of Training Data')
    plt.ylabel('Test Accuracy')
    plt.title('Accuracy vs Training-Set Size')
    plt.legend()
    plt.grid(True)
    out_path = assets_dir / "learning_curve.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
    logger.info(f"Saved learning curve plot to {out_path}")

def plot_accuracy_vs_gamma(X_train: np.ndarray, y_train: np.ndarray,
                           X_test: np.ndarray, y_test: np.ndarray,
                           config: Dict[str, Any], assets_dir: Path) -> None:
    gammas = [0.01, 0.02, 0.05, 0.1, 0.15, 0.25, 0.5, 1.0]
    q_accs = []
    off_diag_means = []
    
    num_qubits = X_train.shape[1]
    hp = config.get("hyperparameters", config)
    reps = hp.get("reps", 2)
    entanglement = hp.get("entanglement", "full")
    C = hp.get("C", 10.0)
    
    logger.info("Starting Plot 2: Accuracy vs gamma")
    for g in gammas:
        logger.info(f"Evaluating gamma {g}")
        fm = build_feature_map(num_qubits, reps, entanglement)
        train_states = compute_states(fm, X_train * g)
        test_states = compute_states(fm, X_test * g)
        
        K_train = fidelity_kernel(train_states)
        K_test = fidelity_kernel(test_states, train_states)
        
        svc = SVC(kernel="precomputed", C=C, random_state=42)
        svc.fit(K_train, y_train)
        q_acc = float(svc.score(K_test, y_test))
        q_accs.append(q_acc)
        
        # Off-diagonal mean
        n = K_train.shape[0]
        off_diag_sum = np.sum(K_train) - np.trace(K_train)
        off_diag_mean = off_diag_sum / (n * (n - 1)) if n > 1 else 0.0
        off_diag_means.append(off_diag_mean)
        
    fig, ax1 = plt.subplots(figsize=(8, 6))
    
    color = 'tab:blue'
    ax1.set_xlabel('Gamma')
    ax1.set_ylabel('Test Accuracy', color=color)
    ax1.plot(gammas, q_accs, marker='o', color=color, label='Accuracy')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True)
    
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Off-diagonal Kernel Mean', color=color)
    ax2.plot(gammas, off_diag_means, marker='x', color=color, linestyle='--', label="Mean K(x, x')")
    ax2.tick_params(axis='y', labelcolor=color)
    
    fig.tight_layout()
    plt.title('Accuracy and Kernel Concentration vs Gamma')
    out_path = assets_dir / "accuracy_vs_gamma.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
    logger.info(f"Saved accuracy vs gamma plot to {out_path}")

def main() -> int:
    parser = argparse.ArgumentParser(description="Generate learning curves and kernel concentration plots.")
    parser.add_argument("--data-dir", type=str, default="data", help="Directory containing dataset")
    parser.add_argument("--model-dir", type=str, default="models", help="Directory containing model config")
    parser.add_argument("--assets-dir", type=str, default="assets", help="Directory to save plots")
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    model_dir = Path(args.model_dir)
    assets_dir = Path(args.assets_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    config_path = model_dir / "config.json"
    if not config_path.exists():
        logger.error(f"Config file not found at {config_path}")
        return 1
        
    try:
        X_train, X_test, y_train, y_test = load_data(data_dir)
        config = load_config(config_path)
    except Exception as e:
        logger.error(f"Failed to load data or config: {e}")
        return 1
        
    try:
        plot_learning_curve(X_train, y_train, X_test, y_test, config, assets_dir)
        plot_accuracy_vs_gamma(X_train, y_train, X_test, y_test, config, assets_dir)
    except Exception as e:
        logger.error(f"Error during plotting: {e}")
        return 1
        
    logger.info("All plots generated successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
