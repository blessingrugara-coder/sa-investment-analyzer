"""Base scraper with ethical practices"""
import time
import requests
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def wait_if_needed(self):
        now = datetime.now()
        cutoff = now.timestamp() - self.time_window
        self.requests = [t for t in self.requests if t > cutoff]
        
        if len(self.requests) >= self.max_requests:
            wait_time = self.requests[0] + self.time_window - now.timestamp()
            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting {wait_time:.1f}s")
                time.sleep(wait_time + 0.1)
                self.requests = []
        
        self.requests.append(now.timestamp())


class BaseScraper(ABC):
    """Base class for all scrapers"""
    
    def __init__(self, domain: str):
        self.domain = domain
        self.base_url = f"https://{domain}"
        self.session = requests.Session()
        self.rate_limiter = RateLimiter(
            max_requests=settings.max_requests_per_minute
        )
        
        self.session.headers.update({
            'User-Agent': settings.user_agent
        })
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make rate-limited GET request"""
        self.rate_limiter.wait_if_needed()
        
        if settings.scraping_delay_seconds > 0:
            time.sleep(settings.scraping_delay_seconds)
        
        response = self.session.get(url, timeout=30, **kwargs)
        response.raise_for_status()
        return response
    
    @abstractmethod
    def scrape(self, *args, **kwargs) -> Any:
        """Main scraping method"""
        pass
    
    def close(self):
        self.session.close()