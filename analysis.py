import argparse
import json
import logging
from pathlib import Path
from typing import Tuple, List, Dict, Any
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from joblib import Parallel, delayed
import itertools

from qkernel import build_feature_map, compute_states, fidelity_kernel

# Setup logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, classes: List[str], assets_dir: Path) -> None:
    cm_raw = confusion_matrix(y_true, y_pred)
    cm_norm = confusion_matrix(y_true, y_pred, normalize="true")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

    sns.heatmap(cm_norm, annot=True, fmt=".2f", cmap="Blues", xticklabels=classes, yticklabels=classes, ax=ax1)
    ax1.set_title("Normalized Confusion Matrix")
    ax1.set_xlabel("Predicted")
    ax1.set_ylabel("True")

    sns.heatmap(cm_raw, annot=True, fmt="d", cmap="Blues", xticklabels=classes, yticklabels=classes, ax=ax2)
    ax2.set_title("Raw Confusion Matrix")
    ax2.set_xlabel("Predicted")
    ax2.set_ylabel("True")

    plt.tight_layout()
    plt.savefig(assets_dir / "confusion_matrix.png", dpi=150, bbox_inches="tight")
    plt.close()
    logger.info("Saved confusion matrix plot.")

def find_top_confused_pairs(y_true: np.ndarray, y_pred: np.ndarray, classes: List[str]) -> List[Tuple[str, str, int]]:
    cm_raw = confusion_matrix(y_true, y_pred)
    pairs = []
    n_classes = len(classes)
    for i in range(n_classes):
        for j in range(n_classes):
            if i != j and cm_raw[i, j] > 0:
                pairs.append((classes[i], classes[j], cm_raw[i, j]))
    
    # Sort by count descending
    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs

def plot_feature_comparison(df: pd.DataFrame, crop1: str, crop2: str, features: List[str], assets_dir: Path) -> None:
    subset = df[df["label"].isin([crop1, crop2])]
    
    df_melted = pd.melt(subset, id_vars=["label"], value_vars=features, var_name="Feature", value_name="Value")
    
    plt.figure(figsize=(12, 6))
    sns.violinplot(x="Feature", y="Value", hue="label", data=df_melted, split=True)
    plt.title(f"Feature Comparison: {crop1} vs {crop2}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(assets_dir / f"feature_comparison_{crop1}_vs_{crop2}.png", dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved feature comparison for {crop1} vs {crop2}.")

def bootstrap_accuracy(y_true: np.ndarray, y_pred: np.ndarray, n_iterations: int = 10000) -> Tuple[float, float]:
    n_size = len(y_true)
    accuracies = np.zeros(n_iterations)
    
    # Pre-generate random indices
    rng = np.random.default_rng(42)
    indices = rng.integers(0, n_size, size=(n_iterations, n_size))
    
    for i in range(n_iterations):
        idx = indices[i]
        accuracies[i] = accuracy_score(y_true[idx], y_pred[idx])
        
    return float(np.percentile(accuracies, 2.5)), float(np.percentile(accuracies, 97.5))

def run_multiseed_stability(
    data_path: Path, 
    config: Dict[str, Any], 
    results_dir: Path
) -> None:
    seeds = [42, 123, 456, 789, 1024]
    
    df = pd.read_csv(data_path)
    X = df.drop("label", axis=1).values
    features_cols = df.drop("label", axis=1).columns.tolist()
    y_raw = df["label"].values
    
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    
    results = []
    
    for seed in seeds:
        logger.info(f"Running multi-seed experiment for seed {seed}...")
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=seed, stratify=y)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        mm_scaler = MinMaxScaler(feature_range=(0, np.pi))
        X_train_scaled = mm_scaler.fit_transform(X_train_scaled)
        X_test_scaled = np.clip(mm_scaler.transform(X_test_scaled), 0, np.pi)
        
        feature_dim = X_train_scaled.shape[1]
        hp = config.get("hyperparameters", config)
        gamma = hp.get("gamma", 0.1)
        reps = hp.get("reps", 2)
        ent = hp.get("entanglement", "full")
        C = hp.get("C", 10.0)
        
        feature_map = build_feature_map(feature_dim, reps=reps, entanglement=ent)
        
        # Train QSVC
        states_train = compute_states(feature_map, X_train_scaled * gamma)
        states_test = compute_states(feature_map, X_test_scaled * gamma)
        
        train_kernel = fidelity_kernel(states_train)
        test_kernel = fidelity_kernel(states_test, states_train)
        
        qsvc = SVC(kernel="precomputed", C=C)
        qsvc.fit(train_kernel, y_train)
        y_pred_qsvc = qsvc.predict(test_kernel)
        qsvc_acc = accuracy_score(y_test, y_pred_qsvc)
        
        # Train Classical RBF-SVM
        rbf_svc = SVC(kernel="rbf", C=config.get("c_param", 1.0))
        rbf_svc.fit(X_train_scaled, y_train)
        y_pred_rbf = rbf_svc.predict(X_test_scaled)
        rbf_acc = accuracy_score(y_test, y_pred_rbf)
        
        results.append({
            "seed": seed,
            "qsvc_accuracy": qsvc_acc,
            "rbf_accuracy": rbf_acc
        })
        
    res_df = pd.DataFrame(results)
    res_df.to_csv(results_dir / "multi_seed_results.csv", index=False)
    
    qsvc_mean = res_df["qsvc_accuracy"].mean()
    qsvc_std = res_df["qsvc_accuracy"].std()
    rbf_mean = res_df["rbf_accuracy"].mean()
    rbf_std = res_df["rbf_accuracy"].std()
    
    logger.info(f"Multi-seed QSVC Accuracy: {qsvc_mean:.4f} +/- {qsvc_std:.4f}")
    logger.info(f"Multi-seed RBF-SVM Accuracy: {rbf_mean:.4f} +/- {rbf_std:.4f}")

def main():
    parser = argparse.ArgumentParser(description="Analyze the trained QSVC model.")
    parser.add_argument("--data_dir", type=str, default="data", help="Directory containing data.")
    parser.add_argument("--models_dir", type=str, default="models", help="Directory containing models.")
    parser.add_argument("--results_dir", type=str, default="results", help="Directory to save results.")
    parser.add_argument("--assets_dir", type=str, default="assets", help="Directory to save plots.")
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    models_dir = Path(args.models_dir)
    results_dir = Path(args.results_dir)
    assets_dir = Path(args.assets_dir)
    
    results_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load data
    logger.info("Loading test data...")
    test_kernel_path = models_dir / "K_test.npy"
    if not test_kernel_path.exists():
        logger.error(f"Missing {test_kernel_path}")
        return
        
    test_kernel = np.load(test_kernel_path)
    
    X_test_path = data_dir / "X_test_scaled.npy"
    y_test_path = data_dir / "y_test.npy"
    
    y_test = np.load(y_test_path)
    
    le_path = models_dir / "label_encoder.joblib"
    le = joblib.load(le_path)
    classes = list(le.classes_)
    
    # 2. Load model & Predict
    qsvc_path = models_dir / "qsvc_model.joblib"
    logger.info("Loading trained QSVC model...")
    qsvc = joblib.load(qsvc_path)
    
    y_pred = qsvc.predict(test_kernel)
    
    # 3. Output Metrics
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="macro")
    logger.info(f"Test Accuracy: {acc:.4f}")
    logger.info(f"Macro F1-Score: {f1:.4f}")
    
    report = classification_report(y_test, y_pred, target_names=classes)
    
    report_out = f"Test Accuracy: {acc:.4f}\nMacro F1-Score: {f1:.4f}\n\n{report}"
    
    with open(results_dir / "classification_report.txt", "w") as f:
        f.write(report_out)
    logger.info("Saved classification report.")
    
    # Plots
    plot_confusion_matrix(y_test, y_pred, classes, assets_dir)
    
    # Top 5 confused
    confused_pairs = find_top_confused_pairs(y_test, y_pred, classes)
    logger.info("Top 5 confused class pairs (True, Predicted, Count):")
    for p in confused_pairs[:5]:
        logger.info(f"  {p[0]} -> {p[1]}: {p[2]}")
        
    # Feature comparison for top 3
    # Load original dataset for feature comparison
    df_path = data_dir / "Crop_recommendation.csv"
    if df_path.exists():
        df_full = pd.read_csv(df_path)
        features = df_full.drop("label", axis=1).columns.tolist()
        for i in range(min(3, len(confused_pairs))):
            c1, c2, _ = confused_pairs[i]
            plot_feature_comparison(df_full, c1, c2, features, assets_dir)
    
    # 4. Bootstrap CI
    logger.info("Computing 95% bootstrap confidence interval...")
    ci_lower, ci_upper = bootstrap_accuracy(y_test, y_pred)
    logger.info(f"95% CI for Accuracy: [{ci_lower:.4f}, {ci_upper:.4f}]")
    
    # 5. Multi-seed stability
    config_path = models_dir / "config.json"
    if config_path.exists() and df_path.exists():
        with open(config_path, "r") as f:
            config = json.load(f)
        run_multiseed_stability(df_path, config, results_dir)

if __name__ == "__main__":
    main()
