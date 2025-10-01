#!/usr/bin/env python3
"""
Script to fetch latest blog posts from Medium and Dev.to and update README.md
"""

import os
import re
import requests
import feedparser
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import json

def fetch_medium_posts(username, max_posts=5):
    """Fetch latest posts from Medium RSS feed"""
    try:
        # Medium RSS feed URL
        rss_url = f"https://medium.com/@{username}/feed"
        
        # Parse RSS feed
        feed = feedparser.parse(rss_url)
        
        posts = []
        for entry in feed.entries[:max_posts]:
            # Extract post data
            post = {
                'title': entry.title,
                'url': entry.link,
                'published': entry.published,
                'platform': 'Medium'
            }
            posts.append(post)
        
        return posts
    except Exception as e:
        print(f"Error fetching Medium posts: {e}")
        return []

def fetch_devto_posts(username, max_posts=5):
    """Fetch latest posts from Dev.to API"""
    try:
        # Dev.to API endpoint
        api_url = f"https://dev.to/api/articles?username={username}"
        
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        articles = response.json()
        posts = []
        
        for article in articles[:max_posts]:
            post = {
                'title': article['title'],
                'url': article['url'],
                'published': article['published_at'],
                'platform': 'Dev.to'
            }
            posts.append(post)
        
        return posts
    except Exception as e:
        print(f"Error fetching Dev.to posts: {e}")
        return []

def sort_posts_by_date(posts):
    """Sort posts by publication date (newest first)"""
    def get_date(post):
        try:
            return date_parser.parse(post['published'])
        except:
            return datetime.min
    
    return sorted(posts, key=get_date, reverse=True)

def format_post_markdown(post, index):
    """Format a single post as markdown"""
    # Parse and format date
    try:
        pub_date = date_parser.parse(post['published'])
        formatted_date = pub_date.strftime("%b %d, %Y")
    except:
        formatted_date = "Recently"
    
    # Get platform emoji
    platform_emoji = "📝" if post['platform'] == 'Medium' else "💻"
    
    return f"{index}. {platform_emoji} **[{post['title']}]({post['url']})** - {formatted_date}"

def update_readme(posts, max_display=8):
    """Update README.md with latest blog posts"""
    try:
        # Read current README
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Sort posts by date
        sorted_posts = sort_posts_by_date(posts)
        
        # Take only the latest posts
        latest_posts = sorted_posts[:max_display]
        
        # Generate markdown for posts
        if latest_posts:
            posts_markdown = "<!-- BLOG-POST-LIST:START -->\n"
            for i, post in enumerate(latest_posts, 1):
                posts_markdown += format_post_markdown(post, i) + "\n"
            posts_markdown += "<!-- BLOG-POST-LIST:END -->"
        else:
            posts_markdown = """<!-- BLOG-POST-LIST:START -->
- 📝 **No recent articles found** - Check back soon for new content!
<!-- BLOG-POST-LIST:END -->"""
        
        # Replace the blog posts section
        pattern = r'<!-- BLOG-POST-LIST:START -->.*?<!-- BLOG-POST-LIST:END -->'
        replacement = posts_markdown
        
        if re.search(pattern, content, re.DOTALL):
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            # If no existing section, add it after the About Me section
            about_section_end = content.find('---', content.find('## 🚀 About Me'))
            if about_section_end != -1:
                next_section_start = content.find('##', about_section_end)
                if next_section_start != -1:
                    insert_position = next_section_start
                else:
                    insert_position = len(content)
            else:
                insert_position = len(content)
            
            new_content = content[:insert_position] + f"\n\n## ✍️ Latest Articles\n\n{posts_markdown}\n\n---\n\n" + content[insert_position:]
        
        # Write updated README
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Successfully updated README with {len(latest_posts)} blog posts")
        return True
        
    except Exception as e:
        print(f"❌ Error updating README: {e}")
        return False

def main():
    """Main function to fetch posts and update README"""
    print("🚀 Starting blog post update...")
    
    # Get usernames from environment variables
    medium_username = os.getenv('MEDIUM_USERNAME', 'mabualzait')
    devto_username = os.getenv('DEVTO_USERNAME', 'mabualzait')
    
    print(f"📝 Fetching Medium posts for @{medium_username}")
    medium_posts = fetch_medium_posts(medium_username)
    print(f"   Found {len(medium_posts)} Medium posts")
    
    print(f"💻 Fetching Dev.to posts for @{devto_username}")
    devto_posts = fetch_devto_posts(devto_username)
    print(f"   Found {len(devto_posts)} Dev.to posts")
    
    # Combine all posts
    all_posts = medium_posts + devto_posts
    print(f"📊 Total posts found: {len(all_posts)}")
    
    # Update README
    if update_readme(all_posts):
        print("✅ Blog post update completed successfully!")
    else:
        print("❌ Blog post update failed!")
        exit(1)

if __name__ == "__main__":
    main()
