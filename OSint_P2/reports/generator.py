"""
Report Generator Module
Creates comprehensive HTML and text reports for analysis results
"""
import pandas as pd
import numpy as np
from typing import Dict
from datetime import datetime
import json
import os


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


def safe_convert_for_json(df, num_rows=10):
    """
    Convert DataFrame to JSON-safe format
    
    Args:
        df: pandas DataFrame
        num_rows: number of rows to convert
    
    Returns:
        List of dictionaries safe for JSON
    """
    if df.empty:
        return []
    
    subset = df.head(num_rows).copy()
    
    # Convert datetime columns to ISO format strings
    for col in subset.columns:
        if pd.api.types.is_datetime64_any_dtype(subset[col]):
            subset[col] = subset[col].apply(lambda x: x.isoformat() if pd.notna(x) else None)
        elif pd.api.types.is_numeric_dtype(subset[col]):
            subset[col] = subset[col].replace({np.nan: None})
    
    return subset.to_dict('records')


class ReportGenerator:
    """Generates comprehensive reports from analysis results"""
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize report generator
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_text_report(self, summary: Dict, filename: str = None) -> str:
        """
        Generate a text-based summary report
        
        Args:
            summary: Summary dictionary from analysis
            filename: Output filename
        
        Returns:
            Path to generated report
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("OSINT SOCIAL MEDIA SENTIMENT ANALYSIS REPORT\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Keyword/Topic: {summary.get('keyword', 'N/A')}\n")
            f.write(f"Analysis Date: {summary.get('timestamp', 'N/A')}\n")
            f.write(f"Data Sources: {', '.join(summary.get('sources_used', []))}\n")
            f.write("\n" + "-"*70 + "\n")
            f.write("SUMMARY STATISTICS\n")
            f.write("-"*70 + "\n\n")
            
            f.write(f"Total Items Analyzed: {summary.get('total_items', 0)}\n\n")
            
            f.write("Sentiment Distribution:\n")
            f.write(f"  • Positive: {summary.get('positive_count', 0)} ")
            f.write(f"({summary.get('positive_percent', 0):.1f}%)\n")
            f.write(f"  • Negative: {summary.get('negative_count', 0)} ")
            f.write(f"({summary.get('negative_percent', 0):.1f}%)\n")
            f.write(f"  • Neutral:  {summary.get('neutral_count', 0)} ")
            f.write(f"({summary.get('neutral_percent', 0):.1f}%)\n\n")
            
            f.write("Average Sentiment Scores:\n")
            f.write(f"  • Positive: {summary.get('avg_positive', 0):.3f}\n")
            f.write(f"  • Neutral:  {summary.get('avg_neutral', 0):.3f}\n")
            f.write(f"  • Negative: {summary.get('avg_negative', 0):.3f}\n")
            f.write(f"  • Compound: {summary.get('avg_compound', 0):.3f}\n\n")
            
            # Overall sentiment
            compound = summary.get('avg_compound', 0)
            if compound >= 0.05:
                overall = "POSITIVE"
            elif compound <= -0.05:
                overall = "NEGATIVE"
            else:
                overall = "NEUTRAL"
            
            f.write(f"Overall Sentiment: {overall}\n\n")
            
            f.write("-"*70 + "\n")
            f.write("KEY FINDINGS\n")
            f.write("-"*70 + "\n\n")
            
            # Determine dominant sentiment
            pos_count = summary.get('positive_count', 0)
            neg_count = summary.get('negative_count', 0)
            neu_count = summary.get('neutral_count', 0)
            
            if pos_count > neg_count and pos_count > neu_count:
                f.write(f"1. The predominant sentiment is POSITIVE ({summary.get('positive_percent', 0):.1f}%)\n")
            elif neg_count > pos_count and neg_count > neu_count:
                f.write(f"1. The predominant sentiment is NEGATIVE ({summary.get('negative_percent', 0):.1f}%)\n")
            else:
                f.write(f"1. The predominant sentiment is NEUTRAL ({summary.get('neutral_percent', 0):.1f}%)\n")
            
            f.write(f"2. Average compound sentiment score: {compound:.3f}\n")
            
            if compound > 0.5:
                f.write("3. Strong positive sentiment detected in the data\n")
            elif compound < -0.5:
                f.write("3. Strong negative sentiment detected in the data\n")
            else:
                f.write("3. Moderate sentiment levels observed\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*70 + "\n")
        
        return filepath
    
    def generate_html_report(self, summary: Dict, visualizations: Dict = None,
                           filename: str = None) -> str:
        """
        Generate an HTML report
        
        Args:
            summary: Summary dictionary
            visualizations: Dictionary of visualization file paths
            filename: Output filename
        
        Returns:
            Path to generated HTML report
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{timestamp}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Determine overall sentiment
        compound = summary.get('avg_compound', 0)
        if compound >= 0.05:
            overall = "Positive"
            badge_class = "success"
        elif compound <= -0.05:
            overall = "Negative"
            badge_class = "danger"
        else:
            overall = "Neutral"
            badge_class = "secondary"
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT Analysis Report - {summary.get('keyword', 'N/A')}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; }}
        .stat-box {{ background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; }}
        .chart-container {{ text-align: center; margin: 2rem 0; }}
        @media print {{ .no-print {{ display: none; }} }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>OSINT Sentiment Analysis Report</h1>
            <p class="lead">Keyword: {summary.get('keyword', 'N/A')}</p>
            <p>Generated: {summary.get('timestamp', 'N/A')}</p>
        </div>
    </div>

    <div class="container my-5">
        <div class="row">
            <div class="col-md-12">
                <h2>Executive Summary</h2>
                <div class="stat-box">
                    <div class="row">
                        <div class="col-md-3">
                            <h3>{summary.get('total_items', 0)}</h3>
                            <p class="text-muted">Total Items</p>
                        </div>
                        <div class="col-md-3">
                            <h3 class="text-success">{summary.get('positive_count', 0)}</h3>
                            <p class="text-muted">Positive ({summary.get('positive_percent', 0):.1f}%)</p>
                        </div>
                        <div class="col-md-3">
                            <h3 class="text-danger">{summary.get('negative_count', 0)}</h3>
                            <p class="text-muted">Negative ({summary.get('negative_percent', 0):.1f}%)</p>
                        </div>
                        <div class="col-md-3">
                            <h3 class="text-secondary">{summary.get('neutral_count', 0)}</h3>
                            <p class="text-muted">Neutral ({summary.get('neutral_percent', 0):.1f}%)</p>
                        </div>
                    </div>
                </div>

                <div class="stat-box">
                    <h4>Overall Sentiment</h4>
                    <span class="badge bg-{badge_class} fs-5">{overall}</span>
                    <p class="mt-2">Average Compound Score: <strong>{compound:.3f}</strong></p>
                </div>

                <h3 class="mt-4">Detailed Metrics</h3>
                <table class="table table-bordered">
                    <thead class="table-light">
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Average Positive Score</td>
                            <td>{summary.get('avg_positive', 0):.3f}</td>
                        </tr>
                        <tr>
                            <td>Average Neutral Score</td>
                            <td>{summary.get('avg_neutral', 0):.3f}</td>
                        </tr>
                        <tr>
                            <td>Average Negative Score</td>
                            <td>{summary.get('avg_negative', 0):.3f}</td>
                        </tr>
                        <tr>
                            <td>Average Compound Score</td>
                            <td><strong>{summary.get('avg_compound', 0):.3f}</strong></td>
                        </tr>
                    </tbody>
                </table>

                <h3 class="mt-4">Data Sources</h3>
                <p>{', '.join(summary.get('sources_used', []))}</p>

                <div class="mt-5 no-print">
                    <button onclick="window.print()" class="btn btn-primary">Print Report</button>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-light py-3 mt-5">
        <div class="container text-center">
            <small class="text-muted">Generated by OSINT Social Media Analyzer</small>
        </div>
    </footer>
</body>
</html>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def generate_json_report(self, summary: Dict, results_df: pd.DataFrame = None,
                           filename: str = None) -> str:
        """
        Generate a JSON report
        
        Args:
            summary: Summary dictionary
            results_df: Optional DataFrame with detailed results
            filename: Output filename
        
        Returns:
            Path to generated JSON file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        report_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'keyword': summary.get('keyword'),
                'sources': summary.get('sources_used', [])
            },
            'summary': summary,
        }
        
        if results_df is not None and not results_df.empty:
            report_data['sample_data'] = safe_convert_for_json(results_df, num_rows=10)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, cls=NumpyEncoder)
        
        return filepath


def main():
    """Test the report generator"""
    # Sample data
    summary = {
        'keyword': 'Test Keyword',
        'timestamp': datetime.now().isoformat(),
        'sources_used': ['reddit', 'news'],
        'total_items': 100,
        'positive_count': 45,
        'negative_count': 25,
        'neutral_count': 30,
        'positive_percent': 45.0,
        'negative_percent': 25.0,
        'neutral_percent': 30.0,
        'avg_compound': 0.15,
        'avg_positive': 0.45,
        'avg_neutral': 0.30,
        'avg_negative': 0.25
    }
    
    generator = ReportGenerator()
    
    print("Generating test reports...")
    text_report = generator.generate_text_report(summary)
    html_report = generator.generate_html_report(summary)
    json_report = generator.generate_json_report(summary)
    
    print(f"Text report: {text_report}")
    print(f"HTML report: {html_report}")
    print(f"JSON report: {json_report}")


if __name__ == "__main__":
    main()
