import argparse
import json
import logging
import time
from pathlib import Path
from typing import Tuple, List, Dict, Optional, Any

import numpy as np
import pandas as pd
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

import qiskit
from qiskit import QuantumCircuit, transpile
from qiskit.primitives import StatevectorSampler

try:
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error
    HAS_AER = True
except ImportError:
    HAS_AER = False

from qkernel import build_feature_map

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def load_data(data_dir: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load train and test data."""
    x_train = np.load(data_dir / "x_train.npy")
    y_train = np.load(data_dir / "y_train.npy")
    x_test = np.load(data_dir / "x_test.npy")
    y_test = np.load(data_dir / "y_test.npy")
    return x_train, y_train, x_test, y_test

def get_stratified_subset(
    x: np.ndarray, y: np.ndarray, size: int, seed: int = 42
) -> Tuple[np.ndarray, np.ndarray]:
    """Get a stratified subset of the data."""
    if len(x) <= size:
        return x, y
    _, x_sub, _, y_sub = train_test_split(
        x, y, test_size=size, stratify=y, random_state=seed
    )
    return x_sub, y_sub

def project_psd(K: np.ndarray) -> Tuple[np.ndarray, float, bool]:
    """Project a symmetric matrix onto the PSD cone if necessary."""
    eigvals, eigvecs = np.linalg.eigh(K)
    min_eig = float(np.min(eigvals))
    if min_eig < -1e-8:
        # Project onto PSD cone
        eigvals[eigvals < 0] = 0
        K_psd = eigvecs @ np.diag(eigvals) @ eigvecs.T
        return K_psd, min_eig, True
    return K, min_eig, False

def build_compute_uncompute_circuit(
    feature_map: QuantumCircuit, x_i: np.ndarray, x_j: np.ndarray
) -> QuantumCircuit:
    """Build the compute-uncompute circuit for a pair of data points."""
    qc1 = feature_map.assign_parameters(x_i)
    qc2 = feature_map.assign_parameters(x_j)
    qc = qc1.compose(qc2.inverse())
    qc.measure_all()
    return qc

def compute_kernel_matrix(
    x_left: np.ndarray,
    x_right: np.ndarray,
    feature_map: QuantumCircuit,
    sampler: Any,
    shots: int,
    is_symmetric: bool = False
) -> np.ndarray:
    """Compute the kernel matrix using the given sampler."""
    n_left = len(x_left)
    n_right = len(x_right)
    K = np.zeros((n_left, n_right))
    
    # Pre-generate param bindings for speed? Actually binding per pair is easier.
    # To handle primitive execution efficiently, we can batch circuits.
    batch_size = 500
    circuits = []
    indices = []
    
    start_time = time.time()
    for i in range(n_left):
        if is_symmetric and i % 50 == 0:
            logger.info(f"Computing row {i}/{n_left} of symmetric kernel...")
        elif not is_symmetric and i % 50 == 0:
            logger.info(f"Computing row {i}/{n_left} of asymmetric kernel...")
            
        for j in range(n_right):
            if is_symmetric and j < i:
                K[i, j] = K[j, i]
                continue
            
            qc = build_compute_uncompute_circuit(feature_map, x_left[i], x_right[j])
            circuits.append(qc)
            indices.append((i, j))
            
            if len(circuits) >= batch_size:
                # Run batch
                job = sampler.run(circuits, shots=shots)
                result = job.result()
                
                # Extract prob of |0...0>
                for idx, (r_i, r_j) in enumerate(indices):
                    # For SamplerV2, pub result contains bitstrings
                    pub_res = result[idx]
                    counts = pub_res.data.meas.get_counts()
                    # The all-zero bitstring
                    zero_str = "0" * feature_map.num_qubits
                    prob = counts.get(zero_str, 0) / shots
                    K[r_i, r_j] = prob
                
                circuits = []
                indices = []
                
    # Run remaining
    if circuits:
        job = sampler.run(circuits, shots=shots)
        result = job.result()
        for idx, (r_i, r_j) in enumerate(indices):
            pub_res = result[idx]
            counts = pub_res.data.meas.get_counts()
            zero_str = "0" * feature_map.num_qubits
            prob = counts.get(zero_str, 0) / shots
            K[r_i, r_j] = prob
            
    if is_symmetric:
        # Just in case, ensure perfect symmetry
        K = (K + K.T) / 2.0
        # Diagonal should be 1.0 (with noise it might not be, but let's keep the raw computed values)
        
    return K

def evaluate_kernel(
    K_train: np.ndarray,
    K_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
    C: float
) -> Tuple[float, float, float, bool]:
    """Train SVC and return train and test accuracies."""
    K_train_psd, min_eig, projected = project_psd(K_train)
    
    svc = SVC(kernel="precomputed", C=C)
    svc.fit(K_train_psd, y_train)
    
    train_acc = accuracy_score(y_train, svc.predict(K_train_psd))
    test_acc = accuracy_score(y_test, svc.predict(K_test))
    
    return train_acc, test_acc, min_eig, projected

def main():
    parser = argparse.ArgumentParser(description="Quantum Kernel Noise Study")
    parser.add_argument("--data_dir", type=str, default="data", help="Data directory")
    parser.add_argument("--models_dir", type=str, default="models", help="Models directory")
    parser.add_argument("--results_dir", type=str, default="results", help="Results directory")
    parser.add_argument("--assets_dir", type=str, default="assets", help="Assets directory")
    parser.add_argument("--train_size", type=int, default=600, help="Subset size for training")
    parser.add_argument("--test_size", type=int, default=300, help="Subset size for testing")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    np.random.seed(args.seed)
    
    data_dir = Path(args.data_dir)
    models_dir = Path(args.models_dir)
    results_dir = Path(args.results_dir)
    assets_dir = Path(args.assets_dir)
    
    results_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load data and take subset
    logger.info("Loading data...")
    x_train_full, y_train_full, x_test_full, y_test_full = load_data(data_dir)
    
    logger.info(f"Taking stratified subsets: train={args.train_size}, test={args.test_size}")
    x_train, y_train = get_stratified_subset(x_train_full, y_train_full, args.train_size, args.seed)
    x_test, y_test = get_stratified_subset(x_test_full, y_test_full, args.test_size, args.seed)
    
    # 2. Load best config
    config_path = models_dir / "config.json"
    logger.info(f"Loading config from {config_path}")
    with open(config_path, "r") as f:
        config = json.load(f)
        
    num_features = x_train.shape[1]
    hp = config.get("hyperparameters", config)
    reps = hp.get("reps", 2)
    entanglement = hp.get("entanglement", "full")
    C = hp.get("C", 10.0)
    gamma = hp.get("gamma", 0.1)
    
    # 3. Build feature map
    logger.info("Building feature map...")
    feature_map = build_feature_map(num_features, reps=reps, entanglement=entanglement)
    
    # We will use SamplerV2 interfaces
    noiseless_sampler = StatevectorSampler()
    
    results_records = []
    
    # 4. Shot-based noiseless study
    shots_list = [256, 512, 1024, 4096, 8192]
    
    for shots in shots_list:
        logger.info(f"--- Computing NOISELESS kernel with {shots} shots ---")
        K_train = compute_kernel_matrix(x_train, x_train, feature_map, noiseless_sampler, shots, is_symmetric=True)
        K_test = compute_kernel_matrix(x_test, x_train, feature_map, noiseless_sampler, shots, is_symmetric=False)
        
        train_acc, test_acc, min_eig, projected = evaluate_kernel(K_train, K_test, y_train, y_test, C)
        logger.info(f"Shots: {shots} | Test Acc: {test_acc:.4f} | Min Eig: {min_eig:.2e} | Projected: {projected}")
        
        results_records.append({
            "method": "noiseless_shots",
            "shots": shots,
            "noise_level": 0.0,
            "min_eigenvalue": min_eig,
            "psd_projected": projected,
            "train_acc": train_acc,
            "test_acc": test_acc
        })
        
    # 5. Noise model study
    if HAS_AER:
        logger.info("qiskit-aer is available. Running noise model study...")
        noise_levels = [0.001, 0.01, 0.05]
        noise_shots = 4096
        
        # Need Sampler for Aer
        from qiskit_aer.primitives import Sampler as AerSamplerV2
        
        for p in noise_levels:
            logger.info(f"--- Computing NOISY kernel with depolarizing p={p} ---")
            noise_model = NoiseModel()
            # single-qubit gates
            error = depolarizing_error(p, 1)
            noise_model.add_all_qubit_quantum_error(error, ['u1', 'u2', 'u3', 'rx', 'ry', 'rz', 'h', 'x', 'y', 'z'])
            
            # Use AerSamplerV2 from qiskit_aer (this is Sampler V2 in newer qiskit-aer)
            # Actually, to be safe with older/newer versions, we can use qiskit_aer.primitives.SamplerV2
            try:
                from qiskit_aer.primitives import SamplerV2 as AerSampler
                noisy_sampler = AerSampler(backend_options={"noise_model": noise_model})
            except ImportError:
                # Fallback to older primitive
                noisy_sampler = AerSamplerV2(backend_options={"noise_model": noise_model})
                
            K_train = compute_kernel_matrix(x_train, x_train, feature_map, noisy_sampler, noise_shots, is_symmetric=True)
            K_test = compute_kernel_matrix(x_test, x_train, feature_map, noisy_sampler, noise_shots, is_symmetric=False)
            
            train_acc, test_acc, min_eig, projected = evaluate_kernel(K_train, K_test, y_train, y_test, C)
            logger.info(f"Noise: {p} | Test Acc: {test_acc:.4f} | Min Eig: {min_eig:.2e} | Projected: {projected}")
            
            results_records.append({
                "method": "depolarizing_noise",
                "shots": noise_shots,
                "noise_level": p,
                "min_eigenvalue": min_eig,
                "psd_projected": projected,
                "train_acc": train_acc,
                "test_acc": test_acc
            })
    else:
        logger.warning("qiskit-aer not found. Skipping noise study.")
        
    # 8. Save results
    df_results = pd.DataFrame(results_records)
    results_csv = results_dir / "noise_results.csv"
    df_results.to_csv(results_csv, index=False)
    logger.info(f"Saved results to {results_csv}")
    
    # 9. Plot accuracy vs shots
    noiseless_df = df_results[df_results["method"] == "noiseless_shots"]
    if not noiseless_df.empty:
        plt.figure(figsize=(8, 6))
        plt.plot(noiseless_df["shots"], noiseless_df["test_acc"], marker='o', linestyle='-', label='Test Accuracy')
        plt.plot(noiseless_df["shots"], noiseless_df["train_acc"], marker='s', linestyle='--', label='Train Accuracy')
        plt.xscale('log', base=2)
        plt.xlabel('Shots')
        plt.ylabel('Accuracy')
        plt.title('Accuracy vs Shots (Noiseless)')
        plt.grid(True, which="both", ls="-", alpha=0.2)
        plt.legend()
        plt.tight_layout()
        plot_path = assets_dir / "accuracy_vs_shots.png"
        plt.savefig(plot_path)
        logger.info(f"Saved plot to {plot_path}")
        plt.close()

if __name__ == "__main__":
    main()
