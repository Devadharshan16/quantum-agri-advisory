import time
import numpy as np
from qiskit.circuit.library import ZZFeatureMap
from qiskit_machine_learning.kernels import FidelityQuantumKernel

for qubits in [4, 7]:
    feature_map = ZZFeatureMap(feature_dimension=qubits, reps=2, entanglement='full')
    kernel = FidelityQuantumKernel(feature_map=feature_map)
    
    # 50 random samples
    X_train = np.random.rand(50, qubits)
    
    start_time = time.time()
    for i in range(50):
        _ = kernel.evaluate(X_train[i:i+1], X_train)[0]
    elapsed = time.time() - start_time
    print(f"{qubits} qubits, 50x50 evals: {elapsed:.2f}s")
