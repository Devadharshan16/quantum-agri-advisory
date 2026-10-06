#!/usr/bin/env python3
"""
VQC Training Script - Main Training Loop (2 Qubits, 7 Features, SLSQP)
"""

import numpy as np
import json
import os
import joblib
import warnings
warnings.filterwarnings('ignore')

from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.circuit.library import EfficientSU2
from qiskit_machine_learning.algorithms import VQC
from qiskit_algorithms.optimizers import SLSQP
from qiskit.primitives import Sampler
from sklearn.metrics import classification_report, accuracy_score
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("=" * 70)
print("PHASE 3: VQC TRAINING")
print("=" * 70)

# Configuration
NUM_QUBITS = 2  # Perfect for 4 target crops
NUM_FEATURES = 7
MAX_ITERATIONS = 300

# Load preprocessed data
print("\n[1/7] Loading preprocessed data...")
X_train = np.load('data/X_train_scaled.npy')
X_test  = np.load('data/X_test_scaled.npy')
y_train = np.load('data/y_train.npy')
y_test  = np.load('data/y_test.npy')

label_encoder = joblib.load('models/label_encoder.joblib')

print(f"  Data loaded")
print(f"  Training set: {X_train.shape[0]} samples, {X_train.shape[1]} features")
print(f"  Test set: {X_test.shape[0]} samples")
print(f"  Classes: {len(label_encoder.classes_)}")

# Build circuits
print("\n[2/7] Building quantum circuits...")
feature_map = QuantumCircuit(NUM_QUBITS)
inputs = ParameterVector('x', NUM_FEATURES)

# Layer 1: Soil Nutrients (N, P)
feature_map.h([0, 1])
feature_map.rx(inputs[0], 0)  # Nitrogen
feature_map.ry(inputs[1], 1)  # Phosphorus
feature_map.cx(0, 1)

# Layer 2: Minerals & Temperature (K, Temp)
feature_map.rx(inputs[2], 0)  # Potassium
feature_map.ry(inputs[3], 1)  # Temperature
feature_map.cx(1, 0)

# Layer 3: Environment (Humidity, pH)
feature_map.rx(inputs[4], 0)  # Humidity
feature_map.ry(inputs[5], 1)  # pH
feature_map.cx(0, 1)

# Layer 4: Decisive Weather (Rainfall encoded on BOTH qubits + Entanglement)
feature_map.rx(inputs[6], 0)  # Rainfall
feature_map.ry(inputs[6], 1)  # Rainfall
feature_map.cx(1, 0)

ansatz = EfficientSU2(
    num_qubits=NUM_QUBITS,
    reps=4,
    entanglement='full'
)

print(f"  Circuits created")
print(f"  Feature map: Balanced Custom Data Re-uploading")
print(f"  Ansatz: EfficientSU2 (variational layer)")
print(f"  Total trainable parameters: {ansatz.num_parameters}")

# Setup optimizer
print("\n[3/7] Setting up optimizer (SLSQP)...")
optimizer = SLSQP(maxiter=MAX_ITERATIONS)
print(f"  Optimizer ready")
print(f"  Algorithm: SLSQP (gradient-based, good for exact statevector simulation)")
print(f"  Max iterations: {MAX_ITERATIONS}")

# Setup sampler
print("\n[4/7] Setting up sampler (Sampler)...")
sampler = Sampler()
print(f"  Sampler ready")
print(f"  Type: Sampler V1 (statevector-based, compatible with qiskit-machine-learning 0.7.2)")

# Callback for progress tracking
objective_values = []
iteration_count = [0]

def callback_fn(weights, obj_val):
    objective_values.append(float(obj_val))
    iteration_count[0] += 1
    print(f"  Iteration {iteration_count[0]:3d}/{MAX_ITERATIONS}: Loss = {obj_val:.6f}")

# Initialize near zero
initial_weights = np.random.normal(0, 0.1, ansatz.num_parameters)

# Assemble VQC
print("\n[5/7] Assembling VQC classifier...")
vqc = VQC(
    sampler=sampler,
    feature_map=feature_map,
    ansatz=ansatz,
    optimizer=optimizer,
    initial_point=initial_weights,
    callback=callback_fn
)
print(f"  VQC ready for training")

# Training
print("\n[6/7] Starting training...")
print(f"  This will take some time depending on your CPU.")
print(f"  Progress updates every iteration")
print()

try:
    # Convert integer labels to One-Hot Encoding for proper Cross-Entropy Gradients
    y_train_oh = np.eye(4)[y_train]
    y_test_oh = np.eye(4)[y_test]

    vqc.fit(X_train, y_train_oh)
    print(f"\n  Training complete!")
except KeyboardInterrupt:
    print(f"\n  Training interrupted by user")
except Exception as e:
    print(f"\n  Training failed: {e}")
    raise

# Evaluation
print("\n[7/7] Evaluation & persistence...")

# Predictions will now be one-hot encoded arrays (N, 4)
y_pred_train_oh = vqc.predict(X_train)
y_pred_test_oh  = vqc.predict(X_test)

# Collapse back to 1D integers (0, 1, 2, 3) for metrics
y_pred_train = np.argmax(y_pred_train_oh, axis=1)
y_pred_test  = np.argmax(y_pred_test_oh, axis=1)

train_acc = accuracy_score(y_train, y_pred_train)
test_acc  = accuracy_score(y_test,  y_pred_test)

print(f"\n  Predictions generated")
print(f"  Training accuracy: {train_acc*100:.1f}%")
print(f"  Test accuracy:     {test_acc*100:.1f}%")

print(f"\n[Classification Report - Test Set]")
print(classification_report(
    y_test,
    y_pred_test,
    labels=list(range(len(label_encoder.classes_))),
    target_names=label_encoder.classes_,
    digits=2
))

# Save trained weights
np.save('models/trained_weights.npy', vqc.weights)
print(f"  Saved: models/trained_weights.npy ({len(vqc.weights)} parameters)")

# Save loss curve
with open('models/training_loss.json', 'w') as f:
    json.dump(objective_values, f)
print(f"  Saved: models/training_loss.json ({len(objective_values)} iterations)")

# Save metrics
metrics = {
    'train_accuracy': float(train_acc),
    'test_accuracy':  float(test_acc),
    'num_iterations': len(objective_values),
    'final_loss':     objective_values[-1] if objective_values else None,
}
with open('models/metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)
print(f"  Saved: models/metrics.json")

print("\n" + "=" * 70)
print("PHASE 3 COMPLETE")
print("=" * 70)
