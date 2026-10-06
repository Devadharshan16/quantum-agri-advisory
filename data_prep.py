import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
import joblib
import os

# Create directories
os.makedirs('data', exist_ok=True)
os.makedirs('models', exist_ok=True)

print("=" * 60)
print("PHASE 1: DATA PREPARATION (ALL 7 FEATURES)")
print("=" * 60)

# Step 1: Dataset
print("\n[1/5] Downloading dataset...")
url = "https://raw.githubusercontent.com/Gladiator07/Harvestify/master/Data-processed/crop_recommendation.csv"
df = pd.read_csv(url)

target_crops = ['rice', 'cotton', 'apple', 'orange']
df = df[df['label'].isin(target_crops)]

print(f"  Dataset filtered to 4 crops: {target_crops}")
print(f"  Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"  Columns: {list(df.columns)}")
print(f"  Unique crops: {df['label'].nunique()}")

# Step 2: Label encoding
print("\n[2/5] Encoding labels...")
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(df['label'])
print(f"  Encoded {len(label_encoder.classes_)} crop classes:")
for i, crop in enumerate(label_encoder.classes_):
    print(f"  {i}: {crop}")
joblib.dump(label_encoder, 'models/label_encoder.joblib')

# Step 3: Feature matrix
print("\n[3/5] Extracting features...")
X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']].values
y = y_encoded
print(f"  Feature matrix shape: {X.shape}")

# Step 4: Stratified train/test split
print("\n[4/5] Stratified train/test split (80/20)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"  Training set: {X_train.shape[0]} samples")
print(f"  Test set:     {X_test.shape[0]} samples")

# Step 5: MinMaxScaler to [0, \pi] - quantum rotation range
print("\n[5/5] Scaling to quantum rotation range [0, \\pi]...")
scaler = MinMaxScaler(feature_range=(0, np.pi))
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

print(f"  Scaling complete")
print(f"  Min value: {X_train_scaled.min():.4f}")
print(f"  Max value: {X_train_scaled.max():.4f}")
joblib.dump(scaler, 'models/minmax_scaler.joblib')

# Save processed data
print("\n[SUMMARY] Saving processed data...")
np.save('data/X_train_scaled.npy', X_train_scaled)
np.save('data/X_test_scaled.npy',  X_test_scaled)
np.save('data/y_train.npy', y_train)
np.save('data/y_test.npy',  y_test)

print("\n" + "=" * 60)
print("  PHASE 1 COMPLETE")
print("=" * 60)
