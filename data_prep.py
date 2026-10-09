import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
import joblib
import json
import os

os.makedirs('data', exist_ok=True)
os.makedirs('models', exist_ok=True)

print("=" * 65)
print("PHASE 1: DATA PREPARATION (ALL 22 CROPS — QSVC PIPELINE)")
print("=" * 65)

NUM_FEATURES = 7   # must match NUM_QUBITS in circuit_design.py & train.py

# ➖➖ Load full dataset (no crop filter — use all 22) ➖➖➖➖➖➖➖➖➖➖➖
print("\n[1/6] Loading dataset...")
url = ("https://raw.githubusercontent.com/Gladiator07/Harvestify"
       "/master/Data-processed/crop_recommendation.csv")
df = pd.read_csv(url)

NUM_CLASSES = df['label'].nunique()
print(f"  Total rows : {df.shape[0]}  ({df.shape[0]//NUM_CLASSES} samples/class)")
print(f"  Unique crops: {NUM_CLASSES}")
print(f"  Crops: {sorted(df['label'].unique().tolist())}")

# ➖➖ Label encoding ➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖
print("\n[2/6] Encoding labels...")
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(df['label'])
print(f"  {len(label_encoder.classes_)} classes:")
for i, crop in enumerate(label_encoder.classes_):
    print(f"    {i:2d}: {crop}")
joblib.dump(label_encoder, 'models/label_encoder.joblib')

# ➖➖ Feature matrix ➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖
print("\n[3/6] Extracting features...")
FEATURES         = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
WEATHER_FEATURES = ['temperature', 'humidity', 'rainfall']   # live inputs in predict.py
SOIL_FEATURES    = ['N', 'P', 'K', 'ph']

X = df[FEATURES].values
y = y_encoded
print(f"  Feature matrix : {X.shape}")
print(f"  Weather features (real-time inputs): {WEATHER_FEATURES}")
print(f"  Soil features                      : {SOIL_FEATURES}")

# ➖➖ Train/test split ➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖
print("\n[4/6] Stratified 80/20 split...")
X_train_full, X_test, y_train_full, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"  Full train : {X_train_full.shape[0]} samples  "
      f"({X_train_full.shape[0]//NUM_CLASSES} per class)")
print(f"  Test       : {X_test.shape[0]} samples  "
      f"({X_test.shape[0]//NUM_CLASSES} per class)")

# ➖➖ Subsample training set (QSVC kernel matrix scales as N^2) ➖
SAMPLES_PER_CLASS = 25   # 25 * 22 = 550 => kernel matrix 550*550 ≈ 150K evals
print(f"\n[5/6] Subsampling training set to {SAMPLES_PER_CLASS} per class...")
sub_idx = []
for c in range(NUM_CLASSES):
    class_idx = np.where(y_train_full == c)[0]
    np.random.seed(42)
    chosen = np.random.choice(class_idx, size=min(SAMPLES_PER_CLASS, len(class_idx)), replace=False)
    sub_idx.extend(chosen)
sub_idx = sorted(sub_idx)
X_train = X_train_full[sub_idx]
y_train = y_train_full[sub_idx]
print(f"  Subsampled : {X_train.shape[0]} samples  "
      f"({SAMPLES_PER_CLASS} per class)")
print(f"  Kernel matrix will be : {X_train.shape[0]}x{X_train.shape[0]}  "
      f"(~{X_train.shape[0]**2:,} evaluations)")

# ➖➖ StandardScaler (zero mean, unit variance) ➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖
print("\n[6/6] Standardizing and Scaling features...")
std_scaler = StandardScaler()
X_train_std = std_scaler.fit_transform(X_train)
X_test_std  = std_scaler.transform(X_test)
print(f"  StandardScaler applied (zero mean, unit variance)")
joblib.dump(std_scaler, 'models/standard_scaler.joblib')

# ➖➖ Scale to [0, π] for angle encoding ➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖
scaler = MinMaxScaler(feature_range=(0, np.pi))
X_train_scaled = scaler.fit_transform(X_train_std)
X_test_scaled  = scaler.transform(X_test_std)
print(f"  MinMaxScaler applied: [{X_train_scaled.min():.4f}, {X_train_scaled.max():.4f}]")
joblib.dump(scaler, 'models/minmax_scaler.joblib')

# ➖➖ Save arrays ➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖
np.save('data/X_train_scaled.npy', X_train_scaled)
np.save('data/X_test_scaled.npy',  X_test_scaled)
np.save('data/y_train.npy', y_train)
np.save('data/y_test.npy',  y_test)

# ➖➖ Save metadata (used by predict.py) ➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖
meta = {
    'features'             : FEATURES,
    'weather_features'     : WEATHER_FEATURES,
    'soil_features'        : SOIL_FEATURES,
    'num_features'         : NUM_FEATURES,
    'num_qubits'           : NUM_FEATURES,   # 1 qubit per feature
    'num_classes'          : NUM_CLASSES,
    'crops'                : list(label_encoder.classes_),
}
with open('models/data_meta.json', 'w') as f:
    json.dump(meta, f, indent=2)
print("  Saved: models/data_meta.json")

print("\n" + "=" * 65)
print("PHASE 1 COMPLETE")
print(f"  {NUM_CLASSES} crops | {X_train_scaled.shape[0]} train | "
      f"{X_test_scaled.shape[0]} test")
print(f"  Output: {X_train_scaled.shape}  ->  {NUM_FEATURES} features "
      f"for {NUM_FEATURES} qubits")
print("=" * 65)
