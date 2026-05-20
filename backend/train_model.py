"""
Train and compare spam-classification models on the UCI SMS Spam Collection
dataset, then save the best-performing model for the FastAPI app.

Outputs:
- spam_model.joblib
- tfidf_vectorizer.joblib
- model_metadata.json
- artifacts/accuracy_comparison.png
- artifacts/confusion_matrix.png
- artifacts/spam_vs_ham.png
- artifacts/spam_wordcloud.png
- artifacts/ham_wordcloud.png
- artifacts/classification_report.txt

Run:
    python train_model.py
"""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from urllib.request import urlopen

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from wordcloud import WordCloud

from preprocessor import clean_text

BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
DATASET_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/"
    "00228/smsspamcollection.zip"
)
MODEL_PATH = BASE_DIR / "spam_model.joblib"
VECTORIZER_PATH = BASE_DIR / "tfidf_vectorizer.joblib"
METADATA_PATH = BASE_DIR / "model_metadata.json"


def load_dataset() -> pd.DataFrame:
    print("Downloading SMS Spam Collection dataset...")
    with urlopen(DATASET_URL) as response:
        payload = response.read()

    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        with archive.open("SMSSpamCollection") as dataset_file:
            frame = pd.read_csv(
                dataset_file,
                sep="\t",
                header=None,
                names=["label", "message"],
                encoding="utf-8",
            )

    frame["label_name"] = frame["label"].str.strip().str.lower()
    frame["label"] = frame["label_name"].map({"ham": 0, "spam": 1})
    frame["clean_text"] = frame["message"].astype(str).map(clean_text)
    print(
        f"Loaded {len(frame)} rows "
        f"({int(frame['label'].sum())} spam, {int((1 - frame['label']).sum())} ham)."
    )
    return frame


def build_models() -> dict[str, object]:
    return {
        "Naive Bayes": MultinomialNB(alpha=0.1),
        "Logistic Regression": LogisticRegression(
            max_iter=2000,
            solver="liblinear",
            random_state=42,
        ),
        "Support Vector Machine (SVM)": SVC(
            kernel="linear",
            probability=True,
            random_state=42,
        ),
    }


def train() -> None:
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    sns.set_theme(style="whitegrid")

    dataset = load_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        dataset["clean_text"],
        dataset["label"],
        test_size=0.2,
        random_state=42,
        stratify=dataset["label"],
    )

    vectorizer = TfidfVectorizer(
        max_features=8000,
        ngram_range=(1, 2),
        min_df=2,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    results: list[dict] = []
    best_model_name = ""
    best_model = None
    best_accuracy = -1.0
    best_predictions = None

    for model_name, model in build_models().items():
        model.fit(X_train_vec, y_train)
        predictions = model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, predictions)
        results.append(
            {
                "model": model_name,
                "accuracy": round(float(accuracy), 4),
            }
        )
        print(f"{model_name}: {accuracy:.4f}")

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model_name = model_name
            best_model = model
            best_predictions = predictions

    assert best_model is not None and best_predictions is not None

    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    report = classification_report(
        y_test,
        best_predictions,
        target_names=["Ham", "Spam"],
    )
    (ARTIFACTS_DIR / "classification_report.txt").write_text(report)

    metadata = {
        "dataset_name": "SMS Spam Collection Dataset",
        "dataset_url": DATASET_URL,
        "row_count": int(len(dataset)),
        "spam_count": int(dataset["label"].sum()),
        "ham_count": int((1 - dataset["label"]).sum()),
        "best_model": best_model_name,
        "best_accuracy": round(float(best_accuracy), 4),
        "model_results": results,
        "vectorizer": {
            "type": "TF-IDF",
            "max_features": 8000,
            "ngram_range": [1, 2],
            "min_df": 2,
        },
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2))

    _save_class_distribution_chart(dataset)
    _save_accuracy_chart(results)
    _save_confusion_matrix(best_model_name, y_test, best_predictions)
    _save_wordclouds(dataset)

    print(f"\nBest model: {best_model_name} ({best_accuracy:.4f})")
    print(f"Saved model to {MODEL_PATH.name}")
    print(f"Saved vectorizer to {VECTORIZER_PATH.name}")
    print(f"Saved metadata to {METADATA_PATH.name}")
    print(f"Artifacts saved in {ARTIFACTS_DIR}")


def _save_class_distribution_chart(dataset: pd.DataFrame) -> None:
    counts = dataset["label_name"].value_counts().reindex(["ham", "spam"]).fillna(0)
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(
        x=counts.index.str.upper(),
        y=counts.values,
        palette=["#8fb996", "#c56e5a"],
    )
    ax.set_title("Spam vs Ham Distribution")
    ax.set_xlabel("Class")
    ax.set_ylabel("Message Count")
    for idx, value in enumerate(counts.values):
        ax.text(idx, value + 20, str(int(value)), ha="center", va="bottom", fontsize=10)
    plt.tight_layout()
    plt.savefig(ARTIFACTS_DIR / "spam_vs_ham.png", dpi=200)
    plt.close()


def _save_accuracy_chart(results: list[dict]) -> None:
    frame = pd.DataFrame(results).sort_values("accuracy", ascending=False)
    plt.figure(figsize=(9, 5))
    ax = sns.barplot(
        data=frame,
        x="model",
        y="accuracy",
        palette="crest",
    )
    ax.set_title("Model Accuracy Comparison")
    ax.set_xlabel("Model")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0.85, 1.0)
    plt.xticks(rotation=12, ha="right")
    for index, row in frame.reset_index(drop=True).iterrows():
        ax.text(index, row["accuracy"] + 0.003, f"{row['accuracy']:.2%}", ha="center")
    plt.tight_layout()
    plt.savefig(ARTIFACTS_DIR / "accuracy_comparison.png", dpi=200)
    plt.close()


def _save_confusion_matrix(
    model_name: str,
    y_true: pd.Series,
    y_pred,
) -> None:
    matrix = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    ax = sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Ham", "Spam"],
        yticklabels=["Ham", "Spam"],
    )
    ax.set_title(f"Confusion Matrix ({model_name})")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    plt.tight_layout()
    plt.savefig(ARTIFACTS_DIR / "confusion_matrix.png", dpi=200)
    plt.close()


def _save_wordclouds(dataset: pd.DataFrame) -> None:
    for label_name, file_name, color in [
        ("spam", "spam_wordcloud.png", "#8f1d1d"),
        ("ham", "ham_wordcloud.png", "#1d4f5f"),
    ]:
        text_blob = " ".join(
            dataset.loc[dataset["label_name"] == label_name, "clean_text"].tolist()
        )
        if not text_blob.strip():
            continue

        cloud = WordCloud(
            width=1200,
            height=700,
            background_color="white",
            colormap="viridis" if label_name == "ham" else "magma",
        ).generate(text_blob)

        plt.figure(figsize=(10, 6))
        plt.imshow(cloud, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"{label_name.upper()} WordCloud", color=color)
        plt.tight_layout()
        plt.savefig(ARTIFACTS_DIR / file_name, dpi=200)
        plt.close()


if __name__ == "__main__":
    train()
