"""
Utility functions for Hacker News data
"""

from datetime import datetime
from typing import Optional
import html


def format_timestamp(timestamp: int) -> str:
    """
    Convert Unix timestamp to readable datetime string
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        Formatted datetime string
    """
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def clean_html(text: Optional[str]) -> str:
    """
    Clean HTML entities from text
    
    Args:
        text: Text with HTML entities
        
    Returns:
        Plain text
    """
    if not text:
        return ""
    return html.unescape(text)


def get_item_url(item_id: int) -> str:
    """
    Get the Hacker News URL for an item
    
    Args:
        item_id: Item ID
        
    Returns:
        Full URL to the item on Hacker News
    """
    return f"https://news.ycombinator.com/item?id={item_id}"


def get_user_url(username: str) -> str:
    """
    Get the Hacker News URL for a user profile
    
    Args:
        username: Username
        
    Returns:
        Full URL to the user profile on Hacker News
    """
    return f"https://news.ycombinator.com/user?id={username}"
