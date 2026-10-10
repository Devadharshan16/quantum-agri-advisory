# Quantum Agricultural Advisory System — Development Log

## Phase 1: Data Preparation
1. `data_prep.py`: Downloads the full crop recommendation dataset (2200 rows, 22 crops, 100 per class). Encodes labels with LabelEncoder. Extracts the 7-feature matrix (N, P, K, temperature, humidity, ph, rainfall). Performs stratified 80/20 split (1760 train / 440 test). Applies StandardScaler and MinMaxScaler to [0, π] — both fit on train only. Clips test values to [0, π]. No PCA — all 7 features map directly to 7 qubits.

2. Dataset: Crop Recommendation Dataset from Kaggle (Atharva Ingle). 2200 rows, perfectly balanced.

## Phase 2: Quantum Circuit Design
3. `circuit_design.py`: Creates a 7-qubit ZZFeatureMap (reps=2, full entanglement). No variational ansatz — circuit is used purely as a feature map for kernel computation.

## Phase 3: QSVC Training (v2 — Production Pipeline)
4. `qkernel.py`: Quantum kernel module. Computes statevectors once per sample via Statevector simulation. Builds fidelity kernel K[i,j] = |⟨ψ_i|ψ_j⟩|² via matrix multiplication. Includes diagnostics: off-diagonal stats, PSD check, effective rank, kernel-target alignment.

5. `trainv2.py`: Full nested cross-validation pipeline. Outer 5-fold × 3 repeats for performance estimate, inner 5-fold for hyperparameter selection. Caches kernels per (reps, entanglement, gamma). Applies one-standard-error rule. Checks for gamma grid edge.

6. `baselines.py`: Fair classical comparison. Tuned RBF-SVM, Linear SVM, Random Forest, k-NN. Same CV protocol. McNemar's test for statistical significance. Kernel alignment between quantum and RBF kernels.

## Phase 4: Analysis & Robustness
7. `analysis.py`: Confusion matrix, top-5 confused pairs, feature comparison plots, 95% bootstrap CI, multi-seed stability (5 seeds).

8. `learning_curve.py`: Accuracy vs training size (25%, 50%, 75%, 100%). Accuracy vs gamma with off-diagonal kernel mean (kernel concentration analysis).

9. `noise_study.py`: Shot noise (256 to 8192 shots) and depolarizing noise robustness. PSD projection for noisy kernels.

## Phase 5: Inference
10. `predict.py`: Loads trained pipeline, accepts CSV or interactive input. Computes quantum kernel vector against saved training states. Outputs predicted crop + top-3 probabilities (via softmax on SVM decision function).

## Key Design Decisions
- Switched from VQC to QSVC to eliminate barren plateaus (Class 43: Swap Test)
- 7-qubit ZZFeatureMap with bandwidth parameter gamma multiplying features before encoding
- Noiseless statevector simulation (exact, no shot noise in main results)
- Classical SVM with precomputed kernel — convex optimization, guaranteed global optimum
- Nested CV prevents information leakage from test set
