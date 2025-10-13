# HackerNews Firebase API Client

A Python client for accessing Hacker News data via the official Firebase API.

## Overview

This project provides a clean and easy-to-use Python interface to the Hacker News Firebase API. It allows you to fetch stories, comments, user profiles, and other data from Hacker News in real-time.

## Features

- ✅ **Full Firebase API coverage** - Access all Hacker News endpoints
- ✅ **Type-safe models** - Dataclasses for Items, Users, and Updates
- ✅ **Easy to use** - Simple, intuitive API
- ✅ **Context manager support** - Automatic resource cleanup
- ✅ **Utility functions** - Helper functions for formatting and cleaning data
- ✅ **Example scripts** - Ready-to-run examples and data collection scripts

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd hn_gh_pull
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## API Endpoints

The client supports all official Hacker News Firebase API endpoints:

- **Items**: Stories, comments, jobs, polls, and poll options
- **Users**: User profiles and submission history
- **Top Stories**: Up to 500 top stories (includes jobs)
- **New Stories**: Up to 500 newest stories
- **Best Stories**: Up to 500 best stories
- **Ask HN**: Up to 200 Ask HN stories
- **Show HN**: Up to 200 Show HN stories
- **Job Stories**: Up to 200 job postings
- **Updates**: Recently changed items and profiles
- **Max Item ID**: Current largest item ID

## Usage

### Basic Example

```python
from hackernews import HackerNewsClient

# Create a client
with HackerNewsClient() as client:
    # Get top stories
    story_ids = client.get_top_stories(limit=10)
    
    # Get story details
    for story_id in story_ids:
        story = client.get_item(story_id)
        if story:
            print(f"{story.title} by {story.by}")
```

### Get User Profile

```python
from hackernews import HackerNewsClient

with HackerNewsClient() as client:
    user = client.get_user("pg")
    if user:
        print(f"Karma: {user.karma}")
        print(f"Submissions: {len(user.submitted)}")
```

### Get Comments for a Story

```python
from hackernews import HackerNewsClient

with HackerNewsClient() as client:
    # Get a story
    story = client.get_item(8863)
    
    # Get all comments (non-recursive)
    comments = client.get_comments_for_item(story.id)
    print(f"Found {len(comments)} comments")
    
    # Get all comments recursively
    all_comments = client.get_comments_for_item(story.id, recursive=True)
    print(f"Found {len(all_comments)} total comments")
```

## Example Scripts

### 1. Run Examples (`example.py`)

Demonstrates all API features with real data:

```bash
python example.py
```

This script shows:
- Top stories with details
- User profiles
- Specific item details
- Ask HN stories
- Show HN stories
- Job postings
- System information
- Recent updates
- Comments extraction

### 2. Save Data (`save_data.py`)

Pull and save Hacker News data to JSON files:

```bash
python save_data.py
```

This script fetches and saves:
- Top 50 stories
- New 50 stories
- Best 50 stories
- Ask HN stories (30)
- Show HN stories (30)
- Job postings (30)
- Recent updates
- System information
- Sample user profiles

All data is saved in a `data/` directory with timestamps.

## Project Structure

```
hn_gh_pull/
├── hackernews/              # Main package
│   ├── __init__.py         # Package initialization
│   ├── client.py           # API client implementation
│   ├── models.py           # Data models (Item, User, Updates)
│   └── utils.py            # Utility functions
├── example.py              # Usage examples
├── save_data.py            # Data collection script
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## API Reference

### HackerNewsClient

Main client class for accessing the API.

#### Methods

- `get_item(item_id: int) -> Item` - Get a specific item by ID
- `get_user(username: str) -> User` - Get a user profile
- `get_max_item_id() -> int` - Get the current largest item ID
- `get_top_stories(limit: int = None) -> List[int]` - Get top story IDs
- `get_new_stories(limit: int = None) -> List[int]` - Get new story IDs
- `get_best_stories(limit: int = None) -> List[int]` - Get best story IDs
- `get_ask_stories(limit: int = None) -> List[int]` - Get Ask HN story IDs
- `get_show_stories(limit: int = None) -> List[int]` - Get Show HN story IDs
- `get_job_stories(limit: int = None) -> List[int]` - Get job story IDs
- `get_updates() -> Updates` - Get recently changed items and profiles
- `get_items(item_ids: List[int]) -> List[Item]` - Get multiple items
- `get_top_stories_with_details(limit: int = 10) -> List[Item]` - Get top stories with full details
- `get_comments_for_item(item_id: int, recursive: bool = False) -> List[Item]` - Get comments for an item

### Models

#### Item

Represents a story, comment, job, poll, or poll option.

**Attributes:**
- `id: int` - Unique identifier
- `type: str` - Type of item (story, comment, job, poll, pollopt)
- `by: str` - Author username
- `time: int` - Creation timestamp (Unix time)
- `text: str` - Comment/story text (HTML)
- `title: str` - Title (for stories)
- `url: str` - URL (for stories)
- `score: int` - Score/votes
- `kids: List[int]` - Child comment IDs
- `descendants: int` - Total comment count
- And more...

#### User

Represents a user profile.

**Attributes:**
- `id: str` - Username
- `created: int` - Account creation timestamp
- `karma: int` - User karma
- `about: str` - User bio (HTML)
- `submitted: List[int]` - IDs of submitted items

#### Updates

Represents recent changes.

**Attributes:**
- `items: List[int]` - Changed item IDs
- `profiles: List[str]` - Changed usernames

### Utilities

Helper functions in `hackernews.utils`:

- `format_timestamp(timestamp: int) -> str` - Convert Unix timestamp to readable format
- `clean_html(text: str) -> str` - Remove HTML entities from text
- `get_item_url(item_id: int) -> str` - Get HN URL for an item
- `get_user_url(username: str) -> str` - Get HN URL for a user

## Firebase API Base URL

```
https://hacker-news.firebaseio.com/v0/
```

All data is accessed in near real-time via Firebase's API. No API key or authentication is required.

## Rate Limiting

Currently, there is no rate limit on the API. However, please be respectful and don't hammer the servers unnecessarily.

## Data Freshness

Data is available in near real-time. The Firebase API updates as changes occur on Hacker News.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided as-is for accessing the public Hacker News API.

## Resources

- [Official Hacker News API Documentation](https://github.com/HackerNews/API)
- [Hacker News Website](https://news.ycombinator.com/)
- [Firebase Documentation](https://firebase.google.com/docs)

## Support

For issues with the API itself, contact: api@ycombinator.com

For issues with this client library, please open an issue on GitHub.