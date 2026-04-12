import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData, ChartEvent, ChartType } from 'chart.js';
import { MonitoringService, PriceHistoryData } from '../../services/monitoring.service';

@Component({
  selector: 'app-charts-page',
  standalone: true,
  imports: [CommonModule, FormsModule, BaseChartDirective],
  template: `
    <div class="container-fluid py-4">
      <!-- Page Header -->
      <div class="row mb-4">
        <div class="col-md-12">
          <div class="card shadow">
            <div class="card-body">
              <h1 class="display-6 mb-3"><i class="bi bi-bar-chart-line me-2"></i>Advanced Charts & Analytics</h1>
              <p class="lead mb-0">Visualize price history, technical indicators, and agent performance metrics</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Symbol Selection & Controls -->
      <div class="row mb-4">
        <div class="col-md-12">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0"><i class="bi bi-sliders me-2"></i>Chart Controls</h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-3">
                  <label for="symbol" class="form-label">Symbol</label>
                  <select class="form-select" id="symbol" [(ngModel)]="selectedSymbol">
                    <option *ngFor="let symbol of symbols" [value]="symbol">{{symbol}}</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label for="chartType" class="form-label">Chart Type</label>
                  <select class="form-select" id="chartType" [(ngModel)]="selectedChartType">
                    <option *ngFor="let type of chartTypes" [value]="type">{{type}}</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label for="period" class="form-label">Time Period</label>
                  <select class="form-select" id="period" [(ngModel)]="selectedPeriod">
                    <option *ngFor="let period of periods" [value]="period">{{period}}</option>
                  </select>
                </div>
                <div class="col-md-3 d-flex align-items-end">
                  <button class="btn btn-primary w-100" (click)="loadChartData()">
                    <i class="bi bi-arrow-clockwise me-2"></i>Update Charts
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Price Chart -->
      <div class="row mb-4">
        <div class="col-md-12">
          <div class="card shadow">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">
                <i class="bi bi-graph-up me-2"></i>
                {{selectedSymbol}} Price History
                <span class="badge bg-primary ms-2">{{selectedPeriod}}</span>
              </h5>
              <div class="btn-group" role="group">
                <button type="button" class="btn btn-sm btn-outline-primary" (click)="toggleIndicators()">
                  <i class="bi bi-gear me-1"></i>
                  {{showIndicators ? 'Hide' : 'Show'}} Indicators
                </button>
              </div>
            </div>
            <div class="card-body">
              <div class="chart-container">
                <canvas baseChart
                  [data]="lineChartData"
                  [options]="lineChartOptions"
                  [type]="lineChartType">
                </canvas>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Technical Indicators -->
      <div class="row mb-4" *ngIf="showIndicators">
        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-header">
              <h6 class="mb-0"><i class="bi bi-speedometer2 me-2"></i>RSI (Relative Strength Index)</h6>
            </div>
            <div class="card-body">
              <div class="chart-container">
                <canvas baseChart
                  [data]="rsiChartData"
                  [options]="rsiChartOptions"
                  [type]="'line'">
                </canvas>
              </div>
              <div class="mt-3">
                <div class="row">
                  <div class="col-4">
                    <div class="card bg-light">
                      <div class="card-body text-center py-2">
                        <div class="small text-muted">Current RSI</div>
                        <div class="h4" [ngClass]="{'text-success': currentRSI < 70, 'text-danger': currentRSI >= 70}">
                          {{currentRSI | number:'1.0-1'}}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="col-4">
                    <div class="card bg-light">
                      <div class="card-body text-center py-2">
                        <div class="small text-muted">Signal</div>
                        <div class="h4" [ngClass]="{
                          'text-success': rsiSignal === 'OVERSOLD',
                          'text-warning': rsiSignal === 'NEUTRAL',
                          'text-danger': rsiSignal === 'OVERBOUGHT'
                        }">
                          {{rsiSignal}}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="col-4">
                    <div class="card bg-light">
                      <div class="card-body text-center py-2">
                        <div class="small text-muted">Trend</div>
                        <div class="h4" [ngClass]="{'text-success': rsiTrend === 'BULLISH', 'text-danger': rsiTrend === 'BEARISH'}">
                          {{rsiTrend}}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-header">
              <h6 class="mb-0"><i class="bi bi-activity me-2"></i>MACD (Moving Average Convergence Divergence)</h6>
            </div>
            <div class="card-body">
              <div class="chart-container">
                <canvas baseChart
                  [data]="macdChartData"
                  [options]="macdChartOptions"
                  [type]="'line'">
                </canvas>
              </div>
              <div class="mt-3">
                <div class="row">
                  <div class="col-4">
                    <div class="card bg-light">
                      <div class="card-body text-center py-2">
                        <div class="small text-muted">MACD Line</div>
                        <div class="h4" [ngClass]="{'text-success': macdLine > 0, 'text-danger': macdLine <= 0}">
                          {{macdLine | number:'1.3-3'}}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="col-4">
                    <div class="card bg-light">
                      <div class="card-body text-center py-2">
                        <div class="small text-muted">Signal</div>
                        <div class="h4" [ngClass]="{'text-success': macdSignal > 0, 'text-danger': macdSignal <= 0}">
                          {{macdSignal | number:'1.3-3'}}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="col-4">
                    <div class="card bg-light">
                      <div class="card-body text-center py-2">
                        <div class="small text-muted">Histogram</div>
                        <div class="h4" [ngClass]="{'text-success': macdHistogram > 0, 'text-danger': macdHistogram <= 0}">
                          {{macdHistogram | number:'1.3-3'}}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Agent Performance Charts -->
      <div class="row mb-4">
        <div class="col-md-12">
          <div class="card shadow">
            <div class="card-header">
              <h5 class="mb-0"><i class="bi bi-people me-2"></i>Agent Performance Metrics</h5>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-8">
                  <div class="chart-container">
                    <canvas baseChart
                      [data]="agentPerformanceChartData"
                      [options]="agentPerformanceChartOptions"
                      [type]="'bar'">
                    </canvas>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="card h-100">
                    <div class="card-body">
                      <h6 class="card-title">Top Performing Agents</h6>
                      <ul class="list-group list-group-flush">
                        <li *ngFor="let agent of topAgents" class="list-group-item d-flex justify-content-between align-items-center">
                          <span>
                            <i class="bi bi-robot me-2"></i>
                            {{agent.name}}
                          </span>
                          <span class="badge rounded-pill" [ngClass]="{
                            'bg-success': agent.successRate >= 80,
                            'bg-warning': agent.successRate >= 60 && agent.successRate < 80,
                            'bg-danger': agent.successRate < 60
                          }">
                            {{agent.successRate}}%
                          </span>
                        </li>
                      </ul>
                      <div class="mt-3">
                        <div class="small text-muted">Performance based on signal accuracy vs actual price movement</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Signal Distribution -->
      <div class="row">
        <div class="col-md-12">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0"><i class="bi bi-pie-chart me-2"></i>Signal Distribution (Last 7 Days)</h5>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-4">
                  <div class="chart-container">
                    <canvas baseChart
                      [data]="signalDistributionChartData"
                      [options]="signalDistributionChartOptions"
                      [type]="'doughnut'">
                    </canvas>
                  </div>
                </div>
                <div class="col-md-8">
                  <div class="table-responsive">
                    <table class="table table-hover">
                      <thead>
                        <tr>
                          <th>Agent</th>
                          <th>BUY Signals</th>
                          <th>SELL Signals</th>
                          <th>HOLD Signals</th>
                          <th>Accuracy</th>
                          <th>Last Signal</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr *ngFor="let agent of agentStats">
                          <td><i class="bi bi-robot me-2"></i>{{agent.name}}</td>
                          <td><span class="badge bg-success">{{agent.buySignals}}</span></td>
                          <td><span class="badge bg-danger">{{agent.sellSignals}}</span></td>
                          <td><span class="badge bg-secondary">{{agent.holdSignals}}</span></td>
                          <td>
                            <div class="progress" style="height: 8px;">
                              <div class="progress-bar" [ngClass]="{
                                'bg-success': agent.accuracy >= 70,
                                'bg-warning': agent.accuracy >= 50 && agent.accuracy < 70,
                                'bg-danger': agent.accuracy < 50
                              }" [style.width.%]="agent.accuracy"></div>
                            </div>
                            <small class="text-muted ms-2">{{agent.accuracy}}%</small>
                          </td>
                          <td>
                            <span class="badge" [ngClass]="{
                              'bg-success': agent.lastSignal === 'BUY',
                              'bg-danger': agent.lastSignal === 'SELL',
                              'bg-secondary': agent.lastSignal === 'HOLD'
                            }">
                              {{agent.lastSignal}}
                            </span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .chart-container {
      position: relative;
      height: 300px;
      width: 100%;
    }
    .card {
      border: none;
      box-shadow: 0 2px 10px rgba(0,0,0,0.08);
      transition: transform 0.2s;
    }
    .card:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 20px rgba(0,0,0,0.12);
    }
    .card-header {
      background-color: rgba(248, 249, 250, 0.9);
      border-bottom: 1px solid rgba(0,0,0,0.1);
    }
  `]
})
export class ChartsPageComponent implements OnInit {
  // Chart controls
  selectedSymbol = 'AAPL';
  selectedChartType = 'line';
  selectedPeriod = '30 days';
  showIndicators = true;

  symbols: string[] = [];
  chartTypes = ['line', 'candlestick', 'bar', 'area'];
  periods = ['7 days', '30 days', '90 days', '1 year'];

  // Price chart
  lineChartData: ChartConfiguration<'line'>['data'] = {
    labels: [],
    datasets: []
  };

  lineChartOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        }
      },
      y: {
        position: 'right',
        ticks: {
          callback: (value) => '$' + value
        }
      }
    }
  };

  lineChartType = 'line' as const;

  // RSI chart
  currentRSI = 58.5;
  rsiSignal = 'NEUTRAL';
  rsiTrend = 'BULLISH';
  rsiChartData: ChartConfiguration<'line'>['data'] = {
    labels: [],
    datasets: []
  };
  rsiChartOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        min: 0,
        max: 100,
        ticks: {
          callback: (value) => value + '%'
        },
        grid: {
          color: (context) => {
            const value = context.tick.value as number;
            if (value === 30 || value === 70) {
              return 'rgba(255, 0, 0, 0.3)';
            }
            if (value === 50) {
              return 'rgba(0, 0, 0, 0.1)';
            }
            return 'rgba(0, 0, 0, 0.05)';
          }
        }
      }
    }
  };

  // MACD chart
  macdLine = 0.045;
  macdSignal = 0.032;
  macdHistogram = 0.013;
  macdChartData: ChartConfiguration<'line' | 'bar'>['data'] = {
    labels: [],
    datasets: []
  };
  macdChartOptions: ChartConfiguration<'line' | 'bar'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true
      }
    }
  };

  // Agent performance
  agentPerformanceChartData: ChartConfiguration<'bar'>['data'] = {
    labels: [],
    datasets: []
  };
  agentPerformanceChartOptions: ChartConfiguration<'bar'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
      legend: {
        display: false
      }
    }
  };

  // Signal distribution
  signalDistributionChartData: ChartConfiguration<'doughnut'>['data'] = {
    labels: [],
    datasets: []
  };
  signalDistributionChartOptions: ChartConfiguration<'doughnut'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right'
      }
    }
  };

  // Agent data
  topAgents = [
    { name: 'Sentiment Analyst', successRate: 85 },
    { name: 'Technical Analyst', successRate: 78 },
    { name: 'Risk Analyst', successRate: 72 },
    { name: 'Options Analyst', successRate: 65 },
    { name: 'Fundamental Analyst', successRate: 60 }
  ];

  agentStats = [
    { name: 'Technical', buySignals: 12, sellSignals: 3, holdSignals: 5, accuracy: 78, lastSignal: 'BUY' },
    { name: 'Fundamental', buySignals: 8, sellSignals: 2, holdSignals: 10, accuracy: 60, lastSignal: 'HOLD' },
    { name: 'Sentiment', buySignals: 15, sellSignals: 4, holdSignals: 1, accuracy: 85, lastSignal: 'BUY' },
    { name: 'Macro', buySignals: 5, sellSignals: 2, holdSignals: 13, accuracy: 55, lastSignal: 'HOLD' },
    { name: 'Options', buySignals: 9, sellSignals: 6, holdSignals: 5, accuracy: 65, lastSignal: 'SELL' },
    { name: 'Risk', buySignals: 7, sellSignals: 3, holdSignals: 10, accuracy: 72, lastSignal: 'HOLD' },
    { name: 'Quant', buySignals: 6, sellSignals: 4, holdSignals: 10, accuracy: 58, lastSignal: 'HOLD' },
    { name: 'Sector', buySignals: 8, sellSignals: 2, holdSignals: 10, accuracy: 62, lastSignal: 'BUY' },
    { name: 'Compliance', buySignals: 0, sellSignals: 0, holdSignals: 20, accuracy: 50, lastSignal: 'HOLD' },
    { name: 'Crypto', buySignals: 11, sellSignals: 5, holdSignals: 4, accuracy: 68, lastSignal: 'BUY' }
  ];

  constructor(private monitoringService: MonitoringService) {}
  private priceHistoryData: PriceHistoryData | null = null;

  ngOnInit() {
    this.loadTickers();
    this.loadChartData();
  }

  loadTickers() {
    // Fetch all tickers from backend
    fetch('http://localhost:8082/api/tickers/all')
      .then(response => response.json())
      .then(data => {
        if (data.tickers && Array.isArray(data.tickers)) {
          this.symbols = data.tickers;
          console.log(`Loaded ${this.symbols.length} tickers from backend`);
          
          // If AAPL is not in the list, add it
          if (!this.symbols.includes('AAPL')) {
            this.symbols.unshift('AAPL');
          }
          
          // Sort symbols for better UX
          this.symbols.sort();
        } else {
          console.error('Invalid ticker data format:', data);
          // Fallback to default symbols
          this.symbols = ['AAPL', 'TSLA', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'BTC', 'ETH'];
        }
      })
      .catch(error => {
        console.error('Failed to load tickers:', error);
        // Fallback to default symbols
        this.symbols = ['AAPL', 'TSLA', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'BTC', 'ETH'];
      });
  }

  loadChartData() {
    this.monitoringService.getPriceHistory(this.selectedSymbol, this.selectedPeriod).subscribe({
      next: (data) => {
        this.priceHistoryData = data;
        this.generatePriceChartData();
        this.generateRSIChartData();
        this.generateMACDChartData();
        this.generateAgentPerformanceData();
        this.generateSignalDistributionData();
      },
      error: (err) => {
        console.error('Failed to load price history:', err);
        // Fallback to mock data
        this.priceHistoryData = null;
        this.generatePriceChartData();
        this.generateRSIChartData();
        this.generateMACDChartData();
        this.generateAgentPerformanceData();
        this.generateSignalDistributionData();
      }
    });
  }

  toggleIndicators() {
    this.showIndicators = !this.showIndicators;
  }

  private generatePriceChartData() {
    if (this.priceHistoryData) {
      const labels = this.priceHistoryData.labels;
      const prices = this.priceHistoryData.prices;

      // Compute SMA 20
      const sma20 = [];
      const period = 20;
      for (let i = 0; i < prices.length; i++) {
        if (i < period - 1) {
          sma20.push(null as any);
        } else {
          const sum = prices.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
          sma20.push(sum / period);
        }
      }

      this.lineChartData = {
        labels: labels,
        datasets: [
          {
            data: prices,
            label: `${this.selectedSymbol} Price`,
            borderColor: '#0d6efd',
            backgroundColor: 'rgba(13, 110, 253, 0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 0
          },
          {
            data: sma20,
            label: 'SMA 20',
            borderColor: '#6c757d',
            borderWidth: 1,
            borderDash: [5, 5],
            pointRadius: 0,
            fill: false
          }
        ]
      };
    } else {
      // Fallback to mock data
      const days = 30;
      const labels = [];
      const prices = [];

      let basePrice = 150;
      for (let i = days; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));

        basePrice += (Math.random() - 0.45) * 5;
        prices.push(Math.max(100, basePrice));
      }

      this.lineChartData = {
        labels: labels,
        datasets: [
          {
            data: prices,
            label: `${this.selectedSymbol} Price`,
            borderColor: '#0d6efd',
            backgroundColor: 'rgba(13, 110, 253, 0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 0
          },
          {
            data: prices.map(p => p * 0.95), // SMA approximation
            label: 'SMA 20',
            borderColor: '#6c757d',
            borderWidth: 1,
            borderDash: [5, 5],
            pointRadius: 0,
            fill: false
          }
        ]
      };
    }
  }

  private generateRSIChartData() {
    if (this.priceHistoryData && this.priceHistoryData.indicators.rsi.length > 0) {
      const labels = this.priceHistoryData.labels;
      const rsiValues = this.priceHistoryData.indicators.rsi;

      // Update current RSI and signal
      const latestRSI = rsiValues[rsiValues.length - 1];
      this.currentRSI = latestRSI;

      if (latestRSI >= 70) {
        this.rsiSignal = 'OVERBOUGHT';
      } else if (latestRSI <= 30) {
        this.rsiSignal = 'OVERSOLD';
      } else {
        this.rsiSignal = 'NEUTRAL';
      }

      // Determine trend
      if (rsiValues.length >= 2) {
        const prevRSI = rsiValues[rsiValues.length - 2];
        this.rsiTrend = latestRSI > prevRSI ? 'BULLISH' : 'BEARISH';
      } else {
        this.rsiTrend = 'NEUTRAL';
      }

      this.rsiChartData = {
        labels: labels,
        datasets: [
          {
            data: rsiValues,
            label: 'RSI (14)',
            borderColor: '#198754',
            backgroundColor: 'rgba(25, 135, 84, 0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 0
          }
        ]
      };
    } else {
      // Fallback to mock data
      const labels = [];
      const rsiValues = [];

      for (let i = 30; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        rsiValues.push(40 + Math.random() * 30);
      }

      this.rsiChartData = {
        labels: labels,
        datasets: [
          {
            data: rsiValues,
            label: 'RSI (14)',
            borderColor: '#198754',
            backgroundColor: 'rgba(25, 135, 84, 0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 0
          }
        ]
      };
    }
  }

  private generateMACDChartData() {
    if (this.priceHistoryData && this.priceHistoryData.indicators.macdLine.length > 0) {
      const labels = this.priceHistoryData.labels;
      const macdLine = this.priceHistoryData.indicators.macdLine;
      const macdSignal = this.priceHistoryData.indicators.macdSignal;
      const macdHistogram = this.priceHistoryData.indicators.macdHistogram;

      // Update latest values
      const lastIdx = macdLine.length - 1;
      this.macdLine = macdLine[lastIdx];
      this.macdSignal = macdSignal[lastIdx];
      this.macdHistogram = macdHistogram[lastIdx];

      this.macdChartData = {
        labels: labels,
        datasets: [
          {
            data: macdLine,
            label: 'MACD Line',
            borderColor: '#0d6efd',
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 0
          },
          {
            data: macdSignal,
            label: 'Signal Line',
            borderColor: '#dc3545',
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 0
          },
          {
            data: macdHistogram,
            label: 'Histogram',
            borderColor: '#6c757d',
            backgroundColor: macdHistogram.map(h => h > 0 ? 'rgba(13, 110, 253, 0.3)' : 'rgba(220, 53, 69, 0.3)'),
            type: 'bar' as const,
            order: 2
          }
        ]
      };
    } else {
      // Fallback to mock data
      const labels = [];
      const macdLine = [];
      const signalLine = [];
      const histogram = [];

      for (let i = 30; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));

        const base = Math.sin(i / 5) * 0.05;
        macdLine.push(base + (Math.random() - 0.5) * 0.02);
        signalLine.push(base * 0.8 + (Math.random() - 0.5) * 0.015);
        histogram.push(macdLine[macdLine.length - 1] - signalLine[signalLine.length - 1]);
      }

      this.macdChartData = {
        labels: labels,
        datasets: [
          {
            data: macdLine,
            label: 'MACD Line',
            borderColor: '#0d6efd',
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 0
          },
          {
            data: signalLine,
            label: 'Signal Line',
            borderColor: '#dc3545',
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 0
          },
          {
            data: histogram,
            label: 'Histogram',
            borderColor: '#6c757d',
            backgroundColor: histogram.map(h => h > 0 ? 'rgba(13, 110, 253, 0.3)' : 'rgba(220, 53, 69, 0.3)'),
            type: 'bar' as const,
            order: 2
          }
        ]
      };
    }
  }

  private generateAgentPerformanceData() {
    const agents = this.agentStats.map(a => a.name);
    const successRates = this.agentStats.map(a => a.accuracy);

    this.agentPerformanceChartData = {
      labels: agents,
      datasets: [
        {
          data: successRates,
          label: 'Success Rate (%)',
          backgroundColor: successRates.map(rate => {
            if (rate >= 80) return '#198754';
            if (rate >= 60) return '#ffc107';
            return '#dc3545';
          })
        }
      ]
    };
  }

  private generateSignalDistributionData() {
    const buySignals = this.agentStats.reduce((sum, a) => sum + a.buySignals, 0);
    const sellSignals = this.agentStats.reduce((sum, a) => sum + a.sellSignals, 0);
    const holdSignals = this.agentStats.reduce((sum, a) => sum + a.holdSignals, 0);

    this.signalDistributionChartData = {
      labels: ['BUY', 'SELL', 'HOLD'],
      datasets: [
        {
          data: [buySignals, sellSignals, holdSignals],
          backgroundColor: ['#198754', '#dc3545', '#6c757d'],
          hoverBackgroundColor: ['#157347', '#bb2d3b', '#5c636a']
        }
      ]
    };
  }
}