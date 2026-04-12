#!/usr/bin/env python3
"""Simple test without emojis"""
import os

print("Testing Trading System Components...")
print("=" * 60)

# Check files
print("\n1. Checking files...")
files_to_check = [
    "stock_scanner.py",
    "enhanced_technical_analyst.py", 
    "trading_leader.py",
    "complete_trading_pipeline.py",
    "docker-compose.trading.yml",
    "Dockerfile.agents",
    "requirements.txt",
    "scripts/run_daily_analysis.py"
]

all_exist = True
for file in files_to_check:
    if os.path.exists(file):
        print(f"  OK: {file}")
    else:
        print(f"  MISSING: {file}")
        all_exist = False

# Check agents
print("\n2. Checking agent files...")
agent_files = [
    "technical_analyst.py",
    "fundamental_analyst.py",
    "sentiment_analyst.py",
    "macro_analyst.py",
    "crypto_analyst.py",
    "options_analyst.py",
    "risk_analyst.py",
    "quant_analyst.py",
    "sector_analyst.py",
    "compliance_analyst.py"
]

agents_exist = True
for file in agent_files:
    if os.path.exists(file):
        print(f"  OK: {file}")
    else:
        print(f"  MISSING: {file}")
        agents_exist = False

print("\n" + "=" * 60)
print("SUMMARY:")
print(f"Core files: {'ALL OK' if all_exist else 'SOME MISSING'}")
print(f"Agent files: {sum(1 for f in agent_files if os.path.exists(f))}/10 present")
print(f"Total files checked: {len(files_to_check) + len(agent_files)}")

if all_exist and agents_exist:
    print("\nSUCCESS: All trading system files are present!")
    print("\nNext steps:")
    print("1. Set API keys in .env file")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Test: python complete_trading_pipeline.py --test-mode")
    print("4. Deploy: docker-compose -f docker-compose.trading.yml up")
else:
    print("\nWARNING: Some files are missing. Please check above.")