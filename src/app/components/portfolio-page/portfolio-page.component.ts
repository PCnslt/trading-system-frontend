import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { TradeTicketComponent } from '../trade-ticket/trade-ticket.component';

@Component({
  selector: 'app-portfolio-page',
  standalone: true,
  imports: [RouterLink, TradeTicketComponent],
  template: `
    <div class="container-fluid py-4">
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
  styles: []
})
export class PortfolioPageComponent {}