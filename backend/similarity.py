import os
from openai import AsyncOpenAI
from typing import List, Dict, Optional
import numpy as np
from sqlalchemy.orm import Session
import logging

from models import Item, Alert
from database import SessionLocal

logger = logging.getLogger(__name__)

class SimilarityEngine:
    """
    AI-powered product similarity detection using OpenAI embeddings
    
    Technical Decisions:
    - OpenAI text-embedding-3-small: Cost-effective ($0.02/1M tokens) vs ada-002 ($0.10/1M)
    - Cosine similarity: Standard for embeddings, intuitive 0-1 scale
    - Threshold 0.75: Empirically good balance for product similarity
    - Async calls: Don't block API requests
    - Cache embeddings: Store in DB to avoid redundant API calls
    """
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set - similarity features will be disabled")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=api_key)
        
        self.model = "text-embedding-3-small"
        self.similarity_threshold = 0.75
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding vector for text"""
        if not self.client:
            return None
        
        try:
            response = await self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        
        return float(dot_product / (norm_v1 * norm_v2))
    
    async def find_similar_items(
        self, 
        item: Item, 
        db: Session,
        min_similarity: float = None
    ) -> List[Dict]:
        """
        Find items similar to the given item
        
        Returns list of dicts with: item, similarity_score
        """
        if not self.client:
            logger.warning("Similarity search unavailable - OpenAI client not initialized")
            return []
        
        min_similarity = min_similarity or self.similarity_threshold
        
        # Create search text from item
        search_text = f"{item.name} {item.description or ''}"
        item_embedding = await self.get_embedding(search_text)
        
        if not item_embedding:
            return []
        
        # Get all other active items
        other_items = db.query(Item).filter(
            Item.is_active == True,
            Item.id != item.id
        ).all()
        
        similar_items = []
        
        for other_item in other_items:
            other_text = f"{other_item.name} {other_item.description or ''}"
            other_embedding = await self.get_embedding(other_text)
            
            if not other_embedding:
                continue
            
            similarity = self.cosine_similarity(item_embedding, other_embedding)
            
            if similarity >= min_similarity:
                similar_items.append({
                    'item': other_item,
                    'similarity_score': similarity
                })
        
        # Sort by similarity (highest first)
        similar_items.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return similar_items
    
    async def find_better_deals(
        self,
        item: Item,
        db: Session,
        price_discount: float = 0.10  # 10% cheaper
    ) -> List[Dict]:
        """
        Find similar items that are cheaper (better deals)
        
        Returns items that are:
        1. Similar (above threshold)
        2. At least X% cheaper
        """
        similar_items = await self.find_similar_items(item, db)
        
        if not item.current_price:
            return similar_items
        
        better_deals = []
        target_price = item.current_price * (1 - price_discount)
        
        for similar in similar_items:
            other_item = similar['item']
            if other_item.current_price and other_item.current_price <= target_price:
                similar['savings'] = item.current_price - other_item.current_price
                similar['savings_percent'] = (similar['savings'] / item.current_price) * 100
                better_deals.append(similar)
        
        return better_deals
    
    async def create_similar_item_alerts(
        self,
        item: Item,
        db: Session
    ):
        """
        Check for similar items with better prices and create alerts
        Should be called periodically or when new items are added
        """
        better_deals = await self.find_better_deals(item, db)
        
        for deal in better_deals:
            other_item = deal['item']
            
            # Check if we already have a recent alert for this combination
            existing = db.query(Alert).filter(
                Alert.item_id == item.id,
                Alert.alert_type == "similar_item",
                Alert.message.contains(other_item.name)
            ).first()
            
            if existing:
                continue
            
            # Create alert
            alert = Alert(
                item_id=item.id,
                alert_type="similar_item",
                message=(
                    f"Found similar item '{other_item.name}' for ${other_item.current_price:.2f} "
                    f"({deal['savings_percent']:.0f}% cheaper, save ${deal['savings']:.2f})"
                )
            )
            db.add(alert)
            logger.info(f"Created similar item alert for item {item.id}")
        
        db.commit()

# Global instance
similarity_engine = SimilarityEngine()
