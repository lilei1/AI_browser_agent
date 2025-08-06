# Yahoo Finance AI Browser Agent

A comprehensive AI-powered browser agent for extracting and analyzing financial data from Yahoo Finance. This agent combines intelligent web scraping, browser automation, and AI analysis to provide detailed insights into stock performance, specifically designed for Apple (AAPL) stock data and easily extensible to other symbols.

## 🚀 Features

- **Intelligent Web Scraping**: Advanced scraping with multiple fallback strategies
- **AI-Powered Analysis**: OpenAI GPT integration for financial insights and recommendations
- **Browser Automation**: Selenium-based automation with anti-detection capabilities
- **Real-time Monitoring**: Live stock price monitoring with customizable intervals
- **Technical Analysis**: Comprehensive technical indicators and pattern recognition
- **Rich UI**: Beautiful console interface with tables, charts, and progress indicators
- **Error Handling**: Robust error handling with retry mechanisms and monitoring
- **Multiple Output Formats**: Text reports, JSON exports, and interactive dashboards

## 📋 Requirements

- Python 3.8+
- Chrome/Chromium browser
- OpenAI API key (optional, for AI analysis)

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone https://github.com/lilei1/AI_browser_agent-.git
cd AI_browser_agent-
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your OpenAI API key and preferences
```

## 🎯 Quick Start

### ✅ **Working Commands (Python 3.7+ Compatible)**

#### Simple CLI (Recommended)
```bash
# Extract comprehensive data for AAPL with report
python3 simple_cli.py extract --symbol AAPL --save-report

# Quick price check
python3 simple_cli.py price --symbol AAPL

# Show CLI information
python3 simple_cli.py info
```

#### Basic Demo
```bash
# Interactive demo with rich interface
python3 basic_demo.py
```

### ⚠️ **Full CLI (Requires Python 3.8+ and Chrome)**
```bash
# Extract comprehensive data for AAPL
python3 main.py extract --symbol AAPL

# Extract data without AI analysis
python3 main.py extract --symbol AAPL --no-analysis

# Save report to file
python3 main.py extract --symbol AAPL --save-report

# Quick price check
python3 main.py price --symbol AAPL
```

**Note**: The full CLI requires Chrome browser and Python 3.8+. For Python 3.7, use `simple_cli.py` instead.

## 🏗️ Architecture

The agent is built with a modular architecture:

```
src/yahoo_finance_agent/
├── core/                 # Core agent and browser management
│   ├── agent.py         # Main YahooFinanceAgent class
│   └── browser.py       # Browser automation manager
├── scrapers/            # Web scraping components
│   ├── yahoo_scraper.py # Main Yahoo Finance scraper
│   └── intelligent_extractor.py # AI-powered extraction strategies
├── ai/                  # AI analysis components
│   └── analyzer.py      # Financial data analyzer using OpenAI
├── data/                # Data models and processing
│   ├── models.py        # Pydantic data models
│   └── processor.py     # Data processing and technical analysis
├── ui/                  # User interface components
│   └── dashboard.py     # Rich console dashboard and reporting
└── utils/               # Utility functions
    ├── helpers.py       # General helper functions
    └── error_handler.py # Error handling and monitoring
```

## 📊 Data Extracted

The agent extracts comprehensive financial data including:

### Price Information
- Current stock price
- Price change (absolute and percentage)
- Previous close, open price
- Day's range (high/low)
- 52-week range

### Trading Metrics
- Current volume
- Average volume (3-month)
- Market capitalization
- Shares outstanding

### Financial Ratios
- Price-to-Earnings (P/E) ratio
- Earnings Per Share (EPS)
- Beta coefficient
- Dividend yield
- Book value per share

### Technical Indicators
- Simple Moving Averages (SMA 20, 50, 200)
- Exponential Moving Averages (EMA 12, 26)
- MACD (Moving Average Convergence Divergence)
- RSI (Relative Strength Index)
- Bollinger Bands
- Volume analysis
- Price performance metrics

## 🤖 AI Analysis Features

When enabled, the AI analyzer provides:

- **Market Insights**: Key observations about current market conditions
- **Investment Recommendations**: AI-generated investment suggestions
- **Risk Assessment**: Potential risks and concerns
- **Trend Analysis**: Price trend direction and strength
- **Pattern Recognition**: Chart and candlestick pattern identification
- **Confidence Scoring**: AI confidence in analysis (0-1 scale)

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
MAX_TOKENS=2000
TEMPERATURE=0.1

# Browser Configuration
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30
PAGE_LOAD_TIMEOUT=20
IMPLICIT_WAIT=10

# Data Extraction Settings
MAX_RETRIES=3
RETRY_DELAY=2.0
REQUEST_DELAY=1.0

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=yahoo_finance_agent.log

# Data Storage
DATA_DIR=data
CACHE_DIR=cache
```

### Browser Settings

The agent supports various browser configurations:

- **Headless Mode**: Run without GUI (default: true)
- **Anti-Detection**: Uses undetected-chromedriver for better reliability
- **Custom User Agents**: Mimics real browser behavior
- **Timeout Controls**: Configurable timeouts for different operations

## 📚 Documentation

- **[API Reference](docs/API_REFERENCE.md)**: Complete API documentation
- **[Basic Examples](examples/basic_usage.py)**: Simple usage examples
- **[Advanced Examples](examples/advanced_usage.py)**: Complex workflows and patterns

## 🔧 Programming Interface

### Basic Usage

```python
from src.yahoo_finance_agent import YahooFinanceAgent

# Extract comprehensive stock data
with YahooFinanceAgent(headless=True, use_ai_analysis=True) as agent:
    result = agent.extract_stock_data("AAPL", include_analysis=True)

    if result["success"]:
        stock_data = result["stock_data"]
        analysis = result.get("analysis")

        print(f"Current Price: ${stock_data['price_info']['current_price']:.2f}")
        print(f"AI Insights: {analysis['insights'][0] if analysis else 'N/A'}")
```

### Advanced Usage

```python
from src.yahoo_finance_agent import YahooFinanceAgent
from src.yahoo_finance_agent.data import DataProcessor
from src.yahoo_finance_agent.ui import FinanceDashboard

# Multi-component analysis
dashboard = FinanceDashboard()
processor = DataProcessor()

with YahooFinanceAgent() as agent:
    # Get current data
    current_data = agent.extract_stock_data("AAPL")

    # Get historical data
    historical = processor.get_historical_data("AAPL", period="1y")

    # Calculate technical indicators
    indicators = processor.calculate_technical_indicators(historical)

    # Display results
    dashboard.display_stock_summary(current_data["stock_data"])
```

## 🚨 Error Handling

The agent includes comprehensive error handling:

```python
from src.yahoo_finance_agent.utils import error_tracker, health_monitor

# Monitor system health
health_status = health_monitor.get_health_status()
print(f"System Status: {health_status['status']}")
print(f"Success Rate: {health_status['success_rate']:.1%}")

# Get error summary
error_summary = error_tracker.get_error_summary(hours=24)
print(f"Errors in last 24h: {error_summary['total_errors']}")
```

## 🧪 Testing

Run the examples to test the installation:

```bash
# Basic functionality test
python examples/basic_usage.py

# Advanced features test
python examples/advanced_usage.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   ```bash
   # Update Chrome driver
   pip install --upgrade webdriver-manager
   ```

2. **OpenAI API Errors**
   - Ensure your API key is set in `.env`
   - Check your OpenAI account has sufficient credits
   - Verify the model name is correct

3. **Network Timeouts**
   - Increase timeout values in `.env`
   - Check your internet connection
   - Try running with `--no-headless` to see browser behavior

4. **Data Extraction Failures**
   - Yahoo Finance may have changed their layout
   - The intelligent extractor will try multiple strategies
   - Check logs for specific error messages

### Debug Mode

Run with verbose logging:

```bash
# Set debug logging
export LOG_LEVEL=DEBUG
python main.py extract --symbol AAPL --no-headless
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Yahoo Finance** for providing financial data
- **OpenAI** for AI analysis capabilities
- **Selenium** for browser automation
- **Rich** for beautiful console interfaces
- **yfinance** for historical data access

## 📞 Support

For support, please:

1. Check the [API Reference](docs/API_REFERENCE.md)
2. Review the [examples](examples/)
3. Check existing [issues](https://github.com/lilei1/AI_browser_agent-/issues)
4. Create a new issue if needed

---

**⚠️ Disclaimer**: This tool is for educational and research purposes. Always verify financial data from official sources before making investment decisions. The AI analysis is for informational purposes only and should not be considered as financial advice.
