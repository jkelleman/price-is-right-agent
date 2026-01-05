from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn

from database import get_db, engine
from models import Base, Item, PriceHistory, Alert
from schemas import ItemCreate, ItemResponse, PriceHistoryResponse, AlertResponse
from price_monitor import price_monitor
from similarity import similarity_engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Price Tracker API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Start background price monitoring on app startup"""
    price_monitor.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background monitoring on app shutdown"""
    price_monitor.stop()

@app.get("/")
async def root():
    return {"message": "Price Tracker API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/items", response_model=ItemResponse)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Add a new item to track"""
    db_item = Item(
        name=item.name,
        url=item.url,
        current_price=item.current_price,
        target_price=item.target_price,
        image_url=item.image_url,
        description=item.description
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items", response_model=List[ItemResponse])
async def get_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all tracked items"""
    items = db.query(Item).filter(Item.is_active == True).offset(skip).limit(limit).all()
    return items

@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific item"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.delete("/items/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.is_active = False
    db.commit()
    return {"message": "Item deleted successfully"}

@app.get("/items/{item_id}/history", response_model=List[PriceHistoryResponse])
async def get_price_history(item_id: int, db: Session = Depends(get_db)):
    """Get price history for an item"""
    history = db.query(PriceHistory).filter(PriceHistory.item_id == item_id).all()
    return history

# Alert endpoints
@app.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all alerts with optional filtering
    
    Query params:
    - skip: Pagination offset
    - limit: Max results to return
    - unread_only: If true, only return unread alerts
    """
    query = db.query(Alert)
    
    if unread_only:
        query = query.filter(Alert.is_read == False)
    
    alerts = query.order_by(Alert.sent_at.desc()).offset(skip).limit(limit).all()
    return alerts

@app.get("/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get a specific alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@app.patch("/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as read"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_read = True
    db.commit()
    return {"message": "Alert marked as read"}

@app.patch("/alerts/read-all")
async def mark_all_alerts_read(db: Session = Depends(get_db)):
    """Mark all alerts as read"""
    db.query(Alert).update({"is_read": True})
    db.commit()
    return {"message": "All alerts marked as read"}

@app.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(alert)
    db.commit()
    return {"message": "Alert deleted successfully"}

# Similarity/AI endpoints
@app.get("/items/{item_id}/similar")
async def get_similar_items(
    item_id: int,
    min_similarity: float = 0.75,
    db: Session = Depends(get_db)
):
    """
    Find similar items using AI embeddings
    
    Query params:
    - min_similarity: Minimum similarity score (0-1), default 0.75
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    similar_items = await similarity_engine.find_similar_items(item, db, min_similarity)
    
    # Format response
    results = []
    for similar in similar_items:
        results.append({
            "item": ItemResponse.from_orm(similar['item']),
            "similarity_score": similar['similarity_score']
        })
    
    return results

@app.get("/items/{item_id}/better-deals")
async def get_better_deals(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Find similar items with better prices (at least 10% cheaper)
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    better_deals = await similarity_engine.find_better_deals(item, db)
    
    # Format response
    results = []
    for deal in better_deals:
        results.append({
            "item": ItemResponse.from_orm(deal['item']),
            "similarity_score": deal['similarity_score'],
            "savings": deal['savings'],
            "savings_percent": deal['savings_percent']
        })
    
    return results

@app.post("/items/{item_id}/find-alternatives")
async def trigger_similarity_check(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Manually trigger similarity check and create alerts for better deals
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await similarity_engine.create_similar_item_alerts(item, db)
    
    return {"message": "Similarity check completed, alerts created if alternatives found"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
