from __future__ import annotations

import random
from collections.abc import Sequence
from typing import Protocol

from ai_intelligence.domain.models import (
    BudgetLevel,
    DiningMode,
    HealthGoal,
    MealOption,
    MealRecommendation,
    MealSlot,
)


class MealPreferenceInput(Protocol):
    preferred_cuisines: list[str]
    flavor_preferences: list[str]
    avoid_ingredients: list[str]
    health_goal: HealthGoal
    budget: BudgetLevel
    dining_mode: DiningMode
    prefer_quick: bool


_BUDGET_RANK = {
    BudgetLevel.LOW: 1,
    BudgetLevel.MEDIUM: 2,
    BudgetLevel.HIGH: 3,
}

_BUDGET_LABELS = {
    BudgetLevel.LOW: "省钱小碗",
    BudgetLevel.MEDIUM: "日常预算",
    BudgetLevel.HIGH: "今天加餐",
}

_HEALTH_GOAL_LABELS = {
    HealthGoal.BALANCED: "吃得均衡",
    HealthGoal.LIGHT: "轻一点",
    HealthGoal.HIGH_PROTEIN: "多补蛋白",
    HealthGoal.COMFORT: "吃得舒服",
}


MEAL_CATALOG: list[MealOption] = [
    MealOption(
        id="breakfast-century-egg-pork-congee",
        name="皮蛋瘦肉粥",
        slot=MealSlot.BREAKFAST,
        cuisine="粤式",
        budget=BudgetLevel.LOW,
        dining_modes=[DiningMode.COOK, DiningMode.EAT_OUT],
        health_tags=[HealthGoal.LIGHT, HealthGoal.COMFORT],
        flavor_tags=["清淡", "热乎", "软乎"],
        avoid_tags=["皮蛋", "猪肉", "米粥"],
        prep_minutes=10,
        description="热粥软乎好入口，早上吃很稳妥。",
    ),
    MealOption(
        id="breakfast-soy-milk-youtiao",
        name="豆浆油条",
        slot=MealSlot.BREAKFAST,
        cuisine="家常",
        budget=BudgetLevel.LOW,
        dining_modes=[DiningMode.EAT_OUT],
        health_tags=[HealthGoal.COMFORT],
        flavor_tags=["咸香", "热乎", "省事"],
        avoid_tags=["豆制品", "油炸", "面食"],
        prep_minutes=5,
        description="早餐摊经典组合，想省事时很顺手。",
    ),
    MealOption(
        id="breakfast-jianbing",
        name="煎饼果子",
        slot=MealSlot.BREAKFAST,
        cuisine="天津",
        budget=BudgetLevel.LOW,
        dining_modes=[DiningMode.EAT_OUT],
        health_tags=[HealthGoal.COMFORT],
        flavor_tags=["咸香", "下饭", "省事"],
        avoid_tags=["鸡蛋", "面食", "油炸"],
        prep_minutes=6,
        description="摊上现做最香，管饱又不费脑子。",
    ),
    MealOption(
        id="breakfast-fresh-wonton",
        name="鲜肉小馄饨",
        slot=MealSlot.BREAKFAST,
        cuisine="江浙",
        budget=BudgetLevel.MEDIUM,
        dining_modes=[DiningMode.EAT_OUT],
        health_tags=[HealthGoal.COMFORT, HealthGoal.BALANCED],
        flavor_tags=["清淡", "热乎", "鲜"],
        avoid_tags=["猪肉", "面食"],
        prep_minutes=10,
        description="一碗热汤下肚，早上会舒服很多。",
    ),
    MealOption(
        id="breakfast-rice-noodle-roll",
        name="鸡蛋肠粉",
        slot=MealSlot.BREAKFAST,
        cuisine="粤式",
        budget=BudgetLevel.MEDIUM,
        dining_modes=[DiningMode.EAT_OUT],
        health_tags=[HealthGoal.BALANCED],
        flavor_tags=["鲜", "软乎", "清淡"],
        avoid_tags=["鸡蛋", "米浆"],
        prep_minutes=8,
        description="滑滑嫩嫩的一份，适合不想吃太重的早晨。",
    ),
    MealOption(
        id="breakfast-hot-dry-noodles",
        name="热干面",
        slot=MealSlot.BREAKFAST,
        cuisine="湖北",
        budget=BudgetLevel.LOW,
        dining_modes=[DiningMode.EAT_OUT],
        health_tags=[HealthGoal.COMFORT],
        flavor_tags=["芝麻香", "咸香", "顶饱"],
        avoid_tags=["芝麻", "面食"],
        prep_minutes=8,
        description="芝麻酱香气足，忙碌早上很顶饱。",
    ),
    MealOption(
        id="lunch-lanzhou-beef-noodles",
        name="兰州牛肉面",
        slot=MealSlot.LUNCH,
        cuisine="西北",
        budget=BudgetLevel.LOW,
        dining_modes=[DiningMode.EAT_OUT],
        health_tags=[HealthGoal.COMFORT, HealthGoal.HIGH_PROTEIN],
        flavor_tags=["热乎", "咸香", "汤面"],
        avoid_tags=["牛肉", "面食", "香菜"],
        prep_minutes=10,
        description="汤热面顺，午饭不知道吃啥时很稳。",
    ),
    MealOption(
        id="lunch-braised-chicken-rice",
        name="黄焖鸡米饭",
        slot=MealSlot.LUNCH,
        cuisine="鲁味",
        budget=BudgetLevel.MEDIUM,
        dining_modes=[DiningMode.EAT_OUT],
        health_tags=[HealthGoal.COMFORT, HealthGoal.HIGH_PROTEIN],
        flavor_tags=["下饭", "热乎", "咸香"],
        avoid_tags=["鸡肉", "米饭", "香菇"],
        prep_minutes=15,
        description="有肉有菜有汤汁，拌饭特别香。",
    ),
    MealOption(
        id="lunch-green-pepper-pork-rice",
        name="青椒肉丝盖饭",
        slot=MealSlot.LUNCH,
        cuisine="家常",
        budget=BudgetLevel.LOW,
        dining_modes=[DiningMode.COOK, DiningMode.EAT_OUT],
        health_tags=[HealthGoal.BALANCED],
        flavor_tags=["下饭", "咸香", "家常"],
        avoid_tags=["猪肉", "青椒", "米饭"],
        prep_minutes=18,
        description="家常菜盖到米饭上，简单但很有安全感。",
    ),
    MealOption(
        id="lunch-malatang",
        name="麻辣烫",
        slot=MealSlot.LUNCH,
        cuisine="川湘",
        budget=BudgetLevel.MEDIUM,
        dining_modes=[DiningMode.EAT_OUT],
        health_tags=[HealthGoal.COMFORT],
        flavor_tags=["麻辣", "热乎", "自由搭配"],
        avoid_tags=["辣", "花椒"],
        prep_minutes=12,
        description="想吃什么夹什么，选择权交给小碗也不错。",
    ),
    MealOption(
        id="lunch-shaxian-steamed-dumpling-soup",
        name="沙县蒸饺配炖汤",
        slot=MealSlot.LUNCH,
        cuisine="福建",
        budget=BudgetLevel.LOW,
        dining_modes=[DiningMode.EAT_OUT],
        health_tags=[HealthGoal.BALANCED, HealthGoal.COMFORT],
        flavor_tags=["省事", "热乎", "咸香"],
        avoid_tags=["猪肉", "面食"],
        prep_minutes=10,
        description="小店经典搭配，便宜省事又有汤喝。",
    ),
    MealOption(
        id="lunch-cantonese-roast-rice",
        name="广东烧腊饭",
        slot=MealSlot.LUNCH,
        cuisine="粤式",
        budget=BudgetLevel.MEDIUM,
        dining_modes=[DiningMode.EAT_OUT],
        health_tags=[HealthGoal.HIGH_PROTEIN, HealthGoal.COMFORT],
        flavor_tags=["咸香", "下饭", "肉香"],
        avoid_tags=["猪肉", "鸡肉", "米饭"],
        prep_minutes=10,
        description="烧腊铺的明档香气，午饭很难拒绝。",
    ),
    MealOption(
        id="dinner-tomato-egg-rice",
        name="番茄炒蛋饭",
        slot=MealSlot.DINNER,
        cuisine="家常",
        budget=BudgetLevel.LOW,
        dining_modes=[DiningMode.COOK, DiningMode.EAT_OUT],
        health_tags=[HealthGoal.BALANCED, HealthGoal.COMFORT],
        flavor_tags=["酸甜", "下饭", "家常"],
        avoid_tags=["鸡蛋", "番茄", "米饭"],
        prep_minutes=12,
        description="酸甜开胃，家里和小店都很容易安排。",
    ),
    MealOption(
        id="dinner-yuxiang-pork-rice",
        name="鱼香肉丝饭",
        slot=MealSlot.DINNER,
        cuisine="川湘",
        budget=BudgetLevel.LOW,
        dining_modes=[DiningMode.COOK, DiningMode.EAT_OUT],
        health_tags=[HealthGoal.COMFORT],
        flavor_tags=["酸甜辣", "下饭", "家常"],
        avoid_tags=["猪肉", "辣", "米饭"],
        prep_minutes=18,
        description="鱼香汁一拌饭，晚餐马上有胃口。",
    ),
    MealOption(
        id="dinner-potato-beef-rice",
        name="土豆牛肉盖饭",
        slot=MealSlot.DINNER,
        cuisine="家常",
        budget=BudgetLevel.MEDIUM,
        dining_modes=[DiningMode.COOK, DiningMode.EAT_OUT],
        health_tags=[HealthGoal.HIGH_PROTEIN, HealthGoal.COMFORT],
        flavor_tags=["软糯", "下饭", "热乎"],
        avoid_tags=["牛肉", "土豆", "米饭"],
        prep_minutes=30,
        description="土豆软糯、牛肉顶饱，适合晚饭吃踏实一点。",
    ),
    MealOption(
        id="dinner-hunan-pork",
        name="农家小炒肉",
        slot=MealSlot.DINNER,
        cuisine="川湘",
        budget=BudgetLevel.MEDIUM,
        dining_modes=[DiningMode.COOK, DiningMode.EAT_OUT],
        health_tags=[HealthGoal.COMFORT],
        flavor_tags=["微辣", "下饭", "锅气"],
        avoid_tags=["猪肉", "辣", "米饭"],
        prep_minutes=18,
        description="锅气足、很下饭，适合想吃点有味道的晚上。",
    ),
    MealOption(
        id="dinner-northeast-dumplings",
        name="东北酸菜猪肉饺子",
        slot=MealSlot.DINNER,
        cuisine="东北",
        budget=BudgetLevel.MEDIUM,
        dining_modes=[DiningMode.COOK, DiningMode.EAT_OUT],
        health_tags=[HealthGoal.COMFORT],
        flavor_tags=["热乎", "顶饱", "酸香"],
        avoid_tags=["猪肉", "酸菜", "面食"],
        prep_minutes=20,
        description="一盘热饺子很有家里味，蘸点醋更香。",
    ),
    MealOption(
        id="dinner-pickled-fish",
        name="酸菜鱼",
        slot=MealSlot.DINNER,
        cuisine="川湘",
        budget=BudgetLevel.HIGH,
        dining_modes=[DiningMode.EAT_OUT],
        health_tags=[HealthGoal.HIGH_PROTEIN, HealthGoal.COMFORT],
        flavor_tags=["酸辣", "热乎", "鲜"],
        avoid_tags=["鱼类", "海鲜", "辣", "酸菜"],
        prep_minutes=20,
        description="酸辣汤底很开胃，适合想吃大菜的时候。",
    ),
    MealOption(
        id="dinner-seafood-congee",
        name="砂锅海鲜粥",
        slot=MealSlot.DINNER,
        cuisine="粤式",
        budget=BudgetLevel.HIGH,
        dining_modes=[DiningMode.EAT_OUT],
        health_tags=[HealthGoal.LIGHT, HealthGoal.BALANCED],
        flavor_tags=["鲜", "清淡", "热乎"],
        avoid_tags=["海鲜", "虾", "米粥"],
        prep_minutes=25,
        description="粥底鲜甜，晚上想吃轻一点时很合适。",
    ),
]


def recommend_day(
    preferences: MealPreferenceInput,
    *,
    seed: int | None = None,
    catalog: Sequence[MealOption] = MEAL_CATALOG,
) -> dict[MealSlot, MealRecommendation]:
    rng = random.Random(seed)
    selected: dict[MealSlot, MealRecommendation] = {}
    used_ids: set[str] = set()

    for slot in MealSlot:
        recommendation = recommend_meal(
            preferences,
            slot=slot,
            excluded_ids=used_ids,
            rng=rng,
            catalog=catalog,
        )
        selected[slot] = recommendation
        used_ids.add(recommendation.meal.id)

    return selected


def swap_meal(
    preferences: MealPreferenceInput,
    *,
    slot: MealSlot,
    current_meal_id: str,
    seed: int | None = None,
    catalog: Sequence[MealOption] = MEAL_CATALOG,
) -> MealRecommendation:
    return recommend_meal(
        preferences,
        slot=slot,
        excluded_ids={current_meal_id},
        rng=random.Random(seed),
        catalog=catalog,
    )


def recommend_meal(
    preferences: MealPreferenceInput,
    *,
    slot: MealSlot,
    excluded_ids: set[str] | None = None,
    rng: random.Random | None = None,
    catalog: Sequence[MealOption] = MEAL_CATALOG,
) -> MealRecommendation:
    rng = rng or random.Random()
    excluded_ids = excluded_ids or set()
    candidates = [
        meal
        for meal in catalog
        if meal.slot == slot
        and meal.id not in excluded_ids
        and _matches_budget(meal, preferences.budget)
        and _matches_dining_mode(meal, preferences.dining_mode)
        and not _has_avoided_ingredient(meal, preferences.avoid_ingredients)
    ]

    if not candidates:
        candidates = [
            meal
            for meal in catalog
            if meal.slot == slot
            and meal.id not in excluded_ids
            and not _has_avoided_ingredient(meal, preferences.avoid_ingredients)
        ]

    if not candidates:
        raise ValueError(f"No meal candidates available for {slot}.")

    scored = [(_score(meal, preferences), meal) for meal in candidates]
    scored.sort(key=lambda item: item[0], reverse=True)
    top_score = scored[0][0]
    top_candidates = [(score, meal) for score, meal in scored if score >= top_score - 1.5]
    score, meal = rng.choice(top_candidates)
    matched = _matched_preferences(meal, preferences)
    return MealRecommendation(
        meal=meal,
        reason=_build_reason(meal, preferences, matched),
        score=round(score, 2),
        matched_preferences=matched,
    )


def _matches_budget(meal: MealOption, budget: BudgetLevel) -> bool:
    return _BUDGET_RANK[meal.budget] <= _BUDGET_RANK[budget]


def _matches_dining_mode(meal: MealOption, dining_mode: DiningMode) -> bool:
    return dining_mode == DiningMode.ANY or dining_mode in meal.dining_modes


def _has_avoided_ingredient(meal: MealOption, avoid_ingredients: list[str]) -> bool:
    normalized = [item.strip().lower() for item in avoid_ingredients if item.strip()]
    if not normalized:
        return False
    searchable = " ".join([meal.name, meal.description, *meal.avoid_tags]).lower()
    return any(item in searchable for item in normalized)


def _score(meal: MealOption, preferences: MealPreferenceInput) -> float:
    score = 1.0
    cuisines = {item.strip().lower() for item in preferences.preferred_cuisines if item.strip()}
    flavors = {item.strip().lower() for item in preferences.flavor_preferences if item.strip()}
    meal_flavors = {item.lower() for item in meal.flavor_tags}

    if meal.cuisine.lower() in cuisines:
        score += 2.0
    if preferences.health_goal in meal.health_tags:
        score += 2.0
    if flavors:
        score += 1.5 * len(flavors & meal_flavors)
    if preferences.prefer_quick and meal.prep_minutes <= 15:
        score += 1.0
    if meal.budget == BudgetLevel.LOW:
        score += 0.3
    if DiningMode.EAT_OUT in meal.dining_modes and DiningMode.COOK in meal.dining_modes:
        score += 0.2

    return score


def _matched_preferences(meal: MealOption, preferences: MealPreferenceInput) -> list[str]:
    matched: list[str] = []
    cuisines = {item.strip().lower() for item in preferences.preferred_cuisines if item.strip()}
    flavors = {item.strip().lower() for item in preferences.flavor_preferences if item.strip()}

    if meal.cuisine.lower() in cuisines:
        matched.append(f"偏好菜系：{meal.cuisine}")
    if preferences.health_goal in meal.health_tags:
        matched.append(f"目标：{_HEALTH_GOAL_LABELS[preferences.health_goal]}")
    for flavor in meal.flavor_tags:
        if flavor.lower() in flavors:
            matched.append(f"口味：{flavor}")
    if preferences.prefer_quick and meal.prep_minutes <= 15:
        matched.append("省时")
    if _matches_budget(meal, preferences.budget):
        matched.append(f"预算：{_BUDGET_LABELS[meal.budget]}")

    return matched


def _build_reason(
    meal: MealOption,
    preferences: MealPreferenceInput,
    matched_preferences: list[str],
) -> str:
    parts = []
    if matched_preferences:
        parts.append("小猪猪帮你挑了这份，因为它刚好匹配" + "、".join(matched_preferences[:3]))
    else:
        parts.append("小猪猪在当前限制里挑了这份，稳稳当当不踩雷")

    if preferences.prefer_quick and meal.prep_minutes <= 15:
        parts.append(f"大概 {meal.prep_minutes} 分钟就能吃上，饿了也不用等太久")
    else:
        parts.append(meal.description)

    return "；".join(parts) + "。"
