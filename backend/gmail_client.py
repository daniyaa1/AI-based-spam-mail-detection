import base64
import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def get_gmail_service(token_info: dict):
    creds = Credentials(
        token=token_info["access_token"],
        refresh_token=token_info.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=token_info["client_id"],
        client_secret=token_info["client_secret"],
    )
    return build("gmail", "v1", credentials=creds)


def fetch_emails(token_info: dict, max_results: int = 30) -> list[dict]:
    service = get_gmail_service(token_info)
    result = service.users().messages().list(
        userId="me",
        maxResults=max_results,
        labelIds=["INBOX"],
    ).execute()

    messages = result.get("messages", [])
    emails = []
    for msg in messages:
        detail = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()
        parsed = _parse_message(detail)
        if parsed:
            emails.append(parsed)
    return emails


def _parse_message(msg: dict) -> dict | None:
    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
    subject = headers.get("Subject", "(no subject)")
    sender = headers.get("From", "unknown")
    date = headers.get("Date", "")
    msg_id = msg.get("id", "")

    body = _extract_body(msg.get("payload", {}))
    snippet = msg.get("snippet", "")

    return {
        "id": msg_id,
        "subject": subject,
        "sender": sender,
        "date": date,
        "body": body or snippet,
        "snippet": snippet,
    }


def _extract_body(payload: dict) -> str:
    mime = payload.get("mimeType", "")
    if mime in ("text/plain", "text/html"):
        data = payload.get("body", {}).get("data", "")
        if data:
            decoded = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="ignore")
            if mime == "text/html":
                decoded = re.sub(r"<[^>]+>", " ", decoded)
            return decoded.strip()
    # recurse into parts
    for part in payload.get("parts", []):
        text = _extract_body(part)
        if text:
            return text
    return ""
