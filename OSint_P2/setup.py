"""
Setup and initialization script for OSINT Analyzer
Downloads required NLTK data and creates necessary directories
"""
import os
import nltk
from pathlib import Path


def setup_directories():
    """Create necessary directories"""
    directories = [
        'static/images/charts',
        'reports',
        'data'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def download_nltk_data():
    """Download required NLTK data"""
    print("\nDownloading NLTK data...")
    
    try:
        nltk.download('vader_lexicon', quiet=True)
        print("✓ Downloaded VADER lexicon")
    except Exception as e:
        print(f"✗ Error downloading VADER lexicon: {e}")
    
    try:
        nltk.download('punkt', quiet=True)
        print("✓ Downloaded punkt tokenizer")
    except Exception as e:
        print(f"✗ Error downloading punkt: {e}")
    
    try:
        nltk.download('averaged_perceptron_tagger', quiet=True)
        print("✓ Downloaded POS tagger")
    except Exception as e:
        print(f"✗ Error downloading POS tagger: {e}")


def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("\n⚠️  .env file not found")
        print("Creating .env from .env.example...")
        
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✓ Created .env file")
            print("\n⚠️  Please edit .env and add your Reddit API credentials")
            print("   (Reddit is optional - tool works with News and RSS without it)")
        else:
            print("✗ .env.example not found")
    else:
        print("\n✓ .env file exists")


def verify_dependencies():
    """Verify that key dependencies are installed"""
    print("\nVerifying dependencies...")
    
    dependencies = [
        ('flask', 'Flask'),
        ('pandas', 'Pandas'),
        ('matplotlib', 'Matplotlib'),
        ('bs4', 'BeautifulSoup'),
        ('praw', 'PRAW'),
        ('feedparser', 'Feedparser'),
        ('textblob', 'TextBlob'),
        ('vaderSentiment', 'VADER Sentiment')
    ]
    
    missing = []
    
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✓ {name} is installed")
        except ImportError:
            print(f"✗ {name} is NOT installed")
            missing.append(module)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
    else:
        print("\n✓ All dependencies are installed")


def main():
    """Run setup"""
    print("="*70)
    print("OSINT SOCIAL MEDIA ANALYZER - SETUP")
    print("="*70)
    
    # Create directories
    print("\n1. Setting up directories...")
    setup_directories()
    
    # Check environment file
    print("\n2. Checking environment configuration...")
    check_env_file()
    
    # Download NLTK data
    print("\n3. Downloading required NLTK data...")
    download_nltk_data()
    
    # Verify dependencies
    print("\n4. Verifying dependencies...")
    verify_dependencies()
    
    print("\n" + "="*70)
    print("SETUP COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Edit .env file with your Reddit API credentials (optional)")
    print("2. Run the web app: python app.py")
    print("3. Open browser to: http://localhost:5000")
    print("\nFor command-line usage: python osint_analyzer.py")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
