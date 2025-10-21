import asyncio
from hackernews.data_puller import DataPuller
from hackernews.client import HackerNewsAPIClient


async def main():
    async with HackerNewsAPIClient(max_concurrent=50) as client:
        puller = DataPuller(client=client, batch_size=100)
        await puller.pull_items(
            item_file_path="data/items.jsonl",
            user_file_path="data/users.jsonl",
            max_items=None,
            n_months=6  # Stop at items older than 6 months
        )


if __name__ == "__main__":
    asyncio.run(main())