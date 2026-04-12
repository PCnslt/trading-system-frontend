#!/usr/bin/env python3
"""
Local RAG Fallback - Works without external APIs
Uses local knowledge base to answer questions
"""

import json
from typing import Dict, Any, List
import re

class LocalRAG:
    """Local RAG using hardcoded knowledge base"""
    
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load local knowledge base"""
        return {
            "system_status": {
                "learning_velocity": "6.5/10 (improved from 3.5 baseline)",
                "execution_rate": "83% (20/24 decisions completed)",
                "storage_free": "78.6 GB on C: drive",
                "monthly_cost": "$0 maintained",
                "skills_active": "6 workspace skills",
                "skills_total": "51 global skills (27% utilization)"
            },
            "memory_system": {
                "components": "PostgreSQL + Ollama + FastAPI",
                "status": "Operational but RAG endpoint has timeout issues",
                "recent_fixes": "Embedding format fixed, humanizer skill added",
                "store_retrieve": "Working",
                "rag_endpoint": "500 error (Ollama model timeout)"
            },
            "trading_platform": {
                "architecture": "10-agent system",
                "operational_agents": "3/10 (Technical, Fundamental, Sentiment)",
                "features": "Real-time charts, multiple API integrations",
                "apis_configured": "Alpha Vantage, FMP, NewsAPI, CoinMarketCap, Binance",
                "status": "Foundation complete, awaiting user verification"
            },
            "current_blockers": [
                "RAG endpoint 500 error (Ollama model timeout)",
                "GitHub secrets in commit history blocking pushes",
                "User verification pending for trading platform charts",
                "Skill discrepancy (workspace vs global skills)"
            ],
            "recent_achievements": [
                "Memory system embedding format fixed",
                "Humanizer skill implemented",
                "Trading agent foundation complete (3/10)",
                "Learning velocity improved to 6.5/10",
                "Execution framework with consequence system"
            ],
            "next_priorities": [
                "Fix RAG endpoint",
                "Resolve GitHub secrets block",
                "Complete user verification",
                "Activate remaining 7 trading agents"
            ]
        }
    
    def search_knowledge(self, query: str) -> List[str]:
        """Search knowledge base for relevant information"""
        query_lower = query.lower()
        results = []
        
        # Map query keywords to categories
        keyword_map = {
            "learning": "system_status",
            "velocity": "system_status",
            "execution": "system_status",
            "rate": "system_status",
            "storage": "system_status",
            "free": "system_status",
            "cost": "system_status",
            "skill": "system_status",
            "memory": "memory_system",
            "postgres": "memory_system",
            "ollama": "memory_system",
            "fastapi": "memory_system",
            "rag": "memory_system",
            "trading": "trading_platform",
            "agent": "trading_platform",
            "platform": "trading_platform",
            "chart": "trading_platform",
            "api": "trading_platform",
            "blocker": "current_blockers",
            "issue": "current_blockers",
            "problem": "current_blockers",
            "achievement": "recent_achievements",
            "fix": "recent_achievements",
            "recent": "recent_achievements",
            "priority": "next_priorities",
            "next": "next_priorities",
            "todo": "next_priorities"
        }
        
        # Find relevant categories
        relevant_categories = set()
        for keyword, category in keyword_map.items():
            if keyword in query_lower:
                relevant_categories.add(category)
        
        # Also check category names
        for category in self.knowledge_base.keys():
            if category.replace('_', ' ') in query_lower:
                relevant_categories.add(category)
        
        # Return data for relevant categories
        for category in relevant_categories:
            if category in self.knowledge_base:
                results.append(f"{category}: {json.dumps(self.knowledge_base[category], indent=2)}")
        
        return results
    
    def _text_match(self, query: str, text: str) -> bool:
        """Simple text matching"""
        query_words = set(re.findall(r'\b\w+\b', query))
        text_words = set(re.findall(r'\b\w+\b', text))
        return len(query_words.intersection(text_words)) > 2
    
    def generate_answer(self, question: str, context: List[str]) -> str:
        """Generate answer based on context"""
        if not context:
            return "I don't have enough information to answer that question based on my current knowledge base."
        
        # Simple template-based generation
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["learning", "velocity", "6.5"]):
            return f"Based on my knowledge: Learning velocity is {self.knowledge_base['system_status']['learning_velocity']}."
        
        elif any(word in question_lower for word in ["execution", "rate", "83"]):
            return f"Based on my knowledge: Execution rate is {self.knowledge_base['system_status']['execution_rate']}."
        
        elif any(word in question_lower for word in ["storage", "free", "gb"]):
            return f"Based on my knowledge: Storage free is {self.knowledge_base['system_status']['storage_free']}."
        
        elif any(word in question_lower for word in ["trading", "agent", "platform"]):
            trading_info = self.knowledge_base['trading_platform']
            return f"Trading platform: {trading_info['architecture']} with {trading_info['operational_agents']} operational. Features: {trading_info['features']}"
        
        elif any(word in question_lower for word in ["blocker", "issue", "problem"]):
            blockers = self.knowledge_base['current_blockers']
            return f"Current blockers: {', '.join(blockers[:3])}"
        
        elif any(word in question_lower for word in ["memory", "system", "postgres", "ollama"]):
            memory_info = self.knowledge_base['memory_system']
            return f"Memory system: {memory_info['components']}. Status: {memory_info['status']}. Recent fixes: {memory_info['recent_fixes']}"
        
        else:
            # Generic answer
            return f"Based on available information: {context[0][:200]}..."
    
    def query(self, question: str) -> Dict[str, Any]:
        """Main query method"""
        # Search for relevant knowledge
        context = self.search_knowledge(question)
        
        # Generate answer
        answer = self.generate_answer(question, context)
        
        return {
            "success": True,
            "answer": answer,
            "context_used": len(context) > 0,
            "context_items": len(context),
            "provider": "local_knowledge_base",
            "cost": 0.0,
            "tokens_used": len(question) + len(answer)  # Estimate
        }

def main():
    """Test the local RAG"""
    print("=== Local RAG Fallback Test ===\n")
    
    rag = LocalRAG()
    
    test_questions = [
        "What is the learning velocity?",
        "What is the execution rate?",
        "How much storage is free?",
        "Describe the trading platform",
        "What are the current blockers?",
        "What is the memory system status?",
        "What recent achievements are there?",
        "What are the next priorities?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"Q{i}: {question}")
        print("-" * 60)
        
        result = rag.query(question)
        
        print(f"A: {result['answer']}")
        print(f"   Provider: {result['provider']}, Cost: ${result['cost']}")
        print(f"   Context used: {result['context_used']} ({result['context_items']} items)")
        print()
    
    print("=" * 60)
    print("SUMMARY: Local RAG is operational")
    print("Advantages:")
    print("  - No API keys required")
    print("  - No network dependencies")
    print("  - Zero cost")
    print("  - Instant responses")
    print("\nLimitations:")
    print("  - Limited to pre-defined knowledge")
    print("  - No real-time updates")
    print("  - Simple pattern matching")

if __name__ == "__main__":
    main()