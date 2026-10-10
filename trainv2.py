import argparse
import json
import logging
import platform
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

import numpy as np
import qiskit
import sklearn
import pandas as pd
from joblib import dump, load, Parallel, delayed
from sklearn.model_selection import StratifiedKFold, RepeatedStratifiedKFold
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

from qkernel import build_feature_map, compute_states, fidelity_kernel, kernel_diagnostics

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Quantum SVM Training with Nested CV")
    parser.add_argument("--data-dir", type=Path, default=Path("data"), help="Data directory")
    parser.add_argument("--model-dir", type=Path, default=Path("models"), help="Models directory")
    parser.add_argument("--results-dir", type=Path, default=Path("results"), help="Results directory")
    parser.add_argument("--gammas", type=str, default="0.02,0.05,0.1,0.15,0.25,0.5")
    parser.add_argument("--reps", type=str, default="1,2,3")
    parser.add_argument("--entanglements", type=str, default="full,linear,circular")
    parser.add_argument("--Cs", type=str, default="0.1,1,10,100,1000")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-jobs", type=int, default=1)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()

def get_entanglement_complexity(ent: str) -> int:
    # linear < circular < full
    if ent == 'linear': return 1
    if ent == 'circular': return 2
    if ent == 'full': return 3
    return 4

def evaluate_config_on_splits(y_train: np.ndarray, K_full: np.ndarray, C: float, splits: List[Tuple[np.ndarray, np.ndarray]]) -> Tuple[float, float, float]:
    scores = []
    for train_idx, test_idx in splits:
        K_train = K_full[np.ix_(train_idx, train_idx)]
        K_test = K_full[np.ix_(test_idx, train_idx)]
        y_train_split = y_train[train_idx]
        y_test_split = y_train[test_idx]
        
        clf = SVC(kernel='precomputed', C=C)
        clf.fit(K_train, y_train_split)
        preds = clf.predict(K_test)
        scores.append(accuracy_score(y_test_split, preds))
    
    mean_acc = float(np.mean(scores))
    std_acc = float(np.std(scores))
    se_acc = std_acc / np.sqrt(len(splits))
    return mean_acc, std_acc, se_acc

def select_best_config(y_train: np.ndarray, K_dict: Dict, C_list: List[float], splits: List[Tuple[np.ndarray, np.ndarray]]) -> Tuple[Dict[str, Any], pd.DataFrame]:
    results = []
    for (reps, ent, gamma), (K_full, _) in K_dict.items():
        for C in C_list:
            mean_acc, std_acc, se_acc = evaluate_config_on_splits(y_train, K_full, C, splits)
            results.append({
                'reps': reps,
                'entanglement': ent,
                'gamma': gamma,
                'C': C,
                'mean_acc': mean_acc,
                'std_acc': std_acc,
                'se_acc': se_acc
            })
    
    df = pd.DataFrame(results)
    df = df.sort_values(by='mean_acc', ascending=False).reset_index(drop=True)
    
    best_mean = df.loc[0, 'mean_acc']
    best_se = df.loc[0, 'se_acc']
    threshold = best_mean - best_se
    
    # ONE-STANDARD-ERROR rule
    candidates = df[df['mean_acc'] >= threshold].copy()
    candidates['ent_complexity'] = candidates['entanglement'].apply(get_entanglement_complexity)
    
    candidates = candidates.sort_values(
        by=['reps', 'C', 'ent_complexity'],
        ascending=[True, True, True]
    ).reset_index(drop=True)
    
    best_config = candidates.iloc[0].to_dict()
    # clean up the added column
    del best_config['ent_complexity']
    
    return best_config, df

def main():
    args = parse_args()
    
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    logger = logging.getLogger(__name__)
    
    logger.info(f"System: {platform.system()} {platform.release()}")
    logger.info(f"Qiskit version: {qiskit.__version__}")
    logger.info(f"Scikit-learn version: {sklearn.__version__}")
    
    # Set seeds
    np.random.seed(args.seed)
    
    # Parse hyperparams
    gammas = [float(x.strip()) for x in args.gammas.split(',')]
    reps_list = [int(x.strip()) for x in args.reps.split(',')]
    ent_list = [x.strip() for x in args.entanglements.split(',')]
    Cs = [float(x.strip()) for x in args.Cs.split(',')]
    
    args.model_dir.mkdir(parents=True, exist_ok=True)
    args.results_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load data
    logger.info("Loading data...")
    X_train = np.load(args.data_dir / "X_train.npy")
    X_test = np.load(args.data_dir / "X_test.npy")
    y_train = np.load(args.data_dir / "y_train.npy")
    y_test = np.load(args.data_dir / "y_test.npy")
    label_encoder = load(args.model_dir / "label_encoder.joblib")
    
    num_qubits = X_train.shape[1]
    num_classes = len(label_encoder.classes_)
    
    # 4. Cache kernels
    logger.info("Precomputing quantum kernels...")
    K_dict = {}
    for reps in reps_list:
        for ent in ent_list:
            for gamma in gammas:
                logger.info(f"Computing kernel for reps={reps}, ent={ent}, gamma={gamma:.3f}")
                fm = build_feature_map(num_qubits, reps=reps, entanglement=ent)
                states = compute_states(fm, X_train * gamma, n_jobs=args.n_jobs)
                K_full = fidelity_kernel(states)
                K_dict[(reps, ent, gamma)] = (K_full, states)
                
    # 3. Nested CV
    logger.info("Running nested cross-validation...")
    outer_cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=args.seed)
    outer_scores = []
    
    for fold_idx, (train_idx, test_idx) in enumerate(outer_cv.split(X_train, y_train)):
        inner_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=args.seed)
        inner_splits = list(inner_cv.split(X_train[train_idx], y_train[train_idx]))
        
        mapped_inner_splits = []
        for itrain, itest in inner_splits:
            mapped_inner_splits.append((train_idx[itrain], train_idx[itest]))
            
        best_outer, _ = select_best_config(y_train, K_dict, Cs, mapped_inner_splits)
        
        K_full, _ = K_dict[(best_outer['reps'], best_outer['entanglement'], best_outer['gamma'])]
        K_outer_train = K_full[np.ix_(train_idx, train_idx)]
        K_outer_test = K_full[np.ix_(test_idx, train_idx)]
        
        clf = SVC(kernel='precomputed', C=best_outer['C'])
        clf.fit(K_outer_train, y_train[train_idx])
        preds = clf.predict(K_outer_test)
        acc = accuracy_score(y_train[test_idx], preds)
        outer_scores.append(acc)
        logger.debug(f"Outer fold {fold_idx+1} accuracy: {acc:.4f} with config {best_outer}")

    cv_mean = float(np.mean(outer_scores))
    cv_std = float(np.std(outer_scores))
    logger.info(f"Nested CV Accuracy: {cv_mean:.4f} ± {cv_std:.4f}")
    
    # Select final hyperparams on full training set using inner CV
    logger.info("Selecting final hyperparameters on full training set...")
    inner_cv_full = StratifiedKFold(n_splits=5, shuffle=True, random_state=args.seed)
    full_splits = list(inner_cv_full.split(X_train, y_train))
    
    final_config, results_df = select_best_config(y_train, K_dict, Cs, full_splits)
    
    # 5. Log a table sorted by CV mean +/- std
    logger.info("\nSearch Results (Full Train):")
    logger.info("\n" + results_df.to_string(index=False))
    
    # 7. Check grid edge for gamma
    edge_gamma_warning = False
    best_gamma = final_config['gamma']
    if best_gamma == min(gammas):
        logger.warning(f"Best gamma ({best_gamma}) is at the minimum of the grid! The optimum may be below the grid.")
        edge_gamma_warning = True
        
    logger.info(f"Selected best config via 1-SE rule: {final_config}")
    
    # 8. Refit and save
    logger.info("Refitting SVC on full training kernel...")
    reps, ent, gamma, C = final_config['reps'], final_config['entanglement'], final_config['gamma'], final_config['C']
    
    K_train, states_train = K_dict[(reps, ent, gamma)]
    clf = SVC(kernel='precomputed', C=C)
    clf.fit(K_train, y_train)
    
    train_acc = accuracy_score(y_train, clf.predict(K_train))
    
    logger.info("Computing test kernel and evaluating...")
    fm_test = build_feature_map(num_qubits, reps=reps, entanglement=ent)
    states_test = compute_states(fm_test, X_test * gamma, n_jobs=args.n_jobs)
    K_test = fidelity_kernel(states_test, states_train)
    test_acc = accuracy_score(y_test, clf.predict(K_test))
    
    logger.info(f"Train Accuracy: {train_acc:.4f}")
    logger.info(f"Test Accuracy: {test_acc:.4f}")
    
    # Diagnostics
    diag = kernel_diagnostics(K_train)
    
    # Save outputs
    dump(clf, args.model_dir / "qsvc_model.joblib")
    np.save(args.model_dir / "train_states.npy", states_train)
    np.save(args.model_dir / "K_train.npy", K_train)
    np.save(args.model_dir / "K_test.npy", K_test)
    results_df.to_csv(args.results_dir / "search_results.csv", index=False)
    
    config_dict = {
        "hyperparameters": {
            "reps": reps,
            "entanglement": ent,
            "gamma": gamma,
            "C": C,
        },
        "seed": args.seed,
        "qiskit_version": qiskit.__version__,
        "sklearn_version": sklearn.__version__,
        "numpy_version": np.__version__,
    }
    with open(args.model_dir / "config.json", "w") as f:
        json.dump(config_dict, f, indent=4)
        
    metrics_dict = {
        "model_type": "QSVC",
        "train_accuracy": train_acc,
        "cv_accuracy_mean": cv_mean,
        "cv_accuracy_std": cv_std,
        "test_accuracy": test_acc,
        "best_hyperparams": final_config,
        "kernel_diagnostics": diag,
        "num_qubits": num_qubits,
        "num_classes": num_classes,
        "train_samples": int(X_train.shape[0]),
        "test_samples": int(X_test.shape[0]),
        "seed": args.seed,
        "versions": {
            "qiskit": qiskit.__version__,
            "sklearn": sklearn.__version__,
            "numpy": np.__version__
        },
        "1SE_applied": True,
        "edge_gamma_warning": edge_gamma_warning
    }
    with open(args.model_dir / "metrics.json", "w") as f:
        json.dump(metrics_dict, f, indent=4)
        
    logger.info("Task 3 complete. Outputs saved to models/ and results/.")

if __name__ == "__main__":
    main()
