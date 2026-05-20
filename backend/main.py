import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from model import predict, get_model_metadata
from preprocessor import extract_signals, build_reason_list

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        ",".join(dict.fromkeys([FRONTEND_URL, *DEFAULT_ALLOWED_ORIGINS])),
    ).split(",")
    if origin.strip()
]

app = FastAPI(title="Gmail Spam Detector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Backend is running. Open the frontend app in your browser, not this API root.",
        "frontend_hint": "Use the Vite URL shown in the frontend terminal, such as http://127.0.0.1:5173 or http://127.0.0.1:5174",
        "api_test": {
            "method": "POST",
            "path": "/analyze",
        },
    }

class AnalyzeRequest(BaseModel):
    subject: str
    body: str


@app.post("/analyze")
def analyze_text(req: AnalyzeRequest):
    """Analyze arbitrary email text (useful for testing without Gmail)."""
    prediction = predict(req.subject, req.body)
    signals = extract_signals(req.subject, req.body)
    reasons = build_reason_list(signals, prediction["top_features"])
    return {
        **prediction,
        "reasons": reasons if prediction["is_spam"] else [],
        "signals": signals,
    }


@app.get("/model-info")
def model_info():
    return get_model_metadata()
