
# Gmail Spam Detection System Using Machine Learning

> A full-stack web application that applies Natural Language Processing and probabilistic classification to detect spam emails in real time via Gmail API integration.

## Abstract

Email spam remains a persistent challenge in digital communication, with billions of unsolicited messages transmitted daily. This project presents a Gmail Spam Detection System that combines a trained Multinomial Naive Bayes classifier with TF-IDF vectorization to classify incoming emails as spam or legitimate (ham). The system integrates with the Gmail API via Google OAuth 2.0, enabling real-time analysis of a user's inbox directly from a React-based frontend. Beyond binary classification, the system provides confidence scores, suspicious keyword annotations, and an NLP preprocessing pipeline — offering interpretability alongside predictive performance.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Features](#features)
4. [Technology Stack](#technology-stack)
5. [Machine Learning Methodology](#machine-learning-methodology)
6. [Installation & Setup](#installation--setup)
7. [Usage](#usage)
8. [API Reference](#api-reference)
9. [Results & Discussion](#results--discussion)
10. [Future Work](#future-work)
11. [References](#references)

---

## Project Overview

The Gmail Spam Detection System is a research-oriented, full-stack application designed to explore the practical application of supervised machine learning in email security. The project addresses the following research objectives:

- **RO1:** Apply TF-IDF vectorization and Naive Bayes classification to email content for spam detection.
- **RO2:** Integrate real-world email data via the Gmail API to test model performance on live inbox data.
- **RO3:** Surface model interpretability through confidence scoring and suspicious keyword extraction.

The system is composed of three primary components: a **React.js frontend**, a **FastAPI backend**, and a **trained scikit-learn classification pipeline**.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User (Browser)                        │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  React.js Frontend (Vite)                    │
│   - Google OAuth 2.0 Login                                   │
│   - Email list view with spam labels                         │
│   - Confidence score display                                 │
└───────────┬─────────────────────────────┬───────────────────┘
            │ REST (Axios)                │ OAuth Token
            ▼                            ▼
┌───────────────────────┐   ┌────────────────────────────────┐
│   FastAPI Backend     │   │       Google Gmail API          │
│   (Uvicorn server)    │◄──│   - Fetch inbox messages        │
│                       │   │   - OAuth 2.0 authentication    │
│   /classify endpoint  │   └────────────────────────────────┘
│   /emails endpoint    │
└───────────┬───────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│              ML Classification Pipeline                      │
│                                                              │
│   Raw Email Text                                             │
│       │                                                      │
│       ▼                                                      │
│   NLP Preprocessing (NLTK)                                   │
│   - Tokenization                                             │
│   - Stopword removal                                         │
│   - Stemming / Lemmatization                                 │
│       │                                                      │
│       ▼                                                      │
│   TF-IDF Vectorization (scikit-learn)                        │
│       │                                                      │
│       ▼                                                      │
│   Multinomial Naive Bayes Classifier                         │
│       │                                                      │
│       ▼                                                      │
│   Output: { label, confidence, suspicious_keywords }         │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

| Feature | Description |
|---|---|
| **Google OAuth 2.0 Login** | Secure authentication using Google's identity platform |
| **Gmail Inbox Integration** | Fetches real emails directly from the authenticated user's inbox |
| **ML-Based Spam Classification** | Binary classification (spam / ham) using a trained probabilistic model |
| **Confidence Scoring** | Posterior probability output from the Naive Bayes classifier |
| **Suspicious Keyword Detection** | Highlights high-weight spam tokens identified by the TF-IDF model |
| **NLP Preprocessing Pipeline** | Tokenization, stopword removal, and stemming via NLTK |
| **Real-Time Analysis** | Email content is classified on demand via REST API calls |
| **React Frontend** | Responsive UI for login, inbox browsing, and classification results |

---

## Technology Stack

### Frontend

| Technology | Purpose |
|---|---|
| React.js | Component-based UI framework |
| Vite | Development build tool and bundler |
| Axios | HTTP client for REST API requests |
| CSS | Styling and layout |

### Backend

| Technology | Purpose |
|---|---|
| Python 3.x | Primary backend language |
| FastAPI | High-performance REST API framework |
| Uvicorn | ASGI server for FastAPI |
| Google Gmail API | Email data retrieval |
| OAuth 2.0 | Authentication and authorization |

### Machine Learning & NLP

| Technology | Purpose |
|---|---|
| scikit-learn | ML model training and pipeline |
| TF-IDF Vectorizer | Text feature extraction |
| Multinomial Naive Bayes | Probabilistic spam classifier |
| NLTK | Natural language preprocessing |

---

## Machine Learning Methodology

### 1. Dataset

The classifier is trained on a labeled email dataset (e.g., the [UCI SMS Spam Collection](https://archive.ics.uci.edu/ml/datasets/sms+spam+collection) or equivalent) containing annotated spam and ham samples.

### 2. Preprocessing Pipeline

Raw email text is passed through the following NLP preprocessing steps before vectorization:

1. **Lowercasing** — Normalize case variation.
2. **Tokenization** — Split text into individual tokens.
3. **Stopword Removal** — Remove common words with low discriminative value (using NLTK's English stopword corpus).
4. **Stemming / Lemmatization** — Reduce words to their root form to handle morphological variation.
5. **Special Character Removal** — Strip URLs, HTML tags, punctuation, and numeric tokens.

### 3. Feature Extraction — TF-IDF

Term Frequency–Inverse Document Frequency (TF-IDF) is used to represent each email as a high-dimensional numerical vector. This method weights terms that are frequent within a given document but rare across the corpus, making it effective for identifying spam-characteristic vocabulary.

### 4. Classification — Multinomial Naive Bayes

The Multinomial Naive Bayes algorithm is well-suited to text classification tasks due to its computational efficiency and strong performance on discrete feature distributions (i.e., word count or TF-IDF features). The classifier outputs:

- **Predicted label:** `spam` or `ham`
- **Confidence score:** The posterior probability `P(spam | email features)`

### 5. Explainability

Top TF-IDF features with the highest learned weights for the spam class are extracted and surfaced as **suspicious keywords**, providing a lightweight interpretability layer.

---

## Installation & Setup

### Prerequisites

- Node.js (v18+)
- Python 3.9+
- A Google Cloud project with the Gmail API enabled and OAuth 2.0 credentials configured

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/gmail-spam-detection.git
cd gmail-spam-detection
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Place your `credentials.json` (from Google Cloud Console) in the `backend/` directory.

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## Usage

1. Navigate to `http://localhost:5173` in your browser.
2. Click **Sign in with Google** to authenticate via OAuth 2.0.
3. Your Gmail inbox will be fetched and displayed.
4. Each email is automatically classified as **Spam** or **Ham**, with a confidence percentage and any flagged suspicious keywords shown inline.

---

## API Reference

### `GET /emails`

Fetches a list of emails from the authenticated user's Gmail inbox.

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
[
  {
    "id": "18e9f...",
    "subject": "Congratulations! You've won a prize",
    "snippet": "Click here to claim your reward..."
  }
]
```

---

### `POST /classify`

Classifies the provided email text using the trained ML model.

**Request Body:**
```json
{
  "text": "Click here to claim your free iPhone now!"
}
```

**Response:**
```json
{
  "label": "spam",
  "confidence": 0.97,
  "suspicious_keywords": ["free", "click", "claim", "prize"]
}
```

---

## Results & Discussion

The Multinomial Naive Bayes classifier with TF-IDF features demonstrates strong baseline performance on email spam detection tasks, consistent with findings in the literature. Key observations include:

- High precision on spam detection, reducing false positives that might cause legitimate emails to be misclassified.
- Confidence scores provide useful signal for borderline cases and enable downstream thresholding.
- Suspicious keyword extraction surfaces the model's reasoning, supporting user trust and interpretability.

Quantitative evaluation metrics (accuracy, precision, recall, F1-score) should be reported from your held-out test set results here.

---

## Future Work

- **Deep Learning Models:** Explore LSTM or transformer-based classifiers (e.g., BERT fine-tuned for spam detection) for improved contextual understanding.
- **Active Learning:** Allow users to flag misclassifications and retrain the model incrementally.
- **Multimodal Analysis:** Extend the pipeline to analyze email attachments and embedded images.
- **Multi-label Classification:** Distinguish between categories of spam (phishing, promotional, malware, etc.) rather than a binary output.
- **Evaluation on Live Data:** Conduct a longitudinal study using real Gmail inbox data with user consent.

---

## References

- McCallum, A., & Nigam, K. (1998). A comparison of event models for Naive Bayes text classification. *AAAI Workshop on Learning for Text Categorization.*
- Sebastiani, F. (2002). Machine learning in automated text categorization. *ACM Computing Surveys, 34*(1), 1–47.
- Almeida, T. A., Hidalgo, J. M. G., & Yamakami, A. (2011). Contributions to the study of SMS spam filtering. *ACM Symposium on Document Engineering.*
- [Google Gmail API Documentation](https://developers.google.com/gmail/api)
- [scikit-learn: Naive Bayes](https://scikit-learn.org/stable/modules/naive_bayes.html)
- [NLTK Documentation](https://www.nltk.org/)

---

## Developed By: 
