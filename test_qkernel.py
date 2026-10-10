#!/usr/bin/env python3
"""
Unit tests for qkernel.py — quantum fidelity kernel module.

Run: python -m pytest test_qkernel.py -v
"""
import numpy as np
import pytest

from qkernel import (
    build_feature_map,
    compute_states,
    fidelity_kernel,
    kernel_diagnostics,
)

# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
N_QUBITS = 3
REPS = 1
N_SAMPLES = 20
SEED = 42


@pytest.fixture(scope="module")
def feature_map():
    return build_feature_map(N_QUBITS, reps=REPS, entanglement="full")


@pytest.fixture(scope="module")
def X_data():
    rng = np.random.default_rng(SEED)
    return rng.uniform(0, np.pi, size=(N_SAMPLES, N_QUBITS))


@pytest.fixture(scope="module")
def states(feature_map, X_data):
    return compute_states(feature_map, X_data, n_jobs=1)


@pytest.fixture(scope="module")
def K(states):
    return fidelity_kernel(states)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
class TestKernelProperties:
    """Test that the fidelity kernel has the expected mathematical properties."""

    def test_symmetric(self, K):
        """K should be symmetric."""
        np.testing.assert_allclose(K, K.T, atol=1e-10)

    def test_diagonal_ones(self, K):
        """Diagonal entries should be 1.0 (self-fidelity)."""
        np.testing.assert_allclose(np.diag(K), 1.0, atol=1e-10)

    def test_entries_in_01(self, K):
        """All entries should be in [0, 1]."""
        assert K.min() >= -1e-10, f"Min entry {K.min()} is below 0"
        assert K.max() <= 1.0 + 1e-10, f"Max entry {K.max()} is above 1"

    def test_psd(self, K):
        """K should be positive semidefinite (min eigenvalue >= -tol)."""
        min_eig = np.linalg.eigvalsh(K).min()
        assert min_eig >= -1e-8, f"Min eigenvalue {min_eig} — not PSD"


class TestQiskitConsistency:
    """Verify our statevector kernel matches Qiskit's FidelityQuantumKernel."""

    def test_matches_qiskit_kernel(self, feature_map, X_data, K):
        from qiskit_machine_learning.kernels import FidelityQuantumKernel

        qiskit_kernel = FidelityQuantumKernel(feature_map=feature_map)
        K_qiskit = qiskit_kernel.evaluate(X_data)

        np.testing.assert_allclose(
            K, K_qiskit, atol=1e-6,
            err_msg="Statevector kernel differs from Qiskit FidelityQuantumKernel"
        )


class TestKernelDiagnostics:
    """Test kernel_diagnostics returns correct structure and values."""

    def test_keys_present(self, K):
        diag = kernel_diagnostics(K)
        expected = {"offdiag_mean", "offdiag_std", "min_eigenvalue", "effective_rank"}
        assert expected.issubset(diag.keys())

    def test_effective_rank_ge_1(self, K):
        diag = kernel_diagnostics(K)
        assert diag["effective_rank"] >= 1.0, (
            f"Effective rank {diag['effective_rank']} is less than 1"
        )

    def test_kta_with_labels(self, K):
        y = np.arange(N_SAMPLES) % 3  # dummy labels
        diag = kernel_diagnostics(K, y=y)
        assert "kernel_target_alignment" in diag
        assert -1.0 <= diag["kernel_target_alignment"] <= 1.0


class TestComputeStates:
    """Test compute_states edge cases."""

    def test_output_shape(self, states):
        assert states.shape == (N_SAMPLES, 2 ** N_QUBITS)

    def test_normalized(self, states):
        """Each statevector should be unit norm."""
        norms = np.linalg.norm(states, axis=1)
        np.testing.assert_allclose(norms, 1.0, atol=1e-10)

    def test_empty_input(self, feature_map):
        X_empty = np.empty((0, N_QUBITS))
        S = compute_states(feature_map, X_empty, n_jobs=1)
        assert S.shape == (0, 2 ** N_QUBITS)


class TestAsymmetricKernel:
    """Test fidelity_kernel with B != None."""

    def test_asymmetric_shape(self, states):
        A = states[:5]
        B = states[5:15]
        K_ab = fidelity_kernel(A, B)
        assert K_ab.shape == (5, 10)

    def test_asymmetric_entries_in_01(self, states):
        A = states[:5]
        B = states[5:15]
        K_ab = fidelity_kernel(A, B)
        assert K_ab.min() >= -1e-10
        assert K_ab.max() <= 1.0 + 1e-10
