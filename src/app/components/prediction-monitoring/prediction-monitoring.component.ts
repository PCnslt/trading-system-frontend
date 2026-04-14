import { Component, OnInit, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/index';
import { MonitoringService } from '../../services/monitoring.service';

interface AgentProgress {
  agentId: string;
  agentName: string;
  stocksAssigned: number;
  stocksAnalyzed: number;
  progressPercentage: number;
  status: string;
  currentStock: string;
  startTime: string;
  estimatedCompletion: string;
}

interface PipelineStage {
  stageId: string;
  stageName: string;
  status: string;
  progress: number;
  startTime: string | null;
  estimatedCompletion: string | null;
  agentsInvolved: string;
  description: string;
}

interface RealStock {
  symbol: string;
  name: string;
  dailyChange: string;
  price: string;
  sector: string;
  volume: string;
  marketCap: string;
  analysisPriority: string;
}

@Component({
  selector: 'app-prediction-monitoring',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="prediction-monitoring">
      <!-- Header -->
      <div *ngIf="showHeader" class="card mb-4">
        <div class="card-header bg-info text-white">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h5 class="mb-0">🔍 Real-time Prediction Monitoring</h5>
              <small>Watch all 10 agents collaborate in real-time</small>
            </div>
            <div class="btn-group">
              <button class="btn btn-sm btn-light" (click)="refreshMonitoring()" [disabled]="isRefreshing">
                <span *ngIf="!isRefreshing">🔄 Refresh</span>
                <span *ngIf="isRefreshing">
                  <span class="spinner-border spinner-border-sm me-1"></span>
                  Updating...
                </span>
              </button>
              <button class="btn btn-sm btn-outline-light" (click)="toggleAutoRefresh()">
                {{autoRefresh ? '⏸️ Pause' : '▶️ Auto-refresh'}}
              </button>
            </div>
          </div>
        </div>
        <div class="card-body">
          <div class="alert alert-info">
            <strong>Live Monitoring:</strong> Watch each agent analyze stocks, see consensus building, and leader validation in real-time.
            Data updates every 10 seconds when auto-refresh is enabled.
          </div>
        </div>
      </div>

      <!-- Pipeline Status -->
      <div class="card mb-4">
        <div class="card-header">
          <h6 class="mb-0">📊 Prediction Pipeline Status</h6>
        </div>
        <div class="card-body">
          <div *ngIf="pipelineStages.length > 0" class="pipeline-tracker">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div>
                <span class="badge bg-primary">Overall Progress: {{overallProgress}}%</span>
                <span class="badge bg-info ms-2">Current: {{currentStage}}</span>
              </div>
              <div class="small text-muted">
                Estimated completion: {{estimatedCompletion}}
              </div>
            </div>
            
            <div class="pipeline-stages">
              <div *ngFor="let stage of pipelineStages" class="pipeline-stage" [ngClass]="getStageStatusClass(stage.status)">
                <div class="stage-header">
                  <div class="stage-name">{{stage.stageName}}</div>
                  <div class="stage-status">{{stage.status}}</div>
                </div>
                <div class="progress" style="height: 8px;">
                  <div class="progress-bar" [ngClass]="getProgressBarClass(stage.status)" 
                       [style.width.%]="stage.progress"></div>
                </div>
                <div class="stage-details">
                  <div class="small">{{stage.description}}</div>
                  <div class="small text-muted">Agents: {{stage.agentsInvolved}}</div>
                  <div *ngIf="stage.startTime" class="small text-muted">
                    Started: {{formatTime(stage.startTime)}}
                  </div>
                  <div *ngIf="stage.estimatedCompletion" class="small text-muted">
                    ETA: {{formatTime(stage.estimatedCompletion)}}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Agent Progress Grid -->
      <div class="card mb-4">
        <div class="card-header">
          <h6 class="mb-0">👥 Agent Analysis Progress</h6>
        </div>
        <div class="card-body">
          <div *ngIf="agentProgress.length > 0" class="row">
            <div *ngFor="let agent of agentProgress" class="col-md-6 mb-3">
              <div class="card h-100">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                      <h6 class="mb-0">{{agent.agentName}}</h6>
                      <small class="text-muted">{{agent.agentId}}</small>
                    </div>
                    <span class="badge" [ngClass]="getAgentStatusClass(agent.status)">
                      {{agent.status}}
                    </span>
                  </div>
                  
                  <div class="mb-3">
                    <div class="d-flex justify-content-between mb-1">
                      <small>Progress: {{agent.stocksAnalyzed}}/{{agent.stocksAssigned}} stocks</small>
                      <small>{{agent.progressPercentage}}%</small>
                    </div>
                    <div class="progress" style="height: 10px;">
                      <div class="progress-bar" [ngClass]="getProgressBarClass(agent.status)" 
                           [style.width.%]="agent.progressPercentage"></div>
                    </div>
                  </div>
                  
                  <div class="row">
                    <div class="col-6">
                      <div class="small text-muted">Current Stock</div>
                      <div class="fw-bold">{{agent.currentStock}}</div>
                    </div>
                    <div class="col-6">
                      <div class="small text-muted">ETA</div>
                      <div class="fw-bold">{{formatTime(agent.estimatedCompletion)}}</div>
                    </div>
                  </div>
                  
                  <div class="mt-2">
                    <button class="btn btn-sm btn-outline-primary w-100" (click)="viewAgentReport(agent.agentId)">
                      View Detailed Report
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Real Stocks from Yahoo Finance -->
      <div class="card mb-4">
        <div class="card-header bg-success text-white">
          <div class="d-flex justify-content-between align-items-center">
            <h6 class="mb-0">📈 Top 10 Gainers (Yahoo Finance)</h6>
            <a href="https://finance.yahoo.com/markets/stocks/gainers/" target="_blank" class="btn btn-sm btn-outline-light">
              ↗️ Source
            </a>
          </div>
        </div>
        <div class="card-body">
          <div *ngIf="realStocks.length > 0" class="table-responsive">
            <table class="table table-hover table-dark">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Name</th>
                  <th>Daily Change</th>
                  <th>Price</th>
                  <th>Sector</th>
                  <th>Volume</th>
                  <th>Market Cap</th>
                  <th>Priority</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let stock of realStocks">
                  <td class="fw-bold">{{stock.symbol}}</td>
                  <td>{{stock.name}}</td>
                  <td [ngClass]="getChangeClass(stock.dailyChange)">{{stock.dailyChange}}</td>
                  <td>{{stock.price}}</td>
                  <td><span class="badge bg-secondary">{{stock.sector}}</span></td>
                  <td class="small">{{stock.volume}}</td>
                  <td class="small">{{stock.marketCap}}</td>
                  <td>
                    <span class="badge" [ngClass]="getPriorityClass(stock.analysisPriority)">
                      {{stock.analysisPriority}}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="text-center small text-muted mt-2">
            Source: <a href="https://finance.yahoo.com/markets/stocks/gainers/" target="_blank">Yahoo Finance Gainers</a>
            • Updated: {{lastUpdated}}
            • Next update: {{nextUpdate}}
          </div>
        </div>
      </div>

      <!-- Leader Consolidation -->
      <div class="card">
        <div class="card-header bg-warning text-dark">
          <h6 class="mb-0">👑 Leader Consolidation & Validation</h6>
        </div>
        <div class="card-body">
          <div *ngIf="leaderConsolidation" class="row">
            <div class="col-md-4">
              <div class="card">
                <div class="card-body">
                  <h6>Leader Agent</h6>
                  <div class="h4">{{leaderConsolidation.leaderName}}</div>
                  <small class="text-muted">{{leaderConsolidation.leaderAgent}}</small>
                  <div class="mt-2">
                    <div class="small text-muted">Role</div>
                    <div>{{leaderConsolidation.role}}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="col-md-8">
              <div class="card">
                <div class="card-body">
                  <h6>Reports Received</h6>
                  <div class="d-flex align-items-center mb-3">
                    <div class="progress flex-grow-1" style="height: 10px;">
                      <div class="progress-bar bg-success" 
                           [style.width.%]="(leaderConsolidation.reportsReceived / leaderConsolidation.totalReportsExpected) * 100">
                      </div>
                    </div>
                    <div class="ms-3">
                      {{leaderConsolidation.reportsReceived}}/{{leaderConsolidation.totalReportsExpected}}
                    </div>
                  </div>
                  
                  <div class="table-responsive">
                    <table class="table table-sm">
                      <thead>
                        <tr>
                          <th>Agent</th>
                          <th>Stocks Analyzed</th>
                          <th>Top Pick</th>
                          <th>Gain</th>
                          <th>Received</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr *ngFor="let report of leaderConsolidation.receivedReports">
                          <td>{{report.agentName}}</td>
                          <td>{{report.stocksAnalyzed}}</td>
                          <td class="fw-bold">{{report.topPick}}</td>
                          <td [ngClass]="getGainClass(report.topPickGain)">{{report.topPickGain}}</td>
                          <td>{{formatTime(report.receivedTime)}}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div *ngIf="leaderConsolidation?.consensusProcess" class="mt-3">
            <h6>Consensus Process</h6>
            <div class="row">
              <div class="col-md-3">
                <div class="small text-muted">Stocks Considered</div>
                <div class="fw-bold">{{leaderConsolidation.consensusProcess.stocksConsidered}}</div>
              </div>
              <div class="col-md-3">
                <div class="small text-muted">Consensus Method</div>
                <div class="small">{{leaderConsolidation.consensusProcess.consensusMethod}}</div>
              </div>
              <div class="col-md-3">
                <div class="small text-muted">Validation Method</div>
                <div class="small">{{leaderConsolidation.consensusProcess.validationMethod}}</div>
              </div>
              <div class="col-md-3">
                <div class="small text-muted">Testing Method</div>
                <div class="small">{{leaderConsolidation.consensusProcess.testingMethod}}</div>
              </div>
            </div>
          </div>
          
          <div class="mt-3">
            <div class="alert" [ngClass]="getConsolidationAlertClass()">
              <strong>Current Status:</strong> {{leaderConsolidation?.consolidationStatus}} • 
              <strong>Current Task:</strong> {{leaderConsolidation?.currentTask}} • 
              <strong>ETA:</strong> {{formatTime(leaderConsolidation?.estimatedCompletion)}}
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div *ngIf="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status"></div>
        <h5 class="mt-3">Loading Monitoring Data...</h5>
        <p class="text-muted">Fetching real-time agent progress and stock data</p>
      </div>

      <div *ngIf="errorMessage" class="alert alert-danger">
        {{errorMessage}}
      </div>
    </div>
  `,
  styles: [`
    .prediction-monitoring {
      font-size: 0.875rem;
    }
    .pipeline-stages {
      display: flex;
      flex-direction: column;
      gap: 15px;
    }
    .pipeline-stage {
      padding: 15px;
      border-radius: 8px;
      background: var(--bg-card);
      border-left: 4px solid var(--border-color);
    }
    .pipeline-stage.completed {
      border-left-color: var(--success);
      background: rgba(0, 214, 143, 0.05);
    }
    .pipeline-stage.in-progress {
      border-left-color: var(--primary);
      background: rgba(0, 123, 255, 0.05);
    }
    .pipeline-stage.pending {
      border-left-color: var(--secondary);
      background: rgba(108, 117, 125, 0.05);
    }
    .stage-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    .stage-name {
      font-weight: 600;
    }
    .stage-status {
      font-size: 0.75rem;
      padding: 2px 8px;
      border-radius: 12px;
      background: var(--bg-secondary);
    }
    .stage-details {
      margin-top: 10px;
      font-size: 0.8rem;
    }
    .table th {
      font-weight: 600;
      background: var(--bg-secondary);
    }
  `]
})
export class PredictionMonitoringComponent implements OnInit {
  @Input() showHeader = true;
  
  agentProgress: AgentProgress[] = [];
  pipelineStages: PipelineStage[] = [];
  realStocks: RealStock[] = [];
  leaderConsolidation: any = null;
  overallProgress = 0;
  currentStage = '';
  estimatedCompletion = '';
  lastUpdated = '';
  nextUpdate = '';
  isLoading = false;
  isRefreshing = false;
  autoRefresh = true;
  errorMessage = '';
  private refreshInterval: any;

  constructor(
    private http: HttpClient,
    private monitoringService: MonitoringService
  ) {}

  ngOnInit() {
    this.loadMonitoringData();
    
    // Set up auto-refresh every 10 seconds
    this.refreshInterval = setInterval(() => {
      if (this.autoRefresh) {
        this.loadMonitoringData();
      }
    }, 10000);
  }

  ngOnDestroy() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }

  loadMonitoringData() {
    this.isLoading = true;
    this.errorMessage = '';
    
    // Load all monitoring data in parallel
    Promise.all([
      this.loadPipelineStatus(),
      this.loadAgentProgress(),
      this.loadRealStocks(),
      this.loadLeaderConsolidation()
    ]).finally(() => {
      this.isLoading = false;
      this.isRefreshing = false;
    });
  }

  loadPipelineStatus() {
    return new Promise<void>((resolve) => {
      this.http.get<any>(`${environment.apiUrl}/predictions/monitoring/pipeline`)
        .subscribe({
          next: (response) => {
            if (response.status === 'success') {
              this.pipelineStages = response.pipeline;
              this.overallProgress = response.overallProgress;
              this.currentStage = response.currentStage;
              this.estimatedCompletion = this.formatTime(response.estimatedTotalCompletion);
            }
            resolve();
          },
          error: (error) => {
            console.error('Failed to load pipeline status:', error);
            resolve();
          }
        });
    });
  }

  loadAgentProgress() {
    return new Promise<void>((resolve) => {
      this.http.get<any>(`${environment.apiUrl}/predictions/monitoring/progress`)
        .subscribe({
          next: (response) => {
            if (response.status === 'success') {
              this.agentProgress = response.progress.agentStatus;
            }
            resolve();
          },
          error: (error) => {
            console.error('Failed to load agent progress:', error);
            resolve();
          }
        });
    });
  }

  loadRealStocks() {
    return new Promise<void>((resolve) => {
      this.http.get<any>(`${environment.apiUrl}/predictions/monitoring/real-stocks`)
        .subscribe({
          next: (response) => {
            if (response.status === 'success') {
              this.realStocks = response.stocks;
              this.lastUpdated = this.formatTime(response.lastUpdated);
              this.nextUpdate = this.formatTime(response.nextUpdate);
            }
            resolve();
          },
          error: (error) => {
            console.error('Failed to load real stocks:', error);
            resolve();
          }
        });
    });
  }

  loadLeaderConsolidation() {
    return new Promise<void>((resolve) => {
      this.http.get<any>(`${environment.apiUrl}/predictions/monitoring/leader-consolidation`)
        .subscribe({
          next: (response) => {
            if (response.status === 'success') {
              this.leaderConsolidation = response.consolidation;
            }
            resolve();
          },
          error: (error) => {
            console.error('Failed to load leader consolidation:', error);
            resolve();
          }
        });
    });
  }

  refreshMonitoring() {
    this.isRefreshing = true;
    this.loadMonitoringData();
  }

  toggleAutoRefresh() {
    this.autoRefresh = !this.autoRefresh;
  }

  viewAgentReport(agentId: string) {
    this.monitoringService.getAgentReport(agentId).subscribe({
      next: (response: any) => {
        if (response.status === 'success') {
          const report = response.report;
          // Create a formatted report message
          let reportMessage = `📊 Detailed Analysis Report for ${report.agentName}\n`;
          reportMessage += `Expertise: ${report.expertise}\n`;
          reportMessage += `Model Used: ${report.modelUsed}\n`;
          reportMessage += `Analysis Focus: ${report.analysisFocus}\n`;
          reportMessage += `Total Analyses: ${report.totalAnalyses}\n`;
          reportMessage += `Average Confidence: ${report.averageConfidence}\n\n`;
          reportMessage += `Recent Analyses:\n`;
          
          if (report.analyses && report.analyses.length > 0) {
            report.analyses.slice(0, 3).forEach((analysis: any, i: number) => {
              reportMessage += `${i+1}. ${analysis.symbol}: ${analysis.signal} (${analysis.confidence}) - ${analysis.reasoning}\n`;
            });
          }
          
          reportMessage += `\nReport generated: ${report.completionTime}`;
          
          alert(reportMessage);
        } else {
          alert(`Failed to load report for ${agentId}: ${response.message}`);
        }
      },
      error: (error: any) => {
        alert(`Error loading report for ${agentId}: ${error.message}`);
      }
    });
  }

  // Helper methods
  getStageStatusClass(status: string): string {
    switch (status) {
      case 'COMPLETED': return 'completed';
      case 'IN_PROGRESS': return 'in-progress';
      default: return 'pending';
    }
  }

  getProgressBarClass(status: string): string {
    switch (status) {
      case 'COMPLETED': return 'bg-success';
      case 'IN_PROGRESS': return 'bg-primary';
      default: return 'bg-secondary';
    }
  }

  getAgentStatusClass(status: string): string {
    switch (status) {
      case 'COMPLETED': return 'bg-success';
      case 'ANALYZING': return 'bg-primary';
      default: return 'bg-secondary';
    }
  }

  getChangeClass(change: string): string {
    return change.includes('+') ? 'text-success' : 'text-danger';
  }

  getPriorityClass(priority: string): string {
    switch (priority) {
      case 'HIGH': return 'bg-danger';
      case 'MEDIUM': return 'bg-warning text-dark';
      default: return 'bg-secondary';
    }
  }

  getGainClass(gain: string): string {
    const value = parseFloat(gain);
    if (value >= 5.0) return 'text-success';
    if (value >= 2.0) return 'text-primary';
    if (value >= 0) return 'text-warning';
    return 'text-danger';
  }

  getConsolidationAlertClass(): string {
    const status = this.leaderConsolidation?.consolidationStatus;
    switch (status) {
      case 'COMPLETED': return 'alert-success';
      case 'IN_PROGRESS': return 'alert-primary';
      default: return 'alert-secondary';
    }
  }

  formatTime(timestamp: string): string {
    if (!timestamp) return 'N/A';
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return timestamp;
    }
  }
}