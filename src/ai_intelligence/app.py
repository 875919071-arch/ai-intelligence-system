from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from ai_intelligence.domain.meals import recommend_day, swap_meal
from ai_intelligence.kernel import IntelligenceKernel
from ai_intelligence.schemas import (
    DayMealRecommendationRequest,
    DayMealRecommendationResponse,
    QueryRequest,
    QueryResponse,
    SwapMealRequest,
    SwapMealResponse,
)

_kernel: IntelligenceKernel | None = None
_ROOT_DIR = Path(__file__).resolve().parents[2]
_MEAL_PICKER_DIR = _ROOT_DIR / "apps" / "meal-picker"


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


@app.post("/v1/meals/recommend-day", response_model=DayMealRecommendationResponse)
async def meal_recommend_day(body: DayMealRecommendationRequest) -> DayMealRecommendationResponse:
    try:
        recommendations = recommend_day(body, seed=body.seed)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return DayMealRecommendationResponse(recommendations=recommendations)


@app.post("/v1/meals/swap", response_model=SwapMealResponse)
async def meal_swap(body: SwapMealRequest) -> SwapMealResponse:
    try:
        recommendation = swap_meal(
            body,
            slot=body.slot,
            current_meal_id=body.current_meal_id,
            seed=body.seed,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return SwapMealResponse(recommendation=recommendation)


app.mount(
    "/meal-picker",
    StaticFiles(directory=_MEAL_PICKER_DIR, html=True),
    name="meal-picker",
)
