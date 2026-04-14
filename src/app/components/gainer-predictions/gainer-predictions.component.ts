import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/index';

interface FinalPrediction {
  rank: number;
  symbol: string;
  expectedGain: string;
  confidence: string;
  signal: string;
  signalStrength: string;
  agentCount: number;
  reasoning: string;
  predictionDate: string;
  targetDate: string;
  leaderValidated: boolean;
  validationScore: string;
  tested: boolean;
  testScore: string;
  testResult: string;
}

interface ConsensusPrediction {
  symbol: string;
  agentCount: number;
  averageGain: string;
  averageConfidence: string;
  consensusSignal: string;
  signalStrength: string;
  reasoning: string;
}

interface HistoricalPrediction {
  id: number;
  symbol: string;
  predictionDate: string;
  predictedGain: string;
  actualGain: string;
  accuracy: string;
  accuracyPercentage: string;
}

interface DashboardStats {
  totalPredictions: number;
  accuratePredictions: number;
  accuracyRate: string;
  averageGain: string;
  bestPrediction: string;
  worstPrediction: string;
  mostAccurateAgent: string;
  predictionDaysAhead: number;
  lastUpdated: string;
}

@Component({
  selector: 'app-gainer-predictions',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="gainer-predictions">
      <!-- Header -->
      <div class="card mb-4">
        <div class="card-header bg-success text-white">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h5 class="mb-0">👥 Collaborative Top Gainers Prediction</h5>
              <small>All 10 agents working together to predict top gainers 2 days in advance</small>
            </div>
            <div class="btn-group">
              <button class="btn btn-sm btn-light" (click)="generatePredictions()" [disabled]="isGenerating">
                <span *ngIf="!isGenerating">🎯 Generate Predictions</span>
                <span *ngIf="isGenerating">
                  <span class="spinner-border spinner-border-sm me-1"></span>
                  Agents Collaborating...
                </span>
              </button>
              <button class="btn btn-sm btn-outline-light" (click)="loadHistorical()">
                📊 History
              </button>
            </div>
          </div>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-8">
              <div class="alert alert-info">
                <strong>How it works:</strong> All 10 agents analyze stocks independently, then collaborate through consensus.
                The leader validates and tests predictions for accuracy. Predictions target 2 days ahead.
              </div>
            </div>
            <div class="col-md-4">
              <div class="d-flex flex-wrap gap-2">
                <span class="badge bg-primary">10 Agents</span>
                <span class="badge bg-success">2-Day Forecast</span>
                <span class="badge bg-warning">Leader Validated</span>
                <span class="badge bg-info">Tested</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Dashboard Stats -->
      <div *ngIf="dashboardStats" class="row mb-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h6 class="mb-0">📈 Prediction Performance</h6>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-3 text-center">
                  <div class="h2 mb-1 text-success">{{dashboardStats.accuracyRate}}</div>
                  <div class="small text-muted">Accuracy Rate</div>
                </div>
                <div class="col-md-3 text-center">
                  <div class="h2 mb-1">{{dashboardStats.totalPredictions}}</div>
                  <div class="small text-muted">Total Predictions</div>
                </div>
                <div class="col-md-3 text-center">
                  <div class="h2 mb-1 text-primary">{{dashboardStats.averageGain}}</div>
                  <div class="small text-muted">Average Gain</div>
                </div>
                <div class="col-md-3 text-center">
                  <div class="h2 mb-1">{{dashboardStats.predictionDaysAhead}} days</div>
                  <div class="small text-muted">Forecast Horizon</div>
                </div>
              </div>
              <div class="mt-3">
                <small class="text-muted">Best: {{dashboardStats.bestPrediction}} | Worst: {{dashboardStats.worstPrediction}} | Most Accurate: {{dashboardStats.mostAccurateAgent}}</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Final Predictions -->
      <div *ngIf="finalPredictions.length > 0" class="card mb-4">
        <div class="card-header bg-primary text-white">
          <div class="d-flex justify-content-between align-items-center">
            <h6 class="mb-0">🏆 Final Top 10 Gainers Prediction (2 Days Ahead)</h6>
            <small>Leader Validated & Tested</small>
          </div>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover table-dark mb-0">
              <thead class="sticky-top" style="top: 0; z-index: 1;">
                <tr>
                  <th scope="col" class="ps-3">Rank</th>
                  <th scope="col">Symbol</th>
                  <th scope="col">Expected Gain</th>
                  <th scope="col">Confidence</th>
                  <th scope="col">Signal</th>
                  <th scope="col">Agreement</th>
                  <th scope="col">Agents</th>
                  <th scope="col">Validation</th>
                  <th scope="col">Test Result</th>
                  <th scope="col" class="text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let pred of finalPredictions" 
                    [ngClass]="{'table-success': pred.rank <= 3, 'table-primary': pred.rank <= 6, 'table-secondary': pred.rank > 6}">
                  <td class="ps-3">
                    <div class="d-flex align-items-center">
                      <div class="rank-badge me-2" [ngClass]="{'bg-warning': pred.rank === 1, 'bg-success': pred.rank === 2, 'bg-primary': pred.rank === 3, 'bg-secondary': pred.rank > 3}">
                        {{pred.rank}}
                      </div>
                      <div *ngIf="pred.rank === 1" class="small text-warning">🔥 Top Pick</div>
                    </div>
                  </td>
                  <td>
                    <div class="fw-bold text-white">{{pred.symbol}}</div>
                    <div class="small text-white-75">Target: {{pred.targetDate}}</div>
                  </td>
                  <td>
                    <div class="h5 mb-0" [ngClass]="getGainClass(pred.expectedGain)">
                      {{pred.expectedGain}}
                    </div>
                  </td>
                  <td>
                    <div class="progress" style="height: 10px; width: 100px;">
                      <div class="progress-bar" 
                           [ngClass]="getConfidenceClass(pred.confidence)"
                           [style.width.%]="parsePercentage(pred.confidence)">
                      </div>
                    </div>
                    <small class="text-white">{{pred.confidence}}</small>
                  </td>
                  <td>
                    <span class="badge" [ngClass]="getSignalBadgeClass(pred.signal)">
                      {{pred.signal}}
                    </span>
                  </td>
                  <td>
                    <div class="progress" style="height: 8px; width: 80px;">
                      <div class="progress-bar bg-info" 
                           [style.width.%]="parsePercentage(pred.signalStrength)">
                      </div>
                    </div>
                    <small class="text-white">{{pred.signalStrength}}</small>
                  </td>
                  <td>
                    <span class="badge bg-dark">{{pred.agentCount}}/10</span>
                  </td>
                  <td>
                    <span *ngIf="pred.leaderValidated" class="badge bg-success">✓ {{pred.validationScore}}</span>
                    <span *ngIf="!pred.leaderValidated" class="badge bg-warning">Pending</span>
                  </td>
                  <td>
                    <span *ngIf="pred.tested" class="badge" [ngClass]="getTestResultClass(pred.testResult)">
                      {{pred.testScore}} {{pred.testResult.includes('PASS') ? '✓' : '⚠️'}}
                    </span>
                    <span *ngIf="!pred.tested" class="badge bg-secondary">Not Tested</span>
                  </td>
                  <td class="text-center">
                    <button class="btn btn-sm btn-outline-primary" (click)="showReasoning(pred)">
                      📝 Reasoning
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Consensus Predictions -->
      <div *ngIf="consensusPredictions.length > 0" class="card mb-4">
        <div class="card-header bg-info text-white">
          <h6 class="mb-0">🤝 Agent Consensus (All Analyzed Stocks)</h6>
        </div>
        <div class="card-body">
          <div class="row">
            <div *ngFor="let pred of consensusPredictions.slice(0, 12)" class="col-md-3 mb-3">
              <div class="card h-100">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="mb-0">{{pred.symbol}}</h6>
                    <span class="badge" [ngClass]="getSignalBadgeClass(pred.consensusSignal)">
                      {{pred.consensusSignal}}
                    </span>
                  </div>
                  <div class="mb-2">
                    <div class="small text-muted">Expected Gain</div>
                    <div class="h5" [ngClass]="getGainClass(pred.averageGain)">{{pred.averageGain}}</div>
                  </div>
                  <div class="mb-2">
                    <div class="small text-muted">Agent Agreement</div>
                    <div class="d-flex align-items-center">
                      <div class="progress flex-grow-1" style="height: 6px;">
                        <div class="progress-bar bg-info" [style.width.%]="parsePercentage(pred.signalStrength)"></div>
                      </div>
                      <small class="ms-2">{{pred.signalStrength}}</small>
                    </div>
                  </div>
                  <div class="small text-muted">
                    {{pred.agentCount}} agents | {{pred.averageConfidence}} confidence
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Historical Predictions -->
      <div *ngIf="showHistory && historicalPredictions.length > 0" class="card mb-4">
        <div class="card-header bg-secondary text-white">
          <div class="d-flex justify-content-between align-items-center">
            <h6 class="mb-0">📜 Historical Accuracy</h6>
            <small>Past prediction performance</small>
          </div>
        </div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Symbol</th>
                  <th>Predicted</th>
                  <th>Actual</th>
                  <th>Accuracy</th>
                  <th>Score</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let hist of historicalPredictions">
                  <td>{{hist.predictionDate | date:'shortDate'}}</td>
                  <td><strong>{{hist.symbol}}</strong></td>
                  <td>{{hist.predictedGain}}</td>
                  <td>{{hist.actualGain}}</td>
                  <td>
                    <span class="badge" [ngClass]="hist.accuracy === '✓' ? 'bg-success' : 'bg-danger'">
                      {{hist.accuracy}}
                    </span>
                  </td>
                  <td>{{hist.accuracyPercentage}}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Agent Logs -->
      <div *ngIf="agentLogs.length > 0" class="card">
        <div class="card-header">
          <h6 class="mb-0">📋 Agent Collaboration Log</h6>
        </div>
        <div class="card-body" style="max-height: 200px; overflow-y: auto;">
          <div *ngFor="let log of agentLogs" class="log-entry mb-1 small text-muted">
            {{log}}
          </div>
        </div>
      </div>

      <!-- Loading/Error States -->
      <div *ngIf="isGenerating" class="text-center py-5">
        <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status"></div>
        <h5 class="mt-3">10 Agents Collaborating...</h5>
        <p class="text-muted">Technical, Fundamental, Sentiment, Macro, Crypto, Options, Risk, Quant, Sector, and Compliance analysts are working together</p>
        <div class="progress mt-3" style="height: 10px;">
          <div class="progress-bar progress-bar-striped progress-bar-animated" [style.width.%]="progress"></div>
        </div>
        <small>{{progress}}% complete</small>
      </div>

      <div *ngIf="errorMessage" class="alert alert-danger">
        {{errorMessage}}
      </div>

      <div *ngIf="!isGenerating && finalPredictions.length === 0 && !showHistory" class="text-center py-5 text-muted">
        <div class="mb-3">🤖</div>
        <h5>No predictions generated yet</h5>
        <p>Click "Generate Predictions" to start 10-agent collaborative analysis</p>
        <button class="btn btn-primary mt-2" (click)="generatePredictions()">
          🎯 Start Collaborative Prediction
        </button>
      </div>
    </div>
  `,
  styles: [`
    .gainer-predictions {
      font-size: 0.875rem;
    }
    .rank-badge {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      color: white;
    }
    .log-entry {
      border-left: 2px solid var(--accent-blue);
      padding-left: 10px;
      background: rgba(255, 255, 255, 0.03);
      border-radius: 4px;
      padding: 4px 8px;
    }
    .table th {
      font-weight: 600;
      background: var(--bg-secondary);
    }
    .progress {
      background-color: var(--bg-secondary);
    }
  `]
})
export class GainerPredictionsComponent implements OnInit {
  finalPredictions: FinalPrediction[] = [];
  consensusPredictions: ConsensusPrediction[] = [];
  historicalPredictions: HistoricalPrediction[] = [];
  dashboardStats: DashboardStats | null = null;
  agentLogs: string[] = [];
  isGenerating = false;
  showHistory = false;
  errorMessage = '';
  progress = 0;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadDashboardStats();
  }

  generatePredictions() {
    this.isGenerating = true;
    this.progress = 0;
    this.errorMessage = '';
    
    // Simulate progress
    const progressInterval = setInterval(() => {
      this.progress = Math.min(this.progress + 10, 90);
    }, 500);

    const requestBody = {
      daysAhead: 2,
      topN: 10,
      forceRefresh: true
    };

    // Start real monitoring first
    this.http.post<any>(`${environment.apiUrl}/predictions/monitoring/start-analysis`, requestBody)
      .subscribe({
        next: (monitoringResponse) => {
          console.log('Real monitoring started:', monitoringResponse);
          
          // Then generate predictions
          this.http.post<any>(`${environment.apiUrl}/predictions/collaborative`, requestBody)
            .subscribe({
              next: (response) => {
                clearInterval(progressInterval);
                this.progress = 100;
                
                if (response.status === 'success') {
                  this.finalPredictions = response.prediction.finalPredictions;
                  this.consensusPredictions = response.prediction.consensusPredictions;
                  this.agentLogs = response.prediction.agentLogs;
                  
                  // Show success message
                  setTimeout(() => {
                    this.isGenerating = false;
                    this.progress = 0;
                  }, 500);
                }
              },
              error: (error) => {
                clearInterval(progressInterval);
                console.error('Failed to generate predictions:', error);
                this.errorMessage = 'Failed to generate predictions. Please try again.';
                this.isGenerating = false;
                this.progress = 0;
              }
            });
        },
        error: (error) => {
          console.warn('Real monitoring failed, falling back to regular predictions:', error);
          
          // Fallback to regular predictions if monitoring fails
          this.http.post<any>(`${environment.apiUrl}/predictions/collaborative`, requestBody)
            .subscribe({
              next: (response) => {
                clearInterval(progressInterval);
                this.progress = 100;
                
                if (response.status === 'success') {
                  this.finalPredictions = response.prediction.finalPredictions;
                  this.consensusPredictions = response.prediction.consensusPredictions;
                  this.agentLogs = response.prediction.agentLogs;
                  
                  // Show success message
                  setTimeout(() => {
                    this.isGenerating = false;
                    this.progress = 0;
                  }, 500);
                }
              },
              error: (error2) => {
                clearInterval(progressInterval);
                console.error('Failed to generate predictions:', error2);
                this.errorMessage = 'Failed to generate predictions. Please try again.';
                this.isGenerating = false;
                this.progress = 0;
              }
            });
        }
      });
  }

  loadHistorical() {
    this.showHistory = !this.showHistory;
    
    if (this.showHistory && this.historicalPredictions.length === 0) {
      this.http.get<any>(`${environment.apiUrl}/predictions/historical?limit=20`)
        .subscribe({
          next: (response) => {
            if (response.status === 'success') {
              this.historicalPredictions = response.historicalPredictions;
            }
          },
          error: (error) => {
            console.error('Failed to load historical predictions:', error);
          }
        });
    }
  }

  loadDashboardStats() {
    this.http.get<any>(`${environment.apiUrl}/predictions/dashboard`)
      .subscribe({
        next: (response) => {
          if (response.status === 'success') {
            this.dashboardStats = response.stats;
          }
        },
        error: (error) => {
          console.error('Failed to load dashboard stats:', error);
        }
      });
  }

  showReasoning(prediction: FinalPrediction) {
    alert(`Reasoning for ${prediction.symbol}:\n\n${prediction.reasoning}`);
  }

  // Helper methods
  getGainClass(gain: string): string {
    const value = parseFloat(gain);
    if (value >= 5.0) return 'text-success';
    if (value >= 2.0) return 'text-primary';
    if (value >= 0) return 'text-warning';
    return 'text-danger';
  }

  getConfidenceClass(confidence: string): string {
    const value = parseFloat(confidence);
    if (value >= 80) return 'bg-success';
    if (value >= 60) return 'bg-warning';
    return 'bg-danger';
  }

  getSignalBadgeClass(signal: string): string {
    switch (signal) {
      case 'STRONG_BUY':
      case 'BUY':
        return 'bg-success';
      case 'SELL':
        return 'bg-danger';
      case 'HOLD':
        return 'bg-warning text-dark';
      default:
        return 'bg-secondary';
    }
  }

  getTestResultClass(testResult: string): string {
    if (testResult.includes('PASS')) return 'bg-success';
    if (testResult.includes('MODERATE')) return 'bg-warning text-dark';
    if (testResult.includes('NEEDS REVIEW')) return 'bg-danger';
    return 'bg-secondary';
  }

  parsePercentage(percentage: string): number {
    return parseFloat(percentage);
  }
}
