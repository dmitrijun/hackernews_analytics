import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional
from .client import HackerNewsAPIClient


class DataPuller:
    """Pull HackerNews items sequentially from max ID down to a time threshold."""

    def __init__(self, client: Optional[HackerNewsAPIClient] = None):
        """Initialize the data puller.

        Args:
            client: HackerNewsAPIClient instance. If None, creates a new one.
        """
        self.client = client or HackerNewsAPIClient()
        self.collected_usernames: set[str] = set()

    def clear_output(self, path: str):
        """Clear the contents of a JSONL file."""
        with open(path, 'w', encoding='utf-8'):
            pass  # Just open in write mode to clear the file

    def save_object(self, obj: dict[str, Any], path: str):
        """Append a Python object as a JSON line to a JSONL file."""
        with open(path, 'a', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False)
            f.write('\n')

    def pull_single_item(self, item_id: int) -> Optional[dict[str, Any]]:
        """Pull a single item by its ID."""
        try:
            return self.client.collect_item(item_id)
        except Exception as e:
            print(f"Error pulling item {item_id}: {e}")
            return None

    def pull_single_user(self, username: str) -> Optional[dict[str, Any]]:
        """Pull user information by username."""
        try:
            return self.client.collect_user(username)
        except Exception as e:
            print(f"Error pulling user {username}: {e}")
            return None

    def save_user(self, username: str, path: str = "data/users.jsonl"):
        user_info = self.pull_single_user(username)
        if user_info is not None:
            self.save_object(user_info, path)
        else:
            print(f"User info for {username} not found, skipping.")

    def pull_items(
        self,
        item_file_path: str = "data/items.jsonl",
        user_file_path: str = "data/users.jsonl",
        max_items: Optional[int] = None,
        n_months: Optional[int] = None
    ) -> int:
        """Pull items sequentially from max ID until conditions are met.

        Args:
            output_path: Path to save items JSONL file
            max_items: Maximum number of items to pull (None for unlimited)
            n_months: Stop when item is older than n_months (None for no time limit)

        Returns:
            Number of items successfully pulled
        """
        # Get max item ID
        max_id = self.client.get_max_item_id()
        if max_id is None:
            print("Failed to get max item ID")
            return 0

        print(f"Starting from max item ID: {max_id}")

        # Calculate cutoff timestamp if n_months is specified
        cutoff_time = None
        if n_months is not None:
            cutoff_date = datetime.now() - timedelta(days=n_months * 30)
            cutoff_time = int(cutoff_date.timestamp())
            print(
                f"Will stop at items older than {cutoff_date.strftime('%Y-%m-%d')}")

        # Ensure output directory exists and empty the output file
        output_file = Path(item_file_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        self.clear_output(item_file_path)
        self.clear_output(user_file_path)

        # Pull items sequentially
        items_pulled = 0
        current_id = max_id

        while True:
            # Check if we've hit max_items
            if max_items is not None and items_pulled >= max_items:
                print(f"Reached max_items limit: {max_items}")
                break

            # Fetch item
            item = self.client.collect_item(current_id)

            if item is None:
                # Failed to fetch item, skip to next
                print(f"Item {current_id} not found, skipping.")
                current_id -= 1
                continue

            # Check if item is older than cutoff
            if cutoff_time is not None and 'time' in item:
                if item['time'] < cutoff_time:
                    cutoff_date_str = datetime.fromtimestamp(
                        item['time']).strftime('%Y-%m-%d')
                    print(
                        f"Item {current_id} is older than cutoff ({cutoff_date_str}). Stopping.")
                    break

            self.save_object(item, item_file_path)
            items_pulled += 1

            # Also save user info if available
            if 'by' in item:
                if item['by'] not in self.collected_usernames:
                    self.collected_usernames.add(item['by'])
                    self.save_user(item['by'], path=user_file_path)

            if items_pulled % 100 == 0:
                print(
                    f"Pulled {items_pulled} items (current ID: {current_id})")

            # Move to next (previous) item
            current_id -= 1

            # Safety check - don't go below item 1
            if current_id < 1:
                print("Reached item ID 1")
                break

        print(f"Completed. Total items pulled: {items_pulled}")
        return items_pulled


if __name__ == "__main__":
    # Example usage
    puller = DataPuller()
    puller.pull_items(
        item_file_path="data/items.jsonl",
        user_file_path="data/users.jsonl",
        max_items=10,  # Pull max 10 items
        n_months=1  # Stop at items older than 1 month
    )
