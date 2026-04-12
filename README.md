# Trading Agent Monitoring System

A comprehensive 10-agent trading system with real-time monitoring, stock analysis, and prediction capabilities.

## 🚀 Features

### Frontend (Angular)
- Real-time dashboard with WebSocket connectivity
- Agent control panel for triggering analyses
- Leader prediction dashboard with stock/crypto recommendations
- Stock ticker browser with 100+ symbols across categories
- Agent status monitoring and activity logs
- Responsive design with Bootstrap 5

### Backend (Spring Boot)
- REST API with 25+ endpoints
- WebSocket support for real-time updates
- 10 specialized trading agents:
  - Technical Analyst (price charts, indicators)
  - Fundamental Analyst (financials, valuation)
  - Sentiment Analyst (news, social media)
  - Macro Analyst (economic trends)
  - Crypto Analyst (cryptocurrency markets)
  - Options Analyst (derivatives, volatility)
  - Risk Analyst (portfolio risk)
  - Quant Analyst (statistical models)
  - Sector Analyst (industry trends)
  - Compliance Analyst (regulatory checks)
- Stock ticker database with 100+ symbols
- Environment-based configuration (no hardcoded secrets)

### Infrastructure
- Docker Compose for easy deployment
- Python trading agents with API integration
- Environment variable configuration
- Production-ready setup

## 📁 Project Structure

```
trading-system/
├── frontend/                 # Angular dashboard (port 4200)
│   ├── src/app/components/
│   │   ├── dashboard-home/      # Main dashboard
│   │   ├── leader-prediction/   # Prediction dashboard
│   │   ├── agent-control-panel/ # Agent controls
│   │   └── ... other components
│   └── environments/         # Environment configuration
├── backend/                  # Spring Boot API (port 8082)
│   ├── src/main/java/com/trading/system/
│   │   ├── controller/       # REST controllers
│   │   ├── model/           # Data models
│   │   └── config/          # Configuration
│   └── resources/           # Application config
└── infrastructure/          # Deployment & agents
    ├── trading-agents/      # Python trading agents
    ├── docker-compose.yml   # Docker setup
    └── requirements.txt     # Python dependencies
```

## 🛠️ Setup & Installation

### Prerequisites
- Java 17+
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose (optional)

### 1. Backend Setup
```bash
cd backend

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Build and run
mvn clean package
java -jar target/trading-system-1.0.0.jar
```

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
ng serve
```

### 3. Infrastructure Setup
```bash
cd infrastructure/trading-agents

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Install Python dependencies
pip install -r requirements.txt

# Run trading agents
python generate_recommendation.py
```

### 4. Docker Deployment (Optional)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
DB_URL=jdbc:mysql://localhost:3306/trading_db
DB_USERNAME=root
DB_PASSWORD=your_password
ALPHA_VANTAGE_API_KEY=your_key_here
FMP_API_KEY=your_key_here
```

#### Frontend (environment.ts)
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8082/api',
  wsUrl: 'http://localhost:8082/ws-monitoring'
};
```

#### Trading Agents (.env)
```env
ALPHA_VANTAGE_API_KEY=your_key_here
FMP_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
BACKEND_URL=http://localhost:8082
```

## 📊 Available Stock Tickers

The system includes 100+ tickers across categories:

### Major US Stocks (50)
- **Technology**: AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, ADBE, NFLX, CRM
- **Financial**: JPM, BAC, WFC, C, GS, MS, V, MA, PYPL, SQ
- **Healthcare**: JNJ, UNH, PFE, ABT, TMO, MRK, BMY, LLY, AMGN, GILD
- **Industrial**: CAT, BA, MMM, GE, HON, UPS, RTX, DE, LMT, GD

### Cryptocurrencies (20)
- BTC, ETH, BNB, XRP, SOL, ADA, AVAX, DOT, DOGE, SHIB, MATIC, TRX, LTC, UNI, LINK, ATOM, ETC, XLM, ICP, FIL

### ETFs (20)
- SPY, QQQ, DIA, IWM, VTI, VOO, IVV, VEA, VWO, BND, AGG, LQD, HYG, GLD, SLV, USO, TLT, IEF, SHY, MUB

## 🔌 API Endpoints

### Stock Tickers
- `GET /api/tickers/all` - Get all tickers
- `GET /api/tickers/categories` - Get tickers by category
- `GET /api/tickers/category/{category}` - Get tickers for specific category
- `GET /api/tickers/info/{ticker}` - Get ticker information
- `GET /api/tickers/stats` - Get ticker statistics

### Trading Recommendations
- `POST /api/trading/generate-recommendation` - Generate trading recommendation
- `GET /api/trading/recommendation/{ticker}` - Get recommendation for ticker
- `GET /api/trading/agent-analysis/{ticker}` - Get agent analysis for ticker
- `GET /api/trading/recent-recommendations` - Get recent recommendations

### Agent Control
- `POST /api/trigger/{agent}/{symbol}` - Trigger specific agent
- `POST /api/trigger/all/{symbol}` - Trigger all agents
- `GET /api/trigger/agents` - Get all agents
- `GET /api/trigger/status/{agent}` - Get agent status

### System Health
- `GET /api/health` - System health check
- `GET /ws-monitoring` - WebSocket endpoint

## 🎯 Usage Examples

### 1. Generate Trading Recommendation
```bash
# Using curl
curl -X POST http://localhost:8082/api/trading/generate-recommendation \
  -H "Content-Type: application/json" \
  -d '{"category": "all"}'

# Using frontend
# Click "Generate Prediction" in Leader Prediction Dashboard
```

### 2. Trigger Agent Analysis
```bash
# Trigger technical analyst for AAPL
curl -X POST http://localhost:8082/api/trigger/technical/AAPL

# Trigger all agents for TSLA
curl -X POST http://localhost:8082/api/trigger/all/TSLA
```

### 3. Get Stock Ticker Information
```bash
# Get all tickers
curl http://localhost:8082/api/tickers/all

# Get ticker info for AAPL
curl http://localhost:8082/api/tickers/info/AAPL
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
mvn test
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Trading Agent Tests
```bash
cd infrastructure/trading-agents
python test_system_simple.py
```

## 🔒 Security

- **No hardcoded secrets**: All API keys use environment variables
- **CORS configured**: Only allowed origins can access API
- **Input validation**: All endpoints validate input data
- **Git security**: .gitignore excludes sensitive files
- **Docker security**: Non-root users in containers

## 📈 Monitoring

### Dashboard Features
- Real-time agent status
- WebSocket connection monitoring
- Activity logs with timestamps
- Confidence scores and signal distribution
- Recent prediction history

### Access Points
- Frontend: http://localhost:4200
- Backend API: http://localhost:8082/api/health
- WebSocket: ws://localhost:8082/ws-monitoring

## 🚢 Deployment

### Production Deployment
1. Set `production: true` in frontend environment
2. Configure production database in backend .env
3. Use Docker Compose for containerized deployment
4. Set up reverse proxy (Nginx/Apache)
5. Configure SSL certificates

### Docker Deployment
```bash
# Build and deploy
docker-compose build
docker-compose up -d

# Monitor logs
docker-compose logs -f trading-backend
docker-compose logs -f trading-frontend
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Alpha Vantage for financial data API
- Financial Modeling Prep for fundamental data
- Spring Boot and Angular teams
- All open-source contributors

## 📞 Support

For issues and questions:
1. Check the [Issues](https://github.com/yourusername/trading-system/issues) page
2. Create a new issue with detailed description
3. Include logs and reproduction steps

---

**Happy Trading!** 📈🚀