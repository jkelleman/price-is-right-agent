from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class ItemCreate(BaseModel):
    name: str
    url: str
    current_price: Optional[float] = None
    target_price: Optional[float] = None
    image_url: Optional[str] = None
    description: Optional[str] = None

class ItemResponse(BaseModel):
    id: int
    name: str
    url: str
    current_price: Optional[float]
    target_price: Optional[float]
    image_url: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True

class PriceHistoryResponse(BaseModel):
    id: int
    item_id: int
    price: float
    recorded_at: datetime
    
    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id: int
    item_id: int
    alert_type: str
    message: str
    sent_at: datetime
    is_read: bool
    
    class Config:
        from_attributes = True
