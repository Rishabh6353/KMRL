#!/usr/bin/env python3
"""
Intelligent Document Processing System - Simplified Startup
This script installs dependencies and starts the application with graceful fallbacks.
"""

import os
import sys
import subprocess
import importlib.util

def check_package(package_name):
    """Check if a package is installed."""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_package(package_name):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def install_core_dependencies():
    """Install core dependencies with fallbacks."""
    print("🚀 Setting up Intelligent Document Processing System...")
    
    # Core packages that are essential
    core_packages = [
        "flask>=2.3.0",
        "flask-cors>=4.0.0", 
        "flask-sqlalchemy>=3.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "pandas>=1.5.0",
        "numpy>=1.24.0",
        "pytesseract>=0.3.10"
    ]
    
    # Try to install Pillow with different approaches
    pillow_alternatives = [
        "Pillow>=9.0.0",
        "Pillow>=8.0.0", 
        "Pillow"
    ]
    
    print("📦 Installing core packages...")
    for package in core_packages:
        print(f"  Installing {package}...")
        if not install_package(package):
            print(f"  ⚠️  Failed to install {package}")
    
    print("🖼️  Installing Pillow (image processing)...")
    pillow_installed = False
    for pillow_version in pillow_alternatives:
        if install_package(pillow_version):
            pillow_installed = True
            break
    
    if not pillow_installed:
        print("  ⚠️  Pillow installation failed. Image processing may not work.")
    
    # Optional ML packages
    optional_packages = {
        "scikit-learn>=1.3.0": "Machine learning classification",
        "opencv-python-headless": "Advanced image processing", 
        "spacy>=3.6.0": "Advanced NLP features",
        "nltk>=3.8.0": "Text processing",
        "pymongo>=4.0.0": "MongoDB support",
        "PyMuPDF>=1.22.0": "PDF processing"
    }
    
    print("🤖 Installing optional ML packages...")
    for package, description in optional_packages.items():
        print(f"  Installing {package} ({description})...")
        if not install_package(package):
            print(f"  ⚠️  Failed to install {package} - {description} will be disabled")

def download_nltk_data():
    """Download required NLTK data."""
    try:
        import nltk
        print("📚 Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('maxent_ne_chunker', quiet=True)
        nltk.download('words', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("  ✅ NLTK data downloaded successfully")
    except ImportError:
        print("  ⚠️  NLTK not available - basic text processing only")

def download_spacy_models():
    """Download spaCy language models."""
    try:
        import spacy
        print("🧠 Downloading spaCy models...")
        models = ["en_core_web_sm"]
        for model in models:
            try:
                subprocess.check_call([sys.executable, "-m", "spacy", "download", model])
                print(f"  ✅ Downloaded {model}")
            except subprocess.CalledProcessError:
                print(f"  ⚠️  Failed to download {model}")
    except ImportError:
        print("  ⚠️  spaCy not available - advanced NLP features disabled")

def setup_directories():
    """Create necessary directories."""
    directories = [
        "uploads",
        "models", 
        "logs",
        "backend/temp"
    ]
    
    print("📁 Creating directories...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ Created {directory}")

def create_basic_env():
    """Create a basic .env file if it doesn't exist."""
    env_file = ".env"
    if not os.path.exists(env_file):
        print("⚙️  Creating basic .env file...")
        with open(env_file, "w") as f:
            f.write("""# Basic Configuration for Development
DATABASE_URL=sqlite:///documents.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=104857600
ALLOWED_EXTENSIONS=pdf,png,jpg,jpeg,tiff,gif,doc,docx,txt,csv,xls,xlsx
SECRET_KEY=development_secret_key_change_in_production
DEBUG=True
FLASK_ENV=development
""")
        print("  ✅ Created .env file")

def main():
    """Main setup function."""
    print("=" * 60)
    print("🔧 INTELLIGENT DOCUMENT PROCESSING SETUP")
    print("=" * 60)
    
    # Setup
    install_core_dependencies()
    setup_directories()
    create_basic_env()
    download_nltk_data()
    download_spacy_models()
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print("\n🚀 Starting the application...")
    print("   Open your browser to: http://localhost:5000")
    print("\n💡 Tips:")
    print("   - Upload documents via the web interface")
    print("   - Check the logs/ directory for troubleshooting")
    print("   - Edit .env file for custom configuration")
    print("\n⚠️  Note: Some advanced features may be disabled if optional packages failed to install.")
    print("\n" + "=" * 60)
    
    # Start the application
    try:
        from app_simple import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except ImportError:
        print("❌ Failed to start application. Check the logs for errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()