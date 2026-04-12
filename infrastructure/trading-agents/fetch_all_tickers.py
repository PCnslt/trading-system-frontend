#!/usr/bin/env python3
"""
Fetch thousands of stock tickers and cryptocurrencies from multiple sources.
Uses free APIs and Hugging Face datasets to get comprehensive ticker lists.
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime
import time
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TickerFetcher:
    """Fetch tickers from multiple sources"""
    
    def __init__(self):
        self.tickers = {
            'stocks': [],
            'crypto': [],
            'etfs': [],
            'indices': []
        }
        
    def fetch_nasdaq_tickers(self) -> List[Dict[str, Any]]:
        """Fetch NASDAQ listed stocks"""
        try:
            # NASDAQ API for listed companies
            url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=5000"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                stocks = []
                for item in data.get('data', {}).get('table', {}).get('rows', []):
                    stocks.append({
                        'symbol': item.get('symbol', ''),
                        'name': item.get('name', ''),
                        'sector': item.get('sector', ''),
                        'industry': item.get('industry', ''),
                        'market_cap': item.get('marketCap', ''),
                        'price': item.get('lastsale', ''),
                        'volume': item.get('volume', ''),
                        'exchange': 'NASDAQ'
                    })
                logger.info(f"Fetched {len(stocks)} NASDAQ stocks")
                return stocks
        except Exception as e:
            logger.error(f"Error fetching NASDAQ tickers: {e}")
        return []
    
    def fetch_nyse_tickers(self) -> List[Dict[str, Any]]:
        """Fetch NYSE listed stocks"""
        try:
            # NYSE API (similar structure)
            url = "https://www.nyse.com/api/quotes/filter"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/json'
            }
            payload = {
                "instrumentType": "EQUITY",
                "pageNumber": 1,
                "sortColumn": "NORMALIZED_TICKER",
                "sortOrder": "ASC",
                "maxResultsPerPage": 5000,
                "filterToken": ""
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                stocks = []
                for item in data:
                    stocks.append({
                        'symbol': item.get('symbolTicker', ''),
                        'name': item.get('instrumentName', ''),
                        'sector': item.get('sector', ''),
                        'industry': item.get('industry', ''),
                        'market_cap': item.get('marketCap', ''),
                        'price': item.get('lastPrice', ''),
                        'volume': item.get('volume', ''),
                        'exchange': 'NYSE'
                    })
                logger.info(f"Fetched {len(stocks)} NYSE stocks")
                return stocks
        except Exception as e:
            logger.error(f"Error fetching NYSE tickers: {e}")
        return []
    
    def fetch_crypto_tickers(self) -> List[Dict[str, Any]]:
        """Fetch cryptocurrency tickers from CoinGecko"""
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 250,
                'page': 1,
                'sparkline': 'false'
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                cryptos = []
                for item in response.json():
                    cryptos.append({
                        'symbol': item.get('symbol', '').upper(),
                        'name': item.get('name', ''),
                        'market_cap': item.get('market_cap', 0),
                        'price': item.get('current_price', 0),
                        'volume': item.get('total_volume', 0),
                        'price_change_24h': item.get('price_change_percentage_24h', 0),
                        'market_cap_rank': item.get('market_cap_rank', 0)
                    })
                logger.info(f"Fetched {len(cryptos)} cryptocurrencies")
                return cryptos
        except Exception as e:
            logger.error(f"Error fetching crypto tickers: {e}")
        return []
    
    def fetch_etf_tickers(self) -> List[Dict[str, Any]]:
        """Fetch ETF tickers"""
        try:
            # Use ETF Database or similar source
            etfs = [
                {'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF', 'category': 'Large Cap'},
                {'symbol': 'QQQ', 'name': 'Invesco QQQ Trust', 'category': 'Technology'},
                {'symbol': 'DIA', 'name': 'SPDR Dow Jones ETF', 'category': 'Large Cap'},
                {'symbol': 'IWM', 'name': 'iShares Russell 2000 ETF', 'category': 'Small Cap'},
                {'symbol': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'category': 'Total Market'},
                {'symbol': 'VOO', 'name': 'Vanguard S&P 500 ETF', 'category': 'Large Cap'},
                {'symbol': 'IVV', 'name': 'iShares Core S&P 500 ETF', 'category': 'Large Cap'},
                {'symbol': 'VEA', 'name': 'Vanguard FTSE Developed Markets ETF', 'category': 'International'},
                {'symbol': 'VWO', 'name': 'Vanguard FTSE Emerging Markets ETF', 'category': 'Emerging Markets'},
                {'symbol': 'BND', 'name': 'Vanguard Total Bond Market ETF', 'category': 'Bond'},
                {'symbol': 'AGG', 'name': 'iShares Core U.S. Aggregate Bond ETF', 'category': 'Bond'},
                {'symbol': 'LQD', 'name': 'iShares iBoxx $ Investment Grade Corporate Bond ETF', 'category': 'Corporate Bond'},
                {'symbol': 'HYG', 'name': 'iShares iBoxx $ High Yield Corporate Bond ETF', 'category': 'High Yield Bond'},
                {'symbol': 'GLD', 'name': 'SPDR Gold Shares', 'category': 'Commodity'},
                {'symbol': 'SLV', 'name': 'iShares Silver Trust', 'category': 'Commodity'},
                {'symbol': 'USO', 'name': 'United States Oil Fund', 'category': 'Commodity'},
                {'symbol': 'TLT', 'name': 'iShares 20+ Year Treasury Bond ETF', 'category': 'Treasury Bond'},
                {'symbol': 'IEF', 'name': 'iShares 7-10 Year Treasury Bond ETF', 'category': 'Treasury Bond'},
                {'symbol': 'SHY', 'name': 'iShares 1-3 Year Treasury Bond ETF', 'category': 'Treasury Bond'},
                {'symbol': 'MUB', 'name': 'iShares National Muni Bond ETF', 'category': 'Municipal Bond'}
            ]
            logger.info(f"Loaded {len(etfs)} ETFs")
            return etfs
        except Exception as e:
            logger.error(f"Error fetching ETF tickers: {e}")
        return []
    
    def fetch_from_huggingface(self) -> List[Dict[str, Any]]:
        """Fetch tickers from Hugging Face datasets"""
        try:
            # Using Hugging Face datasets API
            url = "https://datasets-server.huggingface.co/rows"
            params = {
                'dataset': 'huggingface/financial-data',
                'config': 'default',
                'split': 'train',
                'offset': 0,
                'length': 1000
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                stocks = []
                for row in data.get('rows', []):
                    item = row.get('row', {})
                    stocks.append({
                        'symbol': item.get('symbol', ''),
                        'name': item.get('name', ''),
                        'sector': item.get('sector', ''),
                        'industry': item.get('industry', ''),
                        'market_cap': item.get('market_cap', 0),
                        'price': item.get('price', 0),
                        'volume': item.get('volume', 0)
                    })
                logger.info(f"Fetched {len(stocks)} stocks from Hugging Face")
                return stocks
        except Exception as e:
            logger.error(f"Error fetching from Hugging Face: {e}")
        return []
    
    def fetch_all_tickers(self) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch all tickers from multiple sources"""
        logger.info("Starting ticker fetch from all sources...")
        
        # Fetch from multiple sources in parallel (simulated)
        nasdaq_stocks = self.fetch_nasdaq_tickers()
        nyse_stocks = self.fetch_nyse_tickers()
        crypto_tickers = self.fetch_crypto_tickers()
        etf_tickers = self.fetch_etf_tickers()
        hf_stocks = self.fetch_from_huggingface()
        
        # Combine and deduplicate
        all_stocks = {}
        for stock in nasdaq_stocks + nyse_stocks + hf_stocks:
            symbol = stock.get('symbol', '')
            if symbol and symbol not in all_stocks:
                all_stocks[symbol] = stock
        
        self.tickers['stocks'] = list(all_stocks.values())
        self.tickers['crypto'] = crypto_tickers
        self.tickers['etfs'] = etf_tickers
        
        # Add indices
        self.tickers['indices'] = [
            {'symbol': '^GSPC', 'name': 'S&P 500', 'type': 'Index'},
            {'symbol': '^DJI', 'name': 'Dow Jones Industrial Average', 'type': 'Index'},
            {'symbol': '^IXIC', 'name': 'NASDAQ Composite', 'type': 'Index'},
            {'symbol': '^RUT', 'name': 'Russell 2000', 'type': 'Index'},
            {'symbol': '^VIX', 'name': 'CBOE Volatility Index', 'type': 'Index'}
        ]
        
        logger.info(f"Total fetched: {len(self.tickers['stocks'])} stocks, "
                   f"{len(self.tickers['crypto'])} crypto, "
                   f"{len(self.tickers['etfs'])} ETFs")
        
        return self.tickers
    
    def save_to_json(self, filename: str = "all_tickers.json"):
        """Save tickers to JSON file"""
        data = {
            'metadata': {
                'fetched_at': datetime.now().isoformat(),
                'total_stocks': len(self.tickers['stocks']),
                'total_crypto': len(self.tickers['crypto']),
                'total_etfs': len(self.tickers['etfs']),
                'total_indices': len(self.tickers['indices'])
            },
            'tickers': self.tickers
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved tickers to {filename}")
        return filename
    
    def save_to_backend_format(self, backend_dir: str = "../backend/src/main/resources"):
        """Save tickers in format for Spring Boot backend"""
        # Create Java enum/class content
        java_content = self._generate_java_class()
        
        os.makedirs(backend_dir, exist_ok=True)
        java_file = os.path.join(backend_dir, "TickerDatabase.java")
        
        with open(java_file, 'w') as f:
            f.write(java_content)
        
        logger.info(f"Saved Java class to {java_file}")
        return java_file
    
    def _generate_java_class(self) -> str:
        """Generate Java class with all tickers"""
        java_code = """package com.trading.system.model;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

/**
 * Comprehensive Ticker Database with thousands of stocks and cryptocurrencies
 * Auto-generated from multiple data sources
 */
public class TickerDatabase {
    
    // Stock Tickers (Thousands)
    public static final List<String> ALL_STOCKS = Arrays.asList(
"""
        
        # Add stocks (limit to 500 for readability)
        stock_symbols = [t['symbol'] for t in self.tickers['stocks'][:500]]
        for i in range(0, len(stock_symbols), 20):
            batch = stock_symbols[i:i+20]
            java_code += '        "' + '", "'.join(batch) + '",\n'
        
        java_code += """    );
    
    // Cryptocurrencies
    public static final List<String> ALL_CRYPTO = Arrays.asList(
"""
        
        crypto_symbols = [t['symbol'] for t in self.tickers['crypto']]
        for i in range(0, len(crypto_symbols), 20):
            batch = crypto_symbols[i:i+20]
            java_code += '        "' + '", "'.join(batch) + '",\n'
        
        java_code += """    );
    
    // ETFs
    public static final List<String> ALL_ETFS = Arrays.asList(
"""
        
        etf_symbols = [t['symbol'] for t in self.tickers['etfs']]
        for i in range(0, len(etf_symbols), 20):
            batch = etf_symbols[i:i+20]
            java_code += '        "' + '", "'.join(batch) + '",\n'
        
        java_code += """    );
    
    // Indices
    public static final List<String> ALL_INDICES = Arrays.asList(
        "^GSPC", "^DJI", "^IXIC", "^RUT", "^VIX"
    );
    
    // Get all tickers combined
    public static List<String> getAllTickers() {
        return Arrays.asList(
"""
        
        # Combine all symbols
        all_symbols = stock_symbols[:100] + crypto_symbols[:50] + etf_symbols + ["^GSPC", "^DJI", "^IXIC", "^RUT", "^VIX"]
        for i in range(0, len(all_symbols), 20):
            batch = all_symbols[i:i+20]
            java_code += '            "' + '", "'.join(batch) + '",\n'
        
        java_code += """        );
    }
    
    // Get ticker info
    public static Map<String, String> getTickerInfo(String symbol) {
        Map<String, String> info = new HashMap<>();
        info.put("symbol", symbol);
        
        if (ALL_STOCKS.contains(symbol)) {
            info.put("type", "STOCK");
            info.put("exchange", "NASDAQ/NYSE");
        } else if (ALL_CRYPTO.contains(symbol)) {
            info.put("type", "CRYPTO");
            info.put("exchange", "Crypto Exchange");
        } else if (ALL_ETFS.contains(symbol)) {
            info.put("type", "ETF");
            info.put("exchange", "NYSE/NASDAQ");
        } else if (ALL_INDICES.contains(symbol)) {
            info.put("type", "INDEX");
            info.put("exchange", "CBOE/NYSE");
        } else {
            info.put("type", "UNKNOWN");
            info.put("exchange", "Unknown");
        }
        
        return info;
    }
    
    // Get count statistics
    public static Map<String, Integer> getTickerStats() {
        Map<String, Integer> stats = new HashMap<>();
        stats.put("stocks", ALL_STOCKS.size());
        stats.put("crypto", ALL_CRYPTO.size());
        stats.put("etfs", ALL_ETFS.size());
        stats.put("indices", ALL_INDICES.size());
        stats.put("total", ALL_STOCKS.size() + ALL_CRYPTO.size() + ALL_ETFS.size() + ALL_INDICES.size());
        return stats;
    }
}
"""
        
        return java_code

def main():
    """Main function"""
    logger.info("Starting comprehensive ticker fetch...")
    
    fetcher = TickerFetcher()
    
    # Fetch all tickers
    tickers = fetcher.fetch_all_tickers()
    
    # Save to JSON
    json_file = fetcher.save_to_json("all_tickers.json")
    logger.info(f"Saved to JSON: {json_file}")
    
    # Save to backend format
    java_file = fetcher.save_to_backend_format()
    logger.info(f"Saved to Java class: {java_file}")
    
    # Print statistics
    stats = {
        'stocks': len(tickers['stocks']),
        'crypto': len(tickers['crypto']),
        'etfs': len(tickers['etfs']),
        'indices': len(tickers['indices']),
        'total': len(tickers['stocks']) + len(tickers['crypto']) + len(tickers['etfs']) + len(tickers['indices'])
    }
    
    logger.info(f"Ticker Statistics: {stats}")
    
    # Also create a smaller version for testing
    test_tickers = {
        'stocks': tickers['stocks'][:100],  # First 100 stocks for testing
        'crypto':