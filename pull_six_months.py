"""
Script to pull all Hacker News data for a 6-month period.
Saves items and users to separate JSONL files.
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Set, Optional
from hackernews import HackerNewsClient
from dataclasses import asdict


class DataPuller:
    """Pull and save Hacker News data for a given time period"""
    
    def __init__(self, output_dir: str = "data", rate_limit_delay: float = 0.1):
        """
        Initialize the data puller
        
        Args:
            output_dir: Directory to save output files
            rate_limit_delay: Delay between API requests in seconds (default: 0.1)
        """
        self.output_dir = output_dir
        self.rate_limit_delay = rate_limit_delay
        self.client = HackerNewsClient(timeout=30)
        self.collected_users: Set[str] = set()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize output files
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.items_file = os.path.join(output_dir, f'items_{self.timestamp}.jsonl')
        self.users_file = os.path.join(output_dir, f'users_{self.timestamp}.jsonl')
        
        # Statistics
        self.stats = {
            'items_total': 0,
            'items_saved': 0,
            'items_skipped': 0,
            'users_saved': 0,
            'users_failed': 0,
            'start_time': datetime.now(),
            'errors': []
        }
    
    def _append_to_jsonl(self, filepath: str, data: dict):
        """Append a JSON object to a JSONL file"""
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    def _item_to_dict(self, item) -> Optional[dict]:
        """Convert Item object to dictionary"""
        if item is None:
            return None
        
        return {
            'id': item.id,
            'type': item.type,
            'by': item.by,
            'time': item.time,
            'text': item.text,
            'dead': item.dead,
            'deleted': item.deleted,
            'parent': item.parent,
            'poll': item.poll,
            'kids': item.kids,
            'url': item.url,
            'score': item.score,
            'title': item.title,
            'parts': item.parts,
            'descendants': item.descendants
        }
    
    def _user_to_dict(self, user) -> Optional[dict]:
        """Convert User object to dictionary"""
        if user is None:
            return None
        
        return {
            'id': user.id,
            'created': user.created,
            'karma': user.karma,
            'about': user.about,
            'submitted': user.submitted
        }
    
    def save_item(self, item):
        """Save an item and fetch its author if not already collected"""
        if item is None:
            self.stats['items_skipped'] += 1
            return
        
        # Save the item
        item_dict = self._item_to_dict(item)
        if item_dict:
            self._append_to_jsonl(self.items_file, item_dict)
            self.stats['items_saved'] += 1
            
            # Fetch and save the user if not already collected
            if item.by and item.by not in self.collected_users:
                self.save_user(item.by)
    
    def save_user(self, username: str):
        """Fetch and save a user's data"""
        if username in self.collected_users:
            return
        
        try:
            time.sleep(self.rate_limit_delay)
            user = self.client.get_user(username)
            
            if user:
                user_dict = self._user_to_dict(user)
                if user_dict:
                    self._append_to_jsonl(self.users_file, user_dict)
                    self.collected_users.add(username)
                    self.stats['users_saved'] += 1
            else:
                self.stats['users_failed'] += 1
                
        except Exception as e:
            error_msg = f"Error fetching user {username}: {str(e)}"
            self.stats['errors'].append(error_msg)
            self.stats['users_failed'] += 1
    
    def pull_data_for_period(self, months: int = 6):
        """
        Pull all items from the last N months
        
        Args:
            months: Number of months to go back (default: 6)
        """
        # Calculate cutoff timestamp
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        cutoff_timestamp = int(cutoff_date.timestamp())
        
        print(f"Pulling data from {cutoff_date.strftime('%Y-%m-%d')} to now")
        print(f"Cutoff timestamp: {cutoff_timestamp}")
        print(f"Output files:")
        print(f"  - Items: {self.items_file}")
        print(f"  - Users: {self.users_file}")
        print("=" * 80)
        
        # Get the maximum item ID
        max_item_id = self.client.get_max_item_id()
        print(f"Maximum item ID: {max_item_id}")
        print(f"Starting to pull items backwards from {max_item_id}...")
        print()
        
        # Iterate backwards from max_item_id
        current_id = max_item_id
        items_outside_range = 0
        consecutive_old_items = 0
        max_consecutive_old = 1000  # Stop after 1000 consecutive old items
        
        while current_id > 0:
            # Progress update every 100 items
            if self.stats['items_total'] % 100 == 0:
                elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
                rate = self.stats['items_total'] / elapsed if elapsed > 0 else 0
                print(f"Progress: ID {current_id} | "
                      f"Processed: {self.stats['items_total']} | "
                      f"Saved: {self.stats['items_saved']} | "
                      f"Users: {self.stats['users_saved']} | "
                      f"Rate: {rate:.1f} items/sec")
            
            try:
                # Fetch the item
                time.sleep(self.rate_limit_delay)
                item = self.client.get_item(current_id)
                self.stats['items_total'] += 1
                
                if item and item.time:
                    if item.time >= cutoff_timestamp:
                        # Item is within our time range
                        self.save_item(item)
                        consecutive_old_items = 0
                    else:
                        # Item is too old
                        items_outside_range += 1
                        consecutive_old_items += 1
                        
                        # Stop if we've hit too many consecutive old items
                        if consecutive_old_items >= max_consecutive_old:
                            print(f"\nStopping: Found {consecutive_old_items} consecutive items "
                                  f"older than cutoff date")
                            break
                else:
                    # Item doesn't exist or has no timestamp
                    self.stats['items_skipped'] += 1
                    consecutive_old_items = 0
                
            except Exception as e:
                error_msg = f"Error fetching item {current_id}: {str(e)}"
                self.stats['errors'].append(error_msg)
                if self.stats['items_total'] % 100 == 0:
                    print(f"Error at ID {current_id}: {str(e)}")
            
            current_id -= 1
            
            # Safety check: if we've gone too far back without finding items
            if items_outside_range > max_consecutive_old * 10:
                print(f"\nStopping: Too many items outside date range ({items_outside_range})")
                break
        
        print("\n" + "=" * 80)
        print("Data pull completed!")
        self._print_stats()
    
    def pull_recent_items(self, count: int = 10000):
        """
        Pull the most recent N items and their users
        
        Args:
            count: Number of recent items to pull (default: 10000)
        """
        # Calculate cutoff - 6 months ago
        cutoff_date = datetime.now() - timedelta(days=180)
        cutoff_timestamp = int(cutoff_date.timestamp())
        
        print(f"Pulling up to {count} recent items (filtering by 6-month period)")
        print(f"Cutoff date: {cutoff_date.strftime('%Y-%m-%d')}")
        print(f"Output files:")
        print(f"  - Items: {self.items_file}")
        print(f"  - Users: {self.users_file}")
        print("=" * 80)
        
        # Get the maximum item ID
        max_item_id = self.client.get_max_item_id()
        print(f"Maximum item ID: {max_item_id}")
        print(f"Starting to pull items backwards from {max_item_id}...")
        print()
        
        # Iterate backwards from max_item_id
        current_id = max_item_id
        items_checked = 0
        
        while items_checked < count and current_id > 0:
            # Progress update every 100 items
            if items_checked % 100 == 0:
                elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
                rate = items_checked / elapsed if elapsed > 0 else 0
                print(f"Progress: ID {current_id} | "
                      f"Checked: {items_checked}/{count} | "
                      f"Saved: {self.stats['items_saved']} | "
                      f"Users: {self.stats['users_saved']} | "
                      f"Rate: {rate:.1f} items/sec")
            
            try:
                # Fetch the item
                time.sleep(self.rate_limit_delay)
                item = self.client.get_item(current_id)
                items_checked += 1
                self.stats['items_total'] += 1
                
                if item and item.time:
                    if item.time >= cutoff_timestamp:
                        # Item is within our 6-month range
                        self.save_item(item)
                    else:
                        # Item is too old, just skip it
                        self.stats['items_skipped'] += 1
                else:
                    # Item doesn't exist or has no timestamp
                    self.stats['items_skipped'] += 1
                
            except Exception as e:
                error_msg = f"Error fetching item {current_id}: {str(e)}"
                self.stats['errors'].append(error_msg)
                if items_checked % 100 == 0:
                    print(f"Error at ID {current_id}: {str(e)}")
            
            current_id -= 1
        
        print("\n" + "=" * 80)
        print("Data pull completed!")
        self._print_stats()
    
    def _print_stats(self):
        """Print summary statistics"""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        
        print("\nStatistics:")
        print(f"  Total items processed: {self.stats['items_total']}")
        print(f"  Items saved: {self.stats['items_saved']}")
        print(f"  Items skipped: {self.stats['items_skipped']}")
        print(f"  Users saved: {self.stats['users_saved']}")
        print(f"  Users failed: {self.stats['users_failed']}")
        print(f"  Total time: {elapsed:.1f} seconds")
        print(f"  Average rate: {self.stats['items_total']/elapsed:.1f} items/sec")
        
        if self.stats['errors']:
            print(f"\nErrors encountered: {len(self.stats['errors'])}")
            print("First 5 errors:")
            for error in self.stats['errors'][:5]:
                print(f"  - {error}")
    
    def close(self):
        """Clean up resources"""
        self.client.close()


def main():
    """Main function"""
    print("=" * 80)
    print("Hacker News 6-Month Data Puller")
    print("=" * 80)
    print()
    
    # Create the data puller
    puller = DataPuller(output_dir="data", rate_limit_delay=0.1)
    
    try:
        # Choose method:
        # 1. Pull by time period (scans backwards until 1000 consecutive old items)
        # puller.pull_data_for_period(months=6)
        
        # 2. Pull recent items with time filter (recommended for 6 months)
        puller.pull_recent_items(count=50000)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user!")
        puller._print_stats()
    except Exception as e:
        print(f"\nError: {e}")
        puller._print_stats()
    finally:
        puller.close()
    
    print("\nDone!")


if __name__ == "__main__":
    main()

