from typing import List, Optional
from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    name: str
    quantity: int = 1
    source_id: Optional[str] = None
    replacement_options: List[str] = Field(default_factory=list)


class OrderPlan(BaseModel):
    provider: str
    items: List[OrderItem]
    delivery_slot: Optional[str] = None
    total_estimated_price: Optional[float] = None
    comment: Optional[str] = None


class OrderExecutionResult(BaseModel):
    status: str
    order_id: Optional[str] = None
    provider: Optional[str] = None
    final_price: Optional[float] = None
    delivery_eta: Optional[str] = None
    message: str