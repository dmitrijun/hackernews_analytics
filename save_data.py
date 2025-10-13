"""
Script to pull and save Hacker News data to JSON files
"""

import json
import os
from datetime import datetime
from hackernews import HackerNewsClient


def save_to_json(data, filename):
    """Save data to a JSON file"""
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved: {filepath}")


def item_to_dict(item):
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


def user_to_dict(user):
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


def main():
    """Pull and save Hacker News data"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with HackerNewsClient() as client:
        print("Pulling Hacker News data via Firebase API...")
        print("=" * 80)
        
        # Save top stories
        print("\n1. Fetching top stories...")
        top_story_ids = client.get_top_stories(limit=50)
        top_stories = [item_to_dict(client.get_item(id)) for id in top_story_ids]
        save_to_json(top_stories, f'top_stories_{timestamp}.json')
        
        # Save new stories
        print("\n2. Fetching new stories...")
        new_story_ids = client.get_new_stories(limit=50)
        new_stories = [item_to_dict(client.get_item(id)) for id in new_story_ids]
        save_to_json(new_stories, f'new_stories_{timestamp}.json')
        
        # Save best stories
        print("\n3. Fetching best stories...")
        best_story_ids = client.get_best_stories(limit=50)
        best_stories = [item_to_dict(client.get_item(id)) for id in best_story_ids]
        save_to_json(best_stories, f'best_stories_{timestamp}.json')
        
        # Save Ask HN stories
        print("\n4. Fetching Ask HN stories...")
        ask_story_ids = client.get_ask_stories(limit=30)
        ask_stories = [item_to_dict(client.get_item(id)) for id in ask_story_ids]
        save_to_json(ask_stories, f'ask_stories_{timestamp}.json')
        
        # Save Show HN stories
        print("\n5. Fetching Show HN stories...")
        show_story_ids = client.get_show_stories(limit=30)
        show_stories = [item_to_dict(client.get_item(id)) for id in show_story_ids]
        save_to_json(show_stories, f'show_stories_{timestamp}.json')
        
        # Save job stories
        print("\n6. Fetching job stories...")
        job_story_ids = client.get_job_stories(limit=30)
        job_stories = [item_to_dict(client.get_item(id)) for id in job_story_ids]
        save_to_json(job_stories, f'job_stories_{timestamp}.json')
        
        # Save updates
        print("\n7. Fetching recent updates...")
        updates = client.get_updates()
        updates_data = {
            'items': updates.items,
            'profiles': updates.profiles
        }
        save_to_json(updates_data, f'updates_{timestamp}.json')
        
        # Save system info
        print("\n8. Fetching system info...")
        max_id = client.get_max_item_id()
        system_info = {
            'timestamp': timestamp,
            'max_item_id': max_id,
            'date': datetime.now().isoformat()
        }
        save_to_json(system_info, f'system_info_{timestamp}.json')
        
        # Save sample users
        print("\n9. Fetching sample user profiles...")
        sample_users = ['pg', 'dang', 'jl']
        users_data = {}
        for username in sample_users:
            user = client.get_user(username)
            users_data[username] = user_to_dict(user)
        save_to_json(users_data, f'sample_users_{timestamp}.json')
        
        print("\n" + "=" * 80)
        print("Data pull completed successfully!")
        print(f"All files saved in 'data/' directory with timestamp: {timestamp}")


if __name__ == "__main__":
    main()
