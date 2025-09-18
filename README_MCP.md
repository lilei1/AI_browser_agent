# Yahoo Finance MCP Server

A Model Context Protocol (MCP) server that provides comprehensive Yahoo Finance data extraction and analysis capabilities for AI agents like Goose.

## 🚀 Features

- **MCP Protocol Compliance**: Full implementation of the Model Context Protocol for seamless AI agent integration
- **Comprehensive Stock Data**: Extract real-time prices, volume, market cap, P/E ratios, and more
- **Multi-Company Analysis**: Compare stocks and analyze entire market sectors
- **Goose Integration**: Pre-configured for use with Goose AI agent for chatbot functionality
- **Universal Company Support**: Works with ANY publicly traded company worldwide
- **Real-time Data**: Live market data from Yahoo Finance
- **Sector Analysis**: Built-in analysis for Technology, Finance, Healthcare, Energy, Consumer, and Automotive sectors

## 📋 Requirements

- Python 3.8+
- Internet connection for Yahoo Finance data
- Optional: Goose AI agent for chatbot functionality
- Optional: OpenAI API key for advanced analysis

## 🛠️ Quick Setup

### Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/lilei1/AI_browser_agent.git
cd AI_browser_agent

# Run the automated setup
python setup_mcp.py
```

The setup script will:
- Install all required dependencies
- Test basic functionality
- Configure Goose integration
- Run comprehensive tests
- Provide usage instructions

### Manual Setup

```bash
# Install dependencies
pip install -r mcp_requirements.txt

# Test basic functionality
python basic_demo.py

# Test MCP server
python test_mcp_server.py
```

## 🎯 Usage

### 1. Direct MCP Server

Start the MCP server directly:

```bash
python mcp_server.py
```

The server communicates via JSON-RPC over stdin/stdout following the MCP protocol.

### 2. With Goose AI Agent

If you have Goose installed, you can use the server for chatbot functionality:

```bash
# Start Goose session
goose session start

# Ask questions about stocks
"What's the current price of Apple stock?"
"Compare Tesla and General Motors"
"Analyze the technology sector performance"
"Get detailed data for NVIDIA"
"Is AMZN a valid stock symbol?"
```

### 3. Testing the Server

Run comprehensive tests:

```bash
python test_mcp_server.py
```

## 🔧 MCP Tools Available

### `extract_stock_data`
Extract comprehensive stock data including:
- Current price and price changes
- Trading volume and market cap
- P/E ratio and EPS
- Basic financial analysis

```json
{
  "name": "extract_stock_data",
  "arguments": {
    "symbol": "AAPL",
    "include_analysis": true
  }
}
```

### `get_stock_price`
Quick price lookup for any stock:

```json
{
  "name": "get_stock_price", 
  "arguments": {
    "symbol": "GOOGL"
  }
}
```

### `compare_stocks`
Compare multiple stocks side by side:

```json
{
  "name": "compare_stocks",
  "arguments": {
    "symbols": ["AAPL", "MSFT", "GOOGL"]
  }
}
```

### `analyze_sector`
Analyze entire market sectors:

```json
{
  "name": "analyze_sector",
  "arguments": {
    "sector": "technology"
  }
}
```

Available sectors: `technology`, `finance`, `healthcare`, `energy`, `consumer`, `automotive`

### `validate_symbol`
Check if a stock symbol is valid:

```json
{
  "name": "validate_symbol",
  "arguments": {
    "symbol": "TSLA"
  }
}
```

## 📊 Supported Companies

The server works with **ANY publicly traded company worldwide**, including:

### Technology Sector
- **Apple Inc. (AAPL)** - iPhone, Mac, iPad manufacturer
- **Alphabet/Google (GOOGL)** - Search engine and cloud services
- **Microsoft Corp. (MSFT)** - Software and cloud computing
- **NVIDIA Corp. (NVDA)** - Graphics cards and AI chips
- **Meta Platforms (META)** - Facebook, Instagram, WhatsApp
- **Tesla Inc. (TSLA)** - Electric vehicles and energy

### Financial Sector
- **JPMorgan Chase (JPM)** - Investment banking
- **Bank of America (BAC)** - Commercial banking
- **Wells Fargo (WFC)** - Banking and financial services
- **Goldman Sachs (GS)** - Investment banking

### Healthcare Sector
- **Johnson & Johnson (JNJ)** - Pharmaceuticals and medical devices
- **Pfizer (PFE)** - Pharmaceutical company
- **Moderna (MRNA)** - Biotechnology company
- **UnitedHealth (UNH)** - Health insurance

### And thousands more across all sectors and international markets!

## 🤖 MCP Resources

The server provides these resources:

- `yahoo-finance://market-status` - Current market status and trading hours
- `yahoo-finance://supported-sectors` - List of supported sectors with example companies

## 💬 MCP Prompts

Pre-configured prompts for AI agents:

- `analyze_stock_performance` - Generate comprehensive stock analysis
- `investment_recommendation` - Provide investment recommendations

## ⚙️ Configuration

### MCP Server Configuration (`mcp_config.json`)

```json
{
  "mcpServers": {
    "yahoo-finance": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/AI_browser_agent"
    }
  }
}
```

### Goose Configuration (`goose_config.yaml`)

```yaml
provider: openai
model: gpt-4

mcp_servers:
  yahoo-finance:
    command: python
    args: ["mcp_server.py"]
    cwd: "/path/to/AI_browser_agent"
```

## 🧪 Testing

### Run All Tests

```bash
python test_mcp_server.py
```

### Test Individual Functions

```python
# Test stock data extraction
from basic_demo import scrape_yahoo_finance_basic
data = scrape_yahoo_finance_basic("AAPL")
print(f"AAPL: ${data['current_price']}")
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r mcp_requirements.txt
   export PYTHONPATH=/path/to/AI_browser_agent
   ```

2. **Network Timeouts**
   - Check internet connection
   - Yahoo Finance may be temporarily unavailable
   - Try different stock symbols

3. **No Data Returned**
   - Verify stock symbol is correct
   - Check if market is open (affects some data)
   - Try major stocks like AAPL, GOOGL first

4. **Goose Integration Issues**
   - Ensure Goose is properly installed
   - Check MCP server configuration
   - Verify Python path in config files

### Debug Mode

Run with debug logging:

```bash
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
exec(open('mcp_server.py').read())
"
```

## 🚀 Example Chatbot Conversations

With Goose integration, you can have conversations like:

**User**: "What's Apple's stock price right now?"
**AI**: "Let me get the current Apple stock data for you..."
*[Uses extract_stock_data tool]*
**AI**: "Apple (AAPL) is currently trading at $185.32, up $2.15 (+1.17%) from yesterday's close..."

**User**: "Compare Apple, Microsoft, and Google"
**AI**: "I'll compare these three tech giants for you..."
*[Uses compare_stocks tool]*
**AI**: "Here's the comparison: Apple leads with +1.17%, Microsoft is up +0.85%, while Google is down -0.23%..."

**User**: "How is the technology sector doing today?"
**AI**: "Let me analyze the technology sector performance..."
*[Uses analyze_sector tool]*
**AI**: "The technology sector is showing strong performance today with an average gain of 0.94%..."

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Yahoo Finance** for providing comprehensive financial data
- **Anthropic** for the Model Context Protocol specification
- **Block** for the Goose AI agent
- **OpenAI** for AI analysis capabilities

## 📞 Support

For support:

1. Check this README and run `python test_mcp_server.py`
2. Review the [original project documentation](README.md)
3. Test with reliable stocks: AAPL, GOOGL, MSFT
4. Check existing [issues](https://github.com/lilei1/AI_browser_agent/issues)
5. Create a new issue if needed

---

**⚠️ Disclaimer**: This tool provides financial data for informational and educational purposes only. Always verify data from official sources before making investment decisions. Past performance does not guarantee future results.
