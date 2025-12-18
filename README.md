# CIN Scout 🔍

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-%3E%3D3.11-brightgreen.svg?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-009688?logo=fastapi&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI%20Server-4B8BBE?logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/HTTP-requests-FF6B6B?logo=python&logoColor=white)
![BeautifulSoup4](https://img.shields.io/badge/HTML-BeautifulSoup4-3E63DD)

FastAPI-based tool for searching Indian companies by name and fetching CIN-based details from public registries.  
Search companies via a clean web UI or REST API, and extract ROC code, founding date, and directors using HTML scraping utilities.

## Features

- **Company search by name** – Enter a query and trigger search on demand with a button (or Enter key).
- **CIN-based detail lookup** – Fetch ROC code, legal name, founding date, and directors for a given CIN.
- **Modern themed UI** – Clean light/dark themed interface with a theme toggle and card-style results.
- **Modular utilities** – All scraping and external HTTP logic lives under `utils/` for easy reuse.
- **FastAPI backend** – Simple, well-structured API layer.
- **Static frontend** – Single-page HTML UI served directly by FastAPI from `public/index.html`.

## Installation

### Prerequisites

- **Python**: 3.11 or higher  
- **Package manager**: [`uv`](https://github.com/astral-sh/uv)

### Setup

1. **Clone and install**

   ```bash
   git clone https://github.com/0xaadesh/cin-scout
   cd cin-scout
   uv sync
   ```

2. **Run the application**

   ```bash
   uv run server.py
   # or
   uvicorn server:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Open the web interface**

   - Go to `http://localhost:8000` in your browser.

## Usage

### Web Interface

1. Open `http://localhost:8000`.
2. Type a company name (minimum 3 characters) in the search box.
3. Click **Search Companies** (or press Enter) to fetch results.
4. Click any company card to fetch and expand CIN details inline.
5. View:
   - Legal name  
   - ROC code  
   - Founding date  
   - Directors list  

### API Endpoints

- **Search Companies**

  ```bash
  GET /search?q={company_name}

  curl "http://localhost:8000/search?q=tata"
  ```

  Example JSON response:

  ```json
  [
    {
      "name": "TATA CONSULTANCY SERVICES LIMITED",
      "cin": "L22222MH1995PLC123456",
      "listed": "Y",
      "state": "MAHARASHTRA"
    },
    {
      "name": "TATA STEEL LIMITED",
      "cin": "L28920MH1868PLC000014",
      "listed": "Y",
      "state": "MAHARASHTRA"
    }
  ]
  ```

- **Get Company Details**

  ```bash
  GET /details?cin={CIN}

  curl "http://localhost:8000/details?cin=L28920MH1868PLC000014"
  ```

  Example JSON response:

  ```json
  {
    "cin": "L28920MH1868PLC000014",
    "roc_code": "ROC-Mumbai",
    "legal_name": "TATA STEEL LIMITED",
    "founding_date": "1907-08-26",
    "directors": [
      "Director Name 1",
      "Director Name 2"
    ]
  }
  ```

### Command Line (Optional)

You can also call the detail utilities directly from Python:

```bash
python -m utils.details
```

or import them in your own script:

```python
from utils.details import extract_company_url, extract_company_details
```

## How It Works

1. **Search** – `/search` proxies a query string to the Instafinancials CIN finder endpoint via `utils.search.search_companies_by_name`.
2. **Resolve CIN** – For a given CIN, `utils.details.extract_company_url` locates the corresponding company overview page on AllIndiaITR.
3. **Scrape Details** – `utils.details.extract_company_details` parses the HTML and JSON‑LD to extract:
   - CIN
   - ROC code
   - Legal name
   - Founding date
   - Directors list
4. **Serve to client** – FastAPI returns the structured data to the frontend or any API client.

## Project Structure

```text
cin-scout/
├── server.py          # FastAPI app, routes, static file mounting
├── public/
│   └── index.html     # Frontend (single-page UI)
├── utils/
│   ├── __init__.py
│   ├── details.py     # CIN resolution + company detail scraping
│   └── search.py      # Instafinancials search client
├── pyproject.toml     # Project metadata & dependencies
└── uv.lock            # Locked dependency versions (uv)
```

## Dependencies

- **FastAPI** – Web framework for building REST APIs.
- **Uvicorn** – ASGI server for running the FastAPI app.
- **Requests** – HTTP client for calling third‑party endpoints.
- **BeautifulSoup4** – HTML parsing and scraping.

All dependencies are managed via `pyproject.toml` and `uv.lock`.

## Data Sources

- **Company Search**: `InstaFinancials CIN Finder`  
- **Company Details**: `AllIndiaITR.com`

These are public websites; the project only reads publicly available pages.

## Disclaimer

This tool is for **informational and educational purposes only**:

- Data is sourced from publicly available websites and may be **incomplete or outdated**.
- CIN Scout uses internal/undocumented endpoints and mimics browser requests to Instafinancials and AllIndiaITR solely to make developer access and programmatic experimentation easier.
- You must ensure that any use of this tool complies with the target websites' terms of service and robots/security policies.
- Always verify company details through official government or regulatory channels before making decisions.
- You are solely responsible for any legal, contractual, or regulatory consequences arising from your use of this tool; the authors take no legal responsibility or liability for how it is used.