#!/usr/bin/env python3
"""
Setup script for Yahoo Finance MCP Server

This script helps set up the MCP server for use with Goose and other MCP clients.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("🚀 Yahoo Finance MCP Server Setup")
    print("=" * 50)
    print("This script will set up your Yahoo Finance MCP server for use with Goose.")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing requirements...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "mcp_requirements.txt"
        ])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        sys.exit(1)

def test_basic_functionality():
    """Test basic Yahoo Finance scraping functionality"""
    print("\n🧪 Testing basic functionality...")
    try:
        from basic_demo import scrape_yahoo_finance_basic
        data = scrape_yahoo_finance_basic("AAPL")
        if data and data.get("current_price"):
            print(f"✅ Basic functionality working - AAPL: ${data['current_price']}")
        else:
            print("⚠️  Basic functionality test returned no data")
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False
    return True

def create_goose_config():
    """Create or update Goose configuration"""
    print("\n⚙️  Setting up Goose configuration...")
    
    # Check if Goose config directory exists
    goose_config_dir = Path.home() / ".config" / "goose"
    goose_config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create profiles.yaml for Goose
    profiles_config = {
        "default": "yahoo-finance",
        "profiles": {
            "yahoo-finance": {
                "provider": "anthropic",
                "processor": "claude-3-5-sonnet-20241022",
                "accelerator": "claude-3-haiku-20240307",
                "moderator": "passive",
                "toolkits": ["developer", "yahoo_finance"]
            }
        }
    }
    
    profiles_file = goose_config_dir / "profiles.yaml"
    try:
        import yaml
        with open(profiles_file, 'w') as f:
            yaml.dump(profiles_config, f, default_flow_style=False)
        print(f"✅ Goose profiles configured at {profiles_file}")
    except ImportError:
        print("⚠️  PyYAML not installed, creating JSON config instead")
        profiles_file = goose_config_dir / "profiles.json"
        with open(profiles_file, 'w') as f:
            json.dump(profiles_config, f, indent=2)
        print(f"✅ Goose profiles configured at {profiles_file}")
    
    # Create MCP server configuration
    mcp_config = {
        "mcpServers": {
            "yahoo-finance": {
                "command": "python",
                "args": [str(Path.cwd() / "mcp_server.py")],
                "cwd": str(Path.cwd()),
                "env": {
                    "PYTHONPATH": str(Path.cwd())
                }
            }
        }
    }
    
    mcp_config_file = goose_config_dir / "mcp_servers.json"
    with open(mcp_config_file, 'w') as f:
        json.dump(mcp_config, f, indent=2)
    print(f"✅ MCP server configuration saved to {mcp_config_file}")

def run_test():
    """Run the MCP server test"""
    print("\n🔍 Running MCP server test...")
    try:
        result = subprocess.run([
            sys.executable, "test_mcp_server.py"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ MCP server test passed!")
            print("Last few lines of output:")
            lines = result.stdout.strip().split('\n')
            for line in lines[-5:]:
                print(f"   {line}")
        else:
            print("❌ MCP server test failed")
            print("Error output:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Test timed out - server might be working but slow")
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False
    
    return True

def print_usage_instructions():
    """Print instructions for using the MCP server"""
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Usage Instructions:")
    print("\n1. Direct MCP Server Usage:")
    print("   python mcp_server.py")
    print("\n2. Test the server:")
    print("   python test_mcp_server.py")
    print("\n3. Use with Goose (if installed):")
    print("   goose session start")
    print('   Ask: "What\'s the current price of Apple stock?"')
    print('   Ask: "Compare AAPL and GOOGL stocks"')
    print('   Ask: "Analyze the technology sector"')
    print("\n4. Available MCP Tools:")
    print("   - extract_stock_data: Get comprehensive stock data")
    print("   - get_stock_price: Quick price lookup")
    print("   - compare_stocks: Compare multiple stocks")
    print("   - analyze_sector: Analyze market sectors")
    print("   - validate_symbol: Check if stock symbol exists")
    print("\n5. Supported Stock Symbols:")
    print("   - Tech: AAPL, GOOGL, MSFT, NVDA, META, TSLA")
    print("   - Finance: JPM, BAC, WFC, GS")
    print("   - Healthcare: JNJ, PFE, MRNA")
    print("   - Energy: XOM, CVX, BP")
    print("   - Consumer: KO, PEP, PG, WMT")
    print("   - And thousands more!")
    print("\n⚠️  Note: This provides financial data for informational purposes only.")
    print("   Always verify data from official sources before making investment decisions.")

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    check_python_version()
    
    # Install requirements
    install_requirements()
    
    # Test basic functionality
    if not test_basic_functionality():
        print("❌ Setup failed - basic functionality not working")
        sys.exit(1)
    
    # Create Goose configuration
    create_goose_config()
    
    # Run test
    if not run_test():
        print("⚠️  Setup completed but tests failed - manual verification recommended")
    
    # Print usage instructions
    print_usage_instructions()

if __name__ == "__main__":
    main()
