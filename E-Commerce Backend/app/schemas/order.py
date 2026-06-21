from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.schemas.product import ProductResponse

class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: Optional[int] = None
    quantity: int
    price: float
    product: Optional[ProductResponse] = None

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total_price: float
    created_at: datetime
    items: List[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)

class OrderUpdate(BaseModel):
    status: str
