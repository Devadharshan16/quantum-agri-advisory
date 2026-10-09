#!/usr/bin/env python3
"""
Quantum Agricultural Advisory System
────────────────────────────────────
Takes weather + soil inputs → runs trained QSVC → recommends a crop.
This is the final "product" layer on top of the trained quantum model.

Run:  python predict.py
"""

import numpy as np
import json
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

# ── Crop knowledge base (for richer advisory output) ─────────
CROP_INFO = {
    'apple'      : {'season': 'Oct–Mar',        'region': 'Himachal Pradesh, J&K, Uttarakhand',
                    'tip': 'Requires cold winters and cool summers.'},
    'banana'     : {'season': 'Year-round',     'region': 'Tamil Nadu, AP, Maharashtra',
                    'tip': 'Thrives in humid tropical climate; needs irrigation.'},
    'blackgram'  : {'season': 'Jun–Sep (Kharif)', 'region': 'South India (urad dal)',
                    'tip': 'Drought tolerant; good for light soil.'},
    'chickpea'   : {'season': 'Oct–Mar (Rabi)', 'region': 'MP, Maharashtra, Rajasthan',
                    'tip': 'India produces 70% of world supply; no-waterlog needed.'},
    'coconut'    : {'season': 'Year-round',     'region': 'Kerala, Tamil Nadu, Karnataka',
                    'tip': 'High humidity coastal crop; 4-5 years to first yield.'},
    'coffee'     : {'season': 'Oct–Feb',        'region': 'Karnataka, Kerala, Tamil Nadu',
                    'tip': 'Shade-grown; good drainage essential.'},
    'cotton'     : {'season': 'Apr–Nov (Kharif)', 'region': 'Gujarat, Maharashtra, Telangana',
                    'tip': 'India 2nd largest producer; needs well-drained black soil.'},
    'grapes'     : {'season': 'Jan–May',        'region': 'Maharashtra, Karnataka',
                    'tip': 'Requires training systems (trellis); drip irrigation best.'},
    'jute'       : {'season': 'Mar–Jun (Kharif)', 'region': 'West Bengal, Assam, Bihar',
                    'tip': 'Grows in alluvial soil; needs high rainfall.'},
    'kidneybeans': {'season': 'Oct–Mar (Rabi)', 'region': 'UP, Uttarakhand, J&K',
                    'tip': 'Cool climate pulse; fix nitrogen in soil.'},
    'lentil'     : {'season': 'Oct–Mar (Rabi)', 'region': 'North India (masoor dal)',
                    'tip': 'Highly nutritious; grows well in loamy soil.'},
    'maize'      : {'season': 'Jun–Oct (Kharif)', 'region': 'Karnataka, Rajasthan, MP',
                    'tip': '3rd largest cereal in India; versatile crop.'},
    'mango'      : {'season': 'Mar–Jun',        'region': 'UP, AP, Tamil Nadu',
                    'tip': 'National fruit of India; 5–8 years to first yield.'},
    'mothbeans'  : {'season': 'Jun–Sep (Kharif)', 'region': 'Rajasthan staple',
                    'tip': 'Extreme drought resistance; thrives in arid zones.'},
    'mungbean'   : {'season': 'Jun–Sep (Kharif)', 'region': 'Pan-India (moong dal)',
                    'tip': 'Short-duration; good for crop rotation.'},
    'orange'     : {'season': 'Nov–Mar',        'region': 'Nagpur, Coorg, Sikkim',
                    'tip': 'Nagpur orange is GI-tagged; needs well-drained soil.'},
    'papaya'     : {'season': 'Year-round',     'region': 'AP, Tamil Nadu, Gujarat',
                    'tip': 'Fastest fruiting tropical crop; harvest in 9–12 months.'},
    'pigeonpeas' : {'season': 'Jun–Nov (Kharif)', 'region': 'Maharashtra, AP (tur dal)',
                    'tip': 'India largest producer globally; deep-rooted.'},
    'pomegranate': {'season': 'Aug–Feb',        'region': 'Maharashtra, Rajasthan, Gujarat',
                    'tip': 'Highly drought tolerant; profitable export crop.'},
    'rice'       : {'season': 'Jun–Nov (Kharif)', 'region': 'Punjab, WB, Tamil Nadu',
                    'tip': 'Largest cultivated crop in India; needs waterlogging.'},
    'watermelon' : {'season': 'Feb–Jun',        'region': 'AP, Karnataka, Rajasthan',
                    'tip': 'Sandy loam soil; short 70-90 day crop cycle.'},
}

BANNER = """
+========================================================+
|    QUANTUM AGRICULTURAL ADVISORY SYSTEM                |
|    Powered by QSVC (Quantum Kernel SVM)                |
|    Course: 23CSE463 Quantum Computing - Amrita Chennai  |
+========================================================+
"""

# ── Check model files exist ───────────────────────────────────
REQUIRED = [
    'models/qsvc_model.joblib',
    'models/X_train_kernel.npy',
    'models/label_encoder.joblib',
    'models/standard_scaler.joblib',
    'models/pca_transformer.joblib',
    'models/minmax_scaler.joblib',
    'models/data_meta.json',
]
missing = [f for f in REQUIRED if not os.path.exists(f)]
if missing:
    print("\nERROR: Missing files. Run the pipeline first:")
    print("  python data_prep.py")
    print("  python circuit_design.py")
    print("  python train.py")
    for f in missing:
        print(f"  X  {f}")
    raise SystemExit(1)

# ── Load saved pipeline ───────────────────────────────────────
print(BANNER)
print("Loading quantum model ", end='', flush=True)
label_encoder = joblib.load('models/label_encoder.joblib')
std_scaler    = joblib.load('models/standard_scaler.joblib')
pca           = joblib.load('models/pca_transformer.joblib')
scaler        = joblib.load('models/minmax_scaler.joblib')
svc           = joblib.load('models/qsvc_model.joblib')
X_train_kern  = np.load('models/X_train_kernel.npy')
with open('models/data_meta.json') as f:
    meta = json.load(f)

NUM_QUBITS   = meta['num_qubits']            # 4
NUM_FEATURES = meta['num_pca_components']     # 4
num_classes  = meta['num_classes']

# Build quantum kernel for inference
from qiskit.circuit.library import ZZFeatureMap
from qiskit_machine_learning.kernels import FidelityQuantumKernel

feature_map = ZZFeatureMap(feature_dimension=NUM_QUBITS, reps=2, entanglement='full')
kernel = FidelityQuantumKernel(feature_map=feature_map)
print("done\n")

# ── Helper: validated float input ────────────────────────────
def get_float(prompt, lo, hi):
    while True:
        try:
            v = float(input(prompt))
            if lo <= v <= hi:
                return v
            print(f"    -> Enter a value between {lo} and {hi}")
        except ValueError:
            print("    -> Please enter a number")

# ── Main advisory loop ────────────────────────────────────────
FEATURES = meta['features']   # ['N','P','K','temperature','humidity','ph','rainfall']

print("=" * 60)
print("  Enter your farm conditions to get a crop recommendation")
print("=" * 60)

while True:
    print("\n  -- Soil Nutrients --")
    N   = get_float("    Nitrogen   (N)  [0-140 kg/ha] : ", 0,   140)
    P   = get_float("    Phosphorus (P)  [5-145 kg/ha] : ", 5,   145)
    K   = get_float("    Potassium  (K)  [5-205 kg/ha] : ", 5,   205)
    ph  = get_float("    Soil pH         [3.5-9.5]     : ", 3.5, 9.5)

    print("\n  -- Current Weather --")
    temp     = get_float("    Temperature (C)  [8-44]       : ", 8,  44)
    humidity = get_float("    Humidity     (%) [14-100]     : ", 14, 100)
    rainfall = get_float("    Rainfall    (mm) [20-300]     : ", 20, 300)

    # Build feature vector in training order
    x_raw    = np.array([[N, P, K, temp, humidity, ph, rainfall]])

    # Classical preprocessing pipeline
    x_std    = std_scaler.transform(x_raw)    # standardize
    x_pca    = pca.transform(x_std)           # 7 -> 4 PCA
    x_scaled = scaler.transform(x_pca)        # scale to [0, pi]

    # ── QSVC inference ─────────────────────────────────────────
    print("\n  Running quantum kernel inference ", end='', flush=True)
    # Compute kernel vector: K(x_new, x_train) for all training points
    k_vec     = kernel.evaluate(x_scaled, X_train_kern)
    pred_idx  = svc.predict(k_vec)[0]
    pred_crop = label_encoder.classes_[pred_idx]
    print("done")

    info = CROP_INFO.get(pred_crop, {})

    print("\n" + "=" * 60)
    print(f"  RECOMMENDED CROP: {pred_crop.upper()}")
    print("=" * 60)
    if info:
        print(f"  Season  : {info.get('season', 'N/A')}")
        print(f"  Region  : {info.get('region', 'N/A')}")
        print(f"  Tip     : {info.get('tip', '')}")
    print(f"\n  Your conditions:")
    print(f"    Soil    - N:{N:.0f}  P:{P:.0f}  K:{K:.0f}  pH:{ph:.1f}")
    print(f"    Weather - Temp:{temp:.1f}C  "
          f"Humidity:{humidity:.0f}%  Rainfall:{rainfall:.0f}mm")
    print(f"\n  Quantum pipeline:")
    print(f"    7 raw features")
    print(f"    -> StandardScaler (zero mean, unit variance)")
    print(f"    -> {NUM_FEATURES} PCA components  "
          f"(variance retained: {sum(meta['pca_explained_variance'])*100:.1f}%)")
    print(f"    -> {NUM_QUBITS}-qubit ZZFeatureMap (quantum kernel)")
    print(f"    -> QSVC {num_classes}-class classification")
    print(f"    -> {pred_crop}")

    # Load metrics if available
    if os.path.exists('models/metrics.json'):
        with open('models/metrics.json') as f:
            m = json.load(f)
        print(f"\n  Model: {m.get('model_type','QSVC')} | "
              f"test acc {m.get('test_accuracy',0)*100:.1f}%")

    print()
    again = input("  Try another scenario? [y/n]: ").strip().lower()
    if again != 'y':
        break

print("\nThank you for using the Quantum Agricultural Advisory System!")
print("Course 23CSE463 - Amrita School of Computing, Chennai")
