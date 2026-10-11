from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import os
import asyncio
import urllib.request
import logging

from predict import load_pipeline, predict_crops, FEATURE_RANGES

logger = logging.getLogger("uvicorn")

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

async def keep_alive_task():
    """Pings the public Render URL every 10 minutes to prevent the container from sleeping."""
    # Render automatically sets RENDER_EXTERNAL_URL to your service's public HTTPS URL
    target_url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("BACKEND_URL")
    if not target_url:
        logger.info("Keep-alive task disabled (RENDER_EXTERNAL_URL not set).")
        return
    
    ping_url = f"{target_url.rstrip('/')}/health"
    logger.info(f"Keep-alive self-pinger started for: {ping_url}")
    
    # Wait 2 minutes after boot before starting the cycle
    await asyncio.sleep(120)
    
    while True:
        try:
            req = urllib.request.Request(ping_url, headers={"User-Agent": "Render-SelfPinger/1.0"})
            with urllib.request.urlopen(req, timeout=15) as res:
                logger.info(f"[Keep-Alive] Self-ping status: {res.status}")
        except Exception as e:
            logger.warning(f"[Keep-Alive] Self-ping notice: {e}")
        # Ping every 10 minutes (Render sleeps at 15 minutes)
        await asyncio.sleep(600)

@app.on_event("startup")
async def startup_event():
    global pipeline
    pipeline = load_pipeline(Path("models"))
    # Launch background self-pinger on Render
    asyncio.create_task(keep_alive_task())

@app.get("/")
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Quantum Crop Intelligence API",
        "pipeline_loaded": pipeline is not None
    }

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
