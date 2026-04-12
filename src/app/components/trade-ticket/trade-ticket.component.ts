import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MonitoringService, TradeRecommendation } from '../../services/monitoring.service';

@Component({
  selector: 'app-trade-ticket',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="trade-ticket">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h6 class="mb-0">Active Trade Recommendations</h6>
        <span class="badge" [ngClass]="activeRecommendations.length > 0 ? 'bg-success' : 'bg-secondary'">
          {{activeRecommendations.length}} active
        </span>
      </div>
      
      <div *ngIf="activeRecommendations.length === 0" class="text-center text-muted py-3">
        <div class="mb-2">
          <i class="bi bi-graph-up" style="font-size: 2rem;"></i>
        </div>
        <div>No active trade recommendations</div>
        <small>Check back after next market analysis</small>
      </div>
      
      <div *ngFor="let rec of activeRecommendations" class="trade-card mb-3 p-3 border rounded">
        <div class="d-flex justify-content-between align-items-start mb-2">
          <div>
            <h5 class="mb-0">{{rec.symbol}}</h5>
            <div class="small text-muted">Recommended by: {{rec.recommendedBy || 'Consensus'}}</div>
          </div>
          <div class="text-end">
            <span class="badge bg-primary">{{rec.status || 'active'}}</span>
            <div class="mt-1">
              <span class="badge" [ngClass]="getConfidenceBadgeClass(rec.confidence)">
                {{(rec.confidence * 100).toFixed(0)}}% confidence
              </span>
            </div>
          </div>
        </div>
        
        <div class="row mb-2">
          <div class="col-4">
            <div class="small text-muted">Entry Range</div>
            <div class="fw-bold">{{rec.entryRange || 'N/A'}}</div>
          </div>
          <div class="col-4">
            <div class="small text-muted">Target</div>
            <div class="fw-bold text-success">{{rec.target}}</div>
          </div>
          <div class="col-4">
            <div class="small text-muted">Stop Loss</div>
            <div class="fw-bold text-danger">{{rec.stopLoss}}</div>
          </div>
        </div>
        
        <div class="row mb-2">
          <div class="col-4">
            <div class="small text-muted">Position Size</div>
            <div class="fw-bold">{{rec.positionSize.toFixed(2) || 'N/A'}}%</div>
          </div>
          <div class="col-4">
            <div class="small text-muted">Risk/Reward</div>
            <div class="fw-bold" [ngClass]="{'text-success': rec.riskRewardRatio > 2, 'text-warning': rec.riskRewardRatio > 1, 'text-danger': rec.riskRewardRatio <= 1}">
              {{rec.riskRewardRatio.toFixed(2) || 'N/A'}}:1
            </div>
          </div>
          <div class="col-4">
            <div class="small text-muted">Potential P&L</div>
            <div class="fw-bold" [ngClass]="{'text-success': rec.potentialPnl > 0, 'text-danger': rec.potentialPnl < 0}">
              {{rec.potentialPnl.toFixed(2) || 'N/A'}}%
            </div>
          </div>
        </div>
        
        <div *ngIf="rec.currentPrice" class="mb-2">
          <div class="small text-muted">Current Price</div>
          <div class="fw-bold">{{rec.currentPrice.toFixed(2)}}</div>
        </div>
        
        <div *ngIf="rec.rationale" class="mb-2">
          <div class="small text-muted">Rationale</div>
          <div class="small">{{rec.rationale.substring(0, 120)}}...</div>
        </div>
        
        <div class="d-flex justify-content-between align-items-center mt-2 pt-2 border-top">
          <small class="text-muted">{{formatTime(rec.timestamp)}}</small>
          <div>
            <button class="btn btn-sm btn-outline-primary me-1">Execute</button>
            <button class="btn btn-sm btn-outline-secondary">Dismiss</button>
          </div>
        </div>
      </div>
      
      <div *ngIf="recentRecommendations.length > 0 && activeRecommendations.length > 0" class="mt-3">
        <h6 class="mb-2">Recent Recommendations</h6>
        <div class="list-group list-group-flush">
          <div *ngFor="let rec of recentRecommendations" class="list-group-item py-2">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <span class="badge bg-secondary me-2">{{rec.symbol}}</span>
                <span class="small">{{rec.status}}</span>
              </div>
              <div class="text-end">
                <div class="small">{{formatTime(rec.timestamp)}}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="mt-3">
        <button class="btn btn-sm btn-outline-primary w-100" (click)="loadRecommendations()">
          Refresh Recommendations
        </button>
      </div>
    </div>
  `,
  styles: [`
    /* Component-specific styles for dark theme */
    .trade-ticket {
      font-size: 0.9rem;
    }
    .trade-card {
      background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
      border-left: 4px solid var(--accent-blue);
      border-radius: 10px;
      box-shadow: 0 4px 12px var(--shadow-color);
      transition: all 0.3s;
      border: 1px solid var(--border-color);
    }
    .trade-card:hover {
      box-shadow: 0 8px 24px var(--shadow-color);
      transform: translateY(-4px);
      border-color: var(--accent-blue);
    }
    .trade-card.executed {
      border-left-color: var(--accent-green);
      background: linear-gradient(135deg, rgba(0, 214, 143, 0.1) 0%, var(--bg-card) 100%);
      border-color: rgba(0, 214, 143, 0.3);
    }
    .trade-card.cancelled {
      border-left-color: var(--accent-purple);
      background: linear-gradient(135deg, rgba(143, 155, 179, 0.1) 0%, var(--bg-card) 100%);
      border-color: rgba(143, 155, 179, 0.3);
    }
    .trade-card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 1rem;
      padding-bottom: 0.75rem;
      border-bottom: 1px solid var(--border-color);
    }
    .trade-symbol {
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 0.25rem;
    }
    .trade-agent {
      font-size: 0.875rem;
      color: var(--text-muted);
    }
    .trade-status {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
    }
    .status-badge {
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
    }
    .status-active {
      background: rgba(51, 102, 255, 0.1);
      color: var(--accent-blue);
      border: 1px solid rgba(51, 102, 255, 0.3);
    }
    .status-executed {
      background: rgba(0, 214, 143, 0.1);
      color: var(--accent-green);
      border: 1px solid rgba(0, 214, 143, 0.3);
    }
    .status-cancelled {
      background: rgba(143, 155, 179, 0.1);
      color: var(--text-muted);
      border: 1px solid rgba(143, 155, 179, 0.3);
    }
    .confidence-badge {
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 600;
    }
    .confidence-high {
      background: rgba(0, 214, 143, 0.1);
      color: var(--accent-green);
      border: 1px solid rgba(0, 214, 143, 0.3);
    }
    .confidence-medium {
      background: rgba(255, 170, 0, 0.1);
      color: var(--accent-yellow);
      border: 1px solid rgba(255, 170, 0, 0.3);
    }
    .confidence-low {
      background: rgba(255, 61, 113, 0.1);
      color: var(--accent-red);
      border: 1px solid rgba(255, 61, 113, 0.3);
    }
    .trade-metrics {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1rem;
      margin-bottom: 1rem;
    }
    .metric-item {
      text-align: center;
    }
    .metric-label {
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 0.25rem;
    }
    .metric-value {
      font-size: 1.125rem;
      font-weight: 600;
      color: var(--text-primary);
    }
    .metric-change {
      font-size: 0.875rem;
      font-weight: 500;
      padding: 0.125rem 0.5rem;
      border-radius: 4px;
      display: inline-block;
      margin-top: 0.25rem;
    }
    .change-positive {
      background: rgba(0, 214, 143, 0.1);
      color: var(--accent-green);
    }
    .change-negative {
      background: rgba(255, 61, 113, 0.1);
      color: var(--accent-red);
    }
    .trade-rationale {
      background: rgba(255, 255, 255, 0.03);
      border-radius: 8px;
      padding: 0.75rem;
      margin-bottom: 1rem;
      border-left: 3px solid var(--accent-blue);
    }
    .rationale-label {
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 0.5rem;
    }
    .rationale-text {
      font-size: 0.875rem;
      color: var(--text-secondary);
      line-height: 1.5;
    }
    .trade-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 0.75rem;
      border-top: 1px solid var(--border-color);
    }
    .trade-time {
      font-size: 0.75rem;
      color: var(--text-muted);
    }
    .action-buttons {
      display: flex;
      gap: 0.5rem;
    }
    .empty-trades {
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
    .recent-trades {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 1rem;
      margin-top: 1.5rem;
    }
    .recent-header {
      font-size: 0.875rem;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 0.75rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid var(--border-color);
    }
    .recent-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.5rem 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .recent-item:last-child {
      border-bottom: none;
    }
    .recent-symbol {
      font-size: 0.875rem;
      font-weight: 500;
      color: var(--text-primary);
    }
    .recent-status {
      font-size: 0.75rem;
      padding: 0.125rem 0.5rem;
      border-radius: 4px;
    }
    .recent-time {
      font-size: 0.75rem;
      color: var(--text-muted);
    }
    .border-top {
      border-top: 1px solid var(--border-color) !important;
    }
    .fw-bold {
      font-weight: 600 !important;
    }
  `]
})
export class TradeTicketComponent implements OnInit {
  recommendations: TradeRecommendation[] = [];
  activeRecommendations: TradeRecommendation[] = [];
  recentRecommendations: TradeRecommendation[] = [];
  
  constructor(private monitoringService: MonitoringService) {}
  
  ngOnInit() {
    this.loadRecommendations();
    
    // Subscribe to real-time updates
    this.monitoringService.tradeRecommendation$.subscribe(rec => {
      this.recommendations.unshift(rec);
      if (this.recommendations.length > 50) {
        this.recommendations = this.recommendations.slice(0, 50);
      }
      this.categorizeRecommendations();
    });
  }
  
  loadRecommendations() {
    this.monitoringService.getActiveRecommendations().subscribe({
      next: (recommendations) => {
        this.recommendations = recommendations.slice(0, 50);
        this.categorizeRecommendations();
      },
      error: (err) => console.error('Failed to load recommendations:', err)
    });
  }
  
  categorizeRecommendations() {
    this.activeRecommendations = this.recommendations
      .filter(r => r.status === 'active')
      .slice(0, 5); // Show max 5 active
    
    this.recentRecommendations = this.recommendations
      .filter(r => r.status !== 'active')
      .slice(0, 3); // Show 3 recent non-active
  }
  
  getConfidenceBadgeClass(confidence: number): string {
    if (confidence >= 0.8) return 'bg-success';
    if (confidence >= 0.6) return 'bg-warning text-dark';
    return 'bg-danger';
  }
  
  formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
}