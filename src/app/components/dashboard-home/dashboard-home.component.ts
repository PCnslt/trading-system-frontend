import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { RouterModule, RouterLinkActive } from '@angular/router';
import { environment } from '../../../environments/index'; // environment config
import { AgentActivityFeedComponent } from '../agent-activity-feed/agent-activity-feed.component';
import { AgentStatusTableComponent } from '../agent-status-dashboard/agent-status-table.component';
import { PerformanceMetricsComponent } from '../performance-metrics/performance-metrics.component';
import { ChatPanelComponent } from '../chat-panel/chat-panel.component';
import { LeaderPredictionComponent } from '../leader-prediction/leader-prediction.component';
import { GainerPredictionsComponent } from '../gainer-predictions/gainer-predictions.component';
import { PredictionMonitoringComponent } from '../prediction-monitoring/prediction-monitoring.component';
import { MonitoringService } from '../../services/monitoring.service';

interface TopRecommendation {
  symbol: string;
  name: string;
  type: string;
  signal: string;
  confidence: number;
  profitability_score: number;
  reasoning: string;
  timestamp: string;
  agent: string;
  total_agents: number;
}

interface AgentActivity {
  id: number;
  agentId: string;
  task: string;
  timestamp: string;
  status: string;
  symbol: string;
  reasoning: string;
}

@Component({
  selector: 'app-dashboard-home',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    AgentActivityFeedComponent,
    AgentStatusTableComponent,
    PerformanceMetricsComponent,
    ChatPanelComponent,
    LeaderPredictionComponent,
    GainerPredictionsComponent,
    PredictionMonitoringComponent
  ],
  template: `
    <div class="container-fluid p-3">
      <!-- Main Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card gradient-primary text-white">
            <div class="card-body py-3">
              <div class="row align-items-center">
                <div class="col-md-8">
                  <div class="d-flex align-items-center">
                    <div class="me-3">
                      <div class="h4 mb-1 fw-bold">🚀 Trading Agent System</div>
                      <div class="text-white-75">10-agent real-time analysis dashboard with thousands of stocks, ETFs, and cryptocurrencies</div>
                    </div>
                  </div>
                </div>
                <div class="col-md-4 text-end">
                  <div class="d-flex justify-content-end gap-3">
                    <div class="text-center">
                      <div class="h5 mb-0 fw-bold" [ngClass]="backendStatus === '✅ Connected' ? 'text-success' : 'text-warning'">{{backendStatus}}</div>
                      <div class="small text-white-75">Backend</div>
                    </div>
                    <div class="text-center">
                      <div class="h5 mb-0 fw-bold" [ngClass]="websocketStatus === '✅ Connected' ? 'text-success' : 'text-warning'">{{websocketStatus}}</div>
                      <div class="small text-white-75">WebSocket</div>
                    </div>
                    <div class="text-center">
                      <div class="h5 mb-0 fw-bold text-white">{{totalTickers || 0}}</div>
                      <div class="small text-white-75">Tickers</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card bg-primary text-white">
            <div class="card-body py-2">
              <div class="d-flex flex-wrap gap-2">
                <a routerLink="/" class="btn btn-sm btn-light" routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}">
                  <i class="bi bi-speedometer2 me-1"></i> Dashboard
                </a>
                <a routerLink="/charts" class="btn btn-sm btn-outline-light" routerLinkActive="active">
                  <i class="bi bi-graph-up me-1"></i> Charts
                </a>
                <a routerLink="/portfolio" class="btn btn-sm btn-outline-light" routerLinkActive="active">
                  <i class="bi bi-wallet2 me-1"></i> Portfolio
                </a>
                <button class="btn btn-sm btn-outline-light" disabled title="Coming soon">
                  <i class="bi bi-funnel me-1"></i> Filter
                </button>
                <button class="btn btn-sm btn-outline-light" disabled title="Coming soon">
                  <i class="bi bi-heart-pulse me-1"></i> Health
                </button>
                <!-- Navigation text removed as requested -->
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Stats Row -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card h-100 bg-primary text-white">
            <div class="card-body text-center">
              <div class="h4 mb-2">📊</div>
              <div class="h5 mb-1 fw-bold">{{totalTickers || 0}}</div>
              <div class="small fw-bold">Total Tickers</div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card h-100 bg-success text-white">
            <div class="card-body text-center">
              <div class="h4 mb-2">👥</div>
              <div class="h5 mb-1 fw-bold">10</div>
              <div class="small fw-bold">Active Agents</div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card h-100 bg-warning text-white">
            <div class="card-body text-center">
              <div class="h4 mb-2">📈</div>
              <div class="h5 mb-1 fw-bold">{{totalAnalyses || 0}}</div>
              <div class="small fw-bold">Analyses Today</div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card h-100 bg-info text-white">
            <div class="card-body text-center">
              <div class="h4 mb-2">⏱️</div>
              <div class="h5 mb-1 fw-bold">{{uptime || '0h'}}</div>
              <div class="small fw-bold">System Uptime</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Row -->
      <div class="row mb-4">
        <!-- Left Column: Top Recommendations -->
        <div class="col-lg-8">
          <div class="card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center bg-primary text-white">
              <h5 class="mb-0">🎯 Top Recommendations (Profitability Order)</h5>
              <div>
                <select class="form-select form-select-sm w-auto d-inline-block" [(ngModel)]="selectedCategory" (change)="generateRecommendations()">
                  <option value="all">All Categories</option>
                  <option value="tech">Technology</option>
                  <option value="financial">Financial</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="crypto">Cryptocurrency</option>
                  <option value="etfs">ETFs</option>
                </select>
                <button class="btn btn-sm btn-primary ms-2" (click)="generateRecommendations()" [disabled]="isGenerating">
                  <span *ngIf="!isGenerating">🔄 Refresh</span>
                  <span *ngIf="isGenerating">
                    <span class="spinner-border spinner-border-sm me-1"></span>
                    Analyzing...
                  </span>
                </button>
              </div>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive" style="max-height: 500px; overflow-y: auto;">
                <table class="table table-hover table-dark mb-0">
                  <thead class="sticky-top" style="top: 0; z-index: 1;">
                    <tr>
                      <th scope="col" class="ps-3">Rank</th>
                      <th scope="col">Symbol</th>
                      <th scope="col">Signal</th>
                      <th scope="col">Confidence</th>
                      <th scope="col">Profitability</th>
                      <th scope="col">Type</th>
                      <th scope="col">Time</th>
                      <th scope="col" class="text-center">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr *ngFor="let rec of allRecommendations; let i = index" 
                        [ngClass]="{'table-success': i === 0, 'table-primary': i === 1, 'table-secondary': i > 1}">
                      <td class="ps-3">
                        <div class="d-flex align-items-center">
                          <div class="rank-badge me-2" [ngClass]="i === 0 ? 'bg-warning' : 'bg-secondary'">
                            {{i + 1}}
                          </div>
                          <div *ngIf="i === 0" class="small text-warning">🔥 Top Pick</div>
                        </div>
                      </td>
                      <td>
                        <div class="fw-bold">{{rec.symbol}}</div>
                        <div class="small text-muted">{{rec.name}}</div>
                      </td>
                      <td>
                        <span class="badge" [ngClass]="getSignalBadgeClass(rec.signal)">
                          {{rec.signal}}
                        </span>
                      </td>
                      <td>
                        <div class="d-flex align-items-center gap-2">
                          <div class="progress flex-grow-1" style="height: 8px;">
                            <div class="progress-bar" 
                                 [ngClass]="getConfidenceClass(rec.confidence)"
                                 [style.width.%]="rec.confidence * 100">
                            </div>
                          </div>
                          <div class="small" style="min-width: 40px;">
                            {{rec.confidence * 100 | number:'1.1-1'}}%
                          </div>
                        </div>
                      </td>
                      <td>
                        <div class="d-flex align-items-center gap-2">
                          <div class="progress flex-grow-1" style="height: 8px;">
                            <div class="progress-bar" 
                                 [ngClass]="getProfitabilityBarClass(rec.profitability_score)"
                                 [style.width.%]="rec.profitability_score * 100">
                            </div>
                          </div>
                          <div class="small fw-bold" [ngClass]="getProfitabilityClass(rec.profitability_score)" style="min-width: 40px;">
                            {{rec.profitability_score | number:'1.2-2'}}
                          </div>
                        </div>
                      </td>
                      <td>
                        <span class="badge bg-secondary">{{rec.type}}</span>
                      </td>
                      <td class="small">{{rec.timestamp | date:'shortTime'}}</td>
                      <td class="text-center">
                        <button class="btn btn-sm btn-outline-primary" (click)="triggerAgentAnalysis(rec.symbol, 'technical')">
                          Analyze
                        </button>
                      </td>
                    </tr>
                    <tr *ngIf="allRecommendations.length === 0 && !isGenerating">
                      <td colspan="8" class="text-center py-4 text-muted">
                        No recommendations generated yet. Click "Refresh" to analyze tickers.
                      </td>
                    </tr>
                    <tr *ngIf="isGenerating">
                      <td colspan="8" class="text-center py-4">
                        <div class="spinner-border text-primary" role="status"></div>
                        <p class="mt-2">Analyzing tickers for recommendations...</p>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Chat with Agents -->
          <div class="card mb-4">
            <div class="card-header bg-info text-white">
              <h5 class="mb-0">💬 Chat with All Agents</h5>
            </div>
            <div class="card-body">
              <app-chat-panel></app-chat-panel>
            </div>
          </div>

          <!-- Prediction Monitoring -->
          <div class="card mb-4">
            <div class="card-header bg-info text-white">
              <h5 class="mb-0">🔍 Real-time Prediction Monitoring</h5>
            </div>
            <div class="card-body">
              <app-prediction-monitoring [showHeader]="false"></app-prediction-monitoring>
            </div>
          </div>

          <!-- Collaborative Gainer Predictions -->
          <div class="card mb-4">
            <div class="card-header bg-warning text-white">
              <h5 class="mb-0">👥 10-Agent Collaborative Top Gainers Prediction</h5>
            </div>
            <div class="card-body">
              <app-gainer-predictions></app-gainer-predictions>
            </div>
          </div>

          <!-- Leader Prediction Dashboard -->
          <div class="card mb-4">
            <div class="card-header bg-success text-white">
              <h5 class="mb-0">👑 Leader Prediction Dashboard</h5>
            </div>
            <div class="card-body">
              <app-leader-prediction></app-leader-prediction>
            </div>
          </div>

          <!-- Raw Logs Section -->
          <div class="card">
            <div class="card-header bg-secondary text-white">
              <h5 class="mb-0">📋 Raw System Logs</h5>
            </div>
            <div class="card-body">
              <div class="mb-3">
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="checkbox" id="showRawLogs" [(ngModel)]="showRawLogs">
                  <label class="form-check-label" for="showRawLogs">Show Raw Logs</label>
                </div>
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="checkbox" id="autoRefresh" [(ngModel)]="autoRefresh" (change)="toggleAutoRefresh()">
                  <label class="form-check-label" for="autoRefresh">Auto Refresh (30s)</label>
                </div>
              </div>
              
              <div *ngIf="showRawLogs" class="bg-dark text-light p-3 rounded" style="max-height: 300px; overflow-y: auto; font-family: 'Courier New', monospace; font-size: 12px;">
                <div *ngFor="let log of rawLogs" class="log-entry mb-1" [ngClass]="getLogLevelClass(log.level)">
                  <span class="text-muted">[{{log.timestamp | date:'HH:mm:ss'}}]</span>
                  <span class="ms-2">{{log.level}}</span>
                  <span class="ms-2">{{log.message}}</span>
                  <span *ngIf="log.data" class="text-info ms-2">{{log.data | json}}</span>
                </div>
                <div *ngIf="rawLogs.length === 0" class="text-muted">
                  No logs available. Click "Refresh" above to generate recommendations and see logs.
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Agent Status & Activity -->
        <div class="col-lg-4">
          <!-- Agent Status -->
          <div class="card mb-4">
            <div class="card-header bg-dark text-white">
              <h5 class="mb-0">📊 Agent Status</h5>
            </div>
            <div class="card-body">
              <app-agent-status-table></app-agent-status-table>
            </div>
          </div>

          <!-- Recent Activity -->
          <div class="card mb-4">
            <div class="card-header bg-info text-white">
              <h5 class="mb-0">📝 Recent Activity</h5>
            </div>
            <div class="card-body" style="max-height: 300px; overflow-y: auto;">
              <app-agent-activity-feed></app-agent-activity-feed>
            </div>
          </div>

          <!-- Performance Metrics -->
          <div class="card">
            <div class="card-header bg-success text-white">
              <h5 class="mb-0">📊 Performance Metrics</h5>
            </div>
            <div class="card-body">
              <app-performance-metrics></app-performance-metrics>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <footer class="mt-4 pt-3 border-top">
        <div class="row">
          <div class="col-md-6">
            <div class="small text-white">
              <strong>Trading Agent System v2.0</strong><br>
              Backend: {{backendStatus}} | WebSocket: {{websocketStatus}}<br>
              Memory: {{memoryUsage}} | CPU: {{cpuUsage}}
            </div>
          </div>
          <div class="col-md-6 text-end">
            <div class="small text-white">
              Last Recommendation: {{lastRecommendationTime | date:'medium'}}<br>
              Total Analyses: {{totalAnalyses}} | Successful: {{successfulAnalyses}}<br>
              <button class="btn btn-sm btn-outline-primary mt-1" (click)="forceSystemCheck()">Force System Check</button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  `,
  styles: []
})
export class DashboardHomeComponent implements OnInit {
  backendStatus = 'Checking...';
  websocketStatus = 'Checking...';
  totalTickers = 0;
  totalAnalyses = 0;
  successfulAnalyses = 0;
  uptime = '0h';
  memoryUsage = 'N/A';
  cpuUsage = 'N/A';
  
  topRecommendation: TopRecommendation | null = null;
  allRecommendations: TopRecommendation[] = [];
  selectedCategory = 'all';
  isGenerating = false;
  
  showRawLogs = true;
  autoRefresh = false;
  rawLogs: any[] = [];
  logsLastUpdated = new Date();
  
  lastRecommendationTime = new Date();
  private autoRefreshInterval: any;

  constructor(
    private http: HttpClient,
    private monitoringService: MonitoringService
  ) {}

  ngOnInit() {
    this.checkBackendConnection();
    this.loadSystemStats();
    this.loadRecommendations();
    this.startSystemMonitoring();
  }

  checkBackendConnection() {
    this.http.get<any>(`${environment.apiUrl}/health`)
      .subscribe({
        next: (data) => {
          this.backendStatus = '✅ Connected';
          this.addLog('info', 'Backend connected successfully', data);
        },
        error: (error) => {
          this.backendStatus = '❌ Disconnected';
          this.addLog('error', 'Backend connection failed', error);
        }
      });

    // Monitor WebSocket connection status
    this.monitoringService.connectionStatus$.subscribe(connected => {
      this.websocketStatus = connected ? '✅ Connected' : '❌ Disconnected';
      this.addLog(connected ? 'success' : 'warning', 
                 `WebSocket ${connected ? 'connected' : 'disconnected'}`);
    });
  }

  loadSystemStats() {
    this.http.get<any>(`${environment.apiUrl}/tickers/stats`)
      .subscribe({
        next: (data) => {
          this.totalTickers = data.totalTickers || data.total || 0;
          this.addLog('info', 'Loaded ticker statistics', data);
        },
        error: (error) => {
          this.addLog('error', 'Failed to load ticker statistics', error);
        }
      });

    // Load recent activities count
    this.http.get<any>(`${environment.apiUrl}/agent-activities`)
      .subscribe({
        next: (activities) => {
          this.totalAnalyses = activities.length || 0;
          this.successfulAnalyses = activities.filter((a: any) => a.status === 'success').length;
          this.addLog('info', `Loaded ${this.totalAnalyses} activities`);
        },
        error: (error) => {
          this.addLog('error', 'Failed to load activities', error);
        }
      });
  }

  // Load existing recommendations from backend
  loadRecommendations() {
    // Try to load from collaborative predictions endpoint
    this.http.post<any>(`${environment.apiUrl}/predictions/collaborative`, {
      daysAhead: 2,
      topN: 10,
      forceRefresh: false  // Use cached predictions if available
    }).subscribe({
      next: (response) => {
        if (response.status === 'success' && response.prediction && response.prediction.finalPredictions) {
          const finalPredictions = response.prediction.finalPredictions;
          
          // Convert predictions to recommendation format
          this.allRecommendations = finalPredictions.map((pred: any, index: number) => {
            // Extract confidence percentage from string like "71.0%"
            const confidenceStr = pred.confidence || '0%';
            const confidence = parseFloat(confidenceStr.replace('%', '')) / 100;
            
            // Extract expected gain from string like "5.31%"
            const gainStr = pred.expectedGain || '0%';
            const expectedGain = parseFloat(gainStr.replace('%', ''));
            
            return {
              symbol: pred.symbol || 'Unknown',
              name: pred.symbol || 'Unknown Stock',
              signal: pred.signal || 'HOLD',
              confidence: confidence,
              profitability_score: expectedGain / 100, // Convert percentage to decimal 0-1
              type: this.getStockType(pred.symbol),
              timestamp: pred.predictionDate || new Date().toISOString(),
              rank: index + 1,
              expectedGain: expectedGain,
              reasoning: pred.reasoning || 'No reasoning provided'
            };
          });
          
          // Set the first one as top recommendation
          this.topRecommendation = this.allRecommendations[0];
          
          this.addLog('success', `Loaded ${this.allRecommendations.length} recommendations from collaborative predictions`, {
            topSymbol: this.topRecommendation?.symbol,
            topSignal: this.topRecommendation?.signal,
            topConfidence: this.topRecommendation?.confidence
          });
        } else {
          this.addLog('info', 'No existing predictions found. Click "Refresh" to generate new recommendations.');
        }
      },
      error: (error) => {
        this.addLog('error', 'Failed to load recommendations from collaborative predictions', error);
        // Fallback: generate new recommendations
        this.generateRecommendations();
      }
    });
  }

  generateRecommendations() {
    this.isGenerating = true;
    this.addLog('info', `Generating recommendations for category: ${this.selectedCategory}`);
    
    // Call the collaborative predictions endpoint to get real predictions
    this.http.post<any>(`${environment.apiUrl}/predictions/collaborative`, {
      daysAhead: 2,
      topN: 10,
      forceRefresh: true
    }).subscribe({
      next: (response) => {
        if (response.status === 'success' && response.prediction && response.prediction.finalPredictions) {
          const finalPredictions = response.prediction.finalPredictions;
          
          // Convert predictions to recommendation format
          this.allRecommendations = finalPredictions.map((pred: any, index: number) => {
            // Extract confidence percentage from string like "71.0%"
            const confidenceStr = pred.confidence || '0%';
            const confidence = parseFloat(confidenceStr.replace('%', '')) / 100;
            
            // Extract expected gain from string like "5.31%"
            const gainStr = pred.expectedGain || '0%';
            const expectedGain = parseFloat(gainStr.replace('%', ''));
            
            return {
              symbol: pred.symbol || 'Unknown',
              name: pred.symbol || 'Unknown Stock',
              signal: pred.signal || 'HOLD',
              confidence: confidence,
              profitability_score: expectedGain / 100, // Convert percentage to decimal 0-1
              type: this.getStockType(pred.symbol),
              timestamp: pred.predictionDate || new Date().toISOString(),
              rank: index + 1,
              expectedGain: expectedGain,
              reasoning: pred.reasoning || 'No reasoning provided'
            };
          });
          
          // Set the first one as top recommendation
          this.topRecommendation = this.allRecommendations[0];
          
          this.lastRecommendationTime = new Date();
          this.isGenerating = false;
          
          this.addLog('success', `Generated ${this.allRecommendations.length} recommendations from collaborative predictions`, {
            topSymbol: this.topRecommendation?.symbol,
            topSignal: this.topRecommendation?.signal,
            topConfidence: this.topRecommendation?.confidence
          });
        } else {
          this.addLog('error', 'Failed to generate recommendations: Invalid response from collaborative predictions', response);
          this.isGenerating = false;
        }
      },
      error: (error) => {
        this.addLog('error', 'Failed to generate recommendations', error);
        this.isGenerating = false;
      }
    });
    
    // TEMPORARY: Comment out the mock data generation
    /*
    this.http.post<any>(`${environment.apiUrl}/trade-recommendations`, {
      symbol: 'AAPL', // Example only - would be real analysis
      recommendation: 'HOLD', // Example only - would be real analysis
      confidence: 0.75, // Example only - would be real analysis
      price: 175.50, // Example only - would be real market price
      targetPrice: 185.00, // Example only - would be real target
      stopLoss: 165.00, // Example only - would be real stop loss
      reasoning: 'Real analysis would go here',
      agentId: 'technical-analyst-1',
      timestamp: new Date().toISOString()
    }).subscribe({
      next: (response) => {
        // The backend returns the created recommendation in response.recommendation
        const newRecommendation = response.recommendation;
        
        // Add to the beginning of the list
        this.allRecommendations.unshift(newRecommendation);
        
        // Set as top recommendation
        this.topRecommendation = newRecommendation;
        
        // Keep only last 20 recommendations
        if (this.allRecommendations.length > 20) {
          this.allRecommendations = this.allRecommendations.slice(0, 20);
        }
        
        this.lastRecommendationTime = new Date();
        this.isGenerating = false;
        
        this.addLog('success', `Generated new recommendation for ${newRecommendation.symbol}`, {
          symbol: newRecommendation.symbol,
          signal: newRecommendation.recommendation || newRecommendation.signal,
          confidence: newRecommendation.confidence,
          price: newRecommendation.price
        });
      },
      error: (error) => {
        this.addLog('error', 'Failed to generate recommendations', error);
        this.isGenerating = false;
      }
    });
    */
  }

  triggerAgentAnalysis(symbol: string, agentType: string) {
    this.addLog('info', `Triggering ${agentType} analysis for ${symbol}`);
    
    // Send chat message that agent is starting analysis
    this.sendAgentChatMessage(
      agentType === 'technical' ? 'technical_analyst' : 
      agentType === 'fundamental' ? 'fundamental_analyst' :
      agentType === 'sentiment' ? 'sentiment_analyst' : 'macro_analyst',
      `Starting ${agentType} analysis on ${symbol}...`,
      'analysis_started',
      symbol,
      0.8
    );
    
    this.http.post<any>(`${environment.apiUrl}/trigger/${agentType}/${symbol}`, {})
      .subscribe({
        next: (response) => {
          this.addLog('success', `${agentType} analysis completed for ${symbol}`, {
            signal: response.analysis?.signal,
            confidence: response.analysis?.confidence
          });
          
          // Send chat message with analysis results
          const signal = response.analysis?.signal || 'HOLD';
          const confidence = response.analysis?.confidence || 0.5;
          this.sendAgentChatMessage(
            agentType === 'technical' ? 'technical_analyst' : 
            agentType === 'fundamental' ? 'fundamental_analyst' :
            agentType === 'sentiment' ? 'sentiment_analyst' : 'macro_analyst',
            `${agentType} analysis complete for ${symbol}: ${signal} signal with ${(confidence * 100).toFixed(0)}% confidence`,
            'analysis_complete',
            symbol,
            confidence
          );
          
          this.totalAnalyses++;
          if (response.status === 'success') this.successfulAnalyses++;
        },
        error: (error) => {
          this.addLog('error', `Failed to trigger ${agentType} analysis for ${symbol}`, error);
          
          // Send error chat message
          this.sendAgentChatMessage(
            agentType === 'technical' ? 'technical_analyst' : 
            agentType === 'fundamental' ? 'fundamental_analyst' :
            agentType === 'sentiment' ? 'sentiment_analyst' : 'macro_analyst',
            `Failed to complete ${agentType} analysis on ${symbol}: ${error.message || 'Unknown error'}`,
            'error',
            symbol,
            0.3
          );
        }
      });
  }
  
  sendAgentChatMessage(sender: string, message: string, messageType: string, symbol: string, confidence: number) {
    const chatMessage = {
      sender: sender,
      receiver: 'monitoring_dashboard',
      message: message,
      messageType: messageType,
      timestamp: new Date().toISOString(),
      confidence: confidence,
      symbol: symbol
    };
    
    this.http.post(`${environment.apiUrl}/chat`, chatMessage).subscribe({
      next: () => console.log('Chat message sent:', chatMessage),
      error: (err) => console.error('Failed to send chat message:', err)
    });
  }

  startSystemMonitoring() {
    // Update uptime every minute
    setInterval(() => {
      const hours = Math.floor((Date.now() - this.logsLastUpdated.getTime()) / (1000 * 60 * 60));
      const minutes = Math.floor((Date.now() - this.logsLastUpdated.getTime()) / (1000 * 60)) % 60;
      this.uptime = `${hours}h ${minutes}m`;
    }, 60000);

    // Simulate system metrics
    setInterval(() => {
      this.memoryUsage = `${Math.floor(Math.random() * 30) + 20}%`;
      this.cpuUsage = `${Math.floor(Math.random() * 40) + 10}%`;
    }, 10000);
  }

  toggleAutoRefresh() {
    if (this.autoRefresh) {
      this.autoRefreshInterval = setInterval(() => {
        this.generateRecommendations();
      }, 30000); // Every 30 seconds
      this.addLog('info', 'Auto-refresh enabled (30s interval)');
    } else {
      if (this.autoRefreshInterval) {
        clearInterval(this.autoRefreshInterval);
        this.addLog('info', 'Auto-refresh disabled');
      }
    }
  }

  forceSystemCheck() {
    this.addLog('info', 'Manual system check triggered');
    this.checkBackendConnection();
    this.loadSystemStats();
    this.generateRecommendations();
  }

  addLog(level: string, message: string, data?: any) {
    const logEntry = {
      timestamp: new Date(),
      level: level.toUpperCase(),
      message: message,
      data: data
    };
    this.rawLogs.unshift(logEntry);
    // Keep only last 50 logs
    if (this.rawLogs.length > 50) {
      this.rawLogs = this.rawLogs.slice(0, 50);
    }
    this.logsLastUpdated = new Date();
  }

  // Helper methods for styling
  getSignalClass(signal: string): string {
    switch (signal) {
      case 'BUY': return 'signal-buy';
      case 'SELL': return 'signal-sell';
      case 'HOLD': return 'signal-hold';
      default: return 'text-muted';
    }
  }

  getSignalBadgeClass(signal: string): string {
    switch (signal) {
      case 'BUY': return 'bg-success';
      case 'SELL': return 'bg-danger';
      case 'HOLD': return 'bg-warning text-white';
      default: return 'bg-secondary';
    }
  }

  getConfidenceClass(confidence: number): string {
    if (confidence >= 0.7) return 'bg-success';
    if (confidence >= 0.5) return 'bg-warning';
    return 'bg-danger';
  }

  getProfitabilityClass(score: number): string {
    if (score >= 0.8) return 'profitability-high';
    if (score >= 0.6) return 'profitability-medium';
    return 'profitability-low';
  }

  getProfitabilityBarClass(score: number): string {
    if (score >= 0.8) return 'bg-success';
    if (score >= 0.6) return 'bg-warning';
    return 'bg-danger';
  }

  getStockType(symbol: string): string {
    // Simple classification based on symbol patterns
    if (symbol.includes('BTC') || symbol.includes('ETH') || symbol.includes('SOL') || 
        symbol.includes('ADA') || symbol.includes('DOT') || symbol.includes('XRP')) {
      return 'Crypto';
    }
    if (symbol.length <= 4) {
      return 'Stock';
    }
    if (symbol.includes('ETF') || symbol.includes('FUND')) {
      return 'ETF';
    }
    return 'Stock';
  }

  getLogLevelClass(level: string): string {
    switch (level) {
      case 'INFO': return 'log-info';
      case 'SUCCESS': return 'log-success';
      case 'WARNING': return 'log-warning';
      case 'ERROR': return 'log-error';
      default: return '';
    }
  }

  // In PRODUCTION: Real data methods would be here
  // getRealTimePrice(symbol: string): Observable<number> { ... }
  // getMarketAnalysis(symbol: string): Observable<any> { ... }
  // generateRealRecommendation(): Observable<any> { ... }

  ngOnDestroy() {
    if (this.autoRefreshInterval) {
      clearInterval(this.autoRefreshInterval);
    }
  }
}
