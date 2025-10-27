"""
Reddit Scraper Module
Collects posts and comments from Reddit based on keywords/hashtags
"""
import praw
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Dict, Optional

load_dotenv()


class RedditScraper:
    """Scrapes Reddit for posts containing specific keywords"""
    
    def __init__(self):
        """Initialize Reddit API client with credentials"""
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'OSINT_Analyzer/1.0')
            )
            # Test connection
            self.reddit.user.me()
        except Exception as e:
            print(f"Warning: Reddit API initialization failed: {e}")
            print("Reddit scraping will not be available. Please check your credentials.")
            self.reddit = None
    
    def search_posts(self, keyword: str, limit: int = 100, 
                     subreddit: str = 'all', time_filter: str = 'week') -> List[Dict]:
        """
        Search Reddit posts containing the keyword
        
        Args:
            keyword: The keyword or hashtag to search for
            limit: Maximum number of posts to retrieve
            subreddit: Subreddit to search in (default: 'all')
            time_filter: Time period ('hour', 'day', 'week', 'month', 'year', 'all')
        
        Returns:
            List of dictionaries containing post data
        """
        if not self.reddit:
            print("Reddit API not initialized. Skipping Reddit scraping.")
            return []
        
        posts = []
        
        try:
            subreddit_obj = self.reddit.subreddit(subreddit)
            
            # Search for posts
            for submission in subreddit_obj.search(keyword, limit=limit, time_filter=time_filter):
                try:
                    post_data = {
                        'source': 'reddit',
                        'title': submission.title,
                        'text': submission.selftext if submission.selftext else '',
                        'author': str(submission.author) if submission.author else '[deleted]',
                        'score': submission.score,
                        'num_comments': submission.num_comments,
                        'created_utc': datetime.fromtimestamp(submission.created_utc),
                        'url': f"https://reddit.com{submission.permalink}",
                        'subreddit': str(submission.subreddit),
                        'upvote_ratio': submission.upvote_ratio
                    }
                    posts.append(post_data)
                except Exception as e:
                    print(f"Error processing post: {e}")
                    continue
                    
        except praw.exceptions.PRAWException as e:
            print(f"Reddit API Error: {e}")
            print("This might be due to API rate limits or invalid credentials.")
        except Exception as e:
            print(f"Unexpected error while scraping Reddit: {e}")
        
        return posts
    
    def get_top_posts(self, keyword: str, subreddit: str = 'all', 
                      limit: int = 50, time_filter: str = 'week') -> List[Dict]:
        """
        Get top posts containing the keyword
        
        Args:
            keyword: The keyword to search for
            subreddit: Subreddit to search in
            limit: Maximum number of posts
            time_filter: Time period filter
        
        Returns:
            List of post dictionaries
        """
        if not self.reddit:
            return []
        
        posts = []
        
        try:
            subreddit_obj = self.reddit.subreddit(subreddit)
            
            for submission in subreddit_obj.top(limit=limit, time_filter=time_filter):
                # Check if keyword is in title or selftext
                if keyword.lower() in submission.title.lower() or \
                   (submission.selftext and keyword.lower() in submission.selftext.lower()):
                    try:
                        post_data = {
                            'source': 'reddit',
                            'title': submission.title,
                            'text': submission.selftext if submission.selftext else '',
                            'author': str(submission.author) if submission.author else '[deleted]',
                            'score': submission.score,
                            'num_comments': submission.num_comments,
                            'created_utc': datetime.fromtimestamp(submission.created_utc),
                            'url': f"https://reddit.com{submission.permalink}",
                            'subreddit': str(submission.subreddit),
                            'upvote_ratio': submission.upvote_ratio
                        }
                        posts.append(post_data)
                    except Exception as e:
                        print(f"Error processing post: {e}")
                        continue
                        
        except praw.exceptions.PRAWException as e:
            print(f"Reddit API Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        return posts
    
    def get_post_comments(self, post_url: str, limit: int = 50) -> List[Dict]:
        """
        Get comments from a specific post
        
        Args:
            post_url: URL of the Reddit post
            limit: Maximum number of comments
        
        Returns:
            List of comment dictionaries
        """
        if not self.reddit:
            return []
        
        comments = []
        
        try:
            submission = self.reddit.submission(url=post_url)
            submission.comments.replace_more(limit=0)
            
            for comment in submission.comments.list()[:limit]:
                try:
                    comment_data = {
                        'source': 'reddit_comment',
                        'text': comment.body,
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'score': comment.score,
                        'created_utc': datetime.fromtimestamp(comment.created_utc),
                        'parent_post': submission.title
                    }
                    comments.append(comment_data)
                except Exception as e:
                    print(f"Error processing comment: {e}")
                    continue
                    
        except praw.exceptions.PRAWException as e:
            print(f"Reddit API Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        return comments


def main():
    """Test the Reddit scraper"""
    scraper = RedditScraper()
    
    # Test search
    print("Testing Reddit search...")
    posts = scraper.search_posts("python", limit=5)
    
    print(f"\nFound {len(posts)} posts")
    for post in posts[:3]:
        print(f"\nTitle: {post['title']}")
        print(f"Score: {post['score']}")
        print(f"Subreddit: {post['subreddit']}")


if __name__ == "__main__":
    main()
