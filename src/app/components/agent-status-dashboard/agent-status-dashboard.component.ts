import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MonitoringService, AgentStatus } from '../../services/monitoring.service';
import { AvatarService, AgentAvatar } from '../../services/avatar.service';
import { ActivityLoggerService } from '../../services/activity-logger.service';

@Component({
  selector: 'app-agent-status-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="agent-status-dashboard">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h6 class="mb-0">10-Agent Trading System Status</h6>
        <div class="text-end">
          <div class="small text-muted">Last updated: {{lastUpdateTime}}</div>
        </div>
      </div>
      
      <div class="row g-3">
        <div *ngFor="let agent of agentList" class="col-md-6 col-lg-3">
          <div class="card h-100" [ngClass]="{'border-success': agents[agent].isActive, 'border-danger': !agents[agent].isActive}">
            <div class="card-header d-flex justify-content-between align-items-center py-2">
              <h6 class="mb-0">{{formatAgentName(agent)}}</h6>
              <span class="badge" [ngClass]="agents[agent].isActive ? 'bg-success' : 'bg-danger'">
                {{agents[agent].isActive ? 'ACTIVE' : 'INACTIVE'}}
              </span>
            </div>
            <div class="card-body py-2">
              <div class="mb-2">
                <div class="small text-muted">Last Activity</div>
                <div class="small">{{agents[agent].lastActivity || 'No activity'}}</div>
              </div>
              
              <div class="row small">
                <div class="col-6">
                  <div class="text-success">
                    <div class="fw-bold">{{agents[agent].successCount || 0}}</div>
                    <div>Success</div>
                  </div>
                </div>
                <div class="col-6">
                  <div class="text-danger">
                    <div class="fw-bold">{{agents[agent].errorCount || 0}}</div>
                    <div>Errors</div>
                  </div>
                </div>
              </div>
              
              <div class="mt-2">
                <div class="small text-muted">Success Rate</div>
                <div class="progress" style="height: 6px;">
                  <div class="progress-bar" 
                       [ngClass]="getSuccessRateClass(agents[agent].successRate || 0)"
                       [style.width.%]="agents[agent].successRate || 0">
                  </div>
                </div>
                <div class="text-end small">{{(agents[agent].successRate || 0).toFixed(1)}}%</div>
              </div>
              
              <div *ngIf="agents[agent].lastActivityTime" class="mt-2 small text-muted">
                {{formatTime(agents[agent].lastActivityTime)}}
              </div>
            </div>
            <div class="card-footer py-1">
              <button class="btn btn-sm w-100" 
                      [ngClass]="agents[agent].isActive ? 'btn-outline-success' : 'btn-outline-secondary'"
                      (click)="toggleAgent(agent); $event.stopPropagation()">
                {{agents[agent].isActive ? 'Disable' : 'Enable'}}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="row mt-3">
        <div class="col-md-6">
          <div class="card">
            <div class="card-header py-2">
              <h6 class="mb-0">System Summary</h6>
            </div>
            <div class="card-body py-2">
              <div class="row small">
                <div class="col-6">
                  <div class="text-primary">
                    <div class="fw-bold">{{activeAgentCount}}</div>
                    <div>Active Agents</div>
                  </div>
                </div>
                <div class="col-6">
                  <div class="text-success">
                    <div class="fw-bold">{{totalSuccessCount}}</div>
                    <div>Total Success</div>
                  </div>
                </div>
                <div class="col-6">
                  <div class="text-danger">
                    <div class="fw-bold">{{totalErrorCount}}</div>
                    <div>Total Errors</div>
                  </div>
                </div>
                <div class="col-6">
                  <div class="text-info">
                    <div class="fw-bold">{{overallSuccessRate.toFixed(1)}}%</div>
                    <div>Overall Success</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card">
            <div class="card-header py-2">
              <h6 class="mb-0">Quick Actions</h6>
            </div>
            <div class="card-body py-2">
              <div class="btn-group w-100" role="group">
                <button type="button" class="btn btn-sm btn-outline-primary" (click)="enableAllAgents()">Enable All</button>
                <button type="button" class="btn btn-sm btn-outline-secondary" (click)="disableAllAgents()">Disable All</button>
                <button type="button" class="btn btn-sm btn-outline-success" (click)="refreshStatus()">Refresh</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .agent-status-dashboard {
      font-size: 0.875rem;
    }
    .card {
      transition: all 0.2s;
    }
    .card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
  `]
})
export class AgentStatusDashboardComponent implements OnInit {
  agents: Record<string, AgentStatus> = {};
  agentList: string[] = [];
  lastUpdateTime: string = '';
  
  constructor(private monitoringService: MonitoringService) {}
  
  ngOnInit() {
    // Initialize with default agent list
    this.agentList = [
      'technical-analyst', 'fundamental-analyst', 'sentiment-analyst',
      'macro-analyst', 'crypto-analyst', 'options-analyst',
      'risk-analyst', 'quant-analyst', 'sector-analyst', 'compliance-analyst'
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
    });
    
    this.refreshStatus();
    
    // Auto-refresh every 30 seconds
    setInterval(() => this.refreshStatus(), 30000);
  }
  
  refreshStatus() {
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
        console.log('AgentStatusDashboard: Updated agent status', this.agents);
      },
      error: (err) => {
        console.error('Failed to load agent status:', err);
        // Keep using default data
        this.lastUpdateTime = new Date().toLocaleTimeString() + ' (offline)';
      }
    });
  }
  
  formatAgentName(agentId: string): string {
    return agentId
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }
  
  formatTime(timestamp: string): string {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  
  getSuccessRateClass(rate: number): string {
    if (rate >= 80) return 'bg-success';
    if (rate >= 60) return 'bg-warning';
    return 'bg-danger';
  }
  
  toggleAgent(agentId: string) {
    // Toggle locally for UI demonstration
    if (this.agents[agentId]) {
      this.agents[agentId].isActive = !this.agents[agentId].isActive;
      console.log(`Toggled agent ${agentId} to ${this.agents[agentId].isActive ? 'active' : 'inactive'}`);
    }
  }
  
  enableAllAgents() {
    Object.keys(this.agents).forEach(agentId => {
      this.agents[agentId].isActive = true;
    });
    console.log('Enabled all agents');
  }
  
  disableAllAgents() {
    Object.keys(this.agents).forEach(agentId => {
      this.agents[agentId].isActive = false;
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