# app/api.py
from __future__ import annotations
import asyncio, os, time
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .rag import answer_with_docs_async
from .ingest import run_ingest_async, DATA_DIR

app = FastAPI(title="Company Knowledge Assistant")

# Static frontend
static_dir = Path(__file__).with_name("static")
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Ingestion status
_ingest_lock = asyncio.Lock()
_ingest_task: asyncio.Task | None = None
_ingest_last = {
    "status": "idle",      # idle | running | succeeded | failed
    "started_at": None,
    "finished_at": None,
    "stats": None,         # {"documents":..., "chunks":..., "collection":...}
    "error": None,
}

class Ask(BaseModel):
    question: str
    category: str | None = None

@app.get("/")
async def root_page():
    # prevent browsers from serving a stale cached copy of the SPA shell
    return FileResponse(static_dir / "index.html", headers={"Cache-Control": "no-store"})

@app.get("/categories")
async def list_categories():
    if not os.path.isdir(DATA_DIR):
        return {"ok": True, "categories": []}
    categories = sorted(
        name for name in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, name)) and not name.startswith(".")
    )
    return {"ok": True, "categories": categories}

async def _ingest_job():
    _ingest_last.update({"status": "running", "started_at": time.time(), "finished_at": None, "stats": None, "error": None})
    try:
        #TODO: RUN INGESTION
        stats = await run_ingest_async()
        _ingest_last.update({"status": "succeeded", "finished_at": time.time(), "stats": stats})
    except Exception as e:
        _ingest_last.update({"status": "failed", "finished_at": time.time(), "error": str(e)})

@app.post("/ingest")
async def kick_off_ingest():
    global _ingest_task
    async with _ingest_lock:
        if _ingest_task and not _ingest_task.done():
            return JSONResponse({"ok": False, "message": "Ingestion already running"}, status_code=409)
        #TODO: Create Ingestion Task
        _ingest_task = asyncio.create_task(_ingest_job())
    return {"ok": True, "message": "Ingestion started"}

@app.get("/ingest/status")
async def ingest_status():
    return {"ok": True, **_ingest_last}

@app.post("/ask")
async def ask(q: Ask):
    try:
        start = time.perf_counter()

        answer, sources, contexts = await answer_with_docs_async(q.question, q.category)

        elapsed = time.perf_counter() - start
        print(f"⏱️ /ask execution took {elapsed:.2f} seconds")
        return {
            "answer": answer,
            "sources": sources,
            "contexts": contexts
        }
    except Exception as e:
        print(f"❌ Error in /ask: {str(e)}")
        return JSONResponse(
            {"error": str(e), "answer": "An error occurred while processing your question.", "sources": []},
            status_code=500
        )
    