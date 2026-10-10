from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from predict import load_pipeline, predict_crops, FEATURE_RANGES

app = FastAPI(title="Crop Recommendation API")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = None

@app.on_event("startup")
def startup_event():
    global pipeline
    pipeline = load_pipeline(Path("models"))

class Features(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float

@app.post("/predict")
def predict(features: Features):
    if not pipeline:
        raise HTTPException(status_code=500, detail="Model pipeline not loaded.")
    
    df_input = pd.DataFrame([features.dict()])
    results = predict_crops(pipeline, df_input)
    row = results.iloc[0]
    
    return {
        "primary_recommendation": row['predicted_crop'].title(),
        "candidates": [
            {"name": row['top1'].title(), "probability": float(row['top1_prob'])},
            {"name": row['top2'].title(), "probability": float(row['top2_prob'])},
            {"name": row['top3'].title(), "probability": float(row['top3_prob'])}
        ],
        "meta": {
            "num_qubits": int(pipeline['meta']['num_qubits']),
            "reps": int(pipeline['config']['hyperparameters']['reps']),
            "C": float(pipeline['config']['hyperparameters']['C'])
        }
    }

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
