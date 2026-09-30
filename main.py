@'
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(
    title="FitBuddy AI",
    description="AI Fitness Assistant",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

STATIC_DIR.mkdir(exist_ok=True)

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)


@app.get("/", response_class=HTMLResponse)
async def home():
    html_file = TEMPLATES_DIR / "index.html"

    if not html_file.exists():
        return HTMLResponse(
            "<h1>FitBuddy AI</h1><p>index.html not found</p>",
            status_code=500
        )

    return HTMLResponse(html_file.read_text(encoding="utf-8"))


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "message": "FitBuddy AI is running"
    }
'@ | Set-Content ".\app\main.py" -Encoding UTF8