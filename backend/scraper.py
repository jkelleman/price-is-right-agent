import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import re

class PriceScraper:
    """Scrapes product prices from various e-commerce sites"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_price(self, url: str) -> Optional[Dict[str, any]]:
        """
        Scrape price from a product URL
        Returns dict with price, title, and image_url
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try common price selectors
            price = self._extract_price(soup)
            title = self._extract_title(soup)
            image_url = self._extract_image(soup)
            
            return {
                'price': price,
                'title': title,
                'image_url': image_url
            }
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from various common price elements"""
        price_selectors = [
            {'name': 'span', 'class': 'price'},
            {'name': 'span', 'class': 'a-price-whole'},
            {'name': 'span', 'class': 'product-price'},
            {'itemprop': 'price'}
        ]
        
        for selector in price_selectors:
            element = soup.find(**selector)
            if element:
                price_text = element.get_text()
                price_match = re.search(r'\d+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    return float(price_match.group())
        return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product title"""
        title_selectors = [
            {'name': 'h1'},
            {'itemprop': 'name'},
            {'name': 'title'}
        ]
        
        for selector in title_selectors:
            element = soup.find(**selector)
            if element:
                return element.get_text().strip()
        return None
    
    def _extract_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product image URL"""
        img = soup.find('img', itemprop='image')
        if not img:
            img = soup.find('img', class_='product-image')
        if not img:
            img = soup.find('img')
        
        if img and img.get('src'):
            return img['src']
        return None
