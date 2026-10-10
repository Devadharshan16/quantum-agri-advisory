#!/usr/bin/env python3
"""
Quantum kernel module — statevector fidelity kernel for QSVC.

Provides:
  - build_feature_map: creates a ZZFeatureMap circuit
  - compute_states: simulates |psi(x)> for each sample via exact statevector
  - fidelity_kernel: K[i,j] = |<A_i|B_j>|^2, symmetrised when B is None
  - kernel_diagnostics: off-diagonal stats, PSD check, effective rank, KTA
"""
from __future__ import annotations

import logging
from typing import Sequence

import numpy as np
from joblib import Parallel, delayed
from qiskit.circuit.library import ZZFeatureMap
from qiskit.quantum_info import Statevector

log = logging.getLogger("qkernel")


# --------------------------------------------------------------------------- #
# Feature map
# --------------------------------------------------------------------------- #
def build_feature_map(
    n_qubits: int, reps: int = 2, entanglement: str = "full"
) -> ZZFeatureMap:
    """Return a ZZFeatureMap encoding circuit."""
    return ZZFeatureMap(
        feature_dimension=n_qubits, reps=reps, entanglement=entanglement
    )


# --------------------------------------------------------------------------- #
# Statevector simulation
# --------------------------------------------------------------------------- #
def _encode_chunk(circuit: ZZFeatureMap, X_chunk: np.ndarray) -> np.ndarray:
    """Encode a chunk of samples into statevectors."""
    dim = 2 ** circuit.num_qubits
    out = np.empty((len(X_chunk), dim), dtype=np.complex128)
    for k, x in enumerate(X_chunk):
        out[k] = Statevector(circuit.assign_parameters(x.tolist())).data
    return out


def compute_states(
    circuit: ZZFeatureMap,
    X: np.ndarray,
    n_jobs: int = 1,
    chunk_size: int = 32,
) -> np.ndarray:
    """Simulate |psi(x)> for every row of X.

    Returns
    -------
    np.ndarray of shape (N, 2**n_qubits), dtype complex128.
    """
    n = len(X)
    if n == 0:
        return np.empty((0, 2 ** circuit.num_qubits), dtype=np.complex128)

    chunks = [X[i : i + chunk_size] for i in range(0, n, chunk_size)]

    if n_jobs == 1:
        # Sequential — avoids multiprocessing issues on Windows
        parts = [_encode_chunk(circuit, c) for c in chunks]
    else:
        parts = Parallel(n_jobs=n_jobs)(
            delayed(_encode_chunk)(circuit, c) for c in chunks
        )
    return np.vstack(parts)


# --------------------------------------------------------------------------- #
# Fidelity kernel
# --------------------------------------------------------------------------- #
def fidelity_kernel(
    A: np.ndarray, B: np.ndarray | None = None
) -> np.ndarray:
    """Compute the fidelity kernel K[i,j] = |<A_i|B_j>|^2.

    If B is None the matrix is symmetrised and diag is set to 1.
    """
    symmetric = B is None
    target = A if symmetric else B
    K = np.abs(A.conj() @ target.T) ** 2
    if symmetric:
        K = (K + K.T) / 2.0
        np.fill_diagonal(K, 1.0)
    return K


# --------------------------------------------------------------------------- #
# Diagnostics
# --------------------------------------------------------------------------- #
def kernel_diagnostics(
    K: np.ndarray, y: np.ndarray | None = None
) -> dict:
    """Return diagnostic statistics for a kernel matrix.

    Parameters
    ----------
    K : (N, N) kernel matrix
    y : optional label vector for kernel-target alignment

    Returns
    -------
    dict with keys:
      offdiag_mean, offdiag_std, min_eigenvalue, effective_rank,
      and optionally kernel_target_alignment.
    """
    n = len(K)
    mask = ~np.eye(n, dtype=bool)
    off = K[mask]

    eigenvalues = np.linalg.eigvalsh(K)
    min_eig = float(eigenvalues.min())

    # Effective rank (eigenvalue participation ratio)
    pos_eig = eigenvalues[eigenvalues > 0]
    if len(pos_eig) > 0:
        eff_rank = float(pos_eig.sum() ** 2 / (pos_eig ** 2).sum())
    else:
        eff_rank = 0.0

    result = {
        "offdiag_mean": float(off.mean()),
        "offdiag_std": float(off.std()),
        "min_eigenvalue": min_eig,
        "effective_rank": eff_rank,
    }

    if y is not None:
        # Kernel-target alignment
        # y_outer[i,j] = +1 if y[i] == y[j] else -1
        y_outer = 2.0 * (y[:, None] == y[None, :]).astype(float) - 1.0
        kta_num = np.sum(K * y_outer)
        kta_den = np.linalg.norm(K, "fro") * np.linalg.norm(y_outer, "fro")
        kta = float(kta_num / kta_den) if kta_den > 0 else 0.0
        result["kernel_target_alignment"] = kta

    return result
