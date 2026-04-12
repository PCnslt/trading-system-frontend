#!/usr/bin/env python3
"""
MCP Server for Sentiment analysis tools (news, social media) using HuggingFace models
"""

import asyncio
import json
import os
from typing import Any, Dict, List
from datetime import datetime, timedelta
import numpy as np
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import HuggingFace transformers
try:
    from transformers import pipeline
    import torch
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("Warning: HuggingFace transformers not available. Install with: pip install transformers torch")

# Import NewsAPI
try:
    from newsapi import NewsApiClient
    NEWSAPI_AVAILABLE = True
except ImportError:
    NEWSAPI_AVAILABLE = False
    print("Warning: NewsAPI not available. Install with: pip install newsapi-python")

# Import requests for Twitter/X API
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests not available. Install with: pip install requests")

# Initialize server
server = Server("sentiment-analyst")

# Load API keys from environment
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN", "")
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "")

# Initialize sentiment pipeline (load on first use)
sentiment_pipeline = None

def get_sentiment_pipeline():
    """Get or create HuggingFace sentiment analysis pipeline"""
    global sentiment_pipeline
    if sentiment_pipeline is None and HF_AVAILABLE:
        try:
            # Use a popular sentiment analysis model
            sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                token=HUGGINGFACE_TOKEN if HUGGINGFACE_TOKEN else None
            )
            print("Loaded HuggingFace sentiment pipeline")
        except Exception as e:
            print(f"Failed to load sentiment pipeline: {e}")
            sentiment_pipeline = None
    return sentiment_pipeline

def analyze_sentiment_text(text: str) -> Dict[str, Any]:
    """Analyze sentiment of text using HuggingFace model"""
    pipeline = get_sentiment_pipeline()
    if not pipeline or not text.strip():
        return {"label": "NEUTRAL", "score": 0.5, "error": "Pipeline not available"}
    
    try:
        result = pipeline(text[:512])[0]  # Truncate to model max length
        return {
            "label": result["label"],
            "score": float(result["score"]),
            "error": None
        }
    except Exception as e:
        return {"label": "ERROR", "score": 0.5, "error": str(e)}

def fetch_news_articles(symbol: str, days: int = 7) -> List[Dict[str, Any]]:
    """Fetch news articles for a symbol using NewsAPI"""
    if not NEWSAPI_AVAILABLE or not NEWSAPI_KEY:
        return []
    
    try:
        newsapi = NewsApiClient(api_key=NEWSAPI_KEY)
        
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        
        # Search for news about the symbol/company
        query = f"{symbol} stock OR {symbol} earnings OR {symbol} company"
        
        response = newsapi.get_everything(
            q=query,
            from_param=from_date.strftime("%Y-%m-%d"),
            to=to_date.strftime("%Y-%m-%d"),
            language="en",
            sort_by="relevancy",
            page_size=10
        )
        
        if response["status"] == "ok":
            articles = []
            for article in response["articles"][:5]:  # Limit to 5 articles
                articles.append({
                    "title": article["title"],
                    "description": article["description"],
                    "url": article["url"],
                    "published_at": article["publishedAt"],
                    "source": article["source"]["name"]
                })
            return articles
        else:
            print(f"NewsAPI error: {response.get('message', 'Unknown error')}")
            return []
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def fetch_twitter_sentiment(symbol: str) -> Dict[str, Any]:
    """Fetch Twitter/X sentiment for a symbol"""
    if not REQUESTS_AVAILABLE or not TWITTER_BEARER_TOKEN:
        return {"average_sentiment": 0.5, "tweet_count": 0, "error": "API not available"}
    
    try:
        # Twitter API v2 search recent tweets
        headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
        params = {
            "query": f"${symbol} OR #{symbol} (lang:en)",
            "max_results": 10,
            "tweet.fields": "created_at,public_metrics"
        }
        
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/recent",
            headers=headers,
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            tweets = data.get("data", [])
            
            if not tweets:
                return {"average_sentiment": 0.5, "tweet_count": 0, "error": None}
            
            # Analyze sentiment of each tweet
            sentiments = []
            for tweet in tweets:
                text = tweet.get("text", "")
                if text:
                    sentiment = analyze_sentiment_text(text)
                    if sentiment["error"] is None:
                        # Convert POSITIVE/NEGATIVE to numeric score
                        score = sentiment["score"]
                        if sentiment["label"] == "NEGATIVE":
                            score = 1 - score  # Invert for negative
                        sentiments.append(score)
            
            if sentiments:
                avg_sentiment = sum(sentiments) / len(sentiments)
                return {
                    "average_sentiment": avg_sentiment,
                    "tweet_count": len(tweets),
                    "sample_tweets": len(sentiments),
                    "error": None
                }
            else:
                return {"average_sentiment": 0.5, "tweet_count": len(tweets), "error": "No analyzable tweets"}
        else:
            return {"average_sentiment": 0.5, "tweet_count": 0, "error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"average_sentiment": 0.5, "tweet_count": 0, "error": str(e)}

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools for sentiment-analyst"""
    return [
        types.Tool(
            name="analyze_sentiment",
            description="Analyze sentiment for a symbol using news and social media",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock or asset symbol (e.g., AAPL, TSLA)"
                    },
                    "include_news": {
                        "type": "boolean",
                        "description": "Include news analysis (default: true)",
                        "default": True
                    },
                    "include_twitter": {
                        "type": "boolean", 
                        "description": "Include Twitter/X analysis (default: true)",
                        "default": True
                    }
                },
                "required": ["symbol"]
            }
        ),
        types.Tool(
            name="get_insights",
            description="Get detailed insights and sentiment breakdown",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Symbol to analyze"
                    }
                },
                "required": ["symbol"]
            }
        ),
        types.Tool(
            name="health_check",
            description="Check sentiment-analyst health and API availability",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool execution requests"""
    
    symbol = arguments.get("symbol", "UNKNOWN").upper()
    
    if name == "analyze_sentiment":
        include_news = arguments.get("include_news", True)
        include_twitter = arguments.get("include_twitter", True)
        
        results = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "news_sentiment": None,
            "twitter_sentiment": None,
            "overall_sentiment": 0.5,
            "signal": "HOLD",
            "confidence": 0.0,
            "api_status": {}
        }
        
        # Check API availability
        results["api_status"]["huggingface"] = HF_AVAILABLE and get_sentiment_pipeline() is not None
        results["api_status"]["newsapi"] = NEWSAPI_AVAILABLE and bool(NEWSAPI_KEY)
        results["api_status"]["twitter"] = REQUESTS_AVAILABLE and bool(TWITTER_BEARER_TOKEN)
        
        # Analyze news sentiment
        news_sentiments = []
        if include_news and results["api_status"]["newsapi"]:
            articles = fetch_news_articles(symbol, days=3)
            for article in articles:
                text = f"{article['title']} {article.get('description', '')}"
                sentiment = analyze_sentiment_text(text)
                if sentiment["error"] is None:
                    score = sentiment["score"]
                    if sentiment["label"] == "NEGATIVE":
                        score = 1 - score
                    news_sentiments.append(score)
            
            if news_sentiments:
                avg_news = sum(news_sentiments) / len(news_sentiments)
                results["news_sentiment"] = {
                    "score": avg_news,
                    "articles_analyzed": len(news_sentiments),
                    "label": "BULLISH" if avg_news > 0.6 else "BEARISH" if avg_news < 0.4 else "NEUTRAL"
                }
        
        # Analyze Twitter sentiment
        if include_twitter and results["api_status"]["twitter"]:
            twitter_data = fetch_twitter_sentiment(symbol)
            if twitter_data["error"] is None:
                results["twitter_sentiment"] = {
                    "score": twitter_data["average_sentiment"],
                    "tweets_analyzed": twitter_data["tweet_count"],
                    "label": "BULLISH" if twitter_data["average_sentiment"] > 0.6 else "BEARISH" if twitter_data["average_sentiment"] < 0.4 else "NEUTRAL"
                }
        
        # Calculate overall sentiment (weighted average)
        scores = []
        weights = []
        
        if results["news_sentiment"]:
            scores.append(results["news_sentiment"]["score"])
            weights.append(0.6)  # News has higher weight
        
        if results["twitter_sentiment"]:
            scores.append(results["twitter_sentiment"]["score"])
            weights.append(0.4)
        
        if scores:
            results["overall_sentiment"] = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        else:
            results["overall_sentiment"] = 0.5
        
        # Determine signal
        if results["overall_sentiment"] > 0.65:
            results["signal"] = "BUY"
            results["confidence"] = min(0.9, (results["overall_sentiment"] - 0.65) * 3)
        elif results["overall_sentiment"] < 0.35:
            results["signal"] = "SELL"
            results["confidence"] = min(0.9, (0.35 - results["overall_sentiment"]) * 3)
        else:
            results["signal"] = "HOLD"
            results["confidence"] = 0.3
        
        # Format response
        response_text = f"Sentiment Analysis for {symbol}\n"
        response_text += f"Timestamp: {results['timestamp']}\n"
        response_text += f"Overall Sentiment: {results['overall_sentiment']:.2%}\n"
        response_text += f"Signal: {results['signal']} (Confidence: {results['confidence']:.1%})\n\n"
        
        response_text += "API Status:\n"
        for api, status in results["api_status"].items():
            response_text += f"  • {api}: {'✅' if status else '❌'}\n"
        
        if results["news_sentiment"]:
            response_text += f"\nNews Sentiment: {results['news_sentiment']['label']} ({results['news_sentiment']['score']:.2%})\n"
            response_text += f"  Articles Analyzed: {results['news_sentiment']['articles_analyzed']}\n"
        
        if results["twitter_sentiment"]:
            response_text += f"\nTwitter Sentiment: {results['twitter_sentiment']['label']} ({results['twitter_sentiment']['score']:.2%})\n"
            response_text += f"  Tweets Analyzed: {results['twitter_sentiment']['tweets_analyzed']}\n"
        
        if not results["news_sentiment"] and not results["twitter_sentiment"]:
            response_text += "\n⚠️ No data sources available. Using default sentiment.\n"
        
        return [
            types.TextContent(
                type="text",
                text=response_text
            )
        ]
    
    elif name == "get_insights":
        # Get detailed insights
        insights = []
        
        # Check HuggingFace availability
        if HF_AVAILABLE and get_sentiment_pipeline():
            insights.append("✅ HuggingFace sentiment model loaded and ready")
        else:
            insights.append("❌ HuggingFace sentiment model not available")
        
        # Check NewsAPI
        if NEWSAPI_AVAILABLE and NEWSAPI_KEY:
            insights.append("✅ NewsAPI configured for real-time news analysis")
        else:
            insights.append("❌ NewsAPI not configured (news sentiment will be limited)")
        
        # Check Twitter API
        if REQUESTS_AVAILABLE and TWITTER_BEARER_TOKEN:
            insights.append("✅ Twitter/X API configured for social sentiment")
        else:
            insights.append("❌ Twitter/X API not configured (social sentiment will be limited)")
        
        # Model info
        insights.append(f"🤖 Using model: distilbert-base-uncased-finetuned-sst-2-english")
        insights.append(f"📊 Sentiment scale: 0-100% (Bearish-Neutral-Bullish)")
        insights.append(f"🎯 Buy threshold: >65%, Sell threshold: <35%")
        
        response_text = f"Sentiment Analyst Insights for {symbol}\n\n"
        response_text += "\n".join([f"• {insight}" for insight in insights])
        
        return [
            types.TextContent(
                type="text",
                text=response_text
            )
        ]
    
    elif name == "health_check":
        # Health check response
        health_status = {
            "huggingface": HF_AVAILABLE and get_sentiment_pipeline() is not None,
            "newsapi": NEWSAPI_AVAILABLE and bool(NEWSAPI_KEY),
            "twitter": REQUESTS_AVAILABLE and bool(TWITTER_BEARER_TOKEN),
            "model": "distilbert-base-uncased-finetuned-sst-2-english" if HF_AVAILABLE else "none",
            "timestamp": datetime.now().isoformat()
        }
        
        response_text = "Sentiment Analyst Health Check\n\n"
        response_text += f"✅ HuggingFace: {'Available' if health_status['huggingface'] else 'Unavailable'}\n"
        response_text += f"✅ NewsAPI: {'Available' if health_status['newsapi'] else 'Unavailable'}\n"
        response_text += f"✅ Twitter/X API: {'Available' if health_status['twitter'] else 'Unavailable'}\n"
        response_text += f"🤖 Model: {health_status['model']}\n"
        response_text += f"🕒 Timestamp: {health_status['timestamp']}\n\n"
        
        if all([health_status['huggingface'], health_status['newsapi'], health_status['twitter']]):
            response_text += "Status: ✅ FULLY OPERATIONAL\n"
            response_text += "All APIs configured and ready for sentiment analysis."
        elif health_status['huggingface']:
            response_text += "Status: ⚠️ PARTIALLY OPERATIONAL\n"
            response_text += "HuggingFace available but some data sources missing."
        else:
            response_text += "Status: ❌ DEGRADED\n"
            response_text += "HuggingFace not available. Basic functionality only."
        
        return [
            types.TextContent(
                type="text",
                text=response_text
            )
        ]
    
    else:
        return [
            types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )
        ]

async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sentiment-analyst",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())