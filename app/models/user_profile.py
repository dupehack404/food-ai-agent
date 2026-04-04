from typing import List, Optional
from pydantic import BaseModel, Field


class DeliveryPolicy(BaseModel):
    allow_leave_at_door: bool = False
    forbid_when_user_away: bool = True
    min_buffer_minutes: int = 30


class TimeWindow(BaseModel):
    start: str
    end: str


class WeeklyAvailability(BaseModel):
    monday: List[TimeWindow] = Field(default_factory=list)
    tuesday: List[TimeWindow] = Field(default_factory=list)
    wednesday: List[TimeWindow] = Field(default_factory=list)
    thursday: List[TimeWindow] = Field(default_factory=list)
    friday: List[TimeWindow] = Field(default_factory=list)
    saturday: List[TimeWindow] = Field(default_factory=list)
    sunday: List[TimeWindow] = Field(default_factory=list)


class UserProfile(BaseModel):
    user_id: str

    allergies: List[str] = Field(default_factory=list)
    dislikes: List[str] = Field(default_factory=list)
    likes: List[str] = Field(default_factory=list)
    forbidden_products: List[str] = Field(default_factory=list)

    calorie_target: int
    daily_meal_count: int = 3
    budget_per_day: Optional[float] = None

    preferred_cuisines: List[str] = Field(default_factory=list)
    preferred_delivery_slots: List[str] = Field(default_factory=list)

    weekly_availability: WeeklyAvailability = Field(default_factory=WeeklyAvailability)
    delivery_policy: DeliveryPolicy = Field(default_factory=DeliveryPolicy)

    notes: Optional[str] = None