import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)

_stemmer = PorterStemmer()
_stop_words = set(stopwords.words("english"))

# Spam signals used for rule-based explanations
SPAM_SIGNALS = {
    "keywords": [
        "win", "winner", "won", "prize", "cash", "free", "urgent", "congratulations",
        "claim", "offer", "limited", "deal", "discount", "credit", "loan", "click",
        "verify", "account", "suspended", "password", "bank", "paypal", "bitcoin",
        "investment", "million", "dollars", "pounds", "lottery", "selected",
        "unsubscribe", "opt-out", "buy now", "order now", "act now", "hurry",
        "guaranteed", "risk-free", "no obligation", "earn money", "make money",
        "extra income", "work from home", "be your own boss",
    ],
    "patterns": {
        "excessive_caps": r"[A-Z]{5,}",
        "multiple_exclamation": r"!{2,}",
        "money_amount": r"[\$£€₹]\s*[\d,]+",
        "suspicious_url": r"https?://(?!(?:www\.)?(?:google|gmail|microsoft|apple)\.[a-z]{2,3}/)\S+",
        "phone_number": r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "percentage_off": r"\d+\s*%\s*off",
    },
}


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"<[^>]+>", " ", text)          # strip HTML
    text = re.sub(r"https?://\S+", " url ", text)  # replace URLs with token
    text = re.sub(r"\S+@\S+", " email ", text)     # replace emails with token
    text = re.sub(r"[\$£€₹]\s*[\d,]+", " money ", text)  # replace amounts
    text = re.sub(r"\d+", " num ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = text.split()
    tokens = [_stemmer.stem(t) for t in tokens if t not in _stop_words and len(t) > 1]
    return " ".join(tokens)


def extract_signals(subject: str, body: str) -> dict:
    """Return human-readable spam signals found in the email."""
    full_text = f"{subject} {body}"
    found_keywords = [
        kw for kw in SPAM_SIGNALS["keywords"]
        if re.search(r"\b" + re.escape(kw) + r"\b", full_text, re.IGNORECASE)
    ]
    found_patterns = {}
    for name, pattern in SPAM_SIGNALS["patterns"].items():
        matches = re.findall(pattern, full_text)
        if matches:
            found_patterns[name] = matches[:3]  # cap at 3 examples

    return {
        "spam_keywords": found_keywords,
        "suspicious_patterns": found_patterns,
    }


def build_reason_list(signals: dict, top_features: list[str]) -> list[str]:
    reasons = []
    if signals["spam_keywords"]:
        kws = ", ".join(f'"{k}"' for k in signals["spam_keywords"][:5])
        reasons.append(f"Suspicious keywords detected: {kws}")
    patterns = signals["suspicious_patterns"]
    if "excessive_caps" in patterns:
        reasons.append("Excessive capitalization (shouting style)")
    if "multiple_exclamation" in patterns:
        reasons.append("Multiple exclamation marks used")
    if "money_amount" in patterns:
        reasons.append(f"Money amounts found: {', '.join(patterns['money_amount'])}")
    if "suspicious_url" in patterns:
        reasons.append("Suspicious or unknown links present")
    if "phone_number" in patterns:
        reasons.append("Phone numbers embedded in email")
    if "percentage_off" in patterns:
        reasons.append(f"Discount offers: {', '.join(patterns['percentage_off'])}")
    if top_features:
        feat_str = ", ".join(f'"{f}"' for f in top_features[:5])
        reasons.append(f"ML model flagged these terms as spammy: {feat_str}")
    if not reasons:
        reasons.append("Pattern matches typical spam email structure")
    return reasons
