import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from qiskit.circuit.library import ZZFeatureMap
import warnings
warnings.filterwarnings('ignore')

print("=" * 65)
print("PHASE 2: QUANTUM CIRCUIT DESIGN (4 Qubits — QSVC Kernel)")
print("=" * 65)

NUM_QUBITS   = 4   # 4 qubits = 4 PCA components (one per qubit)
NUM_FEATURES = 4   # 4 PCA components

# ── Feature Map for Quantum Kernel ────────────────────────────
# ZZFeatureMap encodes data into the quantum state |phi(x)>
# The kernel K(x, x') = |<phi(x)|phi(x')>|^2  (fidelity)
# This is the SWAP test from Class 43 applied to ML!
print("\n[1/1] Designing ZZFeatureMap for Quantum Kernel...")

feature_map = ZZFeatureMap(
    feature_dimension=NUM_QUBITS,
    reps=2,                     # 2 repetitions for richer feature interactions
    entanglement='full'         # all qubit pairs interact: ZZ(x_i, x_j)
)

print(f"  Type         : ZZFeatureMap")
print(f"  Qubits       : {NUM_QUBITS}")
print(f"  Reps         : 2")
print(f"  Entanglement : full (all pairs)")
print(f"  Circuit depth: {feature_map.depth()}")
print(f"  Gate count   : {feature_map.size()}")
print()
print("  How it works:")
print("    1. H gates put all qubits in superposition")
print("    2. P(2*x_i) gates encode individual features as phases")
print("    3. ZZ(x_i * x_j) interactions encode pairwise feature products")
print("    4. The kernel K(x,x') = |<phi(x)|phi(x')>|^2 (quantum fidelity)")
print("    5. This is exactly the Swap Test (Class 43) applied to ML!")
print()
print("  Why QSVC beats VQC:")
print("    - VQC trains variational params -> barren plateaus, optimizer wanders")
print("    - QSVC uses quantum circuit ONLY to compute kernel matrix")
print("    - Classical SVM handles classification -> convex, guaranteed-optimal")
print("    - No trainable quantum parameters -> no barren plateau problem!")

# ── Save diagram ──────────────────────────────────────────────
os.makedirs('assets', exist_ok=True)
print("\n[SAVING] Circuit diagram...")
try:
    fig = feature_map.draw(output='mpl', style='clifford', fold=80)
    fig.savefig('assets/circuit_diagram.png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    print("  Saved: assets/circuit_diagram.png")
except Exception as e:
    print(f"  Diagram skipped: {e}")

# ── Print ASCII view ──────────────────────────────────────────
print("\n── ZZFeatureMap (Quantum Kernel Circuit) ────────────────")
print(feature_map.draw())

print("\n" + "=" * 65)
print("PHASE 2 COMPLETE")
print(f"  {NUM_QUBITS} qubits  |  ZZFeatureMap reps=2  |  Quantum Kernel (QSVC)")
print(f"  No trainable parameters — kernel computed via circuit fidelity")
print("=" * 65)
