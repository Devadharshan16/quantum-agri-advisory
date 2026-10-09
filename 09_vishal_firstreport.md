# Quantum Agri-Advisory Repository Status Report

**Report file:** `09_vishal_firstreport.md`  
**Repository:** `Devadharshan16/quantum-agri-advisory`  
**Project:** Quantum Intelligence-Based Agricultural Advisory System for Weather-Driven Crop Recommendations  
**Assessment date:** 2026-10-09

## Executive Summary

This repository is currently a **hybrid quantum-classical research prototype**, not a complete deployed agricultural advisory platform.

- Functional code exists in the repository root:
  - `data_prep.py`
  - `circuit_design.py`
  - `train.py`
  - `predict.py`
  - `benchmark.py`
- The requested `/quantum`, `/data_pipeline`, `/classical_baseline`, `/api`, and `/ui` directories do not exist.
- The current model is a **4-qubit `ZZFeatureMap` plus `FidelityQuantumKernel` and a classical SVM**.
- It is not currently a QAOA, quantum annealing, or QUBO implementation.
- The checked-in current QSVC artifact reports **60.23% test accuracy** in `models/metrics.json`.
- There is no automated test suite and no coverage report. Effective tested coverage is therefore **not measured; functionally 0% tested**.
- The active Python 3.12.3 virtual environment does not currently have Qiskit installed, so the pipeline cannot execute until dependencies are installed.

## 1. Repository Structure and Active Codebase

### Current Directory Layout

```text
quantum-agri-advisory/
├── .gitignore
├── requirements.txt
├── QUANTUM_AGRICULTURE_PIPELINE.md
├── log.md
├── data_prep.py
├── circuit_design.py
├── train.py
├── predict.py
├── benchmark.py
├── assets/
│   ├── circuit_diagram.png
│   ├── confusion_matrix_kernel.png
│   ├── feature_map_7q.png
│   └── vqc_circuit_5q.png
└── models/
    ├── metrics.json
    ├── kernel_metrics.json
    ├── data_meta.json
    ├── K_train.npy
    ├── X_train_kernel.npy
    └── several older model artifacts
```

### Requested Primary Directories

| Directory | Status |
|---|---|
| `/quantum` | Does not exist |
| `/data_pipeline` | Does not exist; root-level `data_prep.py` is the functional preprocessing script |
| `/classical_baseline` | Does not exist; historical baseline metrics are stored in `models/kernel_metrics.json`, but no current baseline implementation directory exists |
| `/api` | Does not exist |
| `/ui` | Does not exist; `predict.py` is an interactive CLI only |

### Functional Root-Level Code

#### `data_prep.py`

Implements the dataset download, label encoding, train/test split, class subsampling, scaling, PCA, and metadata generation.

#### `circuit_design.py`

Creates and draws the 4-qubit `ZZFeatureMap`.

#### `train.py`

Computes training and test quantum kernels and trains a classical SVM over the precomputed kernel.

#### `predict.py`

Loads the trained pipeline, accepts interactive soil and weather values, computes a kernel vector, and returns a crop recommendation.

#### `benchmark.py`

Contains a small timing benchmark for 4- and 7-qubit kernel evaluation. It is present locally, although the latest remote commit removes it.

### Recent Commits and Branches

Current branches:

```text
main
origin/main
```

Recent commits:

| Commit | Date | Description |
|---|---:|---|
| `477030b` | 2026-10-09 | Agent host session baseline checkpoint |
| `8256f76` | 2026-10-09 | Refactor: remove benchmark script, optimize prediction pipeline, update metadata/assets |
| `4005f30` | 2026-10-09 | Local changes and model artifacts |
| `9d83622` | 2026-10-09 | Refactor pipeline from VQC to QSVC |
| `27f8d5f` | 2026-10-07 | Check |
| `ca852b8` | 2026-10-06 | Initial quantum agriculture pipeline specification |

The local `main` branch is **one commit behind `origin/main`**. The remote commit `8256f76` removes `benchmark.py`, while the local branch still contains it.

### Open Integration Blockers

1. **Dependencies are missing in the active environment.** Importing Qiskit currently fails with:

   ```text
   ModuleNotFoundError: No module named 'qiskit'
   ```

2. **Required runtime artifacts are not fully committed.** `predict.py` requires:

   - `models/qsvc_model.joblib`
   - `models/label_encoder.joblib`
   - `models/standard_scaler.joblib`
   - `models/pca_transformer.joblib`
   - `models/minmax_scaler.joblib`

   These files are ignored by `.gitignore`, so a fresh clone cannot run prediction without first running the pipeline.

3. The `data/` directory and generated preprocessing arrays are not present in the tracked repository. Data preparation requires downloading the dataset from the network.
4. Local and remote branches are out of sync.
5. There is no API, frontend, CI configuration, Dockerfile, or environment lock file beyond `requirements.txt`.

### Automated Tests and Coverage

There are:

- No `tests/` directory.
- No pytest tests.
- No unittest tests.
- No integration tests.
- No quantum-circuit tests.
- No preprocessing tests.
- No coverage configuration.
- No coverage report.

Therefore, automated coverage is **not measured**. For practical reporting, the repository has **0% tested code coverage**.

## 2. Quantum Engine and Algorithm Implementation

### Quantum Framework

The declared framework in `requirements.txt` is:

```text
qiskit==1.1.0
qiskit-machine-learning==0.7.2
qiskit-algorithms==0.3.0
qiskit-aer==0.14.2
```

The active environment is Python 3.12.3, but Qiskit is not currently installed in the active `.venv`. Thus, the declared environment and the runnable environment are inconsistent.

### Algorithm Formulation

The active algorithm is **quantum-kernel classification**:

1. Seven agricultural features are preprocessed.
2. PCA reduces them from 7 to 4 features.
3. A 4-qubit `ZZFeatureMap` encodes the four PCA values.
4. `FidelityQuantumKernel` computes:

   \[
   K(x,x') = |\langle \phi(x) \mid \phi(x') \rangle|^2
   \]

5. A classical `sklearn.svm.SVC(kernel='precomputed')` performs the final 22-class crop classification.

This is implemented in `train.py`.

It is **not** currently modeled as:

- QUBO,
- QAOA,
- quantum annealing,
- constrained crop-allocation optimization, or
- a variational quantum classifier.

Older VQC artifacts remain under `models/`, but they are not the active training path.

### Quantum Feature Map

The active mapping is:

```text
ZZFeatureMap
- 4 qubits
- 4 input features
- reps=2
- full entanglement
```

It encodes individual feature phases and pairwise feature interactions through ZZ-style entanglement.

The feature map is defined in `circuit_design.py` and recreated during training and prediction.

### Runtime Backend

No explicit IBM Quantum, AWS Braket, or other live hardware backend is configured.

The code uses Qiskit Machine Learning's `FidelityQuantumKernel` without specifying a hardware backend. The intended execution is therefore local Qiskit reference/simulator execution when dependencies are installed.

| Backend type | Status |
|---|---|
| Live IBM QPU | No evidence |
| IBM Quantum account/backend | Not configured |
| AWS Braket | Not configured |
| Explicit noisy simulator | Not configured |
| Local simulator/reference execution | Intended path |

Although `qiskit-aer` is listed as a dependency, the source does not explicitly instantiate an Aer simulator.

### Circuit Depth and Gate Counts

`circuit_design.py` prints circuit depth and gate count at runtime, but these values are not saved in metadata or metrics.

The active environment cannot currently import Qiskit, so exact runtime values could not be independently measured. There is no recorded average for:

- circuit depth,
- total gate count,
- two-qubit gate count,
- execution latency, or
- backend noise/error rates.

## 3. Weather and Agricultural Data Pipeline

### Data Source

`data_prep.py` downloads:

```text
https://raw.githubusercontent.com/Gladiator07/Harvestify/master/Data-processed/crop_recommendation.csv
```

According to `log.md`, this is a GitHub-hosted mirror of the Kaggle Crop Recommendation Dataset attributed to Atharva Ingle.

Dataset characteristics:

- 2,200 rows.
- 22 crop classes.
- 100 records per crop.
- 7 input features.
- Balanced class distribution.

### Features Used

```text
N
P
K
temperature
humidity
ph
rainfall
```

The metadata classifies them as:

- Weather: `temperature`, `humidity`, `rainfall`
- Soil: `N`, `P`, `K`, `ph`

There is no integration with:

- OpenWeatherMap.
- NOAA.
- ERA5.
- Live weather forecast APIs.
- Soil moisture services.
- Solar radiation APIs.
- Live agricultural sensor feeds.

The weather data is static historical tabular input rather than dynamically fetched forecast data.

### Preprocessing and Normalization

`data_prep.py` performs:

1. Stratified 80/20 train/test split.
2. Training subsampling to 25 samples per class:
   - 550 training samples.
   - 440 test samples.
3. `StandardScaler`:
   - zero mean,
   - unit variance.
4. PCA:
   - 7 features to 4 components.
5. `MinMaxScaler`:
   - maps PCA values to `[0, π]`.
6. Four-qubit angle-style encoding through `ZZFeatureMap`.

The saved PCA metadata indicates approximately **76.95% total variance retention** across the four components:

```text
0.2785 + 0.1898 + 0.1580 + 0.1433 = 0.7695
```

### Missing Values and Extreme Weather

There is no explicit missing-value handling:

- no imputation,
- no null-row removal,
- no missingness indicators,
- no missing-data validation report.

There is also no statistical anomaly detection or outlier treatment:

- no IQR filtering,
- no z-score filtering,
- no winsorization,
- no extreme-weather model.

The CLI predictor applies hard input ranges, but those are interactive validation bounds rather than a general data-quality or anomaly-handling strategy.

## 4. Agricultural Business Logic and Classical Baselines

### Agronomic Constraints

The active model objective contains no explicit agronomic optimization constraints such as:

- crop rotation,
- nitrogen depletion,
- phosphorus/potassium constraints,
- seasonal water quotas,
- irrigation capacity,
- farm-area allocation,
- market-price volatility,
- labor constraints,
- multi-season planning,
- yield maximization.

The model is a supervised classifier that predicts one of 22 crop labels from input features.

The crop descriptions in `predict.py` provide static advisory text for season, region, and tips, but these descriptions do not participate in the model objective.

### Classical Baseline

There is no active, organized `/classical_baseline` module.

Historical saved metrics in `models/kernel_metrics.json` report results for:

- classical SVM with RBF kernel,
- random forest,
- QMeans,
- cross-validation.

However:

- baseline training code is not present in the current repository structure,
- the metrics appear to belong to an earlier 7-qubit or alternative pipeline,
- they are not directly comparable to the current 4-qubit QSVC result without reproducing the exact preprocessing and split.

Therefore, a historical classical comparison exists as saved output, but not as a clean, reproducible baseline implementation.

### Recorded Metrics

The current `models/metrics.json` reports:

| Metric | Value |
|---|---:|
| Training accuracy | 92.73% |
| Test accuracy | 60.23% |
| Number of qubits | 4 |
| Number of features | 4 |
| Number of classes | 22 |
| Training samples | 550 |
| Test samples | 440 |
| Trainable quantum parameters | 0 |

The repository does not record:

- algorithmic convergence rate,
- quantum optimizer iterations,
- expected crop yield,
- economic return,
- solution optimality,
- persisted time-to-solution benchmark,
- hardware execution cost,
- circuit error rate,
- repeated-run confidence intervals.

The training script prints kernel computation timing during execution, but it is not persisted as structured benchmark output.

## 5. API Layer and Deployment

### Backend API

There is no active FastAPI, Flask, Django, or REST backend.

The only serving-like component is the interactive command-line loop in `predict.py`. It:

- prompts for soil and weather values,
- transforms the input,
- evaluates the quantum kernel,
- predicts a crop,
- prints advisory information.

It does not expose:

- HTTP endpoints,
- JSON request/response schemas,
- authentication,
- persistence,
- health checks,
- service monitoring.

### Frontend or Dashboard

There is no frontend UI or dashboard.

Although `streamlit==1.35.0` is listed in `requirements.txt`, there is:

- no Streamlit application,
- no UI source directory,
- no HTML/JavaScript frontend,
- no API-to-UI connection,
- no dashboard displaying weather or recommendations.

### Reproducibility and Deployment Files

| Configuration | Status |
|---|---|
| `requirements.txt` | Present with pinned versions |
| `environment.yml` | Missing |
| `pyproject.toml` | Missing |
| `Dockerfile` | Missing |
| `docker-compose.yml` | Missing |
| CI workflow | Not present |
| Dependency lock file | Missing |
| Installed Qiskit environment | Not functional |

The pinned requirements file is useful, but reproducibility remains incomplete because the repository lacks:

- an environment lock,
- container configuration,
- automated setup validation,
- committed model transformers,
- committed trained classifier,
- automated tests,
- CI execution.

## Final Assessment

The project has a documented and partially implemented **quantum-kernel classification prototype**:

```text
7 agricultural features
        ↓
StandardScaler
        ↓
PCA: 7 → 4
        ↓
MinMaxScaler: [0, π]
        ↓
4-qubit ZZFeatureMap
        ↓
FidelityQuantumKernel
        ↓
Classical SVM
        ↓
22-class crop recommendation
```

The strongest implemented area is the QSVC-style hybrid quantum-classical classification workflow.

The major gaps are:

1. No module-based `/quantum`, `/data_pipeline`, `/api`, `/ui`, or `/classical_baseline` architecture.
2. No tests or coverage.
3. No live weather or soil data sources.
4. No missing-value or anomaly strategy.
5. No agronomic optimization constraints.
6. No active reproducible classical baseline.
7. No HTTP API or frontend.
8. Missing Qiskit dependencies in the active environment.
9. Current QSVC test accuracy is only **60.23%**, not the higher accuracy suggested by older documentation or stale model artifacts.
10. Exact circuit depth, gate counts, and execution benchmarks are not currently recorded.

