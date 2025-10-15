# HackerNews Data Scraper & Analysis Tool

An asynchronous Python scraper and analysis toolkit for collecting and analyzing HackerNews data to uncover posting strategies and engagement patterns.

## Description

This project is designed to help analyze HackerNews posting strategies by scraping historical data from the platform. It provides an efficient, async-based data collection system that fetches items (stories, comments, polls) and user information from the [HackerNews Firebase API](https://github.com/HackerNews/API). The scraped data can be used to conduct exploratory data analysis to answer questions about optimal posting times, title patterns, engagement metrics, and the impact of external links (GitHub, Twitter) on post performance.

The tool is optimized for large-scale data collection with configurable concurrency limits, batch processing, and time-based filtering (e.g., last 6 months of data).

## Project Structure

```
hn_gh_pull/
├── hackernews/              # Main package
│   ├── __init__.py          # Package initialization
│   ├── client.py            # Async HackerNews API client
│   └── data_puller.py       # Data collection orchestrator
├── data/                    # Data storage directory
│   ├── items.jsonl          # Collected HackerNews items (stories, comments, polls)
│   └── users.jsonl          # Collected user profiles
├── docs/                    # Documentation
│   └── task_description.md  # Project requirements and analysis questions
├── notebooks/               # Jupyter notebooks for analysis
│   └── eda.ipynb            # Exploratory data analysis
├── main.py                  # Main script to run data collection
├── questions.md             # Analysis questions to answer
├── pyproject.toml           # Project dependencies and metadata
└── README.md                # This file
```

## Installation

1. Clone this repository:

```bash
git clone <repository-url> && cd hn_gh_pull
```

2. Install dependencies:

```bash
uv sync
```

## Usage

### Quick Start

Run the main data collection script to start scraping HackerNews data:

```bash
uv run main.py
```

This will:

- Fetch items from the HackerNews Firebase API starting from the latest item ID
- Collect up to the last 6 months of data
- Save items to `data/items.jsonl`
- Automatically collect user profiles to `data/users.jsonl`
- Use 50 concurrent connections for optimal performance

### Custom Data Collection

You can customize the data collection behavior:

```python
import asyncio
from hackernews.data_puller import DataPuller
from hackernews.client import HackerNewsAPIClient

async def main():
    async with HackerNewsAPIClient(max_concurrent=50) as client:
        puller = DataPuller(client=client, batch_size=100)
        await puller.pull_items(
            item_file_path="data/items.jsonl",
            user_file_path="data/users.jsonl",
            max_items=1000,      # Limit to 1000 items
            n_months=6           # Only last 6 months
        )

asyncio.run(main())
```

### Parameters

- `max_concurrent`: Maximum number of simultaneous HTTP requests (default: 50)
- `batch_size`: Number of items to fetch in each batch (default: 100)
- `max_items`: Maximum number of items to collect (None = unlimited)
- `n_months`: Stop when items are older than N months (None = no time limit)
