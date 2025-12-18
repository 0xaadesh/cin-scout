from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from utils.details import extract_company_details, extract_company_url
from utils.search import search_companies_by_name

app = FastAPI()


# Allow frontend to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Serve static files (frontend) from ./public
public_dir = Path(__file__).parent / "public"
if public_dir.exists():
    app.mount("/public", StaticFiles(directory=str(public_dir)), name="public")


@app.get("/", response_class=HTMLResponse)
def read_root() -> HTMLResponse:
    """
    Serve the main HTML page from the public folder.
    """
    index_path = public_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return HTMLResponse(index_path.read_text(encoding="utf-8"))


@app.get("/search")
def search_company(q: str = Query(..., min_length=2)):
    """
    Proxy search against Instafinancials endpoint.
    """
    try:
        return search_companies_by_name(q)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch search results: {e}"
        ) from e


@app.get("/details")
def get_company_details(cin: str = Query(..., min_length=1)):
    """
    Resolve a CIN to a company page and return structured company details.
    """
    url = extract_company_url(cin)
    if not url:
        raise HTTPException(
            status_code=404, detail=f"Company with CIN {cin} not found"
        )

    try:
        details = extract_company_details(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return details


# Note: uvicorn entrypoint is expected to be provided externally, for example:
#   uvicorn server:app --reload


if __name__ == "__main__":
    """
    Allow running the API with:

        uv run server.py

    This will spin up a uvicorn development server.
    """
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)