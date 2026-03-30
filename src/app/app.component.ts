import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface TradingAgent {
  id: number;
  name: string;
  status: 'active' | 'inactive';
  description: string;
  confidence: number;
  signals: number;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'Trading System Dashboard';
  agents: TradingAgent[] = [];
  apiResponse: any = 'Click a button to test API endpoints...';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadAgents();
    // Test backend on load
    setTimeout(() => this.testHealth(), 1000);
  }

  loadAgents() {
    this.agents = [
      {
        id: 1,
        name: 'Technical Analyst',
        status: 'active',
        description: 'Analyzes charts, RSI, MACD, and technical indicators',
        confidence: 85,
        signals: 42
      },
      {
        id: 2,
        name: 'Fundamental Analyst',
        status: 'active',
        description: 'Evaluates financial statements, P/E ratios, and valuations',
        confidence: 78,
        signals: 38
      },
      {
        id: 3,
        name: 'Sentiment Analyst',
        status: 'active',
        description: 'Monitors news, social media, and market sentiment',
        confidence: 72,
        signals: 45
      },
      {
        id: 4,
        name: 'Macro Economist',
        status: 'active',
        description: 'Analyzes GDP, inflation, interest rates, and economic indicators',
        confidence: 80,
        signals: 28
      },
      {
        id: 5,
        name: 'Crypto Specialist',
        status: 'active',
        description: 'Focuses on BTC, ETH, and blockchain market analysis',
        confidence: 88,
        signals: 52
      },
      {
        id: 6,
        name: 'Risk Manager',
        status: 'active',
        description: 'Manages position sizing, stop-loss, and portfolio risk',
        confidence: 92,
        signals: 35
      },
      {
        id: 7,
        name: 'Options Strategist',
        status: 'inactive',
        description: 'Analyzes options chains, Greeks, and volatility',
        confidence: 65,
        signals: 18
      },
      {
        id: 8,
        name: 'Quantitative Analyst',
        status: 'inactive',
        description: 'Builds statistical models and machine learning algorithms',
        confidence: 75,
        signals: 22
      },
      {
        id: 9,
        name: 'Sector Specialist',
        status: 'inactive',
        description: 'Focuses on sector rotation and industry analysis',
        confidence: 70,
        signals: 25
      },
      {
        id: 10,
        name: 'Compliance Expert',
        status: 'inactive',
        description: 'Ensures regulatory compliance and risk management',
        confidence: 95,
        signals: 12
      }
    ];
  }

  testHealth() {
    this.apiResponse = 'Testing backend health endpoint...';
    this.http.get('http://localhost:8080/api/health').subscribe({
      next: (response) => {
        this.apiResponse = response;
      },
      error: (error) => {
        this.apiResponse = { error: error.message, status: 'Backend offline' };
      }
    });
  }

  testAgents() {
    this.apiResponse = 'Testing agents endpoint...';
    this.http.get('http://localhost:8080/api/agents').subscribe({
      next: (response) => {
        this.apiResponse = response;
      },
      error: (error) => {
        this.apiResponse = { error: error.message, status: 'API error' };
      }
    });
  }

  clearResponse() {
    this.apiResponse = 'Click a button to test API endpoints...';
  }
}