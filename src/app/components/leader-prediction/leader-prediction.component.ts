import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/index';

interface Prediction {
  symbol: string;
  name: string;
  type: string;
  consensus_signal: string;
  confidence: number;
  agent_count: number;
  signal_distribution: {
    BUY: number;
    SELL: number;
    HOLD: number;
  };
  reasoning: string;
  timestamp: string;
}

@Component({
  selector: 'app-leader-prediction',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="card">
      <div class="card-body">
        <!-- Controls -->
        <div class="row mb-4">
          <div class="col-md-6">
            <div class="input-group">
              <span class="input-group-text">📊</span>
              <select class="form-select" [(ngModel)]="selectedCategory" (change)="loadTickersByCategory()">
                <option value="all">All Tickers</option>
                <option value="stocks">Major Stocks</option>
                <option value="tech">Technology</option>
                <option value="financial">Financial</option>
                <option value="healthcare">Healthcare</option>
                <option value="crypto">Cryptocurrencies</option>
                <option value="etfs">ETFs</option>
              </select>
            </div>
          </div>
          <div class="col-md-6">
            <div class="d-flex gap-2">
              <button class="btn btn-success" (click)="generatePrediction()" [disabled]="isGenerating">
                <span *ngIf="!isGenerating">🎯 Generate Prediction</span>
                <span *ngIf="isGenerating">
                  <span class="spinner-border spinner-border-sm me-2"></span>
                  Analyzing...
                </span>
              </button>
              <button class="btn btn-outline-secondary" (click)="loadRecentPredictions()">
                📋 Recent Predictions
              </button>
            </div>
          </div>
        </div>

        <!-- Ticker Stats -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="alert alert-info">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <strong>Available Tickers:</strong> {{tickerStats.totalTickers || 0}} total
                  ({{tickerStats.stocksCount || 0}} stocks, {{tickerStats.cryptoCount || 0}} crypto, {{tickerStats.etfsCount || 0}} ETFs)
                </div>
                <div>
                  <button class="btn btn-sm btn-outline-info" (click)="showAllTickers = !showAllTickers">
                    {{showAllTickers ? 'Hide' : 'Show'}} All Tickers
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Ticker List -->
            <div *ngIf="showAllTickers" class="mb-4">
              <div class="card">
                <div class="card-header">
                  <h6 class="mb-0">Available Tickers ({{availableTickers.length}})</h6>
                </div>
                <div class="card-body" style="max-height: 200px; overflow-y: auto;">
                  <div class="d-flex flex-wrap gap-2">
                    <span *ngFor="let ticker of availableTickers" 
                          class="badge" 
                          [ngClass]="getTickerBadgeClass(ticker)">
                      {{ticker}}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Current Prediction -->
        <div *ngIf="currentPrediction" class="mb-4">
          <div class="card border-success">
            <div class="card-header bg-success text-white">
              <h5 class="mb-0">Current Top Recommendation</h5>
              <small>Generated: {{currentPrediction.timestamp | date:'medium'}}</small>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-4 text-center">
                  <div class="display-4 mb-2" [ngClass]="getSignalClass(currentPrediction.consensus_signal)">
                    {{currentPrediction.consensus_signal}}
                  </div>
                  <div class="h2">{{currentPrediction.symbol}}</div>
                  <div class="text-muted">{{currentPrediction.name}} ({{currentPrediction.type}})</div>
                </div>
                <div class="col-md-8">
                  <div class="mb-3">
                    <div class="d-flex justify-content-between mb-1">
                      <span>Confidence</span>
                      <span><strong>{{currentPrediction.confidence * 100 | number:'1.1-1'}}%</strong></span>
                    </div>
                    <div class="progress" style="height: 20px;">
                      <div class="progress-bar" 
                           [ngClass]="getConfidenceClass(currentPrediction.confidence)"
                           [style.width.%]="currentPrediction.confidence * 100">
                      </div>
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <h6>Agent Consensus</h6>
                    <div class="d-flex gap-3">
                      <div class="text-center">
                        <div class="h4 text-success">{{currentPrediction.signal_distribution.BUY || 0}}</div>
                        <small>BUY</small>
                      </div>
                      <div class="text-center">
                        <div class="h4 text-danger">{{currentPrediction.signal_distribution.SELL || 0}}</div>
                        <small>SELL</small>
                      </div>
                      <div class="text-center">
                        <div class="h4 text-warning">{{currentPrediction.signal_distribution.HOLD || 0}}</div>
                        <small>HOLD</small>
                      </div>
                      <div class="text-center">
                        <div class="h4 text-primary">{{currentPrediction.agent_count}}</div>
                        <small>Total Agents</small>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h6>Reasoning</h6>
                    <p class="mb-0">{{currentPrediction.reasoning}}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Predictions -->
        <div *ngIf="recentPredictions.length > 0" class="mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">Recent Predictions (Last 5)</h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Symbol</th>
                      <th>Signal</th>
                      <th>Confidence</th>
                      <th>Agents</th>
                      <th>Distribution</th>
                      <th>Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr *ngFor="let pred of recentPredictions">
                      <td>
                        <strong>{{pred?.symbol || 'N/A'}}</strong>
                        <div class="text-muted small">{{pred?.type || 'Unknown'}}</div>
                      </td>
                      <td>
                        <span class="badge" [ngClass]="getSignalBadgeClass(pred?.consensus_signal)">
                          {{pred?.consensus_signal || 'UNKNOWN'}}
                        </span>
                      </td>
                      <td>
                        <div class="progress" style="height: 10px; width: 100px;">
                          <div class="progress-bar" 
                               [ngClass]="getConfidenceClass(pred?.confidence || 0)"
                               [style.width.%]="(pred?.confidence || 0) * 100">
                          </div>
                        </div>
                        <small>{{(pred?.confidence || 0) * 100 | number:'1.1-1'}}%</small>
                      </td>
                      <td>{{pred?.agent_count || 0}}</td>
                      <td>
                        <small>
                          B:{{pred?.signal_distribution?.BUY || 0}} 
                          S:{{pred?.signal_distribution?.SELL || 0}} 
                          H:{{pred?.signal_distribution?.HOLD || 0}}
                        </small>
                      </td>
                      <td>{{pred?.timestamp | date:'shortTime' || 'N/A'}}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading/Error States -->
        <div *ngIf="isLoading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="mt-2">Loading ticker data...</p>
        </div>

        <div *ngIf="errorMessage" class="alert alert-danger">
          {{errorMessage}}
        </div>

        <div *ngIf="!currentPrediction && !isLoading && !errorMessage" class="text-center py-4 text-muted">
          <p>No prediction generated yet. Click "Generate Prediction" to analyze all tickers.</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .progress-bar-high { 
      background: linear-gradient(135deg, var(--accent-green) 0%, #00b377 100%);
    }
    .progress-bar-medium { 
      background: linear-gradient(135deg, var(--accent-yellow) 0%, #e69500 100%);
    }
    .progress-bar-low { 
      background: linear-gradient(135deg, var(--accent-red) 0%, #e62e5c 100%);
    }
    
    .badge-stock { 
      background: linear-gradient(135deg, var(--accent-blue) 0%, #2952cc 100%);
      color: white;
    }
    .badge-crypto { 
      background: linear-gradient(135deg, var(--accent-purple) 0%, #7a1fd2 100%);
      color: white;
    }
    .badge-etf { 
      background: linear-gradient(135deg, var(--accent-cyan) 0%, #00bbd6 100%);
      color: #000;
    }
    
    .signal-buy { 
      color: var(--accent-green);
      font-weight: 600;
    }
    .signal-sell { 
      color: var(--accent-red);
      font-weight: 600;
    }
    .signal-hold { 
      color: var(--accent-yellow);
      font-weight: 600;
    }
    
    .prediction-card {
      background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
      transition: all 0.3s;
    }
    .prediction-card:hover {
      border-color: var(--accent-blue);
      transform: translateY(-4px);
      box-shadow: 0 8px 24px var(--shadow-color);
    }
    .prediction-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      padding-bottom: 0.75rem;
      border-bottom: 1px solid var(--border-color);
    }
    .prediction-symbol {
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--text-primary);
    }
    .prediction-category {
      font-size: 0.875rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .prediction-metrics {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1rem;
      margin-bottom: 1rem;
    }
    .metric-item {
      text-align: center;
      background: rgba(255, 255, 255, 0.03);
      border-radius: 8px;
      padding: 0.75rem;
    }
    .metric-label {
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 0.25rem;
    }
    .metric-value {
      font-size: 1.25rem;
      font-weight: 600;
      color: var(--text-primary);
    }
    .prediction-confidence {
      background: linear-gradient(135deg, rgba(51, 102, 255, 0.1) 0%, rgba(51, 102, 255, 0.05) 100%);
      border: 1px solid rgba(51, 102, 255, 0.3);
      border-radius: 10px;
      padding: 1rem;
      margin-bottom: 1rem;
    }
    .confidence-bar {
      height: 8px;
      background: var(--bg-secondary);
      border-radius: 4px;
      overflow: hidden;
      margin-top: 0.5rem;
    }
    .confidence-fill {
      height: 100%;
      border-radius: 4px;
      background: linear-gradient(135deg, var(--accent-blue) 0%, #2952cc 100%);
    }
    .prediction-reasoning {
      background: rgba(255, 255, 255, 0.03);
      border-radius: 8px;
      padding: 1rem;
      border-left: 3px solid var(--accent-blue);
    }
    .reasoning-label {
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 0.5rem;
    }
    .reasoning-text {
      font-size: 0.875rem;
      color: var(--text-secondary);
      line-height: 1.5;
    }
    .leaderboard {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      overflow: hidden;
    }
    .leaderboard-header {
      background: var(--bg-secondary);
      padding: 1rem 1.25rem;
      border-bottom: 1px solid var(--border-color);
      font-weight: 600;
      color: var(--text-primary);
    }
    .leaderboard-item {
      display: flex;
      align-items: center;
      padding: 0.75rem 1.25rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      transition: background-color 0.2s;
    }
    .leaderboard-item:hover {
      background: var(--bg-hover);
    }
    .leaderboard-item:last-child {
      border-bottom: none;
    }
    .leaderboard-rank {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 0.875rem;
      margin-right: 1rem;
      background: linear-gradient(135deg, var(--accent-blue) 0%, #2952cc 100%);
      color: white;
    }
    .leaderboard-symbol {
      flex: 1;
      font-weight: 600;
      color: var(--text-primary);
    }
    .leaderboard-score {
      font-weight: 600;
      color: var(--text-primary);
      margin-right: 1rem;
    }
    .leaderboard-signal {
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 600;
    }
    .signal-buy-badge {
      background: rgba(0, 214, 143, 0.1);
      color: var(--accent-green);
      border: 1px solid rgba(0, 214, 143, 0.3);
    }
    .signal-sell-badge {
      background: rgba(255, 61, 113, 0.1);
      color: var(--accent-red);
      border: 1px solid rgba(255, 61, 113, 0.3);
    }
    .signal-hold-badge {
      background: rgba(143, 155, 179, 0.1);
      color: var(--text-muted);
      border: 1px solid rgba(143, 155, 179, 0.3);
    }
    .category-filter {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 1rem;
      margin-bottom: 1.5rem;
    }
    .filter-label {
      font-size: 0.875rem;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 0.5rem;
    }
    .filter-buttons {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }
    .filter-btn {
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      padding: 0.375rem 0.75rem;
      border-radius: 6px;
      font-size: 0.875rem;
      transition: all 0.2s;
    }
    .filter-btn:hover {
      background: var(--bg-hover);
      border-color: var(--accent-blue);
    }
    .filter-btn.active {
      background: linear-gradient(135deg, var(--accent-blue) 0%, #2952cc 100%);
      color: white;
      border-color: var(--accent-blue);
    }
    .empty-state {
      text-align: center;
      padding: 3rem 1.5rem;
      color: var(--text-muted);
    }
    .empty-icon {
      font-size: 3rem;
      margin-bottom: 1rem;
      opacity: 0.5;
    }
    .empty-text {
      font-size: 1rem;
      margin-bottom: 0.5rem;
      color: var(--text-secondary);
    }
    .empty-subtext {
      font-size: 0.875rem;
      opacity: 0.7;
    }
  `]
})
export class LeaderPredictionComponent implements OnInit {
  availableTickers: string[] = [];
  selectedCategory = 'all';
  showAllTickers = false;
  currentPrediction: Prediction | null = null;
  recentPredictions: Prediction[] = [];
  tickerStats: any = {};
  isLoading = false;
  isGenerating = false;
  errorMessage = '';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadTickerStats();
    this.loadAllTickers();
    this.loadRecentPredictions();
  }

  loadTickerStats() {
    this.isLoading = true;
    this.http.get<any>(`${environment.apiUrl}/tickers/stats`)
      .subscribe({
        next: (data) => {
          this.tickerStats = data;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error loading ticker stats:', error);
          this.errorMessage = 'Failed to load ticker statistics';
          this.isLoading = false;
        }
      });
  }

  loadAllTickers() {
    this.http.get<any>(`${environment.apiUrl}/tickers/all`)
      .subscribe({
        next: (data) => {
          this.availableTickers = data.tickers || [];
        },
        error: (error) => {
          console.error('Error loading tickers:', error);
        }
      });
  }

  loadTickersByCategory() {
    this.http.get<any>(`${environment.apiUrl}/tickers/category/${this.selectedCategory}`)
      .subscribe({
        next: (data) => {
          this.availableTickers = data.tickers || [];
        },
        error: (error) => {
          console.error('Error loading tickers by category:', error);
        }
      });
  }

  generatePrediction() {
    this.isGenerating = true;
    this.errorMessage = '';
    
    // Call the trading agent recommendation endpoint
    this.http.post<any>(`${environment.apiUrl}/trading/generate-recommendation`, {
      category: this.selectedCategory
    }).subscribe({
      next: (response) => {
        this.currentPrediction = response.recommendation;
        this.addToRecentPredictions(this.currentPrediction!);
        this.isGenerating = false;
      },
      error: (error) => {
        console.error('Error generating prediction:', error);
        this.errorMessage = 'Failed to generate prediction. Please try again.';
        this.isGenerating = false;
        
        // Fallback: Generate mock prediction
        this.generateMockPrediction();
      }
    });
  }

  loadRecentPredictions() {
    // For now, load from localStorage or generate mock data
    const stored = localStorage.getItem('recent_predictions');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        // Filter out any null/undefined entries and ensure they have required properties
        this.recentPredictions = (parsed || []).filter((p: any) => p && typeof p === 'object');
      } catch (error) {
        console.error('Error parsing recent predictions:', error);
        this.generateMockRecentPredictions();
      }
    } else {
      this.generateMockRecentPredictions();
    }
  }

  addToRecentPredictions(prediction: Prediction) {
    this.recentPredictions.unshift(prediction);
    // Keep only last 5 predictions
    if (this.recentPredictions.length > 5) {
      this.recentPredictions = this.recentPredictions.slice(0, 5);
    }
    localStorage.setItem('recent_predictions', JSON.stringify(this.recentPredictions));
  }

  // Helper methods for styling
  getTickerBadgeClass(ticker: string): string {
    if (['BTC', 'ETH', 'BNB', 'XRP', 'SOL'].includes(ticker)) return 'badge-crypto';
    if (['SPY', 'QQQ', 'DIA', 'VTI', 'VOO'].includes(ticker)) return 'badge-etf';
    return 'badge-stock';
  }

  getSignalClass(signal?: string): string {
    if (!signal) return 'signal-unknown';
    return `signal-${signal.toLowerCase()}`;
  }

  getSignalBadgeClass(signal?: string): string {
    if (!signal) return 'bg-secondary';
    switch (signal) {
      case 'BUY': return 'bg-success';
      case 'SELL': return 'bg-danger';
      case 'HOLD': return 'bg-warning text-dark';
      default: return 'bg-secondary';
    }
  }

  getConfidenceClass(confidence?: number): string {
    if (!confidence) return 'progress-bar-low';
    if (confidence >= 0.7) return 'progress-bar-high';
    if (confidence >= 0.5) return 'progress-bar-medium';
    return 'progress-bar-low';
  }

  // Mock data for development
  private generateMockPrediction() {
    const symbols = this.availableTickers.length > 0 ? this.availableTickers : ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'BTC'];
    const randomSymbol = symbols[Math.floor(Math.random() * symbols.length)];
    
    this.currentPrediction = {
      symbol: randomSymbol,
      name: this.getMockName(randomSymbol),
      type: this.getMockType(randomSymbol),
      consensus_signal: Math.random() > 0.6 ? 'BUY' : Math.random() > 0.3 ? 'HOLD' : 'SELL',
      confidence: 0.6 + Math.random() * 0.3,
      agent_count: 10,
      signal_distribution: {
        BUY: Math.floor(Math.random() * 6),
        SELL: Math.floor(Math.random() * 4),
        HOLD: Math.floor(Math.random() * 4)
      },
      reasoning: `Mock analysis based on ${this.selectedCategory} category. ${randomSymbol} shows ${Math.random() > 0.5 ? 'strong' : 'moderate'} performance indicators.`,
      timestamp: new Date().toISOString()
    };
    
    // Ensure BUY+SELL+HOLD = 10
    if (this.currentPrediction) {
      const total = this.currentPrediction.signal_distribution.BUY + 
                    this.currentPrediction.signal_distribution.SELL + 
                    this.currentPrediction.signal_distribution.HOLD;
      if (total !== 10) {
        this.currentPrediction.signal_distribution.BUY += (10 - total);
      }
    }
    
    this.addToRecentPredictions(this.currentPrediction);
    this.isGenerating = false;
  }

  private generateMockRecentPredictions() {
    const symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'BTC', 'ETH', 'SPY'];
    this.recentPredictions = [];
    
    for (let i = 0; i < 3; i++) {
      const symbol = symbols[i];
      const hoursAgo = i + 1;
      const date = new Date();
      date.setHours(date.getHours() - hoursAgo);
      
      this.recentPredictions.push({
        symbol: symbol,
        name: this.getMockName(symbol),
        type: this.getMockType(symbol),
        consensus_signal: ['BUY', 'HOLD', 'SELL'][i],
        confidence: 0.65 + (i * 0.05),
        agent_count: 10,
        signal_distribution: {
          BUY: [6, 4, 2][i],
          SELL: [2, 3, 6][i],
          HOLD: [2, 3, 2][i]
        },
        reasoning: `Mock analysis ${hoursAgo} hour(s) ago`,
        timestamp: date.toISOString()
      });
    }
    
    localStorage.setItem('recent_predictions', JSON.stringify(this.recentPredictions));
  }

  private getMockName(symbol: string): string {
    const names: {[key: string]: string} = {
      'AAPL': 'Apple Inc.',
      'MSFT': 'Microsoft Corporation',
      'GOOGL': 'Alphabet Inc.',
      'AMZN': 'Amazon.com Inc.',
      'TSLA': 'Tesla Inc.',
      'NVDA': 'NVIDIA Corporation',
      'META': 'Meta Platforms Inc.',
      'BTC': 'Bitcoin',
      'ETH': 'Ethereum',
      'SPY': 'SPDR S&P 500 ETF',
      'QQQ': 'Invesco QQQ Trust',
      'DIA': 'SPDR Dow Jones ETF',
      'VTI': 'Vanguard Total Stock Market ETF',
      'VOO': 'Vanguard S&P 500 ETF'
    };
    
    return names[symbol] || symbol + ' Corporation';
  }

  private getMockType(symbol: string): string {
    if (['BTC', 'ETH', 'BNB', 'XRP', 'SOL'].includes(symbol)) return 'Cryptocurrency';
    if (['SPY', 'QQQ', 'DIA', 'VTI', 'VOO'].includes(symbol)) return 'ETF';
    return 'Stock';
  }
}