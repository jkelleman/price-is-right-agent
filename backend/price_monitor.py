from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import logging
import asyncio

from database import SessionLocal
from models import Item, PriceHistory, Alert
from scraper import PriceScraper
from notifications import email_notifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceMonitor:
    """
    Background service for monitoring price changes
    
    Technical Decisions:
    - APScheduler: Lightweight, in-process scheduler (vs Celery which needs Redis/RabbitMQ)
    - BackgroundScheduler: Runs in separate thread, doesn't block FastAPI
    - 6-hour interval: Balance between responsiveness and not overwhelming sites
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scraper = PriceScraper()
        
    def start(self):
        """Start the background price monitoring"""
        # Check prices every 6 hours
        self.scheduler.add_job(
            self.check_all_prices,
            'interval',
            hours=6,
            id='price_check',
            replace_existing=True
        )
        self.scheduler.start()
        logger.info("Price monitoring started - checking every 6 hours")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Price monitoring stopped")
    
    def check_all_prices(self):
        """Check prices for all active items"""
        db = SessionLocal()
        try:
            items = db.query(Item).filter(Item.is_active == True).all()
            logger.info(f"Checking prices for {len(items)} items")
            
            alerts_to_notify = []  # Collect alerts for batch email
            
            for item in items:
                try:
                    alert = self._check_item_price(item, db)
                    if alert:
                        alerts_to_notify.append((item, alert))
                except Exception as e:
                    logger.error(f"Error checking price for item {item.id}: {e}")
                    # Continue with other items even if one fails
            
            db.commit()
            
            # Send batch email notification
            if alerts_to_notify:
                asyncio.run(email_notifier.send_batch_alerts(alerts_to_notify))
            
            logger.info("Price check completed")
        except Exception as e:
            logger.error(f"Error in price check job: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _check_item_price(self, item: Item, db: Session):
        """
        Check price for a single item
        Returns alert if one was created, None otherwise
        """
        # Scrape current price
        result = self.scraper.scrape_price(item.url)
        
        if not result or result['price'] is None:
            logger.warning(f"Could not fetch price for item {item.id}")
            return
        
        new_price = result['price']
        old_price = item.current_price
        
        # Update item's current price
        item.current_price = new_price
        item.updated_at = datetime.utcnow()
        
        # Record in price history
        price_history = PriceHistory(
            item_id=item.id,
            price=new_price
        )
        db.add(price_history)
        
        # Check if price dropped below target
        if item.target_price and new_price <= item.target_price:
            # Create price drop alert
            alert = Alert(
                item_id=item.id,
                alert_type="price_drop",
                message=f"Price dropped to ${new_price:.2f} (target: ${item.target_price:.2f})"
            )
            db.add(alert)
            logger.info(f"Price alert created for item {item.id}: {new_price} <= {item.target_price}")
            return alert
        
        # Log significant price changes (more than 5%)
        if old_price and abs(new_price - old_price) / old_price > 0.05:
            change_pct = ((new_price - old_price) / old_price) * 100
            logger.info(f"Item {item.id} price changed: ${old_price:.2f} → ${new_price:.2f} ({change_pct:+.1f}%)")
        
        return None

# Global instance
price_monitor = PriceMonitor()
