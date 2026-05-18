import os
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from preprocessor import clean_text

MODEL_PATH = os.path.join(os.path.dirname(__file__), "spam_model.joblib")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "tfidf_vectorizer.joblib")

_model: MultinomialNB | None = None
_vectorizer: TfidfVectorizer | None = None


def _load():
    global _model, _vectorizer
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "Model not found. Run `python train_model.py` first."
            )
        _model = joblib.load(MODEL_PATH)
        _vectorizer = joblib.load(VECTORIZER_PATH)


def predict(subject: str, body: str) -> dict:
    _load()
    text = f"{subject} {body}"
    cleaned = clean_text(text)
    vec = _vectorizer.transform([cleaned])

    proba = _model.predict_proba(vec)[0]
    spam_prob = float(proba[1])
    is_spam = spam_prob >= 0.5

    top_features = _get_top_spam_features(vec)
    return {
        "is_spam": is_spam,
        "confidence": round(spam_prob if is_spam else 1 - spam_prob, 4),
        "spam_probability": round(spam_prob, 4),
        "top_features": top_features,
    }


def _get_top_spam_features(vec) -> list[str]:
    """Return the top TF-IDF features that pushed the prediction toward spam."""
    feature_names = np.array(_vectorizer.get_feature_names_out())
    # log probability difference: spam class vs ham class
    log_prob_diff = _model.feature_log_prob_[1] - _model.feature_log_prob_[0]
    # weight by TF-IDF value in this document
    tfidf_scores = vec.toarray()[0]
    weighted = tfidf_scores * log_prob_diff
    top_indices = np.argsort(weighted)[::-1][:10]
    return [
        feature_names[i]
        for i in top_indices
        if weighted[i] > 0 and tfidf_scores[i] > 0
    ]
