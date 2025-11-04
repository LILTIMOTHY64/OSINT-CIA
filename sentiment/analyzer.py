"""
Sentiment Analysis Module
Uses TextBlob and VADER to analyze sentiment of text data
Adapted from Jose-Sabater/marketeer repository
"""
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from typing import Dict, List, Tuple
import numpy as np


class SentimentAnalyzer:
    """Analyzes sentiment using multiple methods"""
    
    def __init__(self):
        """Initialize sentiment analyzers"""
        self.vader = SentimentIntensityAnalyzer()
    
    def analyze_vader(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using VADER
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment scores
        """
        if not text or not isinstance(text, str):
            return {'pos': 0.0, 'neu': 1.0, 'neg': 0.0, 'compound': 0.0}
        
        try:
            scores = self.vader.polarity_scores(text)
            return scores
        except Exception as e:
            print(f"Error in VADER analysis: {e}")
            return {'pos': 0.0, 'neu': 1.0, 'neg': 0.0, 'compound': 0.0}
    
    def analyze_textblob(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using TextBlob
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with polarity and subjectivity scores
        """
        if not text or not isinstance(text, str):
            return {'polarity': 0.0, 'subjectivity': 0.0}
        
        try:
            blob = TextBlob(text)
            return {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        except Exception as e:
            print(f"Error in TextBlob analysis: {e}")
            return {'polarity': 0.0, 'subjectivity': 0.0}
    
    def analyze_combined(self, text: str) -> Dict[str, float]:
        """
        Analyze using both VADER and TextBlob
        
        Args:
            text: Text to analyze
        
        Returns:
            Combined sentiment scores
        """
        vader_scores = self.analyze_vader(text)
        textblob_scores = self.analyze_textblob(text)
        
        # Combine scores
        combined = {
            'vader_positive': vader_scores['pos'],
            'vader_neutral': vader_scores['neu'],
            'vader_negative': vader_scores['neg'],
            'vader_compound': vader_scores['compound'],
            'textblob_polarity': textblob_scores['polarity'],
            'textblob_subjectivity': textblob_scores['subjectivity']
        }
        
        return combined
    
    def categorize_sentiment(self, compound_score: float) -> str:
        """
        Categorize sentiment based on VADER compound score
        
        Args:
            compound_score: VADER compound score (-1 to 1)
        
        Returns:
            Sentiment category: 'positive', 'negative', or 'neutral'
        """
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    def analyze_batch(self, texts: List[str]) -> pd.DataFrame:
        """
        Analyze sentiment for a batch of texts
        
        Args:
            texts: List of text strings
        
        Returns:
            DataFrame with sentiment scores
        """
        results = []
        
        for text in texts:
            if not text:
                continue
            
            scores = self.analyze_combined(text)
            scores['text'] = text[:100]  # Store first 100 chars
            scores['sentiment'] = self.categorize_sentiment(scores['vader_compound'])
            results.append(scores)
        
        return pd.DataFrame(results)
    
    def analyze_data_with_sentiment(self, data: List[Dict], 
                                   text_field: str = 'text',
                                   title_field: str = 'title') -> pd.DataFrame:
        """
        Analyze sentiment for data with title and text fields
        
        Args:
            data: List of dictionaries containing text data
            text_field: Field name containing main text
            title_field: Field name containing title
        
        Returns:
            DataFrame with original data and sentiment scores
        """
        df = pd.DataFrame(data)
        
        if df.empty:
            return df
        
        # Analyze title if present
        if title_field in df.columns:
            print("Analyzing title sentiment...")
            title_sentiments = []
            for title in df[title_field]:
                if pd.isna(title):
                    title = ""
                scores = self.analyze_vader(str(title))
                title_sentiments.append(scores)
            
            title_df = pd.DataFrame(title_sentiments)
            df['title_positive'] = title_df['pos']
            df['title_neutral'] = title_df['neu']
            df['title_negative'] = title_df['neg']
            df['title_compound'] = title_df['compound']
        
        # Analyze text/description if present
        if text_field in df.columns:
            print("Analyzing text sentiment...")
            text_sentiments = []
            for text in df[text_field]:
                if pd.isna(text):
                    text = ""
                scores = self.analyze_vader(str(text))
                text_sentiments.append(scores)
            
            text_df = pd.DataFrame(text_sentiments)
            df['text_positive'] = text_df['pos']
            df['text_neutral'] = text_df['neu']
            df['text_negative'] = text_df['neg']
            df['text_compound'] = text_df['compound']
        
        # Calculate average sentiment if both title and text exist
        if title_field in df.columns and text_field in df.columns:
            df['avg_positive'] = (df['title_positive'] + df['text_positive']) / 2
            df['avg_neutral'] = (df['title_neutral'] + df['text_neutral']) / 2
            df['avg_negative'] = (df['title_negative'] + df['text_negative']) / 2
            df['avg_compound'] = (df['title_compound'] + df['text_compound']) / 2
        elif title_field in df.columns:
            df['avg_positive'] = df['title_positive']
            df['avg_neutral'] = df['title_neutral']
            df['avg_negative'] = df['title_negative']
            df['avg_compound'] = df['title_compound']
        elif text_field in df.columns:
            df['avg_positive'] = df['text_positive']
            df['avg_neutral'] = df['text_neutral']
            df['avg_negative'] = df['text_negative']
            df['avg_compound'] = df['text_compound']
        
        # Categorize overall sentiment
        if 'avg_compound' in df.columns:
            df['sentiment'] = df['avg_compound'].apply(self.categorize_sentiment)
        
        return df
    
    def get_sentiment_summary(self, df: pd.DataFrame) -> Dict:
        """
        Get summary statistics of sentiment analysis
        
        Args:
            df: DataFrame with sentiment scores
        
        Returns:
            Dictionary with summary statistics
        """
        if df.empty or 'avg_compound' not in df.columns:
            return {}
        
        summary = {
            'total_items': len(df),
            'positive_count': len(df[df['sentiment'] == 'positive']),
            'negative_count': len(df[df['sentiment'] == 'negative']),
            'neutral_count': len(df[df['sentiment'] == 'neutral']),
            'avg_compound': float(df['avg_compound'].mean()),
            'avg_positive': float(df['avg_positive'].mean()),
            'avg_neutral': float(df['avg_neutral'].mean()),
            'avg_negative': float(df['avg_negative'].mean()),
        }
        
        # Calculate percentages
        if summary['total_items'] > 0:
            summary['positive_percent'] = (summary['positive_count'] / summary['total_items']) * 100
            summary['negative_percent'] = (summary['negative_count'] / summary['total_items']) * 100
            summary['neutral_percent'] = (summary['neutral_count'] / summary['total_items']) * 100
        
        return summary


def main():
    """Test the sentiment analyzer"""
    analyzer = SentimentAnalyzer()
    
    # Test texts
    texts = [
        "This is absolutely amazing and wonderful!",
        "I hate this, it's terrible and awful.",
        "This is okay, nothing special."
    ]
    
    print("Testing Sentiment Analyzer...\n")
    for text in texts:
        print(f"Text: {text}")
        scores = analyzer.analyze_combined(text)
        sentiment = analyzer.categorize_sentiment(scores['vader_compound'])
        print(f"Sentiment: {sentiment}")
        print(f"VADER Compound: {scores['vader_compound']:.3f}")
        print(f"TextBlob Polarity: {scores['textblob_polarity']:.3f}\n")


if __name__ == "__main__":
    main()
