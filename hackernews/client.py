import aiohttp
import asyncio
from typing import Optional, Dict, Any, Type
from types import TracebackType


class HackerNewsAPIClient:
    """An async data puller class for Hacker News API."""
    
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    
    def __init__(self, max_concurrent: int = 50):
        """Initialize the client.
        
        Args:
            max_concurrent: Maximum number of concurrent requests (default: 50)
        """
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(
        self, 
        exc_type: Optional[Type[BaseException]], 
        exc_val: Optional[BaseException], 
        exc_tb: Optional[TracebackType]
    ) -> None:
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_max_item_id(self) -> Optional[int]:
        """Get the current largest item ID."""
        if not self.session:
            raise RuntimeError("Client session not initialized. Use async context manager.")
        
        try:
            async with self.semaphore:
                async with self.session.get(f"{self.BASE_URL}/maxitem.json") as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            print(f"Error fetching max item ID: {e}")
            return None
    
    async def collect_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Collect an item by its ID."""
        if not self.session:
            raise RuntimeError("Client session not initialized. Use async context manager.")
        
        try:
            async with self.semaphore:
                async with self.session.get(f"{self.BASE_URL}/item/{item_id}.json") as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            print(f"Error fetching item {item_id}: {e}")
            return None
    
    async def collect_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Collect user information by username."""
        if not self.session:
            raise RuntimeError("Client session not initialized. Use async context manager.")
        
        try:
            async with self.semaphore:
                async with self.session.get(f"{self.BASE_URL}/user/{username}.json") as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            print(f"Error fetching user {username}: {e}")
            return None