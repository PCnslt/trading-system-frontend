# 10-Agent Trading System with Docker MCP

A complete trading system featuring 10 specialized AI agents, real-time monitoring dashboard, and Docker MCP (Model Context Protocol) integration.

## 🚀 Features

### 🤖 **10 Specialized Trading Agents**
- **Technical Analyst**: RSI, MACD, trend analysis
- **Fundamental Analyst**: P/E ratios, financial metrics
- **Sentiment Analyst**: News and social media analysis
- **Macro Analyst**: Economic indicators and trends
- **Crypto Analyst**: Cryptocurrency market analysis
- **Options Analyst**: Options pricing and strategies
- **Risk Analyst**: Portfolio risk management
- **Quant Analyst**: Quantitative models and strategies
- **Sector Analyst**: Industry sector analysis
- **Compliance Analyst**: Regulatory compliance checking

### 📊 **Real-time Monitoring Dashboard**
- Angular 17+ frontend with Material Design
- Spring Boot backend with WebSocket support
- PostgreSQL database with JPA/Hibernate
- Redis caching for performance
- Real-time updates via WebSocket

### 🐳 **Docker MCP Integration**
- Each agent runs as isolated Docker container
- Unified MCP gateway for all agents
- Resource limits (1 CPU, 2GB RAM per agent)
- Secure secrets management
- OAuth integration for external services

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Trading Dashboard                        │
│                  (Angular Frontend)                         │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/WebSocket
┌──────────────────────────▼──────────────────────────────────┐
│              Monitoring Backend (Spring Boot)               │
│                    Port: 8083                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                     Docker MCP Gateway                      │
│                      Port: 8081                             │
└─────┬────────────┬────────────┬────────────┬───────────────┘
      │            │            │            │
┌─────▼────┐ ┌─────▼────┐ ┌─────▼────┐ ┌─────▼────┐
│Technical │ │Fundamental│ │Sentiment │ │  Macro   │
│ Analyst  │ │  Analyst  │ │ Analyst  │ │ Analyst  │
└──────────┘ └───────────┘ └──────────┘ └──────────┘
      │            │            │            │
┌─────▼────┐ ┌─────▼────┐ ┌─────▼────┐ ┌─────▼────┐
│  Crypto  │ │ Options  │ │   Risk   │ │  Quant   │
│ Analyst  │ │ Analyst  │ │ Analyst  │ │ Analyst  │
└──────────┘ └───────────┘ └──────────┘ └──────────┘
      │            │
┌─────▼────┐ ┌─────▼────┐
│ Sector   │ │Compliance│
│ Analyst  │ │ Analyst  │
└──────────┘ └──────────┘
```

## 🛠️ Quick Start

### Prerequisites
- Docker Desktop 4.59+ with MCP Toolkit enabled
- Node.js 18+ and npm (for development)
- Java 21+ (for backend development)
- Git

### 1. Clone and Setup
```bash
git clone <repository-url>
cd trading-system
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start with Docker Compose
```bash
# Start all services
docker-compose -f docker-compose.mcp.yml up -d

# Or start monitoring only (without MCP)
docker-compose up -d
```

### 3. Access Applications
- **Dashboard**: http://localhost:4200
- **Monitoring API**: http://localhost:8083
- **MCP Gateway**: http://localhost:8081
- **API Documentation**: http://localhost:8083/swagger-ui.html

### 4. Configure Docker MCP
```bash
# Install Docker MCP CLI (if not already installed)
docker mcp --version

# Create MCP profile
docker mcp profile create --name trading-agents

# Add agents to profile
docker mcp profile server add trading-agents --server docker://technical-analyst:latest
docker mcp profile server add trading-agents --server docker://fundamental-analyst:latest
# ... add all 10 agents

# Add secrets
docker mcp secret add alphavantage-key
docker mcp secret add huggingface-token
docker mcp secret add binance-api-key

# Run gateway
docker mcp gateway run --profile trading-agents --port 8081 --transport sse
```

### 5. Connect Clients
#### Claude Desktop
```json
{
  "mcpServers": {
    "trading-agents": {
      "url": "http://localhost:8081/sse",
      "transport": "sse"
    }
  }
}
```

#### VS Code/Cursor
Add to `.vscode/mcp.json`:
```json
{
  "mcp": {
    "servers": {
      "trading-agents": {
        "url": "http://localhost:8081/sse",
        "transport": "sse"
      }
    }
  }
}
```

## 📁 Project Structure

```
├── backend/                 # Spring Boot monitoring backend
│   ├── src/main/java/com/trading/system/
│   │   ├── monitoring/      # Monitoring entities and repositories
│   │   ├── controller/      # REST controllers
│   │   ├── service/        # Business logic
│   │   └── config/         # Configuration
│   └── pom.xml
│
├── frontend/               # Angular dashboard
│   ├── src/app/
│   │   ├── components/     # UI components
│   │   ├── services/       # API services
│   │   └── models/         # TypeScript models
│   └── package.json
│
├── mcp-servers/            # Docker MCP servers
│   ├── technical-analyst/
│   ├── fundamental-analyst/
│   └── ... (10 agents)
│
├── docker-compose.yml      # Monitoring stack
├── docker-compose.mcp.yml  # Full stack with MCP
└── README.md
```

## 🔧 API Endpoints

### Monitoring Backend (Port 8083)
```
GET    /api/monitoring/health          # System health
GET    /api/monitoring/stats           # System statistics
GET    /api/monitoring/agents/status   # Agent statuses

POST   /api/agent-activities           # Log agent activity
GET    /api/agent-activities           # Get activities

POST   /api/chat                       # Send chat message
GET    /api/chat                       # Get chat history

POST   /api/consensus                  # Submit consensus vote
GET    /api/consensus                  # Get consensus votes
GET    /api/consensus/latest           # Latest consensus

POST   /api/trade-recommendations      # Create recommendation
GET    /api/trade-recommendations      # Get recommendations
GET    /api/trade-recommendations/active # Active recommendations
```

### WebSocket Endpoints
```
/ws-monitoring                    # WebSocket connection
/topic/agent-activities           # Real-time activities
/topic/chat                       # Real-time chat
/topic/consensus                  # Real-time consensus
/topic/trade-recommendations      # Real-time recommendations
```

## 🤝 Integration with OpenClaw

### Send Agent Activities
```bash
# Example: Send agent activity via curl
curl -X POST http://localhost:8083/api/agent-activities \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "technical_analyst",
    "task": "RSI Analysis",
    "activityType": "analysis",
    "inputData": "{\"symbol\": \"AAPL\", \"period\": 14}",
    "outputData": "{\"rsi\": 65.5, \"signal\": \"NEUTRAL\"}",
    "reasoning": "RSI indicates neutral market conditions",
    "status": "success",
    "symbol": "AAPL"
  }'
```

### OpenClaw Skill Configuration
Create a skill that posts to the monitoring backend:
```yaml
# skills/trading-monitoring/skill.yaml
name: trading-monitoring
description: Post trading agent activities to monitoring system
tools:
  - name: post_agent_activity
    description: Post agent activity to monitoring backend
    parameters:
      agentId: string
      task: string
      # ... other parameters
```

## 🔒 Security

- **API Keys**: Stored in Docker MCP secrets, never in code
- **Container Isolation**: Each agent runs in isolated container with resource limits
- **Network Security**: Internal Docker network, only gateway exposed
- **Authentication**: JWT tokens for API access (optional)
- **Rate Limiting**: Implemented at gateway level

## 📈 Monitoring & Logging

- **Application Logs**: Structured JSON logging
- **Metrics**: Prometheus metrics endpoint at `/actuator/prometheus`
- **Health Checks**: Docker health checks and Spring Boot Actuator
- **Tracing**: Distributed tracing with OpenTelemetry

## 🚢 Deployment

### Production Deployment
```bash
# Build and push images
docker-compose -f docker-compose.mcp.yml build
docker-compose -f docker-compose.mcp.yml push

# Deploy to Kubernetes
kubectl apply -f kubernetes/
```

### Environment Variables
See `.env.example` for required environment variables. In production:
- Use Docker secrets or HashiCorp Vault
- Rotate API keys regularly
- Enable TLS/SSL for all endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- Issues: GitHub Issues
- Documentation: [docs.openclaw.ai](https://docs.openclaw.ai)
- Community: [Discord](https://discord.gg/clawd)

---

**Built with ❤️ by OpenClaw AI**