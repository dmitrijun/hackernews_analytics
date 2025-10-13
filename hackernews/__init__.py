"""
HackerNews Firebase API Client
A Python client for accessing Hacker News data via Firebase API
"""

from .client import HackerNewsClient
from .models import Item, User, ItemType

__version__ = "1.0.0"
__all__ = ["HackerNewsClient", "Item", "User", "ItemType"]
