import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple

import numpy as np
import joblib
import pandas as pd
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV, RepeatedStratifiedKFold
from sklearn.metrics import accuracy_score, f1_score
from sklearn.metrics.pairwise import rbf_kernel
from scipy.stats import chi2

def setup_logger(verbose: bool) -> logging.Logger:
    logger = logging.getLogger("baselines")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    if not logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

def mcnemar_test(y_true: np.ndarray, y_pred1: np.ndarray, y_pred2: np.ndarray) -> Tuple[np.ndarray, float, float]:
    """Computes McNemar's test for two models."""
    correct1 = (y_true == y_pred1)
    correct2 = (y_true == y_pred2)
    
    a = np.sum(correct1 & correct2)
    b = np.sum(correct1 & ~correct2)
    c = np.sum(~correct1 & correct2)
    d = np.sum(~correct1 & ~correct2)
    
    table = np.array([[a, b], [c, d]])
    
    if b + c == 0:
        statistic = 0.0
        p_value = 1.0
    else:
        statistic = (abs(b - c) - 1)**2 / (b + c)
        p_value = float(chi2.sf(statistic, df=1))
        
    return table, statistic, p_value

def main():
    parser = argparse.ArgumentParser(description="Train and evaluate classical baselines")
    parser.add_argument("--data-dir", type=str, default="data", help="Data directory")
    parser.add_argument("--model-dir", type=str, default="models", help="Models directory")
    parser.add_argument("--results-dir", type=str, default="results", help="Results directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--n-jobs", type=int, default=-1, help="Number of parallel jobs")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    logger = setup_logger(args.verbose)
    
    np.random.seed(args.seed)
    
    data_dir = Path(args.data_dir)
    model_dir = Path(args.model_dir)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Loading data...")
    try:
        X_train = np.load(data_dir / "X_train.npy")
        X_test = np.load(data_dir / "X_test.npy")
        y_train = np.load(data_dir / "y_train.npy")
        y_test = np.load(data_dir / "y_test.npy")
    except FileNotFoundError as e:
        logger.error(f"Failed to load data: {e}")
        return

    logger.info(f"Loaded data: X_train {X_train.shape}, X_test {X_test.shape}")
    
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=args.seed)
    
    models_to_evaluate = {
        "RBF-SVM": {
            "estimator": SVC(kernel='rbf', random_state=args.seed),
            "param_grid": {
                'C': [0.1, 1, 10, 100, 1000],
                'gamma': [1e-4, 1e-3, 1e-2, 1e-1, 1, 'scale']
            }
        },
        "Linear-SVM": {
            "estimator": SVC(kernel='linear', random_state=args.seed),
            "param_grid": {
                'C': [0.01, 0.1, 1, 10, 100]
            }
        },
        "Random-Forest": {
            "estimator": RandomForestClassifier(random_state=args.seed),
            "param_grid": {
                'n_estimators': [100, 300, 500],
                'max_depth': [None, 10, 20, 30]
            }
        },
        "k-NN": {
            "estimator": KNeighborsClassifier(),
            "param_grid": {
                'n_neighbors': [3, 5, 7, 11, 15]
            }
        }
    }
    
    results = []
    best_classical_model_name = None
    best_classical_acc = -1
    best_classical_preds = None
    
    for name, config in models_to_evaluate.items():
        logger.info(f"Training {name}...")
        grid = GridSearchCV(
            estimator=config["estimator"],
            param_grid=config["param_grid"],
            cv=cv,
            scoring='accuracy',
            n_jobs=args.n_jobs,
            verbose=1 if args.verbose else 0
        )
        grid.fit(X_train, y_train)
        
        best_params = grid.best_params_
        cv_mean = grid.cv_results_['mean_test_score'][grid.best_index_]
        cv_std = grid.cv_results_['std_test_score'][grid.best_index_]
        
        y_pred = grid.predict(X_test)
        test_acc = accuracy_score(y_test, y_pred)
        macro_f1 = f1_score(y_test, y_pred, average='macro')
        
        logger.info(f"{name}: Test Acc={test_acc:.4f}, CV={cv_mean:.4f} +/- {cv_std:.4f}")
        
        results.append({
            "model": name,
            "best_params": json.dumps(best_params),
            "cv_mean": cv_mean,
            "cv_std": cv_std,
            "test_acc": test_acc,
            "macro_f1": macro_f1
        })
        
        if test_acc > best_classical_acc:
            best_classical_acc = test_acc
            best_classical_model_name = name
            best_classical_preds = y_pred

    logger.info("Loading QSVC metrics...")
    try:
        with open(model_dir / "metrics.json", "r") as f:
            qsvc_metrics = json.load(f)
            
        results.append({
            "model": "QSVC",
            "best_params": "see config.json",
            "cv_mean": qsvc_metrics.get("cv_accuracy_mean", np.nan),
            "cv_std": qsvc_metrics.get("cv_accuracy_std", np.nan),
            "test_acc": qsvc_metrics.get("test_accuracy", np.nan),
            "macro_f1": qsvc_metrics.get("test_f1_macro", np.nan)
        })
    except FileNotFoundError:
        logger.warning("QSVC metrics.json not found.")

    df_results = pd.DataFrame(results)
    df_results.to_csv(results_dir / "baselines_comparison.csv", index=False)
    logger.info(f"Saved results to {results_dir / 'baselines_comparison.csv'}")

    logger.info("Running McNemar's test...")
    try:
        qsvc_model = joblib.load(model_dir / "qsvc_model.joblib")
        K_test = np.load(model_dir / "K_test.npy")
        y_pred_qsvc = qsvc_model.predict(K_test)
        
        table, chi2_stat, p_value = mcnemar_test(y_test, y_pred_qsvc, best_classical_preds)
        
        mcnemar_res = {
            "best_classical_model": best_classical_model_name,
            "contingency_table": table.tolist(),
            "chi2": float(chi2_stat),
            "p_value": float(p_value)
        }
        with open(results_dir / "mcnemar_result.json", "w") as f:
            json.dump(mcnemar_res, f, indent=4)
        logger.info(f"McNemar's test: p-value={p_value:.4f}")
    except Exception as e:
        logger.error(f"Failed to run McNemar's test: {e}")

    logger.info("Computing Kernel Alignment...")
    try:
        with open(model_dir / "config.json", "r") as f:
            config = json.load(f)
            hp = config.get("hyperparameters", config)
            if "gamma" in hp:
                gamma = hp["gamma"]
            else:
                gamma = 1.0
            
        K_train = np.load(model_dir / "K_train.npy")
        K_rbf = rbf_kernel(X_train, gamma=gamma)
        
        alignment = np.sum(K_train * K_rbf) / (np.linalg.norm(K_train, ord='fro') * np.linalg.norm(K_rbf, ord='fro'))
        
        alignment_res = {
            "quantum_bandwidth_gamma": float(gamma),
            "kernel_alignment": float(alignment)
        }
        with open(results_dir / "kernel_alignment.json", "w") as f:
            json.dump(alignment_res, f, indent=4)
        logger.info(f"Kernel alignment: {alignment:.4f}")
    except Exception as e:
        logger.error(f"Failed to compute Kernel Alignment: {e}")

    logger.info("Baselines script complete.")

if __name__ == "__main__":
    main()
