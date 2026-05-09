from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from ai_intelligence.kernel import IntelligenceKernel
from ai_intelligence.schemas import QueryRequest, QueryResponse

_kernel: IntelligenceKernel | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global _kernel
    _kernel = IntelligenceKernel()
    yield
    _kernel = None


app = FastAPI(title="AI Intelligence System", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/intelligence/query", response_model=QueryResponse)
async def intelligence_query(body: QueryRequest) -> QueryResponse:
    if _kernel is None:
        raise HTTPException(status_code=503, detail="kernel not ready")
    sid, reply, used, mode = await _kernel.query(body.message, body.session_id)
    return QueryResponse(session_id=sid, reply=reply, used_tools=used, mode=mode)


@app.get("/v1/intelligence/sessions/{session_id}")
async def session_transcript(session_id: str) -> dict[str, object]:
    if _kernel is None:
        raise HTTPException(status_code=503, detail="kernel not ready")
    return {"session_id": session_id, "messages": _kernel.memory.transcript(session_id)}
