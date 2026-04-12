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
    .trade-ticket {
      font-size: 0.875rem;
    }
    .trade-card {
      background-color: #f8f9fa;
      border-left: 4px solid #0d6efd;
    }
    .trade-card.executed {
      border-left-color: #198754;
      background-color: #f0fff4;
    }
    .trade-card.cancelled {
      border-left-color: #6c757d;
      background-color: #f8f9fa;
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