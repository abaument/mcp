"""Gmail API client using OAuth2 refresh tokens."""

import base64
import json
import os
import urllib.parse
import urllib.request
from email.utils import parseaddr


TOKEN_URI = "https://oauth2.googleapis.com/token"
GMAIL_API = "https://gmail.googleapis.com/gmail/v1/users/me"


def _get_access_token() -> str:
    data = urllib.parse.urlencode({
        "client_id": os.environ["GMAIL_CLIENT_ID"],
        "client_secret": os.environ["GMAIL_CLIENT_SECRET"],
        "refresh_token": os.environ["GMAIL_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(TOKEN_URI, data=data)
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())["access_token"]


def _gmail_request(path: str, method: str = "GET", body: dict | None = None) -> dict:
    token = _get_access_token()
    url = f"{GMAIL_API}/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if data:
        req.add_header("Content-Type", "application/json")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


def list_messages(query: str = "is:unread", max_results: int = 10) -> list[dict]:
    q = urllib.parse.quote(query)
    result = _gmail_request(f"messages?q={q}&maxResults={max_results}")
    messages = result.get("messages", [])
    summaries = []
    for msg in messages:
        detail = _gmail_request(f"messages/{msg['id']}?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date")
        headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
        summaries.append({
            "id": msg["id"],
            "thread_id": detail.get("threadId"),
            "from": headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "snippet": detail.get("snippet", ""),
        })
    return summaries


def get_message(message_id: str) -> dict:
    detail = _gmail_request(f"messages/{message_id}?format=full")
    headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}

    body = ""
    payload = detail.get("payload", {})

    # Try to get plain text body
    if payload.get("body", {}).get("data"):
        body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
    elif payload.get("parts"):
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
                break
        # Fallback to HTML if no plain text
        if not body:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/html" and part.get("body", {}).get("data"):
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
                    break

    sender_name, sender_email = parseaddr(headers.get("From", ""))

    return {
        "id": message_id,
        "thread_id": detail.get("threadId"),
        "from_name": sender_name,
        "from_email": sender_email,
        "to": headers.get("To", ""),
        "subject": headers.get("Subject", ""),
        "date": headers.get("Date", ""),
        "body": body,
        "labels": detail.get("labelIds", []),
    }


def modify_message(message_id: str, add_labels: list[str] | None = None, remove_labels: list[str] | None = None) -> dict:
    body = {
        "addLabelIds": add_labels or [],
        "removeLabelIds": remove_labels or [],
    }
    return _gmail_request(f"messages/{message_id}/modify", method="POST", body=body)
