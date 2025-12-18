import json
import re
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup


def extract_company_url(cin: str) -> Optional[str]:
    """
    Given a CIN, fetch the search page and extract the company's overview URL.
    Returns None if not found.
    """
    search_url = f"https://www.allindiaitr.com/search/{cin}"
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(search_url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    anchor = soup.find("a", onclick=re.compile(r"gotoCompanyOverviewPage\("))
    if not anchor:
        return None

    match = re.search(
        r"gotoCompanyOverviewPage\('([^']+)'\s*,\s*'([^']+)'\)", anchor["onclick"]
    )
    if not match:
        return None

    company_name, company_cin = match.group(1), match.group(2)
    slug = company_name.replace(" ", "-").lower()
    return f"https://www.allindiaitr.com/company/{slug}/{company_cin}"


def extract_company_details(company_url: str) -> Dict[str, Any]:
    """
    Given a company overview URL, fetch the page, extract ROC Code and Organization JSON-LD.
    Returns a dict with CIN, ROC code, legal name, founding date, and directors list.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(company_url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract ROC Code by finding parent text of the span label
    roc_code = "Not found"
    span = soup.find("span", string=re.compile(r"ROC Code:", re.I))
    if span and span.parent:
        text = span.parent.get_text(separator=" ", strip=True)
        roc_code = text.replace("ROC Code:", "").strip()

    # Locate the correct JSON-LD block with @type == Organization
    org_data: Optional[Dict[str, Any]] = None
    for script in soup.find_all("script", type="application/ld+json"):
        raw = script.get_text(strip=True)
        try:
            jd = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(jd, dict) and jd.get("@type") == "Organization":
            org_data = jd
            break

    if not org_data:
        raise RuntimeError("Could not find Organization JSON-LD on page")

    legal_name = org_data.get("legalName", "N/A")
    founding_date = org_data.get("foundingDate", "N/A")
    employees: List[Dict[str, Any]] = org_data.get("employee", []) or []
    directors = [e.get("name", "").strip() for e in employees if e.get("name")]

    return {
        "cin": company_url.rsplit("/", 1)[-1],
        "roc_code": roc_code,
        "legal_name": legal_name,
        "founding_date": founding_date,
        "directors": directors or ["N/A"],
    }


