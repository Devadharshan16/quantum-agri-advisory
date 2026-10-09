Phase 1:
1. Data Preparation (`data_prep.py`): Downloaded the crop recommendation dataset (2200 rows, 22 crops). Encoded crop names to integers using LabelEncoder. Extracted the 7-feature matrix. Applied StandardScaler to normalize features, then applied PCA to compress 7 features down to 4 principal components. Applied MinMaxScaler to scale the PCA components to the [0, π] range for quantum angle encoding. Subsampled the training set to 25 samples per class (550 total) to ensure the QSVC kernel matrix computation is feasible on a classical CPU simulator, while keeping the full test set for honest evaluation.

2. Dataset — Crop Recommendation Dataset:
   - Full name: Crop Recommendation Dataset
   - Original source: Kaggle, published by Atharva Ingle
   - Working URL: https://raw.githubusercontent.com/Gladiator07/Harvestify/master/Data-processed/crop_recommendation.csv
   - Total rows: 2200 (exactly 100 samples per crop — perfectly balanced)
   - Total columns: 8
   - Features (7 input columns): N, P, K, temperature, humidity, ph, rainfall
   - Target column: label — 22 unique crop classes

3. Why this dataset was chosen:
   - Perfect class balance (100 samples per crop).
   - Features map directly to real-world agricultural parameters.
   - PCA + MinMaxScaling fits all values cleanly into [0, π].

Phase 2 
4. Quantum Circuit Design (`circuit_design.py`): Transitioned from a Variational Quantum Classifier (VQC) to a Quantum Support Vector Classifier (QSVC) to overcome the barren plateau problem. The circuit now consists purely of a `ZZFeatureMap` with 4 qubits, 2 repetitions, and full entanglement. This circuit encodes the classical data into a quantum state |φ(x)⟩. Crucially, there are zero trainable quantum parameters. The circuit is used solely to compute the quantum kernel (fidelity) between data points.

5. Phase 2 completed successfully. ZZFeatureMap circuit structure confirmed: Hadamard → P(2x) → ZZ entanglement. Full circuit depth and gate count logged. Circuit diagram saved to assets/circuit_diagram.png.

Phase 3
6. QSVC Training (`train.py`): Loads the preprocessed data, builds the ZZFeatureMap and FidelityQuantumKernel. Computes the quantum kernel matrix K(x, x') = |⟨φ(x)|φ(x')⟩|² for the training data row-by-row with a progress bar. This fidelity computation is a direct application of the Swap Test (Class 43 from the syllabus). The precomputed kernel matrix is then fed into a classical SVM (sklearn.svm.SVC). Unlike VQC's gradient-free optimization which wanders on flat landscapes, SVM uses convex optimization to guarantee a global optimum.

7. Phase 3 completed. Computed a 550x550 kernel matrix for training and a 440x550 kernel matrix for testing. The QSVC model achieved much higher accuracy by avoiding the barren plateaus of VQC. Saved the SVC model (`qsvc_model.joblib`), the precomputed training kernel (`K_train.npy`), and metrics (`metrics.json`).

Phase 4 (Current State)
8. Prediction (`predict.py`): Updated to load the QSVC pipeline. It accepts user inputs, applies StandardScaler → PCA → MinMaxScaler, computes the quantum kernel vector against the saved training data, and outputs the optimal crop recommendation via the trained SVM.

Conclusion:
Switching from VQC to QSVC provided a massive breakthrough. By offloading the optimization to a classical SVM and using the quantum circuit purely as a kernel feature map (Swap Test), we bypassed barren plateaus and achieved stable, high-accuracy multi-class classification for all 22 crops.
