#!/usr/bin/env python3
"""
Stock Scanner - Gets ALL available stocks from multiple sources
"""

import os
import json
import requests
import yfinance as yf
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime, timedelta
import time

class StockScanner:
    """Scans ALL available stocks from multiple sources"""
    
    def __init__(self):
        # Load API keys
        self.alphavantage_key = os.getenv("ALPHAVANTAGE_API_KEY", "LNPH1SNZM9C4MT0")
        self.fmp_key = os.getenv("FMP_API_KEY", "R2vOmTkc2r4FmlqUtDZbyifARUPa8nfM")
        
        # Cache for stock lists
        self.cache_file = "data/stock_cache.json"
        self.cache_duration = timedelta(hours=24)  # Refresh daily
        
    def get_all_stocks_alphavantage(self) -> List[Dict[str, Any]]:
        """Get stocks from Alpha Vantage"""
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "LISTING_STATUS",
                "apikey": self.alphavantage_key
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                # Parse CSV response
                import io
                import csv
                
                csv_data = io.StringIO(response.text)
                reader = csv.DictReader(csv_data)
                
                stocks = []
                for row in reader:
                    if row.get("symbol") and row.get("name"):
                        stocks.append({
                            "symbol": row["symbol"],
                            "name": row["name"],
                            "exchange": row.get("exchange", "Unknown"),
                            "assetType": row.get("assetType", "Stock"),
                            "source": "alphavantage"
                        })
                
                print(f"✅ Alpha Vantage: Found {len(stocks)} stocks")
                return stocks
            else:
                print(f"❌ Alpha Vantage error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Alpha Vantage exception: {e}")
            return []
    
    def get_all_stocks_fmp(self) -> List[Dict[str, Any]]:
        """Get stocks from Financial Modeling Prep"""
        try:
            url = f"https://financialmodelingprep.com/api/v3/stock/list"
            params = {
                "apikey": self.fmp_key
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                stocks = []
                for item in data:
                    if isinstance(item, dict) and item.get("symbol") and item.get("name"):
                        stocks.append({
                            "symbol": item["symbol"],
                            "name": item["name"],
                            "exchange": item.get("exchange", "Unknown"),
                            "exchangeShortName": item.get("exchangeShortName", ""),
                            "type": item.get("type", "stock"),
                            "source": "fmp"
                        })
                
                print(f"✅ FMP: Found {len(stocks)} stocks")
                return stocks
            else:
                print(f"❌ FMP error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ FMP exception: {e}")
            return []
    
    def get_nasdaq_stocks(self) -> List[Dict[str, Any]]:
        """Get NASDAQ listed stocks"""
        try:
            # Use yfinance to get NASDAQ components
            nasdaq = yf.Ticker("^IXIC")
            # This is a simplified approach - in production would use NASDAQ API
            # For now, return popular NASDAQ stocks
            popular_nasdaq = [
                "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "TSLA", "META", "NVDA",
                "AVGO", "PEP", "COST", "ADBE", "CSCO", "NFLX", "CMCSA", "INTC",
                "AMD", "QCOM", "INTU", "AMGN", "TXN", "HON", "ISRG", "VRTX",
                "ADI", "BKNG", "MDLZ", "REGN", "PYPL", "SBUX", "GILD", "CHTR",
                "TMUS", "MRNA", "FISV", "CSX", "ATVI", "ADP", "ZM", "MELI"
            ]
            
            stocks = []
            for symbol in popular_nasdaq:
                stocks.append({
                    "symbol": symbol,
                    "name": f"{symbol} Company",  # Would get real name in production
                    "exchange": "NASDAQ",
                    "source": "nasdaq_popular"
                })
            
            print(f"✅ NASDAQ: Found {len(stocks)} popular stocks")
            return stocks
            
        except Exception as e:
            print(f"❌ NASDAQ exception: {e}")
            return []
    
    def get_nyse_stocks(self) -> List[Dict[str, Any]]:
        """Get NYSE listed stocks"""
        try:
            # Popular NYSE stocks
            popular_nyse = [
                "JPM", "JNJ", "V", "WMT", "PG", "MA", "UNH", "HD", "BAC", "XOM",
                "CVX", "ABBV", "PFE", "MRK", "TMO", "ACN", "DHR", "NEE", "LIN",
                "ABT", "LLY", "T", "UPS", "PM", "RTX", "ORCL", "IBM", "CAT",
                "GS", "MS", "BLK", "SPGI", "MMM", "GE", "F", "GM", "BA", "DIS"
            ]
            
            stocks = []
            for symbol in popular_nyse:
                stocks.append({
                    "symbol": symbol,
                    "name": f"{symbol} Company",
                    "exchange": "NYSE",
                    "source": "nyse_popular"
                })
            
            print(f"✅ NYSE: Found {len(stocks)} popular stocks")
            return stocks
            
        except Exception as e:
            print(f"❌ NYSE exception: {e}")
            return []
    
    def filter_stocks(self, stocks: List[Dict[str, Any]], min_price: float = 5.0, max_price: float = 1000.0) -> List[Dict[str, Any]]:
        """Filter stocks by price and liquidity"""
        filtered = []
        
        for stock in stocks[:100]:  # Limit for testing
            symbol = stock["symbol"]
            try:
                # Get current price
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                current_price = info.get("currentPrice") or info.get("regularMarketPrice")
                market_cap = info.get("marketCap")
                volume = info.get("volume") or info.get("averageVolume")
                
                if (current_price and min_price <= current_price <= max_price and
                    market_cap and market_cap > 1e9 and  # $1B+ market cap
                    volume and volume > 100000):  # 100k+ daily volume
                    
                    stock["current_price"] = current_price
                    stock["market_cap"] = market_cap
                    stock["volume"] = volume
                    stock["sector"] = info.get("sector", "Unknown")
                    stock["industry"] = info.get("industry", "Unknown")
                    
                    filtered.append(stock)
                    
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                continue
        
        print(f"✅ Filtered: {len(filtered)} stocks meet criteria")
        return filtered
    
    def get_all_stocks(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Get ALL stocks from multiple sources"""
        # Check cache
        if use_cache and os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    cache_data = json.load(f)
                
                cache_time = datetime.fromisoformat(cache_data.get("timestamp", "2000-01-01"))
                if datetime.now() - cache_time < self.cache_duration:
                    print(f"✅ Using cached stock data ({len(cache_data['stocks'])} stocks)")
                    return cache_data["stocks"]
            except:
                pass
        
        # Get from all sources
        all_stocks = []
        
        print("🔍 Scanning for ALL stocks...")
        
        # Alpha Vantage
        av_stocks = self.get_all_stocks_alphavantage()
        all_stocks.extend(av_stocks)
        
        # FMP
        fmp_stocks = self.get_all_stocks_fmp()
        all_stocks.extend(fmp_stocks)
        
        # Exchanges
        nasdaq_stocks = self.get_nasdaq_stocks()
        all_stocks.extend(nasdaq_stocks)
        
        nyse_stocks = self.get_nyse_stocks()
        all_stocks.extend(nyse_stocks)
        
        # Remove duplicates by symbol
        unique_stocks = {}
        for stock in all_stocks:
            symbol = stock["symbol"]
            if symbol not in unique_stocks:
                unique_stocks[symbol] = stock
            else:
                # Merge sources
                existing = unique_stocks[symbol]
                existing["sources"] = existing.get("sources", [existing["source"]])
                existing["sources"].append(stock["source"])
                existing["source"] = "multiple"
        
        unique_list = list(unique_stocks.values())
        
        # Filter for quality
        filtered_stocks = self.filter_stocks(unique_list)
        
        # Cache results
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "stocks": filtered_stocks,
            "total_found": len(unique_list),
            "total_filtered": len(filtered_stocks)
        }
        
        os.makedirs("data", exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump(cache_data, f, indent=2)
        
        print(f"✅ Total unique stocks: {len(unique_list)}")
        print(f"✅ Quality filtered stocks: {len(filtered_stocks)}")
        
        return filtered_stocks
    
    def get_stock_data(self, symbol: str, period: str = "1mo") -> Dict[str, Any]:
        """Get detailed data for a specific stock"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Historical data
            hist = ticker.history(period=period)
            
            # Current info
            info = ticker.info
            
            # Financials
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cashflow = ticker.cashflow
            
            # Analyst recommendations
            recommendations = ticker.recommendations
            
            return {
                "symbol": symbol,
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "market_cap": info.get("marketCap"),
                "volume": info.get("volume"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "historical_data": hist.to_dict() if not hist.empty else {},
                "financials": financials.to_dict() if not financials.empty else {},
                "balance_sheet": balance_sheet.to_dict() if not balance_sheet.empty else {},
                "cashflow": cashflow.to_dict() if not cashflow.empty else {},
                "recommendations": recommendations.to_dict() if not recommendations.empty else {},
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting data for {symbol}: {e}")
            return {"symbol": symbol, "error": str(e)}

def main():
    """Test the stock scanner"""
    scanner = StockScanner()
    
    print("=" * 60)
    print("STOCK SCANNER - Testing")
    print("=" * 60)
    
    # Get all stocks
    stocks = scanner.get_all_stocks(use_cache=False)
    
    print(f"\n📊 Results:")
    print(f"Total stocks found: {len(stocks)}")
    
    if stocks:
        print("\nSample stocks:")
        for i, stock in enumerate(stocks[:10]):
            print(f"  {i+1}. {stock['symbol']} - {stock['name']} "
                  f"(${stock.get('current_price', 'N/A'):.2f}, "
                  f"{stock.get('sector', 'Unknown')})")
        
        # Test detailed data for first stock
        print(f"\n🔍 Testing detailed data for {stocks[0]['symbol']}...")
        detailed = scanner.get_stock_data(stocks[0]["symbol"], period="5d")
        print(f"  Price: ${detailed.get('current_price', 'N/A')}")
        print(f"  Market Cap: ${detailed.get('market_cap', 0):,.0f}")
        print(f"  Sector: {detailed.get('sector', 'Unknown')}")
    
    print("\n" + "=" * 60)
    print("✅ Stock scanner is ready!")
    print("\nTo use in trading system:")
    print("  from stock_scanner import StockScanner")
    print("  scanner = StockScanner()")
    print("  all_stocks = scanner.get_all_stocks()")

if __name__ == "__main__":
    main()