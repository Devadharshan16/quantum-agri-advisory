#!/usr/bin/env python3
"""
QSVC Training — Quantum Kernel SVM · 4 Qubits · 22 Crops
─────────────────────────────────────────────────────────
Computes the quantum kernel matrix row-by-row with a progress bar,
then feeds the precomputed kernel to classical SVM.

  K(x, x') = |<phi(x)|phi(x')>|^2   (quantum fidelity / Swap test)
"""

import numpy as np
import json
import os
import sys
import time
import joblib
import warnings
warnings.filterwarnings('ignore')

from qiskit.circuit.library import ZZFeatureMap
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score

print("=" * 70)
print("PHASE 3: QSVC TRAINING  (Quantum Kernel SVM · 4 Qubits · 22 Crops)")
print("=" * 70)

# ── Config ────────────────────────────────────────────────────
NUM_QUBITS   = 4
NUM_FEATURES = 4

# ── Data ──────────────────────────────────────────────────────
print("\n[1/6] Loading preprocessed data...")
X_train = np.load('data/X_train_scaled.npy')
X_test  = np.load('data/X_test_scaled.npy')
y_train = np.load('data/y_train.npy')
y_test  = np.load('data/y_test.npy')
label_encoder = joblib.load('models/label_encoder.joblib')
NUM_CLASSES   = len(label_encoder.classes_)

print(f"  Train   : {X_train.shape}")
print(f"  Test    : {X_test.shape}")
print(f"  Classes : {NUM_CLASSES}")

assert X_train.shape[1] == NUM_FEATURES, (
    f"Feature mismatch: got {X_train.shape[1]}, expected {NUM_FEATURES}. "
    "Re-run data_prep.py."
)

# ── Quantum Kernel ────────────────────────────────────────────
print("\n[2/6] Building quantum kernel...")
feature_map = ZZFeatureMap(
    feature_dimension=NUM_QUBITS,
    reps=2,
    entanglement='full'
)

kernel = FidelityQuantumKernel(feature_map=feature_map)

print(f"  Feature map  : ZZFeatureMap (reps=2, full entanglement)")
print(f"  Qubits       : {NUM_QUBITS}")
print(f"  Kernel       : FidelityQuantumKernel (quantum fidelity)")
print(f"  Trainable quantum params : 0")

# ── Compute TRAINING kernel matrix with progress bar ──────────
print("\n[3/6] Computing training kernel matrix (with progress)...")
n_train = X_train.shape[0]
total_rows = n_train
print(f"  Matrix size: {n_train} x {n_train}")
print(f"  Total rows to compute: {total_rows}")
print()

K_train = np.zeros((n_train, n_train))
start_time = time.time()

for i in range(n_train):
    # Compute row i: K(x_i, x_j) for all j
    row = kernel.evaluate(X_train[i:i+1], X_train)[0]
    K_train[i] = row

    # Progress bar
    elapsed = time.time() - start_time
    pct = (i + 1) / n_train * 100
    if i > 0:
        eta = elapsed / (i + 1) * (n_train - i - 1)
        eta_str = f"ETA {eta:.0f}s"
    else:
        eta_str = "ETA calculating..."

    bar_len = 30
    filled = int(bar_len * (i + 1) / n_train)
    bar = '=' * filled + '-' * (bar_len - filled)
    sys.stdout.write(f"\r  [{bar}] {pct:5.1f}%  Row {i+1}/{n_train}  "
                     f"Elapsed {elapsed:.0f}s  {eta_str}    ")
    sys.stdout.flush()

print(f"\n\n  Training kernel matrix computed in {time.time()-start_time:.1f}s")

# ── Compute TEST kernel matrix with progress bar ──────────────
print("\n[4/6] Computing test kernel matrix...")
n_test = X_test.shape[0]
print(f"  Matrix size: {n_test} x {n_train}")

K_test = np.zeros((n_test, n_train))
start_time2 = time.time()

for i in range(n_test):
    row = kernel.evaluate(X_test[i:i+1], X_train)[0]
    K_test[i] = row

    elapsed = time.time() - start_time2
    pct = (i + 1) / n_test * 100
    if i > 0:
        eta = elapsed / (i + 1) * (n_test - i - 1)
        eta_str = f"ETA {eta:.0f}s"
    else:
        eta_str = "ETA calculating..."

    bar_len = 30
    filled = int(bar_len * (i + 1) / n_test)
    bar = '=' * filled + '-' * (bar_len - filled)
    sys.stdout.write(f"\r  [{bar}] {pct:5.1f}%  Row {i+1}/{n_test}  "
                     f"Elapsed {elapsed:.0f}s  {eta_str}    ")
    sys.stdout.flush()

print(f"\n\n  Test kernel matrix computed in {time.time()-start_time2:.1f}s")

# ── Train classical SVM on precomputed kernel ─────────────────
print("\n[5/6] Training SVM on precomputed quantum kernel...")
svc = SVC(kernel='precomputed', C=1.0, decision_function_shape='ovr')
svc.fit(K_train, y_train)
print("  SVM training complete (convex optimization — guaranteed global optimum)")

# ── Evaluate ──────────────────────────────────────────────────
print("\n[6/6] Evaluation & saving...")
y_pred_train = svc.predict(K_train)
y_pred_test  = svc.predict(K_test)
train_acc    = accuracy_score(y_train, y_pred_train)
test_acc     = accuracy_score(y_test,  y_pred_test)

print(f"\n  Train accuracy : {train_acc*100:.1f}%")
print(f"  Test  accuracy : {test_acc*100:.1f}%")

print("\n[Classification Report — Test Set]")
print(classification_report(
    y_test, y_pred_test,
    labels=list(range(NUM_CLASSES)),
    target_names=label_encoder.classes_,
    digits=2
))

# ── Persist ───────────────────────────────────────────────────
# Save the SVM model, kernel matrices, and training data for predict.py
joblib.dump(svc, 'models/qsvc_model.joblib')
print("  Saved: models/qsvc_model.joblib")

np.save('models/K_train.npy', K_train)
np.save('models/X_train_kernel.npy', X_train)
print("  Saved: models/K_train.npy, models/X_train_kernel.npy")

metrics = {
    'model_type'      : 'QSVC (Quantum Kernel SVM)',
    'train_accuracy'  : float(train_acc),
    'test_accuracy'   : float(test_acc),
    'num_qubits'      : NUM_QUBITS,
    'num_features'    : NUM_FEATURES,
    'num_classes'     : NUM_CLASSES,
    'train_samples'   : int(n_train),
    'test_samples'    : int(n_test),
    'feature_map'     : 'ZZFeatureMap (reps=2, full entanglement)',
    'kernel'          : 'FidelityQuantumKernel (quantum fidelity / Swap test)',
    'classifier'      : 'SVM (kernel=precomputed, convex optimization)',
    'trainable_quantum_params' : 0,
    'crops'           : list(label_encoder.classes_),
    'notes'           : (
        "QSVC uses quantum circuit purely for kernel computation. "
        "K(x,x') = |<phi(x)|phi(x')>|^2 is the fidelity (Swap test, Class 43). "
        "Classical SVM handles classification — convex, no barren plateaus."
    ),
}
with open('models/metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)
print("  Saved: models/metrics.json")

print("\n" + "=" * 70)
print("PHASE 3 COMPLETE")
print(f"  Test accuracy: {test_acc*100:.1f}%  (QSVC — quantum kernel SVM)")
print(f"  No barren plateaus. Convex optimum reached.")
print("=" * 70)
