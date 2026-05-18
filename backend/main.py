import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from auth import get_authorization_url, exchange_code_for_token, get_user_info
from gmail_client import fetch_emails
from model import predict
from preprocessor import extract_signals, build_reason_list

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app = FastAPI(title="Gmail Spam Detector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory token store keyed by a simple session token.
# For production, use Redis or a database with proper session management.
_sessions: dict[str, dict] = {}


# ── Auth routes ──────────────────────────────────────────────────────────────

@app.get("/auth/login")
def login():
    url = get_authorization_url()
    return {"url": url}


@app.get("/auth/callback")
async def callback(code: str = Query(...)):
    token_info = await exchange_code_for_token(code)
    user = await get_user_info(token_info["access_token"])

    session_token = user["sub"]  # Google user ID as session key
    _sessions[session_token] = {**token_info, "user": user}

    return RedirectResponse(
        url=f"{FRONTEND_URL}/dashboard?session={session_token}"
    )


@app.get("/auth/me")
async def me(session: str = Query(...)):
    sess = _get_session(session)
    return {"user": sess["user"]}


@app.post("/auth/logout")
def logout(session: str = Query(...)):
    _sessions.pop(session, None)
    return {"ok": True}


# ── Email analysis routes ─────────────────────────────────────────────────────

@app.get("/emails")
def get_emails(session: str = Query(...), max_results: int = 30):
    sess = _get_session(session)
    raw_emails = fetch_emails(sess, max_results=max_results)
    results = []
    for email in raw_emails:
        prediction = predict(email["subject"], email["body"])
        signals = extract_signals(email["subject"], email["body"])
        reasons = build_reason_list(signals, prediction["top_features"])
        results.append({
            **email,
            "is_spam": prediction["is_spam"],
            "confidence": prediction["confidence"],
            "spam_probability": prediction["spam_probability"],
            "reasons": reasons if prediction["is_spam"] else [],
            "top_features": prediction["top_features"],
        })
    # sort: spam first
    results.sort(key=lambda e: e["spam_probability"], reverse=True)
    return {"emails": results, "total": len(results)}


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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_session(session_token: str) -> dict:
    sess = _sessions.get(session_token)
    if not sess:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return sess
