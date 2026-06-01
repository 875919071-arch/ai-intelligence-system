from fastapi.testclient import TestClient

from ai_intelligence.app import app
from ai_intelligence.domain.meals import MEAL_CATALOG, recommend_day, swap_meal
from ai_intelligence.domain.models import BudgetLevel, HealthGoal, MealSlot
from ai_intelligence.schemas import DayMealRecommendationRequest, SwapMealRequest


def test_recommend_day_returns_three_meals() -> None:
    request = DayMealRecommendationRequest(
        preferred_cuisines=["中式", "轻食"],
        flavor_preferences=["清爽"],
        health_goal=HealthGoal.BALANCED,
        budget=BudgetLevel.MEDIUM,
        seed=7,
    )

    recommendations = recommend_day(request, seed=request.seed)

    assert set(recommendations) == {MealSlot.BREAKFAST, MealSlot.LUNCH, MealSlot.DINNER}
    assert all(item.reason for item in recommendations.values())


def test_recommend_day_filters_avoided_ingredients() -> None:
    request = DayMealRecommendationRequest(
        avoid_ingredients=["海鲜", "虾", "鱼类"],
        budget=BudgetLevel.HIGH,
        seed=11,
    )

    recommendations = recommend_day(request, seed=request.seed)

    for recommendation in recommendations.values():
        searchable = " ".join(recommendation.meal.avoid_tags)
        assert "海鲜" not in searchable
        assert "虾" not in searchable
        assert "鱼类" not in searchable


def test_recommend_day_respects_low_budget() -> None:
    request = DayMealRecommendationRequest(budget=BudgetLevel.LOW, seed=5)

    recommendations = recommend_day(request, seed=request.seed)

    assert all(item.meal.budget == BudgetLevel.LOW for item in recommendations.values())


def test_swap_meal_excludes_current_meal() -> None:
    request = SwapMealRequest(
        slot=MealSlot.LUNCH,
        current_meal_id="lunch-green-pepper-pork-rice",
        budget=BudgetLevel.HIGH,
        seed=3,
    )

    recommendation = swap_meal(
        request,
        slot=request.slot,
        current_meal_id=request.current_meal_id,
        seed=request.seed,
    )

    assert recommendation.meal.id != request.current_meal_id
    assert recommendation.meal.slot == MealSlot.LUNCH


def test_meal_api_recommend_day() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/meals/recommend-day",
            json={
                "preferred_cuisines": ["中式"],
                "flavor_preferences": ["省事"],
                "health_goal": "balanced",
                "budget": "medium",
                "seed": 13,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert set(body["recommendations"]) == {"breakfast", "lunch", "dinner"}


def test_catalog_has_more_than_one_option_for_swap_slots() -> None:
    for slot in MealSlot:
        assert sum(1 for meal in MEAL_CATALOG if meal.slot == slot) > 1


def test_catalog_uses_chinese_daily_meal_names() -> None:
    western_demo_words = ["牛油果", "藜麦", "火鸡", "三文鱼"]
    names = " ".join(meal.name for meal in MEAL_CATALOG)

    for word in western_demo_words:
        assert word not in names

    assert "黄焖鸡米饭" in names
    assert "番茄炒蛋饭" in names
    assert "皮蛋瘦肉粥" in names
