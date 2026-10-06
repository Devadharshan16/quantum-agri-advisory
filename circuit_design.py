import os
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.circuit.library import EfficientSU2
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("PHASE 2: QUANTUM CIRCUIT DESIGN (2 Qubits, 7 Features)")
print("=" * 60)

NUM_QUBITS = 2
NUM_FEATURES = 7

# Custom Data Re-uploading Feature Map
print("\n[1/2] Designing balanced data re-uploading feature map...")
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

print("  Feature map created")
print(f"  Type: Balanced Custom Data Re-uploading")
print(f"  Qubits: {NUM_QUBITS}")
print(f"  Features mapped: {NUM_FEATURES}")

print("\n[2/2] Designing variational ansatz (EfficientSU2)...")
ansatz = EfficientSU2(num_qubits=NUM_QUBITS, reps=8, entanglement='full')
print("  Ansatz created")
print(f"  Type: EfficientSU2")
print(f"  Qubits: {NUM_QUBITS}")
print(f"  Repetitions: 8")
print(f"  Trainable parameters: {ansatz.num_parameters}")

# Combine them for visualization
circuit = QuantumCircuit(NUM_QUBITS)
circuit.compose(feature_map, inplace=True)
circuit.barrier()
circuit.compose(ansatz, inplace=True)

# Save diagram
os.makedirs('assets', exist_ok=True)
print("\n[SAVING] Circuit diagram as PNG...")
fig = circuit.draw(output='mpl', style='clifford')
fig.savefig('assets/circuit_diagram.png', bbox_inches='tight')
plt.close(fig)
print("  Saved: assets/circuit_diagram.png")

print("\n[CIRCUIT STRUCTURE - Feature Map]")
print(feature_map.draw())
print("\n[CIRCUIT STRUCTURE - Ansatz]")
print(ansatz.draw())
print("\n" + "=" * 60)
print("PHASE 2 COMPLETE")
print("=" * 60)
