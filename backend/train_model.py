"""
Train a Naive Bayes spam classifier on the SMS Spam Collection dataset.
Downloads the dataset automatically, trains, and saves the model + vectorizer.

Run once before starting the server:
    python train_model.py
"""

import os
import io
import zipfile
import urllib.request
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from preprocessor import clean_text

DATASET_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip"
MODEL_PATH = "spam_model.joblib"
VECTORIZER_PATH = "tfidf_vectorizer.joblib"


def load_dataset() -> tuple[list[str], list[int]]:
    print("Downloading SMS Spam Collection dataset...")
    with urllib.request.urlopen(DATASET_URL) as resp:
        data = resp.read()
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        with zf.open("SMSSpamCollection") as f:
            lines = f.read().decode("utf-8").strip().split("\n")

    texts, labels = [], []
    for line in lines:
        parts = line.split("\t", 1)
        if len(parts) == 2:
            label_str, text = parts
            labels.append(1 if label_str.strip() == "spam" else 0)
            texts.append(text.strip())
    print(f"Loaded {len(texts)} examples ({sum(labels)} spam, {len(labels)-sum(labels)} ham)")
    return texts, labels


def train():
    texts, labels = load_dataset()
    cleaned = [clean_text(t) for t in texts]

    X_train, X_test, y_train, y_test = train_test_split(
        cleaned, labels, test_size=0.2, random_state=42, stratify=labels
    )

    vectorizer = TfidfVectorizer(max_features=8000, ngram_range=(1, 2), min_df=2)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = MultinomialNB(alpha=0.1)
    model.fit(X_train_vec, y_train)

    y_pred = model.predict(X_test_vec)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Ham", "Spam"]))

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"\nModel saved to {MODEL_PATH}")
    print(f"Vectorizer saved to {VECTORIZER_PATH}")


if __name__ == "__main__":
    train()
