from pydantic import BaseModel, Field

from ai_intelligence.domain.models import (
    BudgetLevel,
    DiningMode,
    HealthGoal,
    MealRecommendation,
    MealSlot,
)


class QueryRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=32000)
    session_id: str | None = None


class QueryResponse(BaseModel):
    session_id: str
    reply: str
    used_tools: list[str] = Field(default_factory=list)
    mode: str  # "llm" | "echo"


class MealPreferences(BaseModel):
    preferred_cuisines: list[str] = Field(default_factory=list)
    flavor_preferences: list[str] = Field(default_factory=list)
    avoid_ingredients: list[str] = Field(default_factory=list)
    health_goal: HealthGoal = HealthGoal.BALANCED
    budget: BudgetLevel = BudgetLevel.MEDIUM
    dining_mode: DiningMode = DiningMode.ANY
    prefer_quick: bool = True


class DayMealRecommendationRequest(MealPreferences):
    seed: int | None = None


class DayMealRecommendationResponse(BaseModel):
    recommendations: dict[MealSlot, MealRecommendation]


class SwapMealRequest(MealPreferences):
    slot: MealSlot
    current_meal_id: str
    seed: int | None = None


class SwapMealResponse(BaseModel):
    recommendation: MealRecommendation
