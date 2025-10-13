"""
Example usage of the HackerNews Firebase API client
"""

from hackernews import HackerNewsClient
from hackernews.utils import format_timestamp, clean_html, get_item_url


def main():
    # Create a client instance
    with HackerNewsClient() as client:
        print("=" * 80)
        print("HACKER NEWS FIREBASE API CLIENT - EXAMPLES")
        print("=" * 80)
        
        # Example 1: Get top stories
        print("\n1. TOP 5 STORIES:")
        print("-" * 80)
        top_stories = client.get_top_stories_with_details(limit=5)
        for i, story in enumerate(top_stories, 1):
            if story:
                print(f"\n{i}. {story.title}")
                print(f"   By: {story.by} | Score: {story.score} | Comments: {story.descendants or 0}")
                print(f"   URL: {story.url or get_item_url(story.id)}")
                print(f"   Posted: {format_timestamp(story.time)}")
        
        # Example 2: Get a specific user
        print("\n\n2. USER PROFILE:")
        print("-" * 80)
        user = client.get_user("pg")  # Paul Graham
        if user:
            print(f"Username: {user.id}")
            print(f"Karma: {user.karma}")
            print(f"Created: {format_timestamp(user.created)}")
            print(f"Submitted items: {len(user.submitted)}")
            if user.about:
                print(f"About: {clean_html(user.about)[:100]}...")
        
        # Example 3: Get a specific item
        print("\n\n3. SPECIFIC ITEM DETAILS:")
        print("-" * 80)
        item = client.get_item(8863)  # Famous Dropbox story
        if item:
            print(f"Title: {item.title}")
            print(f"Type: {item.type}")
            print(f"By: {item.by}")
            print(f"Score: {item.score}")
            print(f"Comments: {len(item.kids) if item.kids else 0}")
            print(f"URL: {item.url}")
        
        # Example 4: Get Ask HN stories
        print("\n\n4. ASK HN STORIES (Top 3):")
        print("-" * 80)
        ask_story_ids = client.get_ask_stories(limit=3)
        ask_stories = client.get_items(ask_story_ids)
        for i, story in enumerate(ask_stories, 1):
            if story:
                print(f"\n{i}. {story.title}")
                print(f"   By: {story.by} | Score: {story.score}")
        
        # Example 5: Get Show HN stories
        print("\n\n5. SHOW HN STORIES (Top 3):")
        print("-" * 80)
        show_story_ids = client.get_show_stories(limit=3)
        show_stories = client.get_items(show_story_ids)
        for i, story in enumerate(show_stories, 1):
            if story:
                print(f"\n{i}. {story.title}")
                print(f"   By: {story.by} | Score: {story.score}")
        
        # Example 6: Get job postings
        print("\n\n6. JOB POSTINGS (Top 3):")
        print("-" * 80)
        job_ids = client.get_job_stories(limit=3)
        jobs = client.get_items(job_ids)
        for i, job in enumerate(jobs, 1):
            if job:
                print(f"\n{i}. {job.title}")
                print(f"   By: {job.by}")
        
        # Example 7: Get max item ID
        print("\n\n7. SYSTEM INFO:")
        print("-" * 80)
        max_id = client.get_max_item_id()
        print(f"Current max item ID: {max_id}")
        
        # Example 8: Get recent updates
        print("\n\n8. RECENT UPDATES:")
        print("-" * 80)
        updates = client.get_updates()
        print(f"Recently changed items: {len(updates.items)}")
        print(f"Recently changed profiles: {len(updates.profiles)}")
        if updates.items:
            print(f"Sample changed item IDs: {updates.items[:5]}")
        if updates.profiles:
            print(f"Sample changed profiles: {updates.profiles[:5]}")
        
        # Example 9: Get comments for a story
        print("\n\n9. COMMENTS FOR A STORY:")
        print("-" * 80)
        if top_stories and top_stories[0]:
            story = top_stories[0]
            comments = client.get_comments_for_item(story.id, recursive=False)
            print(f"Story: {story.title}")
            print(f"Number of top-level comments: {len(comments)}")
            if comments:
                print(f"\nFirst comment by {comments[0].by}:")
                comment_text = clean_html(comments[0].text) if comments[0].text else ""
                print(f"{comment_text[:200]}...")
        
        print("\n" + "=" * 80)
        print("Done!")


if __name__ == "__main__":
    main()
