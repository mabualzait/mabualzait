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

def fetch_future_forem_posts(username, max_posts=5):
    """Fetch latest posts from Future Forem API"""
    try:
        # Future Forem API endpoint
        api_url = f"https://future.forem.com/api/articles?username={username}&per_page={max_posts}"
        
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        articles = response.json()
        posts = []
        
        for article in articles:
            post = {
                'title': article['title'],
                'url': article['url'],
                'published': article['published_at'],
                'platform': 'Future Forem'
            }
            posts.append(post)
        
        return posts
    except Exception as e:
        print(f"Error fetching Future Forem posts: {e}")
        return []

def fetch_udemy_courses():
    """Fetch Udemy courses information"""
    try:
        # Note: This would require Udemy API credentials
        # For now, we'll return static data that can be updated manually
        # In production, you'd use: https://www.udemy.com/instructor-api/v1/taught-courses/courses/
        
        courses = [
            {
                'title': 'Design Patterns in Software Development',
                'url': 'https://www.udemy.com/user/malik-abualzait/',
                'students': 12500,
                'rating': 4.8,
                'duration': '1h 43min'
            },
            {
                'title': 'Mobile App Development with Android',
                'url': 'https://www.udemy.com/user/malik-abualzait/',
                'students': 8500,
                'rating': 4.7,
                'duration': '2h 15min'
            },
            {
                'title': 'Enterprise Software Architecture',
                'url': 'https://www.udemy.com/user/malik-abualzait/',
                'students': 2231,
                'rating': 4.9,
                'duration': '3h 30min'
            }
        ]
        
        return courses
    except Exception as e:
        print(f"Error fetching Udemy courses: {e}")
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
    if post['platform'] == 'Medium':
        platform_emoji = "📝"
    elif post['platform'] == 'Dev.to':
        platform_emoji = "💻"
    elif post['platform'] == 'Future Forem':
        platform_emoji = "🚀"
    else:
        platform_emoji = "📄"
    
    return f"{index}. {platform_emoji} **[{post['title']}]({post['url']})** - {formatted_date}"

def update_readme(posts, udemy_courses, max_display=8):
    """Update README.md with latest blog posts and Udemy courses"""
    try:
        # Read current README
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Separate posts by platform
        devto_posts = [post for post in posts if post['platform'] == 'Dev.to']
        future_posts = [post for post in posts if post['platform'] == 'Future Forem']
        medium_posts = [post for post in posts if post['platform'] == 'Medium']
        
        # Sort each platform's posts by date
        devto_posts = sort_posts_by_date(devto_posts)[:max_display//2]
        future_posts = sort_posts_by_date(future_posts)[:max_display//2]
        
        # Generate markdown for Dev.to posts
        devto_markdown = "<!-- DEVTO-POST-LIST:START -->\n"
        if devto_posts:
            for i, post in enumerate(devto_posts, 1):
                devto_markdown += f"{i}. **[{post['title']}]({post['url']})** - {format_date(post['published'])}\n"
        else:
            devto_markdown += "**No recent Dev.to articles found** - Check back soon for new content!\n"
        devto_markdown += "<!-- DEVTO-POST-LIST:END -->"
        
        # Generate markdown for Future Forem posts
        future_markdown = "<!-- FUTURE-POST-LIST:START -->\n"
        if future_posts:
            for i, post in enumerate(future_posts, 1):
                future_markdown += f"{i}. **[{post['title']}]({post['url']})** - {format_date(post['published'])}\n"
        else:
            future_markdown += "**No recent Future Forem articles found** - Check back soon for new content!\n"
        future_markdown += "<!-- FUTURE-POST-LIST:END -->"
        
        # Generate markdown for Udemy courses
        udemy_markdown = "<!-- UDEMY-COURSES:START -->\n"
        if udemy_courses:
            total_students = sum(course['students'] for course in udemy_courses)
            udemy_markdown += f"**Total Students Enrolled: {total_students:,}**\n\n"
            for i, course in enumerate(udemy_courses, 1):
                udemy_markdown += f"{i}. **[{course['title']}]({course['url']})**\n"
                udemy_markdown += f"   - 👥 {course['students']:,} students • ⭐ {course['rating']}/5.0 • ⏱️ {course['duration']}\n\n"
        else:
            udemy_markdown += "**No courses found** - Check back soon for new courses!\n"
        udemy_markdown += "<!-- UDEMY-COURSES:END -->"
        
        # Replace Dev.to posts section
        devto_pattern = r'<!-- DEVTO-POST-LIST:START -->.*?<!-- DEVTO-POST-LIST:END -->'
        if re.search(devto_pattern, content, re.DOTALL):
            content = re.sub(devto_pattern, devto_markdown, content, flags=re.DOTALL)
        
        # Replace Future Forem posts section
        future_pattern = r'<!-- FUTURE-POST-LIST:START -->.*?<!-- FUTURE-POST-LIST:END -->'
        if re.search(future_pattern, content, re.DOTALL):
            content = re.sub(future_pattern, future_markdown, content, flags=re.DOTALL)
        
        # Replace Udemy courses section
        udemy_pattern = r'<!-- UDEMY-COURSES:START -->.*?<!-- UDEMY-COURSES:END -->'
        if re.search(udemy_pattern, content, re.DOTALL):
            content = re.sub(udemy_pattern, udemy_markdown, content, flags=re.DOTALL)
        
        # Write updated README
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Successfully updated README with {len(devto_posts)} Dev.to posts, {len(future_posts)} Future Forem posts, and {len(udemy_courses)} Udemy courses")
        return True
        
    except Exception as e:
        print(f"❌ Error updating README: {e}")
        return False

def format_date(date_string):
    """Format date string for display"""
    try:
        pub_date = date_parser.parse(date_string)
        return pub_date.strftime("%b %d, %Y")
    except:
        return "Recently"

def main():
    """Main function to fetch posts and update README"""
    print("🚀 Starting blog post update...")
    
    # Get usernames from environment variables
    medium_username = os.getenv('MEDIUM_USERNAME', 'mabualzait')
    devto_username = os.getenv('DEVTO_USERNAME', 'mabualzait')
    future_username = os.getenv('FUTURE_USERNAME', 'mabualzait')
    
    print(f"📝 Fetching Medium posts for @{medium_username}")
    medium_posts = fetch_medium_posts(medium_username)
    print(f"   Found {len(medium_posts)} Medium posts")
    
    print(f"💻 Fetching Dev.to posts for @{devto_username}")
    devto_posts = fetch_devto_posts(devto_username)
    print(f"   Found {len(devto_posts)} Dev.to posts")
    
    print(f"🚀 Fetching Future Forem posts for @{future_username}")
    future_posts = fetch_future_forem_posts(future_username)
    print(f"   Found {len(future_posts)} Future Forem posts")
    
    print(f"🎓 Fetching Udemy courses...")
    udemy_courses = fetch_udemy_courses()
    print(f"   Found {len(udemy_courses)} Udemy courses")
    
    # Combine all posts
    all_posts = medium_posts + devto_posts + future_posts
    print(f"📊 Total posts found: {len(all_posts)}")
    
    # Update README
    if update_readme(all_posts, udemy_courses):
        print("✅ Blog post update completed successfully!")
    else:
        print("❌ Blog post update failed!")
        exit(1)

if __name__ == "__main__":
    main()
