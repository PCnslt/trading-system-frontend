#!/usr/bin/env python3
"""
Sentiment Analyst Agent - Analyzes news sentiment for stocks using NewsAPI and HuggingFace sentiment models.
"""

import os
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "YOUR_FMP_API_KEY_HERE")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "YOUR_HUGGINGFACE_TOKEN_HERE")

# HuggingFace Router API (replaces deprecated Inference API)
from hf_router import analyze_with_llm

def fetch_news(symbol: str, days: int = 7) -> List[Dict[str, Any]]:
    """Fetch recent news articles for a symbol using NewsAPI."""
    # Map common symbols to company names for better search
    symbol_map = {
        "AAPL": "Apple",
        "TSLA": "Tesla",
        "MSFT": "Microsoft",
        "GOOGL": "Google",
        "AMZN": "Amazon",
        "META": "Meta",
        "NVDA": "NVIDIA",
        "JPM": "JPMorgan",
        "V": "Visa",
        "JNJ": "Johnson & Johnson"
    }
    
    query = symbol_map.get(symbol, symbol)
    from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": from_date,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": NEWSAPI_KEY,
        "pageSize": 20  # Max per request
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "ok":
            raise ValueError(f"NewsAPI error: {data.get('message', 'Unknown error')}")
        
        articles = data.get("articles", [])
        # Filter out articles with no content
        filtered = []
        for article in articles:
            if article.get("title") and article.get("description"):
                filtered.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "published_at": article.get("publishedAt", ""),
                    "url": article.get("url", "")
                })
        
        return filtered
        
    except Exception as e:
        raise Exception(f"Failed to fetch news: {e}")

def analyze_sentiment_huggingface(text: str) -> Dict[str, float]:
    """Analyze sentiment of text using HuggingFace Router LLM."""
    prompt = f'''Classify the sentiment of the following text as POSITIVE or NEGATIVE. Return a JSON object with keys "positive" and "negative" as floating point scores between 0 and 1 that sum to 1. Text: "{text[:500]}" '''
    try:
        result = analyze_with_llm(prompt, json_output=True, max_tokens=100, temperature=0.1)
        if isinstance(result, dict) and "positive" in result and "negative" in result:
            # Ensure scores are floats
            pos = float(result["positive"])
            neg = float(result["negative"])
            # Normalize
            total = pos + neg
            if total > 0:
                pos = pos / total
                neg = neg / total
            else:
                pos = neg = 0.5
            return {"positive": pos, "negative": neg}
        else:
            # Fallback to keyword analysis
            return analyze_sentiment_keywords(text)
    except Exception:
        return analyze_sentiment_keywords(text)

def analyze_sentiment_keywords(text: str) -> Dict[str, float]:
    """Simple keyword-based sentiment analysis as fallback."""
    positive_words = ["up", "rise", "gain", "profit", "growth", "strong", "bull", "buy", "positive", "good", "great"]
    negative_words = ["down", "fall", "loss", "drop", "decline", "weak", "bear", "sell", "negative", "bad", "poor"]
    
    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    total = pos_count + neg_count
    
    if total > 0:
        positive_score = pos_count / total
        negative_score = neg_count / total
    else:
        positive_score = 0.5
        negative_score = 0.5
    
    return {"positive": positive_score, "negative": negative_score}

def analyze_news_sentiment(articles: List[Dict]) -> Dict[str, Any]:
    """Analyze sentiment across multiple news articles."""
    if not articles:
        return {
            "article_count": 0,
            "average_sentiment": 0.5,
            "sentiment_score": 0.0,
            "summary": "No news articles found"
        }
    
    sentiments = []
    positive_count = 0
    negative_count = 0
    
    for i, article in enumerate(articles[:10]):  # Limit to 10 articles for performance
        text = f"{article['title']}. {article['description']}"
        scores = analyze_sentiment_huggingface(text[:512])  # Limit text length
        
        positive = scores.get("positive", 0.5)
        negative = scores.get("negative", 0.5)
        
        # Calculate sentiment score: positive - negative normalized to -1 to 1
        sentiment = positive - negative
        sentiments.append(sentiment)
        
        if sentiment > 0.2:
            positive_count += 1
        elif sentiment < -0.2:
            negative_count += 1
    
    # Average sentiment
    if sentiments:
        avg_sentiment = sum(sentiments) / len(sentiments)
    else:
        avg_sentiment = 0
    
    # Determine overall sentiment
    if avg_sentiment > 0.2:
        overall = "POSITIVE"
        signal = "BUY"
        confidence = min(0.9, (avg_sentiment + 1) / 2)
    elif avg_sentiment < -0.2:
        overall = "NEGATIVE"
        signal = "SELL"
        confidence = min(0.9, (-avg_sentiment + 1) / 2)
    else:
        overall = "NEUTRAL"
        signal = "HOLD"
        confidence = 0.5
    
    return {
        "article_count": len(articles),
        "analyzed_count": min(10, len(articles)),
        "positive_articles": positive_count,
        "negative_articles": negative_count,
        "neutral_articles": len(articles) - positive_count - negative_count,
        "average_sentiment": avg_sentiment,
        "overall_sentiment": overall,
        "signal": signal,
        "confidence": confidence,
        "summary": f"{overall} sentiment based on {len(articles)} articles"
    }

def analyze_symbol(symbol: str, use_ai: bool = True) -> Dict[str, Any]:
    """Main analysis function for a symbol."""
    symbol = symbol.upper()
    result = {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "error": None,
        "news_data": {},
        "analysis": {}
    }
    
    try:
        # Fetch news articles
        articles = fetch_news(symbol)
        result["news_data"] = {
            "total_articles": len(articles),
            "articles": articles[:5]  # Include first 5 for reference
        }
        
        # Analyze sentiment
        sentiment_result = analyze_news_sentiment(articles)
        
        result["analysis"] = {
            "signal": sentiment_result["signal"],
            "confidence": sentiment_result["confidence"],
            "reasoning": f"News sentiment analysis: {sentiment_result['overall_sentiment']} based on {sentiment_result['article_count']} articles",
            "summary": sentiment_result["summary"],
            "details": {
                "article_count": sentiment_result["article_count"],
                "positive_articles": sentiment_result["positive_articles"],
                "negative_articles": sentiment_result["negative_articles"],
                "average_sentiment": sentiment_result["average_sentiment"]
            }
        }
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

def print_result(result: Dict):
    """Print analysis result in readable format."""
    if not result["success"]:
        print(f"❌ Sentiment analysis failed for {result['symbol']}: {result['error']}")
        return
    
    symbol = result["symbol"]
    analysis = result["analysis"]
    news_data = result["news_data"]
    
    print("\n" + "="*60)
    print(f"📰 SENTIMENT ANALYSIS: {symbol}")
    print("="*60)
    
    print(f"\n📊 NEWS SUMMARY:")
    print(f"   Articles analyzed: {news_data.get('total_articles', 0)}")
    if analysis.get("details"):
        details = analysis["details"]
        print(f"   Positive articles: {details.get('positive_articles', 0)}")
        print(f"   Negative articles: {details.get('negative_articles', 0)}")
        print(f"   Average sentiment: {details.get('average_sentiment', 0):.3f}")
    
    print(f"\n🤖 ANALYSIS:")
    print(f"   Signal: {analysis.get('signal', 'HOLD')}")
    print(f"   Confidence: {analysis.get('confidence', 0.5):.1%}")
    print(f"   Reasoning: {analysis.get('reasoning', '')}")
    
    # Show sample headlines
    articles = news_data.get("articles", [])
    if articles:
        print(f"\n📰 SAMPLE HEADLINES:")
        for i, article in enumerate(articles[:3], 1):
            title = article.get("title", "No title")
            source = article.get("source", "Unknown")
            print(f"   {i}. {title[:80]}... ({source})")
    
    print(f"\n⏰ Timestamp: {result['timestamp']}")
    print("="*60)

def main():
    """Command line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sentiment Analyst Agent")
    parser.add_argument("symbol", help="Stock symbol (e.g., AAPL, TSLA)")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI sentiment (use keyword-based)")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--save", help="Save result to JSON file")
    
    args = parser.parse_args()
    
    # Perform analysis (use_ai parameter not fully implemented, but kept for consistency)
    result = analyze_symbol(args.symbol, use_ai=not args.no_ai)
    
    # Output
    if args.output == "json":
        output = json.dumps(result, indent=2)
        print(output)
    else:
        print_result(result)
    
    # Save to file if requested
    if args.save:
        with open(args.save, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Saved to: {args.save}")
    
    # Exit code
    sys.exit(0 if result["success"] else 1)

if __name__ == "__main__":
    main()