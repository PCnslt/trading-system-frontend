#!/usr/bin/env python3
"""
Daily Trading Analysis Script
Runs complete trading pipeline and saves results
"""

import os
import sys
import json
from datetime import datetime
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.complete_trading_pipeline import CompleteTradingPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/trading_analysis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_daily_analysis():
    """Run complete daily analysis"""
    
    logger.info("=" * 70)
    logger.info("STARTING DAILY TRADING ANALYSIS")
    logger.info("=" * 70)
    
    try:
        # Initialize pipeline
        pipeline = CompleteTradingPipeline()
        
        # Run analysis
        logger.info("Running complete trading pipeline...")
        result = pipeline.run_daily_pipeline(max_stocks=100)
        
        # Print final report
        pipeline.print_final_report(result)
        
        # Save summary
        summary_file = f"/app/data/daily_reports/summary_{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(summary_file, "w") as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"Analysis complete. Results saved to {summary_file}")
        
        # Check if we have a BUY decision
        final_decision = result.get("final_decision", {})
        if final_decision.get("decision") == "BUY":
            logger.info(f"✅ BUY RECOMMENDATION: {final_decision.get('symbol')}")
            logger.info(f"   Expected Return: {final_decision.get('expected_return', 0):.2%}")
            logger.info(f"   Confidence: {final_decision.get('confidence', 0):.1%}")
            
            # Send notification (in production would be email/SMS)
            notification = {
                "type": "buy_recommendation",
                "symbol": final_decision.get("symbol"),
                "expected_return": final_decision.get("expected_return"),
                "confidence": final_decision.get("confidence"),
                "timestamp": datetime.now().isoformat(),
                "message": f"Buy {final_decision.get('symbol')} - Expected return: {final_decision.get('expected_return', 0):.2%}"
            }
            
            notification_file = f"/app/data/notifications/notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs(os.path.dirname(notification_file), exist_ok=True)
            with open(notification_file, "w") as f:
                json.dump(notification, f, indent=2)
            
            logger.info(f"Notification saved to {notification_file}")
        
        logger.info("=" * 70)
        logger.info("DAILY ANALYSIS COMPLETE")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"Error running daily analysis: {e}", exc_info=True)
        return False

def update_performance():
    """Update performance metrics with actual returns"""
    try:
        from agents.trading_leader import TradingLeader
        
        logger.info("Updating performance metrics...")
        leader = TradingLeader()
        leader.update_performance()
        
        logger.info("Performance metrics updated")
        return True
        
    except Exception as e:
        logger.error(f"Error updating performance: {e}")
        return False

def main():
    """Main function"""
    
    # Create necessary directories
    os.makedirs("/app/data/daily_reports", exist_ok=True)
    os.makedirs("/app/data/agent_results", exist_ok=True)
    os.makedirs("/app/data/performance", exist_ok=True)
    os.makedirs("/app/data/notifications", exist_ok=True)
    os.makedirs("/app/logs", exist_ok=True)
    
    # Run daily analysis
    success = run_daily_analysis()
    
    # Update performance metrics
    if success:
        update_performance()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()