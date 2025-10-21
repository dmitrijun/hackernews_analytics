import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional
from .client import HackerNewsAPIClient


class DataPuller:
    """Pull HackerNews items asynchronously with concurrent downloads."""

    def __init__(self, client: HackerNewsAPIClient, batch_size: int = 100):
        """Initialize the data puller.

        Args:
            client: HackerNewsAPIClient instance (required, must be initialized).
            batch_size: Number of items to fetch concurrently in each batch.
        """
        self.client = client
        self.collected_usernames: set[str] = set()
        self.batch_size = batch_size

    def clear_output(self, path: str):
        """Clear the contents of a JSONL file."""
        with open(path, 'w', encoding='utf-8'):
            pass  # Just open in write mode to clear the file

    def save_object(self, obj: dict[str, Any], path: str):
        """Append a Python object as a JSON line to a JSONL file."""
        with open(path, 'a', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False)
            f.write('\n')

    async def pull_single_item(self, item_id: int) -> Optional[dict[str, Any]]:
        """Pull a single item by its ID."""
        try:
            return await self.client.collect_item(item_id)
        except Exception as e:
            print(f"Error pulling item {item_id}: {e}")
            return None

    async def pull_single_user(self, username: str) -> Optional[dict[str, Any]]:
        """Pull user information by username."""
        try:
            return await self.client.collect_user(username)
        except Exception as e:
            print(f"Error pulling user {username}: {e}")
            return None

    async def save_user(self, username: str, path: str = "data/users.jsonl"):
        """Save user info asynchronously."""
        user_info = await self.pull_single_user(username)
        if user_info is not None:
            self.save_object(user_info, path)
        else:
            print(f"User info for {username} not found, skipping.")

    async def pull_items(
        self,
        item_file_path: str = "data/items.jsonl",
        user_file_path: str = "data/users.jsonl",
        max_items: Optional[int] = None,
        n_months: Optional[int] = None
    ) -> int:
        """Pull items concurrently from max ID until conditions are met.

        Args:
            item_file_path: Path to save items JSONL file
            user_file_path: Path to save users JSONL file
            max_items: Maximum number of items to pull (None for unlimited)
            n_months: Stop when item is older than n_months (None for no time limit)

        Returns:
            Number of items successfully pulled
        """
        # Get max item ID
        max_id = await self.client.get_max_item_id()
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

        # Pull items in batches concurrently
        items_pulled = 0
        current_id = max_id
        should_stop = False

        while not should_stop:
            # Check if we've hit max_items
            if max_items is not None and items_pulled >= max_items:
                print(f"Reached max_items limit: {max_items}")
                break

            # Determine batch of IDs to fetch
            batch_end = current_id - self.batch_size + 1
            if batch_end < 1:
                batch_end = 1
            
            # Calculate how many items to fetch in this batch
            if max_items is not None:
                remaining = max_items - items_pulled
                batch_ids = list(range(current_id, max(batch_end - 1, current_id - remaining), -1))
            else:
                batch_ids = list(range(current_id, batch_end - 1, -1))

            # Fetch batch concurrently
            tasks = [self.pull_single_item(item_id) for item_id in batch_ids]
            items = await asyncio.gather(*tasks)
            
            # Get first valid item's datetime for batch info
            first_item_datetime = None
            for item in items:
                if item is not None and 'time' in item:
                    first_item_datetime = datetime.fromtimestamp(item['time']).strftime('%Y-%m-%d %H:%M:%S')
                    break
            
            datetime_info = f" (first item: {first_item_datetime})" if first_item_datetime else ""
            print(f"Fetching batch: IDs {batch_ids[0]} to {batch_ids[-1]} ({len(batch_ids)} items){datetime_info}")

            # Process fetched items and collect usernames for this batch
            batch_usernames: set[str] = set()
            for item_id, item in zip(batch_ids, items):
                if item is None:
                    # Failed to fetch item, skip
                    print(f"Item {item_id} not found, skipping.")
                    continue

                # Check if item is older than cutoff
                if cutoff_time is not None and 'time' in item:
                    if item['time'] < cutoff_time:
                        cutoff_date_str = datetime.fromtimestamp(
                            item['time']).strftime('%Y-%m-%d')
                        print(
                            f"Item {item_id} is older than cutoff ({cutoff_date_str}). Stopping.")
                        should_stop = True
                        break

                self.save_object(item, item_file_path)
                items_pulled += 1

                # Collect username for immediate fetching
                if 'by' in item and item['by'] not in self.collected_usernames:
                    batch_usernames.add(item['by'])
                    self.collected_usernames.add(item['by'])

            # Fetch users for this batch immediately
            if batch_usernames:
                print(f"  Fetching {len(batch_usernames)} users for this batch...")
                user_tasks = [self.save_user(username, user_file_path) 
                             for username in batch_usernames]
                await asyncio.gather(*user_tasks)

            print(f"Pulled {items_pulled} items so far (last ID: {batch_ids[-1]})")

            # Move to next batch
            current_id = batch_end - 1

            # Safety check - don't go below item 1
            if current_id < 1:
                print("Reached item ID 1")
                break

            # Check if we should stop
            if max_items is not None and items_pulled >= max_items:
                break

        print(f"Completed. Total items pulled: {items_pulled}")
        print(f"Total unique users collected: {len(self.collected_usernames)}")
        return items_pulled


if __name__ == "__main__":
    # Example usage
    async def main():
        async with HackerNewsAPIClient() as client:
            puller = DataPuller(client=client, batch_size=100)
            await puller.pull_items(
                item_file_path="data/items.jsonl",
                user_file_path="data/users.jsonl",
                max_items=10,  # Pull max 10 items
                n_months=1  # Stop at items older than 1 month
            )
    
    asyncio.run(main())
