"""
AI-powered financial data analyzer
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from loguru import logger

from ..data.models import StockData, AnalysisResult
from ..utils.helpers import format_currency, format_percentage, is_market_hours
from config import settings

class FinancialAnalyzer:
    """
    AI-powered analyzer for financial data using OpenAI GPT models
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize the financial analyzer
        
        Args:
            api_key: OpenAI API key (defaults to settings)
            model: OpenAI model to use (defaults to settings)
        """
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        
        if not self.api_key:
            logger.warning("OpenAI API key not provided. AI analysis will be disabled.")
            self.enabled = False
        else:
            openai.api_key = self.api_key
            self.enabled = True
            logger.info(f"Financial analyzer initialized with model: {self.model}")
    
    def analyze_stock_data(self, stock_data: StockData) -> AnalysisResult:
        """
        Perform comprehensive AI analysis of stock data
        
        Args:
            stock_data: Stock data to analyze
            
        Returns:
            Analysis result with insights and recommendations
        """
        if not self.enabled:
            return AnalysisResult(
                symbol=stock_data.symbol,
                analysis_type="disabled",
                insights=["AI analysis is disabled - OpenAI API key not provided"],
                recommendations=[]
            )
        
        try:
            logger.info(f"Starting AI analysis for {stock_data.symbol}")
            
            # Prepare data for analysis
            analysis_prompt = self._create_analysis_prompt(stock_data)
            
            # Get AI analysis
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                max_tokens=settings.max_tokens,
                temperature=settings.temperature
            )

            # Parse response
            analysis_text = response['choices'][0]['message']['content']
            parsed_analysis = self._parse_analysis_response(analysis_text)
            
            result = AnalysisResult(
                symbol=stock_data.symbol,
                analysis_type="comprehensive",
                insights=parsed_analysis.get("insights", []),
                recommendations=parsed_analysis.get("recommendations", []),
                confidence_score=parsed_analysis.get("confidence_score", 0.7)
            )
            
            logger.success(f"AI analysis completed for {stock_data.symbol}")
            return result
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return AnalysisResult(
                symbol=stock_data.symbol,
                analysis_type="error",
                insights=[f"Analysis failed: {str(e)}"],
                recommendations=[]
            )
    
    def analyze_price_trend(self, stock_data: StockData) -> Dict[str, Any]:
        """
        Analyze price trends and patterns
        
        Args:
            stock_data: Stock data to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        try:
            price_info = stock_data.price_info
            
            # Basic trend analysis
            trend_direction = "neutral"
            if price_info.price_change and price_info.price_change > 0:
                trend_direction = "bullish"
            elif price_info.price_change and price_info.price_change < 0:
                trend_direction = "bearish"
            
            # Volatility assessment
            volatility = "low"
            if price_info.price_change_percent:
                abs_change = abs(price_info.price_change_percent)
                if abs_change > 5:
                    volatility = "high"
                elif abs_change > 2:
                    volatility = "moderate"
            
            # Support and resistance levels
            support_resistance = self._calculate_support_resistance(price_info)
            
            return {
                "trend_direction": trend_direction,
                "volatility": volatility,
                "price_change": price_info.price_change,
                "price_change_percent": price_info.price_change_percent,
                "support_resistance": support_resistance,
                "analysis_timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Price trend analysis failed: {str(e)}")
            return {"error": str(e)}
    
    def generate_investment_insights(self, stock_data: StockData) -> List[str]:
        """
        Generate investment insights based on stock data
        
        Args:
            stock_data: Stock data to analyze
            
        Returns:
            List of investment insights
        """
        insights = []
        
        try:
            price_info = stock_data.price_info
            financial_ratios = stock_data.financial_ratios
            trading_metrics = stock_data.trading_metrics
            
            # Price-based insights
            if price_info.price_change_percent:
                if abs(price_info.price_change_percent) > 5:
                    insights.append(f"High volatility detected: {price_info.price_change_percent:.2f}% change")
                elif price_info.price_change_percent > 2:
                    insights.append("Positive momentum with moderate gains")
                elif price_info.price_change_percent < -2:
                    insights.append("Negative momentum with moderate losses")
            
            # Valuation insights
            if financial_ratios.pe_ratio:
                if financial_ratios.pe_ratio > 30:
                    insights.append(f"High P/E ratio ({financial_ratios.pe_ratio:.2f}) suggests premium valuation")
                elif financial_ratios.pe_ratio < 15:
                    insights.append(f"Low P/E ratio ({financial_ratios.pe_ratio:.2f}) may indicate undervaluation")
            
            # Volume insights
            if trading_metrics.volume and trading_metrics.avg_volume:
                volume_ratio = trading_metrics.volume / trading_metrics.avg_volume
                if volume_ratio > 2:
                    insights.append("Unusually high trading volume detected")
                elif volume_ratio < 0.5:
                    insights.append("Below-average trading volume")
            
            # Market timing insights
            if is_market_hours():
                insights.append("Market is currently open - real-time data available")
            else:
                insights.append("Market is closed - data reflects last trading session")
            
            return insights
            
        except Exception as e:
            logger.error(f"Investment insights generation failed: {str(e)}")
            return [f"Error generating insights: {str(e)}"]
    
    def _create_analysis_prompt(self, stock_data: StockData) -> str:
        """Create analysis prompt for AI model"""
        price_info = stock_data.price_info
        financial_ratios = stock_data.financial_ratios
        trading_metrics = stock_data.trading_metrics
        company_info = stock_data.company_info
        
        prompt = f"""
        Analyze the following stock data for {company_info.company_name} ({stock_data.symbol}):

        PRICE INFORMATION:
        - Current Price: {format_currency(price_info.current_price)}
        - Price Change: {format_currency(price_info.price_change)}
        - Price Change %: {format_percentage(price_info.price_change_percent)}
        - Previous Close: {format_currency(price_info.previous_close)}
        - Day Range: {format_currency(price_info.day_low)} - {format_currency(price_info.day_high)}
        - 52-Week Range: {format_currency(price_info.week_52_low)} - {format_currency(price_info.week_52_high)}

        FINANCIAL RATIOS:
        - P/E Ratio: {financial_ratios.pe_ratio}
        - EPS: {format_currency(financial_ratios.eps)}
        - Beta: {financial_ratios.beta}
        - Dividend Yield: {format_percentage(financial_ratios.dividend_yield)}

        TRADING METRICS:
        - Volume: {trading_metrics.volume:,} shares
        - Average Volume: {trading_metrics.avg_volume:,} shares
        - Market Cap: {trading_metrics.market_cap}

        Please provide:
        1. Key insights about the stock's current performance
        2. Investment recommendations based on the data
        3. Risk assessment and potential concerns
        4. Confidence score (0-1) for your analysis

        Format your response as JSON with keys: insights, recommendations, confidence_score
        """
        
        return prompt
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for AI model"""
        return """
        You are an expert financial analyst with deep knowledge of stock markets, 
        financial ratios, and investment strategies. Analyze the provided stock data 
        and provide actionable insights and recommendations. Be objective, consider 
        both risks and opportunities, and base your analysis on the quantitative data provided.
        
        Always format your response as valid JSON with the following structure:
        {
            "insights": ["insight1", "insight2", ...],
            "recommendations": ["recommendation1", "recommendation2", ...],
            "confidence_score": 0.8
        }
        """
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI analysis response"""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                return json.loads(json_text)
            else:
                # Fallback: parse as plain text
                return {
                    "insights": [response_text],
                    "recommendations": [],
                    "confidence_score": 0.5
                }
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse AI response as JSON")
            return {
                "insights": [response_text],
                "recommendations": [],
                "confidence_score": 0.5
            }
    
    def _calculate_support_resistance(self, price_info) -> Dict[str, float]:
        """Calculate basic support and resistance levels"""
        try:
            current = price_info.current_price or 0
            day_low = price_info.day_low or current
            day_high = price_info.day_high or current
            week_52_low = price_info.week_52_low or current
            week_52_high = price_info.week_52_high or current
            
            return {
                "immediate_support": day_low,
                "immediate_resistance": day_high,
                "long_term_support": week_52_low,
                "long_term_resistance": week_52_high
            }
            
        except Exception:
            return {}
