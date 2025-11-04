"""
Core OSINT Analyzer Engine
Orchestrates data collection, sentiment analysis, and reporting
"""
from scrapers.reddit_scraper import RedditScraper
from scrapers.news_scraper import NewsScraper
from scrapers.rss_scraper import RSSFeedScraper
from sentiment.analyzer import SentimentAnalyzer
from visualization.charts import SentimentVisualizer
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
import json


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj) if not np.isnan(obj) and not np.isinf(obj) else None
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        return super().default(obj)


class OSINTAnalyzer:
    """Main OSINT analyzer that coordinates all components"""
    
    def __init__(self):
        """Initialize all components"""
        print("Initializing OSINT Analyzer...")
        self.reddit_scraper = RedditScraper()
        self.news_scraper = NewsScraper()
        self.rss_scraper = RSSFeedScraper()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.visualizer = SentimentVisualizer()
        
        self.results = None
        self.summary = None
    
    def collect_data(self, keyword: str, sources: List[str] = None, 
                    reddit_limit: int = 50, news_pages: int = 2,
                    rss_limit: int = 20) -> List[Dict]:
        """
        Collect data from multiple sources
        
        Args:
            keyword: Keyword or hashtag to search for
            sources: List of sources to use ('reddit', 'news', 'rss')
                    If None, uses all available sources
            reddit_limit: Max Reddit posts to collect
            news_pages: Max news pages to scrape
            rss_limit: Max RSS articles per feed
        
        Returns:
            Combined list of collected data
        """
        if sources is None:
            sources = ['reddit', 'news', 'rss']
        
        all_data = []
        
        print(f"\n{'='*60}")
        print(f"Collecting data for keyword: '{keyword}'")
        print(f"{'='*60}\n")
        
        # Collect from Reddit
        if 'reddit' in sources:
            try:
                print("📱 Collecting Reddit posts...")
                reddit_posts = self.reddit_scraper.search_posts(
                    keyword, 
                    limit=reddit_limit
                )
                all_data.extend(reddit_posts)
                print(f"✓ Collected {len(reddit_posts)} Reddit posts")
            except Exception as e:
                print(f"✗ Error collecting Reddit data: {e}")
        
        # Collect from Google News
        if 'news' in sources:
            try:
                print("\n📰 Collecting Google News articles...")
                news_articles = self.news_scraper.search_news(
                    keyword,
                    max_pages=news_pages
                )
                all_data.extend(news_articles)
                print(f"✓ Collected {len(news_articles)} news articles")
            except Exception as e:
                print(f"✗ Error collecting news data: {e}")
        
        # Collect from RSS feeds
        if 'rss' in sources:
            try:
                print("\n📡 Collecting RSS feed articles...")
                rss_articles = self.rss_scraper.search_default_feeds(
                    keyword,
                    limit_per_feed=rss_limit
                )
                all_data.extend(rss_articles)
                print(f"✓ Collected {len(rss_articles)} RSS articles")
            except Exception as e:
                print(f"✗ Error collecting RSS data: {e}")
        
        print(f"\n{'='*60}")
        print(f"Total items collected: {len(all_data)}")
        print(f"{'='*60}\n")
        
        return all_data
    
    def analyze(self, keyword: str, sources: List[str] = None,
               reddit_limit: int = 50, news_pages: int = 2,
               rss_limit: int = 20) -> Tuple[pd.DataFrame, Dict]:
        """
        Complete analysis pipeline: collect data and analyze sentiment
        
        Args:
            keyword: Keyword to search for
            sources: Sources to use
            reddit_limit: Reddit post limit
            news_pages: News pages to scrape
            rss_limit: RSS articles per feed
        
        Returns:
            Tuple of (DataFrame with results, summary dictionary)
        """
        # Collect data
        data = self.collect_data(
            keyword,
            sources=sources,
            reddit_limit=reddit_limit,
            news_pages=news_pages,
            rss_limit=rss_limit
        )
        
        if not data:
            print("⚠️  No data collected. Analysis cannot proceed.")
            return pd.DataFrame(), {}
        
        # Analyze sentiment
        print("\n🔍 Analyzing sentiment...")
        
        # Determine text fields based on data structure
        df = pd.DataFrame(data)
        
        # Standardize field names
        if 'description' in df.columns:
            df['text'] = df['description']
        elif 'selftext' in df.columns:
            df['text'] = df['selftext']
        
        # Analyze sentiment
        results_df = self.sentiment_analyzer.analyze_data_with_sentiment(
            data,
            text_field='text' if 'text' in df.columns else 'description',
            title_field='title'
        )
        
        # Get summary
        summary = self.sentiment_analyzer.get_sentiment_summary(results_df)
        
        # Add metadata
        summary['keyword'] = keyword
        summary['timestamp'] = datetime.now().isoformat()
        summary['sources_used'] = sources if sources else ['reddit', 'news', 'rss']
        
        print(f"✓ Sentiment analysis complete")
        print(f"\nResults Summary:")
        print(f"  • Total items analyzed: {summary['total_items']}")
        print(f"  • Positive: {summary['positive_count']} ({summary.get('positive_percent', 0):.1f}%)")
        print(f"  • Negative: {summary['negative_count']} ({summary.get('negative_percent', 0):.1f}%)")
        print(f"  • Neutral: {summary['neutral_count']} ({summary.get('neutral_percent', 0):.1f}%)")
        print(f"  • Average compound score: {summary['avg_compound']:.3f}")
        
        self.results = results_df
        self.summary = summary
        
        return results_df, summary
    
    def generate_visualizations(self, results_df: pd.DataFrame = None,
                               summary: Dict = None) -> Dict[str, str]:
        """
        Generate all visualizations
        
        Args:
            results_df: Results DataFrame (uses self.results if None)
            summary: Summary dictionary (uses self.summary if None)
        
        Returns:
            Dictionary of visualization file paths
        """
        if results_df is None:
            results_df = self.results
        if summary is None:
            summary = self.summary
        
        if results_df is None or summary is None:
            print("⚠️  No analysis results available for visualization")
            return {}
        
        print("\n📊 Generating visualizations...")
        
        visualizations = self.visualizer.create_all_visualizations(
            results_df,
            summary
        )
        
        print(f"✓ Generated {len(visualizations)} visualizations")
        
        return visualizations
    
    def save_results(self, filename: str = None, include_raw: bool = False):
        """
        Save analysis results to files
        
        Args:
            filename: Base filename (without extension)
            include_raw: Whether to include raw data DataFrame
        """
        if self.results is None or self.summary is None:
            print("⚠️  No results to save")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"osint_analysis_{timestamp}"
        
        # Save summary as JSON
        summary_path = f"reports/{filename}_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(self.summary, f, indent=2, cls=NumpyEncoder)
        print(f"✓ Summary saved to: {summary_path}")
        
        # Save detailed results as CSV
        if include_raw:
            csv_path = f"reports/{filename}_detailed.csv"
            self.results.to_csv(csv_path, index=False)
            print(f"✓ Detailed results saved to: {csv_path}")
    
    def get_top_items(self, n: int = 10, sort_by: str = 'score') -> pd.DataFrame:
        """
        Get top N items from results
        
        Args:
            n: Number of items to return
            sort_by: Column to sort by ('score', 'avg_compound', etc.)
        
        Returns:
            DataFrame with top N items
        """
        if self.results is None or self.results.empty:
            return pd.DataFrame()
        
        if sort_by not in self.results.columns:
            sort_by = 'avg_compound'
        
        return self.results.nlargest(n, sort_by)
    
    def get_trending_topics(self) -> List[str]:
        """
        Extract trending topics from analyzed data
        
        Returns:
            List of trending topics/keywords
        """
        if self.results is None or self.results.empty:
            return []
        
        # Simple implementation: extract from titles
        if 'title' in self.results.columns:
            titles = ' '.join(self.results['title'].dropna().astype(str))
            # You could add NLP processing here for better topic extraction
            return []
        
        return []


def main():
    """Test the OSINT analyzer"""
    analyzer = OSINTAnalyzer()
    
    # Test analysis
    keyword = "artificial intelligence"
    print(f"\nTesting OSINT Analyzer with keyword: '{keyword}'\n")
    
    results_df, summary = analyzer.analyze(
        keyword,
        sources=['news'],  # Start with just news for testing
        reddit_limit=10,
        news_pages=1,
        rss_limit=5
    )
    
    # Generate visualizations
    if not results_df.empty:
        visualizations = analyzer.generate_visualizations()
        
        # Save results
        analyzer.save_results(include_raw=True)
        
        print("\n✓ Analysis complete!")
    else:
        print("\n⚠️  No results to analyze")


if __name__ == "__main__":
    main()
