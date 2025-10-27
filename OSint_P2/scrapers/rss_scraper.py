"""
RSS Feed Scraper Module
Adapted from Jose-Sabater/marketeer repository
Scrapes RSS feeds from public news sources
"""
import feedparser
from typing import List, Dict
from datetime import datetime
import time


class RSSFeedScraper:
    """Scrapes RSS feeds from various news sources"""
    
    def __init__(self):
        """Initialize RSS scraper with default news sources"""
        self.default_feeds = [
            "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
            "http://feeds.bbci.co.uk/news/rss.xml",
            "https://feeds.reuters.com/reuters/topNews",
            "https://www.theguardian.com/world/rss"
        ]
    
    def scrape_feed(self, feed_url: str, keyword: str = None, limit: int = 50) -> List[Dict]:
        """
        Scrape articles from a single RSS feed
        
        Args:
            feed_url: URL of the RSS feed
            keyword: Optional keyword to filter articles
            limit: Maximum number of articles to retrieve
        
        Returns:
            List of article dictionaries
        """
        articles = []
        
        try:
            print(f"Scraping RSS feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            # Check if feed was parsed successfully
            if feed.bozo:
                print(f"Warning: Feed may have parsing issues: {feed_url}")
            
            for entry in feed.entries[:limit]:
                try:
                    # Extract article data
                    article = {
                        'source': 'rss_feed',
                        'feed_url': feed_url,
                        'title': entry.get('title', ''),
                        'description': entry.get('summary', '').strip(),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'author': entry.get('author', 'Unknown'),
                        'scraped_at': datetime.now()
                    }
                    
                    # Try to parse publication date
                    if 'published_parsed' in entry and entry.published_parsed:
                        try:
                            # Ensure we have valid time components
                            time_tuple = entry.published_parsed[:6]
                            if all(isinstance(x, int) for x in time_tuple):
                                article['published_date'] = datetime(*time_tuple)
                            else:
                                article['published_date'] = None
                        except (ValueError, TypeError, AttributeError):
                            article['published_date'] = None
                    else:
                        article['published_date'] = None
                    
                    # Filter by keyword if provided
                    if keyword:
                        keyword_lower = keyword.lower()
                        title_lower = article['title'].lower()
                        desc_lower = article['description'].lower()
                        
                        if keyword_lower in title_lower or keyword_lower in desc_lower:
                            articles.append(article)
                    else:
                        articles.append(article)
                
                except Exception as e:
                    print(f"Error processing RSS entry: {e}")
                    continue
        
        except ConnectionError as e:
            print(f"Connection error while fetching RSS feed {feed_url}: {e}")
        except Exception as e:
            print(f"Error scraping RSS feed {feed_url}: {e}")
        
        return articles
    
    def scrape_multiple_feeds(self, feed_urls: List[str], keyword: str = None, 
                             limit_per_feed: int = 20) -> List[Dict]:
        """
        Scrape multiple RSS feeds
        
        Args:
            feed_urls: List of RSS feed URLs
            keyword: Optional keyword to filter articles
            limit_per_feed: Maximum articles per feed
        
        Returns:
            Combined list of articles from all feeds
        """
        all_articles = []
        
        for feed_url in feed_urls:
            try:
                articles = self.scrape_feed(feed_url, keyword, limit_per_feed)
                all_articles.extend(articles)
                
                # Be polite - add small delay between requests
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error scraping feed {feed_url}: {e}")
                continue
        
        print(f"Total articles scraped from RSS feeds: {len(all_articles)}")
        return all_articles
    
    def search_default_feeds(self, keyword: str, limit_per_feed: int = 20) -> List[Dict]:
        """
        Search default news feeds for keyword
        
        Args:
            keyword: Keyword to search for
            limit_per_feed: Maximum articles per feed
        
        Returns:
            List of matching articles
        """
        return self.scrape_multiple_feeds(self.default_feeds, keyword, limit_per_feed)
    
    def get_feed_info(self, feed_url: str) -> Dict:
        """
        Get information about an RSS feed
        
        Args:
            feed_url: URL of the RSS feed
        
        Returns:
            Dictionary with feed metadata
        """
        try:
            feed = feedparser.parse(feed_url)
            
            feed_info = {
                'title': feed.feed.get('title', 'Unknown'),
                'description': feed.feed.get('description', ''),
                'link': feed.feed.get('link', ''),
                'updated': feed.feed.get('updated', ''),
                'entry_count': len(feed.entries)
            }
            
            return feed_info
            
        except Exception as e:
            print(f"Error getting feed info for {feed_url}: {e}")
            return {}


def main():
    """Test the RSS scraper"""
    scraper = RSSFeedScraper()
    
    # Test single feed
    print("Testing RSS feed scraper...")
    articles = scraper.scrape_feed(
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        keyword="technology",
        limit=5
    )
    
    print(f"\nFound {len(articles)} articles matching keyword")
    for article in articles[:3]:
        print(f"\nTitle: {article['title']}")
        print(f"Published: {article.get('published', 'N/A')}")
        print(f"Link: {article['link']}")


if __name__ == "__main__":
    main()
