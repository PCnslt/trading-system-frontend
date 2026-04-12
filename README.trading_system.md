# 10-Agent Trading System

A complete AI-powered trading system that scans ALL stocks using 10 specialized agents and makes daily buy recommendations.

## 🎯 Features

- **10 Specialized Agents**: Technical, Fundamental, Sentiment, Macro, Crypto, Options, Risk, Quant, Sector, and Compliance analysis
- **ALL Stock Scanning**: Comprehensive coverage of NASDAQ, NYSE, and major exchanges
- **Intelligent Decision Making**: Leader agent aggregates signals and predicts tomorrow's returns
- **Complete Stack**: Frontend (Angular), Backend (Spring Boot), Agents (Python), Infrastructure (Docker)
- **Real-time Dashboard**: Live monitoring of recommendations and performance
- **Performance Tracking**: Accuracy metrics and continuous improvement

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/yourusername/trading-system.git
cd trading-system

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run with Docker (Recommended)
```bash
docker-compose -f infrastructure/docker-compose.trading.yml up --build
```

### 3. Run Daily Analysis
```bash
# Manually trigger analysis
docker exec trading-agents python /app/scripts/run_daily_analysis.py

# Or schedule with cron
0 9 * * * docker exec trading-agents python /app/scripts/run_daily_analysis.py
```

### 4. Access Dashboard
- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8080
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## 📊 How It Works

### 1. Stock Scanning
- Scans 1000+ stocks from Alpha Vantage, FMP, NASDAQ, NYSE
- Filters by price, market cap, volume
- Caches results for performance

### 2. 10-Agent Analysis
Each agent provides BUY/SELL/HOLD signals with confidence:

1. **Technical Analyst**: RSI, MACD, moving averages, trends
2. **Fundamental Analyst**: P/E ratios, margins, valuation
3. **Sentiment Analyst**: News, social media, market sentiment
4. **Macro Analyst**: Economic indicators, interest rates
5. **Crypto Analyst**: Cryptocurrency markets
6. **Options Analyst**: Options flow, volatility
7. **Risk Analyst**: Risk assessment, position sizing
8. **Quant Analyst**: Statistical models, arbitrage
9. **Sector Analyst**: Industry rotation, sector trends
10. **Compliance Analyst**: Regulatory rules, trading compliance

### 3. Leader Decision
- Aggregates all agent signals with weighted scoring
- Predicts tomorrow's return for each stock
- Selects stock with highest expected return
- Provides reasoning and confidence score

### 4. Daily Report
- Top 10 BUY recommendations
- Top 10 SELL recommendations
- Final decision with expected return
- Agent performance metrics

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │     Agents      │
│   (Angular)     │◄──►│   (Spring Boot) │◄──►│    (Python)     │
│   Dashboard     │    │      API        │    │  10 Analysts    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │   Prometheus    │
│   Database      │    │     Cache       │    │   Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Configuration

### API Keys Required
Add to `.env` file:
```env
ALPHAVANTAGE_API_KEY=your_key_here
FMP_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here
HUGGINGFACE_TOKEN=your_key_here
DEEPSEEK_API_KEY=your_key_here
```

### Agent Weights
Adjust in `trading_leader.py`:
```python
self.agent_weights = {
    "technical": 0.30,
    "fundamental": 0.25,
    "sentiment": 0.15,
    "macro": 0.10,
    "crypto": 0.05,
    "options": 0.05,
    "risk": 0.05,
    "quant": 0.03,
    "sector": 0.01,
    "compliance": 0.01
}
```

## 📈 Performance Metrics

### Success Criteria
- **Accuracy**: > 60% prediction accuracy
- **Coverage**: 1000+ stocks analyzed daily
- **Speed**: < 5 minutes for complete analysis
- **Uptime**: 99.9% system availability
- **Cost**: < $10/month (free APIs where possible)

### Monitoring
- Daily accuracy tracking
- Agent performance dashboard
- System resource monitoring
- API rate limit tracking

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Individual Tests
```bash
# Test stock scanner
python tests/test_stock_scanner.py

# Test technical analyst
python tests/test_technical_analyst.py

# Test complete pipeline
python tests/test_complete_pipeline.py
```

### Integration Test
```bash
# Test full system (limited mode)
python complete_trading_pipeline.py --test-mode
```

## 🚢 Deployment

### Production Deployment
```bash
# Build production images
docker-compose -f infrastructure/docker-compose.prod.yml build

# Deploy
docker-compose -f infrastructure/docker-compose.prod.yml up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### Kubernetes (Optional)
```bash
kubectl apply -f k8s/
```

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Agent Specifications](docs/AGENTS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This is an educational project. Not financial advice. Trading involves risk. Past performance does not guarantee future results. Always do your own research and consult with a licensed financial advisor before making investment decisions.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/trading-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/trading-system/discussions)
- **Email**: trading-support@yourdomain.com

---

## 🎯 Getting Your First Recommendation

1. **Set up the system** (5 minutes)
2. **Run daily analysis** (2-5 minutes)
3. **Check dashboard** for today's recommendation
4. **Monitor performance** over time
5. **Adjust weights** based on agent accuracy

### Example Output:
```
DAILY TRADING REPORT
==================================================

✅ FINAL DECISION: BUY NVDA
   Confidence: 78%
   Expected Return: 3.2% by tomorrow
   Expected Price: $950.25
   Reasoning: Strong technical uptrend, positive sentiment, high expected return

Top BUY Recommendations:
1. NVDA: 78% confidence, 3.2% expected return
2. AAPL: 72% confidence, 2.1% expected return
3. MSFT: 68% confidence, 1.8% expected return

Agent Performance:
- Technical: 65% accuracy
- Fundamental: 62% accuracy
- Sentiment: 58% accuracy
```

---

**Ready to start?** Run `docker-compose up` and visit http://localhost:4200!