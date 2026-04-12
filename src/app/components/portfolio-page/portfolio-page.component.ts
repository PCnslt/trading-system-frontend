import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { TradeTicketComponent } from '../trade-ticket/trade-ticket.component';

@Component({
  selector: 'app-portfolio-page',
  standalone: true,
  imports: [RouterLink, TradeTicketComponent],
  template: `
    <div class="container-fluid py-4">
      <!-- Navigation Header -->
      <div class="row mb-4">
        <div class="col-md-12">
          <div class="card bg-primary text-white">
            <div class="card-body py-2">
              <div class="d-flex flex-wrap gap-2 align-items-center">
                <a routerLink="/" class="btn btn-sm btn-outline-light">
                  <i class="bi bi-speedometer2 me-1"></i> Back to Dashboard
                </a>
                <a routerLink="/charts" class="btn btn-sm btn-outline-light">
                  <i class="bi bi-graph-up me-1"></i> Charts
                </a>
                <a routerLink="/portfolio" class="btn btn-sm btn-light active">
                  <i class="bi bi-wallet2 me-1"></i> Portfolio
                </a>
                <div class="ms-auto">
                  <span class="badge bg-success">Portfolio Management Page</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-12">
          <div class="card shadow">
            <div class="card-body">
              <h1 class="display-6 mb-3"><i class="bi bi-wallet2 me-2"></i>Portfolio Management</h1>
              <p class="lead">Real-time portfolio tracking based on agent trade recommendations.</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="row">
        <div class="col-md-8">
          <div class="card shadow">
            <div class="card-header">
              <h5 class="mb-0"><i class="bi bi-currency-dollar me-2"></i>Active Trade Recommendations</h5>
            </div>
            <div class="card-body p-0">
              <app-trade-ticket></app-trade-ticket>
            </div>
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="card shadow">
            <div class="card-header">
              <h5 class="mb-0"><i class="bi bi-pie-chart me-2"></i>Portfolio Summary</h5>
            </div>
            <div class="card-body">
              <div class="text-center py-4">
                <h2 class="display-4">$0.00</h2>
                <p class="text-muted">Total Portfolio Value</p>
              </div>
              <div class="list-group list-group-flush">
                <div class="list-group-item d-flex justify-content-between">
                  <span>Active Positions</span>
                  <span class="badge bg-primary">0</span>
                </div>
                <div class="list-group-item d-flex justify-content-between">
                  <span>Total P&L</span>
                  <span class="badge bg-success">+0.00%</span>
                </div>
                <div class="list-group-item d-flex justify-content-between">
                  <span>Risk Exposure</span>
                  <span class="badge bg-warning">Low</span>
                </div>
                <div class="list-group-item d-flex justify-content-between">
                  <span>Best Performer</span>
                  <span class="badge bg-success">N/A</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="row mt-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0"><i class="bi bi-clock-history me-2"></i>Recent Activity</h5>
            </div>
            <div class="card-body">
              <p class="text-muted mb-0">Portfolio tracking will be updated with real positions once trade execution is implemented.</p>
              <p class="small text-muted mt-2">Currently showing agent trade recommendations. Click "Execute" on any recommendation to simulate a position.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    /* Component-specific styles for dark theme */
    .display-4 {
      font-weight: 700;
      color: var(--text-primary);
      text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    .portfolio-summary {
      background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 2rem;
      text-align: center;
      margin-bottom: 1.5rem;
    }
    .portfolio-value {
      font-size: 3rem;
      font-weight: 800;
      background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-cyan) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 0.5rem;
    }
    .portfolio-label {
      font-size: 1rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 1.5rem;
    }
    .portfolio-stats {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 1.5rem;
    }
    .stat-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem 0;
      border-bottom: 1px solid var(--border-color);
    }
    .stat-item:last-child {
      border-bottom: none;
    }
    .stat-label {
      font-size: 0.875rem;
      color: var(--text-muted);
    }
    .stat-value {
      font-size: 1rem;
      font-weight: 600;
      color: var(--text-primary);
    }
    .stat-badge {
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 600;
    }
    .badge-positive {
      background: rgba(0, 214, 143, 0.1);
      color: var(--accent-green);
      border: 1px solid rgba(0, 214, 143, 0.3);
    }
    .badge-negative {
      background: rgba(255, 61, 113, 0.1);
      color: var(--accent-red);
      border: 1px solid rgba(255, 61, 113, 0.3);
    }
    .badge-neutral {
      background: rgba(143, 155, 179, 0.1);
      color: var(--text-muted);
      border: 1px solid rgba(143, 155, 179, 0.3);
    }
    .portfolio-section {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      overflow: hidden;
      margin-bottom: 1.5rem;
    }
    .section-header {
      background: var(--bg-secondary);
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid var(--border-color);
    }
    .section-body {
      padding: 1.5rem;
    }
    .activity-log {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 1.25rem;
    }
    .activity-item {
      display: flex;
      align-items: center;
      padding: 0.75rem 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .activity-item:last-child {
      border-bottom: none;
    }
    .activity-icon {
      width: 36px;
      height: 36px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 1rem;
      font-size: 1rem;
    }
    .icon-buy {
      background: rgba(0, 214, 143, 0.1);
      color: var(--accent-green);
    }
    .icon-sell {
      background: rgba(255, 61, 113, 0.1);
      color: var(--accent-red);
    }
    .icon-hold {
      background: rgba(143, 155, 179, 0.1);
      color: var(--text-muted);
    }
    .activity-details {
      flex: 1;
    }
    .activity-symbol {
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 0.25rem;
    }
    .activity-description {
      font-size: 0.875rem;
      color: var(--text-muted);
    }
    .activity-time {
      font-size: 0.75rem;
      color: var(--text-disabled);
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
    }
    .empty-subtext {
      font-size: 0.875rem;
      opacity: 0.7;
    }
  `]
})
export class PortfolioPageComponent {}