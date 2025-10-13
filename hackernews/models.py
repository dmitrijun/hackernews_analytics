"""
Data models for Hacker News API
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class ItemType(Enum):
    """Types of items in Hacker News"""
    STORY = "story"
    COMMENT = "comment"
    JOB = "job"
    POLL = "poll"
    POLLOPT = "pollopt"


@dataclass
class Item:
    """
    Represents a Hacker News item (story, comment, job, poll, or pollopt)
    """
    id: int
    type: str
    by: Optional[str] = None
    time: Optional[int] = None
    text: Optional[str] = None
    dead: Optional[bool] = None
    deleted: Optional[bool] = None
    parent: Optional[int] = None
    poll: Optional[int] = None
    kids: Optional[List[int]] = field(default_factory=list)
    url: Optional[str] = None
    score: Optional[int] = None
    title: Optional[str] = None
    parts: Optional[List[int]] = field(default_factory=list)
    descendants: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Item':
        """Create an Item from a dictionary"""
        if data is None:
            return None
        
        return cls(
            id=data.get('id'),
            type=data.get('type'),
            by=data.get('by'),
            time=data.get('time'),
            text=data.get('text'),
            dead=data.get('dead'),
            deleted=data.get('deleted'),
            parent=data.get('parent'),
            poll=data.get('poll'),
            kids=data.get('kids', []),
            url=data.get('url'),
            score=data.get('score'),
            title=data.get('title'),
            parts=data.get('parts', []),
            descendants=data.get('descendants')
        )

    def is_story(self) -> bool:
        """Check if item is a story"""
        return self.type == ItemType.STORY.value

    def is_comment(self) -> bool:
        """Check if item is a comment"""
        return self.type == ItemType.COMMENT.value

    def is_job(self) -> bool:
        """Check if item is a job posting"""
        return self.type == ItemType.JOB.value


@dataclass
class User:
    """
    Represents a Hacker News user
    """
    id: str
    created: int
    karma: int
    about: Optional[str] = None
    submitted: Optional[List[int]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create a User from a dictionary"""
        if data is None:
            return None
        
        return cls(
            id=data.get('id'),
            created=data.get('created'),
            karma=data.get('karma'),
            about=data.get('about'),
            submitted=data.get('submitted', [])
        )


@dataclass
class Updates:
    """
    Represents recent updates from Hacker News
    """
    items: List[int] = field(default_factory=list)
    profiles: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> 'Updates':
        """Create Updates from a dictionary"""
        if data is None:
            return None
        
        return cls(
            items=data.get('items', []),
            profiles=data.get('profiles', [])
        )
