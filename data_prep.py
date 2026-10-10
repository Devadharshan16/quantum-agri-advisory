import argparse
import codecs
import csv
import json
import logging
import urllib.request
from pathlib import Path
from typing import Tuple, List

import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder

def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def download_and_parse_data(url: str) -> Tuple[np.ndarray, np.ndarray, List[str], LabelEncoder, List[str]]:
    logging.info(f"Downloading data from {url}")
    response = urllib.request.urlopen(url)
    reader = csv.reader(codecs.iterdecode(response, 'utf-8'))
    
    header = next(reader)
    features_list = header[:-1]
    
    X = []
    y_str = []
    
    for row in reader:
        if not row: 
            continue
        X.append([float(x) for x in row[:-1]])
        y_str.append(row[-1])
        
    X_np = np.array(X)
    
    le = LabelEncoder()
    y_np = le.fit_transform(y_str)
    
    return X_np, y_np, features_list, le, le.classes_.tolist()

def main() -> None:
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Data Preparation for Quantum ML Capstone")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for splitting (default: 42)")
    parser.add_argument("--data-dir", type=str, default="data", help="Directory for data outputs")
    parser.add_argument("--model-dir", type=str, default="models", help="Directory for model outputs")
    args = parser.parse_args()
    
    np.random.seed(args.seed)
    
    data_dir = Path(args.data_dir)
    model_dir = Path(args.model_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)
    
    url = "https://raw.githubusercontent.com/Gladiator07/Harvestify/master/Data-processed/crop_recommendation.csv"
    X, y, features_list, le, crops_list = download_and_parse_data(url)
    
    # 2. Check basics
    assert X.shape == (2200, 7), f"Expected X shape (2200, 7), got {X.shape}"
    assert len(y) == 2200, f"Expected 2200 labels, got {len(y)}"
    assert len(crops_list) == 22, f"Expected 22 crop classes, got {len(crops_list)}"
    logging.info(f"Data shape: {X.shape}. Found {len(crops_list)} classes.")
    
    # 3. Stratified 80/20 split
    indices = np.arange(len(y))
    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, indices, test_size=0.20, stratify=y, random_state=args.seed
    )
    
    assert len(X_train) == 1760, f"Expected 1760 train samples, got {len(X_train)}"
    assert len(X_test) == 440, f"Expected 440 test samples, got {len(X_test)}"
    
    # Check class balance in train
    unique, counts = np.unique(y_train, return_counts=True)
    assert len(set(counts)) == 1, f"Class counts in train are not balanced. Counts: {counts}"
    
    # 4. Standard Scaler on TRAIN
    ss = StandardScaler()
    X_train = ss.fit_transform(X_train)
    X_test = ss.transform(X_test)
    
    # 4. MinMax Scaler (0 to pi) on TRAIN
    mms = MinMaxScaler(feature_range=(0.0, np.pi))
    X_train = mms.fit_transform(X_train)
    X_test = mms.transform(X_test)
    
    # 5. Clip test values to [0, pi]
    X_test_clipped = np.clip(X_test, 0.0, np.pi)
    num_clipped = np.sum(X_test != X_test_clipped)
    X_test = X_test_clipped
    logging.info(f"Number of test values clipped to [0, pi]: {num_clipped}")
    
    # 6. Final assertions
    assert not np.isnan(X_train).any(), "NaN found in X_train"
    assert not np.isinf(X_train).any(), "Inf found in X_train"
    assert not np.isnan(X_test).any(), "NaN found in X_test"
    assert not np.isinf(X_test).any(), "Inf found in X_test"
    
    # 7 & 8. Save arrays and indices
    np.save(data_dir / "X_train.npy", X_train)
    np.save(data_dir / "X_test.npy", X_test)
    np.save(data_dir / "y_train.npy", y_train)
    np.save(data_dir / "y_test.npy", y_test)
    np.save(data_dir / "train_indices.npy", idx_train)
    np.save(data_dir / "test_indices.npy", idx_test)
    logging.info(f"Saved dataset numpy arrays to '{data_dir}'")
    
    # 9. Save models
    joblib.dump(le, model_dir / "label_encoder.joblib")
    joblib.dump(ss, model_dir / "standard_scaler.joblib")
    joblib.dump(mms, model_dir / "minmax_scaler.joblib")
    logging.info(f"Saved sklearn models to '{model_dir}'")
    
    # 10. Save metadata
    data_meta = {
        "features": features_list,
        "num_features": 7,
        "num_qubits": 7,
        "num_classes": 22,
        "crops": crops_list,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "seed": args.seed
    }
    with open(model_dir / "data_meta.json", "w", encoding="utf-8") as f:
        json.dump(data_meta, f, indent=4)
    logging.info(f"Saved data metadata to '{model_dir}/data_meta.json'")
    
    logging.info("Data preparation completed successfully.")

if __name__ == '__main__':
    main()
