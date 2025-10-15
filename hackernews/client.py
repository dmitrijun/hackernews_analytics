import requests
from typing import Optional, Dict, Any

class HackerNewsAPIClient:
    """A simple data puller class for Hacker News API."""
    
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    
    def get_max_item_id(self) -> Optional[int]:
        """Get the current largest item ID."""
        try:
            response = requests.get(f"{self.BASE_URL}/maxitem.json")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching max item ID: {e}")
            return None
    
    def collect_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Collect an item by its ID."""
        try:
            response = requests.get(f"{self.BASE_URL}/item/{item_id}.json")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching item {item_id}: {e}")
            return None
    
    def collect_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Collect user information by username."""
        try:
            response = requests.get(f"{self.BASE_URL}/user/{username}.json")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching user {username}: {e}")
            return None