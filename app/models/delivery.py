from typing import Optional
from pydantic import BaseModel


class DeliveryDecision(BaseModel):
    action: str
    chosen_slot: Optional[str] = None
    reason: str