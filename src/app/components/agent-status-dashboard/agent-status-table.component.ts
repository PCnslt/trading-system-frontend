import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MonitoringService, AgentStatus } from '../../services/monitoring.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-agent-status-table',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="agent-status-table">
      <!-- Table Header with Controls -->
      <div class="card mb-3">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">📊 Agent Status Table</h5>
          <div class="d-flex align-items-center gap-2">
            <div class="input-group input-group-sm" style="width: 200px;">
              <span class="input-group-text bg-dark border-dark">
                <i class="bi bi-search"></i>
              </span>
              <input type="text" class="form-control form-control-sm bg-dark border-dark" 
                     placeholder="Search agents..." [(ngModel)]="searchTerm" 
                     (ngModelChange)="filterAgents()">
            </div>
            <button class="btn btn-sm btn-outline-primary" (click)="refreshStatus()" [disabled]="isRefreshing">
              <i class="bi bi-arrow-clockwise" [class.spin]="isRefreshing"></i>
              Refresh
            </button>
          </div>
        </div>
        
        <!-- Stats Summary -->
        <div class="card-body py-2">
          <div class="row g-3">
            <div class="col-md-3">
              <div class="text-center p-2 rounded bg-success bg-opacity-10">
                <div class="h4 mb-0 text-success">{{activeAgentCount}}</div>
                <div class="small text-muted">Active Agents</div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="text-center p-2 rounded bg-primary bg-opacity-10">
                <div class="h4 mb-0 text-primary">{{totalSuccessCount}}</div>
                <div class="small text-muted">Total Success</div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="text-center p-2 rounded bg-danger bg-opacity-10">
                <div class="h4 mb-0 text-danger">{{totalErrorCount}}</div>
                <div class="small text-muted">Total Errors</div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="text-center p-2 rounded bg-info bg-opacity-10">
                <div class="h4 mb-0" [ngClass]="overallSuccessRate >= 80 ? 'text-success' : overallSuccessRate >= 60 ? 'text-warning' : 'text-danger'">
                  {{overallSuccessRate.toFixed(1)}}%
                </div>
                <div class="small text-muted">Overall Success Rate</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Agent Status Table -->
      <div class="card">
        <div class="card-body p-0">
          <div class="table-responsive" style="max-height: 500px; overflow-y: auto;">
            <table class="table table-hover table-dark mb-0">
              <thead class="sticky-top" style="top: 0; z-index: 1;">
                <tr>
                  <th scope="col" class="ps-3">Agent</th>
                  <th scope="col">Status</th>
                  <th scope="col">Last Activity</th>
                  <th scope="col">Last Activity Time</th>
                  <th scope="col">Success</th>
                  <th scope="col">Errors</th>
                  <th scope="col">Success Rate</th>
                  <th scope="col" class="text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let agent of filteredAgents" 
                    [ngClass]="{'table-success': agents[agent].isActive, 'table-danger': !agents[agent].isActive}">
                  <td class="ps-3">
                    <div class="d-flex align-items-center">
                      <div class="agent-icon me-2" [ngClass]="agents[agent].isActive ? 'bg-success' : 'bg-danger'">
                        <i class="bi bi-robot"></i>
                      </div>
                      <div>
                        <div class="fw-bold">{{formatAgentName(agent)}}</div>
                        <div class="small text-muted">{{agent}}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span class="badge" [ngClass]="agents[agent].isActive ? 'bg-success' : 'bg-danger'">
                      {{agents[agent].isActive ? 'ACTIVE' : 'INACTIVE'}}
                      <span *ngIf="agents[agent].isActive" class="ms-1 pulse">●</span>
                    </span>
                  </td>
                  <td>
                    <div class="small">{{agents[agent].lastActivity || 'No activity'}}</div>
                  </td>
                  <td>
                    <div class="small">{{formatTime(agents[agent].lastActivityTime) || 'Never'}}</div>
                  </td>
                  <td>
                    <div class="text-success fw-bold">{{agents[agent].successCount || 0}}</div>
                  </td>
                  <td>
                    <div class="text-danger fw-bold">{{agents[agent].errorCount || 0}}</div>
                  </td>
                  <td>
                    <div class="d-flex align-items-center gap-2">
                      <div class="progress flex-grow-1" style="height: 8px;">
                        <div class="progress-bar" 
                             [ngClass]="getSuccessRateClass(agents[agent].successRate || 0)"
                             [style.width.%]="agents[agent].successRate || 0">
                        </div>
                      </div>
                      <div class="small" style="min-width: 40px;">
                        {{(agents[agent].successRate || 0).toFixed(1)}}%
                      </div>
                    </div>
                  </td>
                  <td class="text-center">
                    <button class="btn btn-sm" 
                            [ngClass]="agents[agent].isActive ? 'btn-outline-danger' : 'btn-outline-success'"
                            (click)="toggleAgent(agent)" [disabled]="isProcessing[agent]">
                      <span *ngIf="isProcessing[agent]" class="spinner-border spinner-border-sm me-1"></span>
                      {{agents[agent].isActive ? 'Disable' : 'Enable'}}
                    </button>
                  </td>
                </tr>
                <tr *ngIf="filteredAgents.length === 0">
                  <td colspan="8" class="text-center py-4 text-muted">
                    No agents found matching "{{searchTerm}}"
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Table Footer -->
        <div class="card-footer py-2">
          <div class="d-flex justify-content-between align-items-center">
            <div class="small text-muted">
              Showing {{filteredAgents.length}} of {{agentList.length}} agents • 
              Last updated: {{lastUpdateTime}}
            </div>
            <div class="btn-group btn-group-sm">
              <button type="button" class="btn btn-outline-primary" (click)="enableAllAgents()">
                <i class="bi bi-play-circle me-1"></i> Enable All
              </button>
              <button type="button" class="btn btn-outline-secondary" (click)="disableAllAgents()">
                <i class="bi bi-pause-circle me-1"></i> Disable All
              </button>
              <button type="button" class="btn btn-outline-success" (click)="refreshStatus()">
                <i class="bi bi-arrow-clockwise me-1"></i> Refresh
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .agent-status-table {
      font-size: 0.9rem;
    }
    .agent-icon {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1rem;
    }
    .table-dark {
      background-color: var(--bg-card);
      color: var(--text-primary);
    }
    .table-dark thead th {
      background-color: var(--bg-secondary);
      border-color: var(--border-color);
      font-weight: 600;
    }
    .table-dark tbody tr {
      border-color: var(--border-color);
    }
    .table-dark tbody tr:hover {
      background-color: var(--bg-hover) !important;
    }
    .table-success {
      background-color: rgba(0, 214, 143, 0.1) !important;
    }
    .table-danger {
      background-color: rgba(255, 61, 113, 0.1) !important;
    }
    .spin {
      animation: spin 1s linear infinite;
    }
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    .pulse {
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0% { opacity: 1; }
      50% { opacity: 0.3; }
      100% { opacity: 1; }
    }
  `]
})
export class AgentStatusTableComponent implements OnInit {
  agents: Record<string, AgentStatus> = {};
  agentList: string[] = [];
  filteredAgents: string[] = [];
  searchTerm: string = '';
  lastUpdateTime: string = '';
  isRefreshing: boolean = false;
  isProcessing: Record<string, boolean> = {};

  constructor(private monitoringService: MonitoringService) {}

  ngOnInit() {
    // Initialize with default agent list
    this.agentList = [
      'technical_analyst', 'fundamental_analyst', 'sentiment_analyst',
      'macro_analyst', 'crypto_analyst', 'options_analyst',
      'risk_analyst', 'quant_analyst', 'sector_analyst', 'compliance_analyst'
    ];
    
    // Initialize default empty status for each agent
    this.agentList.forEach(agent => {
      this.agents[agent] = {
        lastActivity: 'No activity',
        lastActivityTime: '',
        lastStatus: 'unknown',
        successCount: 0,
        errorCount: 0,
        successRate: 0,
        isActive: true
      };
      this.isProcessing[agent] = false;
    });
    
    this.filteredAgents = [...this.agentList];
    this.refreshStatus();
    
    // Auto-refresh every 30 seconds
    setInterval(() => this.refreshStatus(), 30000);
  }

  refreshStatus() {
    this.isRefreshing = true;
    this.monitoringService.getAgentsStatus().subscribe({
      next: (agents) => {
        // Merge backend data with our default agents
        if (agents && typeof agents === 'object') {
          Object.keys(agents).forEach(agentKey => {
            if (agents[agentKey] && typeof agents[agentKey] === 'object') {
              this.agents[agentKey] = { ...this.agents[agentKey], ...agents[agentKey] };
            }
          });
        }
        this.lastUpdateTime = new Date().toLocaleTimeString();
        console.log('AgentStatusTable: Updated agent status', this.agents);
      },
      error: (err) => {
        console.error('Failed to load agent status:', err);
        // Keep using default data
        this.lastUpdateTime = new Date().toLocaleTimeString() + ' (offline)';
      },
      complete: () => {
        this.isRefreshing = false;
      }
    });
  }

  filterAgents() {
    if (!this.searchTerm.trim()) {
      this.filteredAgents = [...this.agentList];
      return;
    }
    
    const term = this.searchTerm.toLowerCase();
    this.filteredAgents = this.agentList.filter(agent => 
      agent.toLowerCase().includes(term) || 
      this.formatAgentName(agent).toLowerCase().includes(term)
    );
  }

  formatAgentName(agentId: string): string {
    return agentId
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  formatTime(timestamp: string): string {
    if (!timestamp) return 'Never';
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      
      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
      return date.toLocaleDateString();
    } catch {
      return 'Invalid date';
    }
  }

  getSuccessRateClass(rate: number): string {
    if (rate >= 80) return 'bg-success';
    if (rate >= 60) return 'bg-warning';
    return 'bg-danger';
  }

  toggleAgent(agentId: string) {
    this.isProcessing[agentId] = true;
    
    // Simulate API call delay
    setTimeout(() => {
      if (this.agents[agentId]) {
        const wasActive = this.agents[agentId].isActive;
        this.agents[agentId].isActive = !wasActive;
        
        // Update success rate based on activity
        if (this.agents[agentId].isActive) {
          this.agents[agentId].successCount = (this.agents[agentId].successCount || 0) + 1;
        }
        
        this.isProcessing[agentId] = false;
        console.log(`Toggled agent ${agentId} to ${this.agents[agentId].isActive ? 'active' : 'inactive'}`);
      }
    }, 500);
  }

  enableAllAgents() {
    Object.keys(this.agents).forEach(agentId => {
      if (!this.agents[agentId].isActive) {
        this.agents[agentId].isActive = true;
      }
    });
    console.log('Enabled all agents');
  }

  disableAllAgents() {
    Object.keys(this.agents).forEach(agentId => {
      if (this.agents[agentId].isActive) {
        this.agents[agentId].isActive = false;
      }
    });
    console.log('Disabled all agents');
  }

  get activeAgentCount(): number {
    return Object.values(this.agents).filter(a => a.isActive).length;
  }

  get totalSuccessCount(): number {
    return Object.values(this.agents).reduce((sum, a) => sum + (a.successCount || 0), 0);
  }

  get totalErrorCount(): number {
    return Object.values(this.agents).reduce((sum, a) => sum + (a.errorCount || 0), 0);
  }

  get overallSuccessRate(): number {
    const total = this.totalSuccessCount + this.totalErrorCount;
    return total > 0 ? (this.totalSuccessCount / total) * 100 : 0;
  }
}