"""
Visualization Module
Creates charts and graphs for sentiment analysis results
"""
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List
import os
from datetime import datetime


class SentimentVisualizer:
    """Creates visualizations for sentiment analysis data"""
    
    def __init__(self, output_dir: str = "static/images/charts"):
        """
        Initialize visualizer
        
        Args:
            output_dir: Directory to save chart images
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)
    
    def create_sentiment_pie_chart(self, summary: Dict, filename: str = None) -> str:
        """
        Create pie chart showing sentiment distribution
        
        Args:
            summary: Dictionary with sentiment counts
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to saved image
        """
        if not filename:
            filename = f"sentiment_pie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Extract data
        labels = ['Positive', 'Negative', 'Neutral']
        sizes = [
            summary.get('positive_count', 0),
            summary.get('negative_count', 0),
            summary.get('neutral_count', 0)
        ]
        colors = ['#4CAF50', '#F44336', '#9E9E9E']
        explode = (0.1, 0.1, 0)
        
        # Create pie chart
        fig, ax = plt.subplots()
        ax.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=90)
        ax.axis('equal')
        
        plt.title('Sentiment Distribution', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_sentiment_bar_chart(self, summary: Dict, filename: str = None) -> str:
        """
        Create bar chart showing sentiment counts
        
        Args:
            summary: Dictionary with sentiment counts
            filename: Output filename
        
        Returns:
            Path to saved image
        """
        if not filename:
            filename = f"sentiment_bar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Prepare data
        sentiments = ['Positive', 'Negative', 'Neutral']
        counts = [
            summary.get('positive_count', 0),
            summary.get('negative_count', 0),
            summary.get('neutral_count', 0)
        ]
        colors = ['#4CAF50', '#F44336', '#9E9E9E']
        
        # Create bar chart
        fig, ax = plt.subplots()
        bars = ax.bar(sentiments, counts, color=colors, alpha=0.7, edgecolor='black')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax.set_title('Sentiment Analysis Results', fontsize=16, fontweight='bold')
        ax.set_ylim(0, max(counts) * 1.15 if max(counts) > 0 else 10)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_score_distribution(self, df: pd.DataFrame, filename: str = None) -> str:
        """
        Create histogram of compound sentiment scores
        
        Args:
            df: DataFrame with sentiment scores
            filename: Output filename
        
        Returns:
            Path to saved image
        """
        if not filename:
            filename = f"score_dist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        filepath = os.path.join(self.output_dir, filename)
        
        if df.empty or 'avg_compound' not in df.columns:
            # Create empty plot
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', fontsize=14)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            return filepath
        
        # Create histogram
        fig, ax = plt.subplots()
        
        n, bins, patches = ax.hist(df['avg_compound'], bins=30, 
                                   edgecolor='black', alpha=0.7)
        
        # Color bars based on sentiment
        for i, patch in enumerate(patches):
            if bins[i] < -0.05:
                patch.set_facecolor('#F44336')  # Red for negative
            elif bins[i] > 0.05:
                patch.set_facecolor('#4CAF50')  # Green for positive
            else:
                patch.set_facecolor('#9E9E9E')  # Gray for neutral
        
        ax.axvline(x=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        ax.set_xlabel('Compound Sentiment Score', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title('Distribution of Sentiment Scores', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_time_series(self, df: pd.DataFrame, date_column: str = 'created_utc',
                          filename: str = None) -> str:
        """
        Create time series plot of sentiment over time
        
        Args:
            df: DataFrame with sentiment scores and dates
            date_column: Name of the date column
            filename: Output filename
        
        Returns:
            Path to saved image
        """
        if not filename:
            filename = f"time_series_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        filepath = os.path.join(self.output_dir, filename)
        
        if df.empty or date_column not in df.columns or 'avg_compound' not in df.columns:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, 'Insufficient data for time series', 
                   ha='center', va='center', fontsize=14)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            return filepath
        
        # Ensure date column is datetime
        df_copy = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df_copy[date_column]):
            df_copy[date_column] = pd.to_datetime(df_copy[date_column], errors='coerce')
        
        # Remove rows with invalid dates
        df_copy = df_copy.dropna(subset=[date_column])
        
        if df_copy.empty:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, 'No valid dates for time series', 
                   ha='center', va='center', fontsize=14)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            return filepath
        
        # Sort by date
        df_copy = df_copy.sort_values(date_column)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot compound score over time
        ax.plot(df_copy[date_column], df_copy['avg_compound'], 
               marker='o', linestyle='-', linewidth=2, markersize=4, alpha=0.7)
        
        # Add horizontal reference lines
        ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        ax.axhline(y=0.05, color='green', linestyle=':', linewidth=1, alpha=0.3)
        ax.axhline(y=-0.05, color='red', linestyle=':', linewidth=1, alpha=0.3)
        
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Compound Sentiment Score', fontsize=12, fontweight='bold')
        ax.set_title('Sentiment Trends Over Time', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_source_comparison(self, df: pd.DataFrame, filename: str = None) -> str:
        """
        Create bar chart comparing sentiment across different sources
        
        Args:
            df: DataFrame with sentiment scores and source column
            filename: Output filename
        
        Returns:
            Path to saved image
        """
        if not filename:
            filename = f"source_comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        filepath = os.path.join(self.output_dir, filename)
        
        if df.empty or 'source' not in df.columns or 'avg_compound' not in df.columns:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, 'Insufficient data for source comparison', 
                   ha='center', va='center', fontsize=14)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            return filepath
        
        # Calculate average sentiment by source
        source_sentiment = df.groupby('source')['avg_compound'].mean().sort_values()
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = ['#F44336' if x < 0 else '#4CAF50' for x in source_sentiment.values]
        bars = ax.barh(source_sentiment.index, source_sentiment.values, color=colors, alpha=0.7)
        
        ax.axvline(x=0, color='black', linestyle='--', linewidth=1)
        ax.set_xlabel('Average Compound Sentiment', fontsize=12, fontweight='bold')
        ax.set_title('Sentiment by Source', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_all_visualizations(self, df: pd.DataFrame, summary: Dict) -> Dict[str, str]:
        """
        Create all visualizations
        
        Args:
            df: DataFrame with sentiment data
            summary: Summary statistics dictionary
        
        Returns:
            Dictionary mapping visualization names to file paths
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        visualizations = {}
        
        try:
            visualizations['pie_chart'] = self.create_sentiment_pie_chart(
                summary, f"pie_{timestamp}.png"
            )
        except Exception as e:
            print(f"Error creating pie chart: {e}")
        
        try:
            visualizations['bar_chart'] = self.create_sentiment_bar_chart(
                summary, f"bar_{timestamp}.png"
            )
        except Exception as e:
            print(f"Error creating bar chart: {e}")
        
        try:
            visualizations['distribution'] = self.create_score_distribution(
                df, f"dist_{timestamp}.png"
            )
        except Exception as e:
            print(f"Error creating distribution chart: {e}")
        
        try:
            visualizations['time_series'] = self.create_time_series(
                df, filename=f"timeseries_{timestamp}.png"
            )
        except Exception as e:
            print(f"Error creating time series: {e}")
        
        try:
            visualizations['source_comparison'] = self.create_source_comparison(
                df, f"sources_{timestamp}.png"
            )
        except Exception as e:
            print(f"Error creating source comparison: {e}")
        
        return visualizations


def main():
    """Test the visualizer"""
    # Create sample data
    summary = {
        'positive_count': 45,
        'negative_count': 25,
        'neutral_count': 30
    }
    
    visualizer = SentimentVisualizer()
    
    print("Creating test visualizations...")
    pie_path = visualizer.create_sentiment_pie_chart(summary)
    bar_path = visualizer.create_sentiment_bar_chart(summary)
    
    print(f"Pie chart saved to: {pie_path}")
    print(f"Bar chart saved to: {bar_path}")


if __name__ == "__main__":
    main()
