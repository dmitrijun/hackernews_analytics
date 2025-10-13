"""
Hacker News Firebase API Client
"""

import requests
from typing import List, Optional
from .models import Item, User, Updates


class HackerNewsClient:
    """
    Client for accessing Hacker News data via Firebase API
    
    Base URL: https://hacker-news.firebaseio.com/v0/
    """
    
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    
    def __init__(self, timeout: int = 10):
        """
        Initialize the Hacker News client
        
        Args:
            timeout: Request timeout in seconds (default: 10)
        """
        self.timeout = timeout
        self.session = requests.Session()
    
    def _get(self, endpoint: str) -> dict:
        """
        Make a GET request to the API
        
        Args:
            endpoint: API endpoint (without base URL)
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.BASE_URL}/{endpoint}.json"
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def get_item(self, item_id: int) -> Optional[Item]:
        """
        Get a specific item by ID
        
        Args:
            item_id: The item's unique ID
            
        Returns:
            Item object or None if not found
        """
        try:
            data = self._get(f"item/{item_id}")
            return Item.from_dict(data)
        except requests.exceptions.HTTPError:
            return None
    
    def get_user(self, username: str) -> Optional[User]:
        """
        Get a user's profile
        
        Args:
            username: The user's username (case-sensitive)
            
        Returns:
            User object or None if not found
        """
        try:
            data = self._get(f"user/{username}")
            return User.from_dict(data)
        except requests.exceptions.HTTPError:
            return None
    
    def get_max_item_id(self) -> int:
        """
        Get the current largest item ID
        
        Returns:
            Maximum item ID
        """
        return self._get("maxitem")
    
    def get_top_stories(self, limit: Optional[int] = None) -> List[int]:
        """
        Get up to 500 top stories (includes jobs)
        
        Args:
            limit: Maximum number of story IDs to return
            
        Returns:
            List of story IDs
        """
        story_ids = self._get("topstories")
        return story_ids[:limit] if limit else story_ids
    
    def get_new_stories(self, limit: Optional[int] = None) -> List[int]:
        """
        Get up to 500 new stories
        
        Args:
            limit: Maximum number of story IDs to return
            
        Returns:
            List of story IDs
        """
        story_ids = self._get("newstories")
        return story_ids[:limit] if limit else story_ids
    
    def get_best_stories(self, limit: Optional[int] = None) -> List[int]:
        """
        Get up to 500 best stories
        
        Args:
            limit: Maximum number of story IDs to return
            
        Returns:
            List of story IDs
        """
        story_ids = self._get("beststories")
        return story_ids[:limit] if limit else story_ids
    
    def get_ask_stories(self, limit: Optional[int] = None) -> List[int]:
        """
        Get up to 200 Ask HN stories
        
        Args:
            limit: Maximum number of story IDs to return
            
        Returns:
            List of story IDs
        """
        story_ids = self._get("askstories")
        return story_ids[:limit] if limit else story_ids
    
    def get_show_stories(self, limit: Optional[int] = None) -> List[int]:
        """
        Get up to 200 Show HN stories
        
        Args:
            limit: Maximum number of story IDs to return
            
        Returns:
            List of story IDs
        """
        story_ids = self._get("showstories")
        return story_ids[:limit] if limit else story_ids
    
    def get_job_stories(self, limit: Optional[int] = None) -> List[int]:
        """
        Get up to 200 job stories
        
        Args:
            limit: Maximum number of story IDs to return
            
        Returns:
            List of story IDs
        """
        story_ids = self._get("jobstories")
        return story_ids[:limit] if limit else story_ids
    
    def get_updates(self) -> Updates:
        """
        Get recently changed items and profiles
        
        Returns:
            Updates object containing changed item IDs and profile names
        """
        data = self._get("updates")
        return Updates.from_dict(data)
    
    def get_items(self, item_ids: List[int]) -> List[Item]:
        """
        Get multiple items by their IDs
        
        Args:
            item_ids: List of item IDs
            
        Returns:
            List of Item objects (None for not found items)
        """
        return [self.get_item(item_id) for item_id in item_ids]
    
    def get_top_stories_with_details(self, limit: int = 10) -> List[Item]:
        """
        Get top stories with full details
        
        Args:
            limit: Number of stories to retrieve (default: 10)
            
        Returns:
            List of Item objects with full details
        """
        story_ids = self.get_top_stories(limit=limit)
        return self.get_items(story_ids)
    
    def get_comments_for_item(self, item_id: int, recursive: bool = False) -> List[Item]:
        """
        Get all comments for a specific item
        
        Args:
            item_id: The parent item ID
            recursive: If True, fetch all nested comments recursively
            
        Returns:
            List of comment Item objects
        """
        item = self.get_item(item_id)
        if not item or not item.kids:
            return []
        
        comments = []
        for kid_id in item.kids:
            comment = self.get_item(kid_id)
            if comment:
                comments.append(comment)
                if recursive and comment.kids:
                    comments.extend(self.get_comments_for_item(kid_id, recursive=True))
        
        return comments
    
    def close(self):
        """Close the HTTP session"""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
