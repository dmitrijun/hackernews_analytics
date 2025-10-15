from hackernews.data_puller import DataPuller

def main():
    puller = DataPuller()
    puller.pull_items(
        item_file_path="data/items.jsonl",
        user_file_path="data/users.jsonl",
        max_items=None,
        n_months=6  # Stop at items older than 6 months
    )

if __name__ == "__main__":
    main()