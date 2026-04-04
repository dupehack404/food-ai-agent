from typing import List, Optional
from pydantic import BaseModel, Field


class MealCandidate(BaseModel):
    id: str
    name: str
    calories: int
    price: float
    ingredients: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    cuisine: Optional[str] = None
    source: str
    available: bool = True


class PlannedMeal(BaseModel):
    meal_type: str
    item_id: str
    item_name: str
    calories: int
    price: float
    reason: Optional[str] = None
    score: Optional[int] = None


class MealPlan(BaseModel):
    day: str
    meals: List[PlannedMeal]
    total_calories: int
    total_price: float
    notes: Optional[str] = None