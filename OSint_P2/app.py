"""
Flask Web Application for OSINT Analyzer
"""
from flask import Flask, render_template, request, jsonify, send_from_directory, session
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
import os
from dotenv import load_dotenv
from osint_analyzer import OSINTAnalyzer
from datetime import datetime
import json
import pandas as pd
import numpy as np

load_dotenv()


class NumpyJSONProvider(DefaultJSONProvider):
    """Custom JSON provider that handles numpy and pandas types"""
    
    @staticmethod
    def default(obj):
        # Handle numpy types
        if isinstance(obj, (np.integer, np.floating)):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return [NumpyJSONProvider.default(x) if isinstance(x, (np.integer, np.floating)) 
                    else x for x in obj.tolist()]
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        # Handle pandas NA/NaT
        try:
            if pd.isna(obj):
                return None
        except (ValueError, TypeError):
            pass
        raise TypeError(f'Object of type {type(obj)} is not JSON serializable')


app = Flask(__name__)
app.json = NumpyJSONProvider(app)  # Use custom JSON provider
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
CORS(app)

# Global analyzer instance (in production, consider using sessions or caching)
analyzer = None


def dataframe_to_json_safe(df, num_rows=10):
    """
    Convert DataFrame to JSON-safe format, handling NaT and NaN values
    
    Args:
        df: pandas DataFrame
        num_rows: number of rows to return
    
    Returns:
        List of dictionaries safe for JSON serialization
    """
    if df.empty:
        return []
    
    # Get subset of rows
    subset = df.head(num_rows).copy()
    
    # Process all columns
    for col in subset.columns:
        if pd.api.types.is_datetime64_any_dtype(subset[col]):
            # Handle datetime columns
            subset[col] = subset[col].apply(lambda x: x.isoformat() if pd.notna(x) else None)
        elif pd.api.types.is_numeric_dtype(subset[col]):
            # Replace NaN/Inf with None for numeric columns
            subset[col] = subset[col].replace({np.nan: None, np.inf: None, -np.inf: None})
        else:
            # For object columns (strings, etc), replace NaN with None
            subset[col] = subset[col].apply(lambda x: None if pd.isna(x) else x)
    
    # Convert to dict and clean again to be absolutely sure
    records = subset.to_dict('records')
    return clean_dict_for_json(records)


def clean_dict_for_json(data):
    """
    Clean dictionary/list for JSON serialization, replacing NaN/inf with None
    
    Args:
        data: Dictionary, list, or value to clean
    
    Returns:
        Cleaned data safe for JSON serialization
    """
    if isinstance(data, dict):
        return {k: clean_dict_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_dict_for_json(item) for item in data]
    elif isinstance(data, np.ndarray):
        # Convert numpy array to list
        return [clean_dict_for_json(item) for item in data.tolist()]
    elif isinstance(data, (np.integer, np.floating)):
        # Handle numpy numeric types
        if np.isnan(data) or np.isinf(data):
            return None
        return float(data)
    elif isinstance(data, float):
        # Handle regular Python floats
        if np.isnan(data) or np.isinf(data):
            return None
        return data
    elif isinstance(data, pd.Timestamp):
        return data.isoformat()
    else:
        # Try pandas isna for other types
        try:
            if pd.isna(data):
                return None
        except (ValueError, TypeError):
            pass
        return data


@app.route('/')
def index():
    """Render home page"""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Perform OSINT analysis
    
    Expects JSON with:
    - keyword: str
    - sources: list of str (optional)
    - reddit_limit: int (optional)
    - news_pages: int (optional)
    - rss_limit: int (optional)
    """
    global analyzer
    
    try:
        data = request.get_json()
        
        keyword = data.get('keyword', '').strip()
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        # Get parameters
        sources = data.get('sources', ['reddit', 'news', 'rss'])
        reddit_limit = int(data.get('reddit_limit', 50))
        news_pages = int(data.get('news_pages', 2))
        rss_limit = int(data.get('rss_limit', 20))
        
        # Initialize analyzer
        analyzer = OSINTAnalyzer()
        
        # Perform analysis
        results_df, summary = analyzer.analyze(
            keyword=keyword,
            sources=sources,
            reddit_limit=reddit_limit,
            news_pages=news_pages,
            rss_limit=rss_limit
        )
        
        if results_df.empty:
            return jsonify({
                'error': 'No data found for the given keyword',
                'keyword': keyword
            }), 404
        
        # Generate visualizations
        visualizations = analyzer.generate_visualizations(results_df, summary)
        
        # Convert visualization paths to web-accessible URLs
        viz_urls = {}
        for name, path in visualizations.items():
            # Extract filename from path
            filename = os.path.basename(path)
            viz_urls[name] = f'/static/images/charts/{filename}'
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"analysis_{keyword.replace(' ', '_')}_{timestamp}"
        analyzer.save_results(filename, include_raw=True)
        
        # Store in session for results page
        session['last_analysis'] = {
            'keyword': keyword,
            'summary': clean_dict_for_json(summary),
            'visualizations': viz_urls,
            'timestamp': timestamp
        }
        
        # Return results - ensure everything is JSON-safe
        response_data = {
            'success': True,
            'keyword': keyword,
            'summary': clean_dict_for_json(summary),
            'visualizations': viz_urls,
            'top_items': dataframe_to_json_safe(results_df, num_rows=10)
        }
        
        # Double-check: clean the entire response
        response_data = clean_dict_for_json(response_data)
        
        return jsonify(response_data)
    
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/results')
def results():
    """Display analysis results page"""
    analysis_data = session.get('last_analysis')
    
    if not analysis_data:
        return render_template('error.html', 
                             message='No analysis results found. Please perform an analysis first.')
    
    return render_template('results.html', **analysis_data)


@app.route('/api/status')
def status():
    """Check system status"""
    global analyzer
    
    status_info = {
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'analyzer_initialized': analyzer is not None
    }
    
    return jsonify(status_info)


@app.route('/static/images/charts/<filename>')
def serve_chart(filename):
    """Serve chart images"""
    return send_from_directory('static/images/charts', filename)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error.html', 
                         message='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('error.html',
                         message='Internal server error. Please try again.'), 500


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static/images/charts', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # Run app
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
