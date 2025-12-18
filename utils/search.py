import json
from typing import Any, Dict, List

import requests


def search_companies_by_name(query: str) -> List[Dict[str, Any]]:
    """
    Call Instafinancials search endpoint and return the raw JSON payload.

    This is kept in a separate utility so the FastAPI layer in `server.py`
    only deals with HTTP concerns and delegates external I/O here.
    """
    session = requests.Session()

    # Step 1: Visit the finder page to receive a fresh session cookie
    session.get(
        "https://projects.instafinancials.com/cin-finder/cin-finder-by-name.aspx",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )

    # Step 2: Prepare headers and payload for POST
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-US,en;q=0.8",
        "content-type": "application/json; charset=UTF-8",
        "origin": "https://projects.instafinancials.com",
        "referer": "https://projects.instafinancials.com/cin-finder/cin-finder-by-name.aspx",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    body = json.dumps({"strSearch": query, "mode": "SCBN"})

    response = session.post(
        "https://projects.instafinancials.com/ajax-caller.aspx/GetCompanyNames",
        headers=headers,
        data=body,
    )
    response.raise_for_status()
    raw: Dict[str, Any] = response.json()

    entries: List[str] = raw.get("d") or []
    normalized: List[Dict[str, Any]] = []

    for entry in entries:
        # Each entry is "NAME;CIN;LISTED;STATE"
        parts = entry.split(";")
        if len(parts) < 4:
            # Skip malformed entries defensively
            continue
        name, cin, listed, state = [p.strip() for p in parts[:4]]
        normalized.append(
            {
                "name": name,
                "cin": cin,
                "listed": listed,
                "state": state,
            }
        )

    return normalized


