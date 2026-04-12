#!/usr/bin/env python3
"""
Enhanced Trading Agent System with Hugging Face models and RAG
Uses free most powerful Hugging Face models for analysis
"""

import os
import json
import requests
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass, asdict
import sqlite3
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hugging Face Free Models (most powerful free options)
HUGGINGFACE_MODELS = {
    "analysis": "mistralai/Mistral-7B-Instruct-v0.3",  # Powerful 7B model
    "sentiment": "cardiffnlp/twitter-roberta-base-sentiment-latest",
    "financial": "yiyanghkust/finbert-tone",  # Financial sentiment
    "embedding": "sentence-transformers/all-MiniLM-L6-v2",  # For RAG
    "reasoning": "microsoft/phi-2",  # Good reasoning capabilities
    "summarization": "facebook/bart-large-cnn"
}

class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"

@dataclass
class AnalysisResult:
    symbol: str
    agent_type: str
    signal: Signal
    confidence: float
    reasoning: str
    indicators: Dict[str, Any]
    timestamp: str
    model_used: str
    
    def to_dict(self):
        return {
            **asdict(self),
            "signal": self.signal.value
        }

class HuggingFaceAnalyzer:
    """Analyze using Hugging Face free models"""
    
    def __init__(self, api_token: str = None):
        self.api_token = api_token or os.getenv("HUGGINGFACE_TOKEN")
        self.base_url = "https://api-inference.huggingface.co/models"
        
    def analyze_with_model(self, prompt: str, model: str, max_length: int = 500) -> str:
        """Analyze using Hugging Face model"""
        try:
            headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": max_length,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{self.base_url}/{model}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', str(result))
                return str(result)
            else:
                logger.warning(f"Hugging Face API error: {response.status_code}")
                return self._fallback_analysis(prompt)
                
        except Exception as e:
            logger.error(f"Error analyzing with Hugging Face: {e}")
            return self._fallback_analysis(prompt)
    
    def _fallback_analysis(self, prompt: str) -> str:
        """Fallback analysis when API fails"""
        # Simple rule-based fallback
        if "positive" in prompt.lower():
            return "Analysis indicates positive outlook based on available data."
        elif "negative" in prompt.lower():
            return "Analysis indicates negative outlook based on available data."
        else:
            return "Analysis completed with neutral outlook."

class RAGMemorySystem:
    """RAG (Retrieval-Augmented Generation) memory system for agents"""
    
    def __init__(self, db_path: str = "trading_memory.db"):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create analysis history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                signal TEXT NOT NULL,
                confidence REAL NOT NULL,
                reasoning TEXT,
                indicators TEXT,
                timestamp DATETIME NOT NULL,
                model_used TEXT,
                success BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create market knowledge base
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT,
                embedding BLOB,
                timestamp DATETIME NOT NULL
            )
        ''')
        
        # Create performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_type TEXT NOT NULL,
                total_analyses INTEGER DEFAULT 0,
                successful_analyses INTEGER DEFAULT 0,
                avg_confidence REAL DEFAULT 0,
                last_analysis DATETIME,
                best_symbol TEXT,
                worst_symbol TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def store_analysis(self, analysis: AnalysisResult):
        """Store analysis in memory database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_history 
            (symbol, agent_type, signal, confidence, reasoning, indicators, timestamp, model_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis.symbol,
            analysis.agent_type,
            analysis.signal.value,
            analysis.confidence,
            analysis.reasoning,
            json.dumps(analysis.indicators),
            analysis.timestamp,
            analysis.model_used
        ))
        
        conn.commit()
        conn.close()
        
    def retrieve_similar_analyses(self, symbol: str, agent_type: str, limit: int = 5) -> List[Dict]:
        """Retrieve similar past analyses for context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol, agent_type, signal, confidence, reasoning, timestamp
            FROM analysis_history
            WHERE symbol = ? OR agent_type = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (symbol, agent_type, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'symbol': row[0],
                'agent_type': row[1],
                'signal': row[2],
                'confidence': row[3],
                'reasoning': row[4],
                'timestamp': row[5]
            })
        
        conn.close()
        return results
    
    def get_agent_performance(self, agent_type: str) -> Dict:
        """Get performance metrics for an agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                AVG(confidence) as avg_confidence,
                MAX(timestamp) as last_analysis
            FROM analysis_history
            WHERE agent_type = ?
        ''', (agent_type,))
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            'total_analyses': row[0] if row else 0,
            'avg_confidence': row[1] if row and row[1] else 0,
            'last_analysis': row[2] if row else None
        }

class EnhancedTradingAgent:
    """Enhanced trading agent with Hugging Face models and RAG memory"""
    
    def __init__(self, agent_type: str, hf_token: str = None):
        self.agent_type = agent_type
        self.analyzer = HuggingFaceAnalyzer(hf_token)
        self.memory = RAGMemorySystem()
        self.model = self._select_model_for_agent()
        
    def _select_model_for_agent(self) -> str:
        """Select appropriate Hugging Face model for agent type"""
        model_map = {
            "technical": HUGGINGFACE_MODELS["analysis"],
            "fundamental": HUGGINGFACE_MODELS["financial"],
            "sentiment": HUGGINGFACE_MODELS["sentiment"],
            "macro": HUGGINGFACE_MODELS["analysis"],
            "crypto": HUGGINGFACE_MODELS["analysis"],
            "options": HUGGINGFACE_MODELS["reasoning"],
            "risk": HUGGINGFACE_MODELS["reasoning"],
            "quant": HUGGINGFACE_MODELS["analysis"],
            "sector": HUGGINGFACE_MODELS["analysis"],
            "compliance": HUGGINGFACE_MODELS["analysis"]
        }
        return model_map.get(self.agent_type, HUGGINGFACE_MODELS["analysis"])
    
    def analyze(self, symbol: str, market_data: Dict[str, Any]) -> AnalysisResult:
        """Analyze symbol with enhanced capabilities"""
        logger.info(f"{self.agent_type} agent analyzing {symbol}")
        
        # Retrieve similar past analyses for context
        past_analyses = self.memory.retrieve_similar_analyses(symbol, self.agent_type)
        
        # Prepare context for analysis
        context = self._prepare_context(symbol, market_data, past_analyses)
        
        # Generate analysis prompt
        prompt = self._generate_analysis_prompt(symbol, context)
        
        # Use Hugging Face model for analysis
        analysis_text = self.analyzer.analyze_with_model(prompt, self.model)
        
        # Parse analysis results
        signal, confidence, reasoning = self._parse_analysis_results(analysis_text, symbol)
        
        # Generate indicators
        indicators = self._generate_indicators(market_data)
        
        # Create analysis result
        result = AnalysisResult(
            symbol=symbol,
            agent_type=self.agent_type,
            signal=signal,
            confidence=confidence,
            reasoning=reasoning,
            indicators=indicators,
            timestamp=datetime.now().isoformat(),
            model_used=self.model
        )
        
        # Store in memory
        self.memory.store_analysis(result)
        
        return result
    
    def _prepare_context(self, symbol: str, market_data: Dict, past_analyses: List[Dict]) -> str:
        """Prepare context for analysis"""
        context_parts = []
        
        # Add market data context
        if market_data:
            context_parts.append(f"Current market data for {symbol}:")
            for key, value in market_data.items():
                if isinstance(value, (int, float)):
                    context_parts.append(f"  {key}: {value:.2f}")
                else:
                    context_parts.append(f"  {key}: {value}")
        
        # Add past analyses context
        if past_analyses:
            context_parts.append(f"\nPast analyses for {symbol}:")
            for analysis in past_analyses[:3]:  # Last 3 analyses
                context_parts.append(
                    f"  {analysis['timestamp']}: {analysis['signal']} "
                    f"(confidence: {analysis['confidence']:.1%}) - {analysis['reasoning'][:100]}..."
                )
        
        # Add agent-specific context
        context_parts.append(f"\n{self.agent_type.capitalize()} analysis perspective:")
        context_parts.append(self._get_agent_perspective())
        
        return "\n".join(context_parts)
    
    def _get_agent_perspective(self) -> str:
        """Get agent-specific analysis perspective"""
        perspectives = {
            "technical": "Focus on price trends, technical indicators, chart patterns, and momentum.",
            "fundamental": "Focus on financial statements, valuation metrics, growth prospects, and competitive position.",
            "sentiment": "Focus on market sentiment, news analysis, social media buzz, and investor psychology.",
            "macro": "Focus on economic indicators, interest rates, inflation, geopolitical factors, and policy impacts.",
            "crypto": "Focus on blockchain metrics, adoption trends, regulatory environment, and crypto-specific factors.",
            "options": "Focus on options flow, implied volatility, Greeks, and derivatives market sentiment.",
            "risk": "Focus on risk metrics, drawdown potential, volatility, and portfolio risk management.",
            "quant": "Focus on statistical models, algorithmic signals, quantitative factors, and data patterns.",
            "sector": "Focus on industry trends, competitive landscape, sector rotation, and thematic investing.",
            "compliance": "Focus on regulatory requirements, compliance checks, legal considerations, and risk controls."
        }
        return perspectives.get(self.agent_type, "General market analysis.")
    
    def _generate_analysis_prompt(self, symbol: str, context: str) -> str:
        """Generate analysis prompt for Hugging Face model"""
        prompt = f"""As a {self.agent_type} trading analyst, analyze {symbol} based on the following context:

{context}

Provide a comprehensive analysis with:
1. Clear trading signal (BUY, SELL, or HOLD)
2. Confidence level (0-100%)
3. Detailed reasoning based on {self.agent_type} factors
4. Key indicators supporting your analysis

Format your response as:
SIGNAL: [BUY/SELL/HOLD]
CONFIDENCE: [0-100]%
REASONING: [Detailed analysis here]
INDICATORS: [Key indicators]

Analysis:"""
        
        return prompt
    
    def _parse_analysis_results(self, analysis_text: str, symbol: str) -> tuple:
        """Parse analysis results from model output"""
        # Default values
        signal = Signal.HOLD
        confidence = 0.5
        reasoning = analysis_text[:500]  # Truncate if too long
        
        try:
            # Parse signal
            if "BUY" in analysis_text.upper():
                signal = Signal.BUY
            elif "SELL" in analysis_text.upper():
                signal = Signal.SELL
            elif "HOLD" in analysis_text.upper():
                signal = Signal.HOLD
            
            # Parse confidence
            import re
            confidence_match = re.search(r'CONFIDENCE:\s*(\d+)%', analysis_text.upper())
            if confidence_match:
                confidence = float(confidence_match.group(1)) / 100.0
            else:
                # Estimate confidence based on text
                if "high confidence" in analysis_text.lower():
                    confidence = 0.8
                elif "moderate confidence" in analysis_text.lower():
                    confidence = 0.6
                elif "low confidence" in analysis_text.lower():
                    confidence = 0.4
            
            # Extract reasoning
            reasoning_match = re.search(r'REASONING:\s*(.+?)(?=\n\w+:|$)', analysis_text, re.DOTALL | re.IGNORECASE)
            if reasoning_match:
                reasoning = reasoning_match.group(1).strip()
                
        except Exception as e:
            logger.warning(f"Error parsing analysis results: {e}")
            reasoning = f"Analysis completed for {symbol}. {analysis_text[:200]}"
        
        return signal, confidence, reasoning
    
    def _generate_indicators(self, market_data: Dict) -> Dict[str, Any]:
        """Generate indicators based on market data"""
        indicators = {}
        
        if not market_data:
            return {"status": "No market data available"}
        
        # Common indicators
        if 'price' in market_data and 'volume' in market_data:
            price = market_data['price']
            volume = market_data['volume']
            
            # Simulate some indicators
            indicators['price_trend'] = "up" if price > 100 else "down" if price < 50 else "neutral"
            indicators['volume_trend'] = "high" if volume > 1000000 else "low"
            indicators['liquidity'] = "good" if volume > 500000 else "poor"
        
        # Agent-specific indicators
        if self.agent_type == "technical":
            indicators['rsi'] = np.random.uniform(30, 70)
            indicators['macd'] = "bullish" if np.random.random() > 0.5 else "bearish"
            indicators['bollinger_band'] = "within" if np.random.random() > 0.3 else "outside"
            
        elif self.agent_type == "fundamental":
            indicators['pe_ratio'] = np.random.uniform(10, 30)
            indicators['profit_margin'] = np.random.uniform(5, 25)
            indicators['debt_to_equity'] = np.random.uniform(0.5, 2)
            
        elif self.agent_type == "sentiment":
            indicators['sentiment_score'] = np.random.uniform(-1, 1)
            indicators['news_coverage'] = np.random.uniform(0, 100)
            indicators['social_buzz'] = np.random.uniform(0, 100)
        
        return indicators

class TradingAgentOrchestrator:
    """Orchestrator for all 10 trading agents"""
    
    def __init__(self, hf_token: str = None):
        self.agents = {}
        self.hf_token = hf_token
        self.memory = RAGMemorySystem()
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize all 10 trading agents"""
        agent_types = [
            "technical", "fundamental", "sentiment", "macro", "crypto",
            "options", "risk", "quant", "sector", "compliance"
        ]
        
        for agent_type in agent_types:
            self.agents[agent_type] = EnhancedTradingAgent(agent_type, self.hf_token)
            logger.info(f"Initialized {agent_type} agent")
    
    def analyze_symbol(self, symbol: str, market_data: Dict = None) -> Dict[str, Any]:
        """Analyze symbol with all agents"""
        logger.info(f"Analyzing {symbol} with all 10 agents")
        
        if market_data is None:
            market_data = self._get_market_data(symbol)
        
        results = {}
        consensus_signals = {"BUY": 0, "SELL": 0, "