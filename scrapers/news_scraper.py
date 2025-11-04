"""
Google News Scraper Module
Adapted from Jose-Sabater/marketeer repository
Scrapes Google News for articles containing specific keywords
"""
from urllib.request import Request, urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import requests
from typing import List, Dict, Tuple
from datetime import datetime


class NewsScraper:
    """Scrapes Google News based on keywords"""
    
    def __init__(self):
        """Initialize the news scraper"""
        self.root = "https://google.com"
        self.headers = {"User-Agent": "Mozilla/5.0"}
    
    def search_news(self, keyword: str, max_pages: int = 3) -> List[Dict]:
        """
        Scrape Google News articles based on a keyword
        
        Args:
            keyword: The keyword to search for
            max_pages: Maximum number of pages to scrape (default: 3)
        
        Returns:
            List of dictionaries containing news article data
        """
        print(f"Started scraping Google News for '{keyword}'...")
        news_list = []
        
        # Build Google News search URL with proper encoding
        encoded_keyword = quote_plus(keyword)
        link = f"https://www.google.com/search?q={encoded_keyword}&tbm=nws"
        
        try:
            for page in range(max_pages):
                page_news, next_link = self._scrape_page(link)
                news_list.extend(page_news)
                
                if not next_link:
                    break
                    
                link = next_link
                
        except Exception as e:
            print(f"Error during news scraping: {e}")
        
        print(f"Scraped {len(news_list)} news articles")
        return news_list
    
    def _scrape_page(self, link: str) -> Tuple[List[Dict], str]:
        """
        Scrape a single page of Google News results
        
        Args:
            link: URL of the page to scrape
        
        Returns:
            Tuple of (news_list, next_page_link)
        """
        news_list = []
        next_link = ""
        
        try:
            req = Request(link, headers=self.headers)
            webpage = urlopen(req, timeout=10).read()
            
            soup = BeautifulSoup(webpage, "html.parser", from_encoding="utf-8")
            
            # Try multiple selectors for Google News articles
            # Google frequently changes these class names
            articles = soup.find_all("div", attrs={"class": "SoaBEf"})
            
            if not articles:
                articles = soup.find_all("div", attrs={"class": "Gx5Zad"})
            
            if not articles:
                # Try finding by data-hveid attribute (more stable)
                articles = soup.find_all("div", attrs={"data-hveid": True})
                articles = [a for a in articles if a.find("a", href=True)]
            
            if not articles:
                # Try finding all divs with links (broader search)
                articles = soup.find_all("div", class_=lambda x: x and "xuvV6b" in x)
            
            print(f"Found {len(articles)} article containers on page")
            
            for item in articles:
                news_dict = {}
                
                try:
                    # Extract link - try multiple methods
                    link_tag = item.find("a", href=True)
                    if link_tag:
                        raw_link = link_tag["href"]
                        if "/url?q=" in raw_link:
                            article_link = raw_link.split("/url?q=")[1].split("&sa=")[0]
                        elif raw_link.startswith("http"):
                            article_link = raw_link
                        else:
                            article_link = self.root + raw_link
                        news_dict["link"] = article_link
                    
                    # Extract title - try multiple methods
                    title_tag = item.find("div", attrs={"role": "heading"})
                    if not title_tag:
                        title_tag = item.find("div", attrs={"class": "BNeawe vvjwJb AP7Wnd"})
                    if not title_tag:
                        # Try finding any heading-like element
                        title_tag = item.find(["h1", "h2", "h3", "h4"])
                    if not title_tag and link_tag:
                        # Use link text as fallback
                        title_tag = link_tag
                    
                    if title_tag:
                        title = title_tag.get_text().strip()
                        news_dict["title"] = title.replace(",", "")
                        news_dict["text"] = title  # Add text field for sentiment analysis
                    
                    # Extract description
                    desc_tag = item.find("div", attrs={"class": "BNeawe s3v9rd AP7Wnd"})
                    if desc_tag:
                        full_text = desc_tag.get_text()
                        
                        # Try to extract time and description
                        if "..." in full_text:
                            parts = full_text.split("...")
                            description = parts[0].strip()
                            time_info = parts[1].strip() if len(parts) > 1 else ""
                        else:
                            description = full_text
                            time_info = ""
                        
                        news_dict["description"] = description.replace(",", "")
                        news_dict["time"] = time_info
                    
                    # Add source and timestamp
                    news_dict["source"] = "google_news"
                    news_dict["scraped_at"] = datetime.now()
                    
                    # Only add if we have at least a title and link
                    # Filter out navigation elements like "Past hour", "Past 24 hours"
                    if ("title" in news_dict and news_dict["title"] and 
                        "link" in news_dict and 
                        "http" in news_dict["link"] and
                        not any(time_word in news_dict["title"].lower() 
                               for time_word in ["past hour", "past 24", "past week", "all results"])):
                        news_list.append(news_dict)
                
                except UnicodeEncodeError as e:
                    print(f"Unicode error: {e}")
                    continue
                except IndexError as e:
                    print(f"Index error: {e}")
                    continue
                except AttributeError as e:
                    print(f"Attribute error: {e}")
                    continue
                except Exception as e:
                    print(f"Unexpected error processing article: {e}")
                    continue
            
            # Try to find next page link
            try:
                next_button = soup.find("a", attrs={"aria-label": "Next page"})
                if not next_button:
                    next_button = soup.find("a", attrs={"id": "pnnext"})
                
                if next_button and next_button.get("href"):
                    next_link = self.root + next_button["href"]
            except Exception as e:
                print(f"Could not find next page: {e}")
        
        except requests.exceptions.Timeout:
            print("Request timed out while scraping news")
        except requests.exceptions.ConnectionError:
            print("Connection error while scraping news")
        except Exception as e:
            print(f"Error scraping page: {e}")
        
        return news_list, next_link
    
    def search_news_simple(self, keyword: str, count: int = 20) -> List[Dict]:
        """
        Simplified news search that returns a specific number of articles
        
        Args:
            keyword: Keyword to search for
            count: Number of articles to retrieve
        
        Returns:
            List of news article dictionaries
        """
        all_news = self.search_news(keyword, max_pages=3)
        return all_news[:count] if all_news else []


def main():
    """Test the news scraper"""
    scraper = NewsScraper()
    
    # Test search
    print("Testing Google News scraper...")
    articles = scraper.search_news("artificial intelligence", max_pages=1)
    
    print(f"\nFound {len(articles)} articles")
    for article in articles[:3]:
        print(f"\nTitle: {article.get('title', 'N/A')}")
        print(f"Description: {article.get('description', 'N/A')[:100]}...")
        print(f"Link: {article.get('link', 'N/A')}")


if __name__ == "__main__":
    main()
