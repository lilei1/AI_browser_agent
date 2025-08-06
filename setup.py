#!/usr/bin/env python3
"""
Setup script for Yahoo Finance AI Browser Agent
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False

    if sys.version_info < (3, 8):
        print(f"⚠️  Python version: {sys.version.split()[0]} (3.8+ recommended)")
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = ["data", "cache", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✅ Created: {directory}/")
    
    return True

def setup_environment():
    """Set up environment file"""
    print("⚙️  Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        # Copy example to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your OpenAI API key")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No .env.example found, creating basic .env file")
        with open(env_file, 'w') as f:
            f.write("""# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Browser Configuration
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=yahoo_finance_agent.log
""")
        print("✅ Created basic .env file")
    
    return True

def check_chrome():
    """Check if Chrome is available"""
    print("🌐 Checking Chrome browser...")
    
    try:
        # Try to find Chrome executable
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
            "/usr/bin/google-chrome",  # Linux
            "/usr/bin/chromium-browser",  # Linux (Chromium)
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",  # Windows
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",  # Windows
        ]
        
        chrome_found = False
        for path in chrome_paths:
            if os.path.exists(path):
                print(f"✅ Found Chrome: {path}")
                chrome_found = True
                break
        
        if not chrome_found:
            print("⚠️  Chrome not found in standard locations")
            print("   Chrome will be downloaded automatically when first used")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Could not check Chrome: {e}")
        return True

def run_test():
    """Run a basic test"""
    print("🧪 Running basic test...")
    
    try:
        # Import test
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from src.yahoo_finance_agent.utils.helpers import validate_symbol, format_currency
        
        # Test basic functions
        assert validate_symbol("AAPL") == True
        assert format_currency(123.45) == "$123.45"
        
        print("✅ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Yahoo Finance AI Browser Agent Setup")
    print("=" * 50)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install dependencies
    if success and not install_dependencies():
        success = False
    
    # Create directories
    if success and not create_directories():
        success = False
    
    # Setup environment
    if success and not setup_environment():
        success = False
    
    # Check Chrome
    if success and not check_chrome():
        success = False
    
    # Run basic test
    if success and not run_test():
        success = False
    
    print("\n" + "=" * 50)
    
    if success:
        print("✅ Setup completed successfully!")
        print("\n🎯 Next steps:")
        print("1. Edit .env file with your OpenAI API key (optional)")
        print("2. Run the demo: python demo.py")
        print("3. Try the CLI: python main.py extract --symbol AAPL")
        print("4. Check examples: python examples/basic_usage.py")
        print("\n📚 Documentation:")
        print("• README.md - Complete guide")
        print("• docs/API_REFERENCE.md - API documentation")
        print("• examples/ - Usage examples")
    else:
        print("❌ Setup failed!")
        print("Please check the errors above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
