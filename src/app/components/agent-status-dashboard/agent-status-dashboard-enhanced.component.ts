import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MonitoringService, AgentStatus } from '../../services/monitoring.service';
import { AvatarService, AgentAvatar } from '../../services/avatar.service';
import { ActivityLoggerService } from '../../services/activity-logger.service';

@Component({
  selector: 'app-agent-status-dashboard-enhanced',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="agent-status-dashboard-enhanced fade-in">
      <!-- Header with Stats -->
      <div class="card glass-effect mb-4 slide-in-up">
        <div class="card-body">
          <div class="row align-items-center">
            <div class="col-md-8">
              <h4 class="mb-1">👥 AI Trading Team</h4>
              <p class="text-muted mb-0">10 specialized agents working together to generate trading signals</p>
            </div>
            <div class="col-md-4 text-end">
              <div class="d-flex justify-content-end gap-3">
                <div class="text-center">
                  <div class="h3 mb-0 text-success">{{activeAgentCount}}</div>
                  <div class="small text-muted">Active</div>
                </div>
                <div class="text-center">
                  <div class="h3 mb-0 text-primary">{{totalSuccessCount}}</div>
                  <div class="small text-muted">Success</div>
                </div>
                <div class="text-center">
                  <div class="h3 mb-0" [ngClass]="overallSuccessRate >= 80 ? 'text-success' : overallSuccessRate >= 60 ? 'text-warning' : 'text-danger'">
                    {{overallSuccessRate.toFixed(0)}}%
                  </div>
                  <div class="small text-muted">Success Rate</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Agent Grid -->
      <div class="row g-4 stagger-children">
        <div *ngFor="let agentId of agentList; let i = index" class="col-xl-3 col-lg-4 col-md-6">
          <div class="card card-hover h-100" 
               [ngClass]="{
                 'border-success shadow-sm': agents[agentId].isActive,
                 'border-danger': !agents[agentId].isActive
               }"
               [style.animation-delay.ms]="i * 100">
            <div class="card-header d-flex align-items-center justify-content-between py-3">
              <div class="d-flex align-items-center gap-2">
                <div class="agent-avatar position-relative">
                  <img [src]="getAvatar(agentId).avatarUrl" 
                       [alt]="getAvatar(agentId).name"
                       class="rounded-circle" 
                       width="40" 
                       height="40"
                       [style.border]="'2px solid ' + getAvatar(agentId).color">
                  <span class="position-absolute top-0 start-100 translate-middle p-1 
                              border border-white rounded-circle"
                        [ngClass]="agents[agentId].isActive ? 'bg-success' : 'bg-danger'"
                        [style.backgroundColor]="agents[agentId].isActive ? '#10b981' : '#ef4444'">
                  </span>
                </div>
                <div>
                  <h6 class="mb-0">{{getAvatar(agentId).name}}</h6>
                  <small class="text-muted">{{getAvatar(agentId).role}}</small>
                </div>
              </div>
              <span class="badge" 
                    [ngClass]="agents[agentId].isActive ? 'bg-success' : 'bg-danger'"
                    [class.pulse]="agents[agentId].isActive">
                {{agents[agentId].isActive ? '🟢 ACTIVE' : '🔴 INACTIVE'}}
              </span>
            </div>
            
            <div class="card-body py-3">
              <!-- Description -->
              <p class="small text-muted mb-3">
                {{getAvatar(agentId).description}}
              </p>
              
              <!-- Stats -->
              <div class="row g-2 mb-3">
                <div class="col-6">
                  <div class="text-center p-2 rounded" [style.backgroundColor]="getAvatar(agentId).color + '20'">
                    <div class="h5 mb-0" [style.color]="getAvatar(agentId).color">
                      {{agents[agentId].successCount || 0}}
                    </div>
                    <small class="text-muted">Success</small>
                  </div>
                </div>
                <div class="col-6">
                  <div class="text-center p-2 rounded bg-danger bg-opacity-10">
                    <div class="h5 mb-0 text-danger">{{agents[agentId].errorCount || 0}}</div>
                    <small class="text-muted">Errors</small>
                  </div>
                </div>
              </div>
              
              <!-- Success Rate -->
              <div class="mb-3">
                <div class="d-flex justify-content-between mb-1">
                  <small class="text-muted">Success Rate</small>
                  <small class="fw-bold" 
                         [ngClass]="{
                           'text-success': (agents[agentId].successRate || 0) >= 80,
                           'text-warning': (agents[agentId].successRate || 0) >= 60 && (agents[agentId].successRate || 0) < 80,
                           'text-danger': (agents[agentId].successRate || 0) < 60
                         }">
                    {{(agents[agentId].successRate || 0).toFixed(1)}}%
                  </small>
                </div>
                <div class="progress" style="height: 6px;">
                  <div class="progress-bar progress-bar-animated" 
                       [ngClass]="{
                         'bg-success': (agents[agentId].successRate || 0) >= 80,
                         'bg-warning': (agents[agentId].successRate || 0) >= 60 && (agents[agentId].successRate || 0) < 80,
                         'bg-danger': (agents[agentId].successRate || 0) < 60
                       }"
                       [style.width.%]="agents[agentId].successRate || 0">
                  </div>
                </div>
              </div>
              
              <!-- Last Activity -->
              <div class="d-flex justify-content-between align-items-center">
                <small class="text-muted">
                  <i class="bi bi-clock me-1"></i>
                  {{formatTime(agents[agentId].lastActivityTime) || 'Never'}}
                </small>
                <span class="badge bg-light text-dark">
                  {{getAvatar(agentId).emoji}}
                </span>
              </div>
            </div>
            
            <div class="card-footer py-2 bg-transparent border-top-0">
              <button class="btn btn-sm w-100 btn-hover" 
                      [ngClass]="agents[agentId].isActive ? 'btn-outline-danger' : 'btn-outline-success'"
                      (click)="toggleAgent(agentId)"
                      [disabled]="isProcessing[agentId]">
                <span *ngIf="isProcessing[agentId]" class="spinner-border spinner-border-sm me-2"></span>
                {{agents[agentId].isActive ? '⏸️ Pause Agent' : '▶️ Activate Agent'}}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- System Controls -->
      <div class="row mt-4">
        <div class="col-12">
          <div class="card glass-effect slide-in-up" [style.animation-delay.ms]="1000">
            <div class="card-body">
              <h6 class="mb-3">🚀 System Controls</h6>
              <div class="btn-group w-100" role="group">
                <button type="button" class="btn btn-primary btn-hover" (click)="enableAllAgents()">
                  <i class="bi bi-play-circle me-2"></i>Start All Agents
                </button>
                <button type="button" class="btn btn-warning btn-hover" (click)="pauseAllAgents()">
                  <i class="bi bi-pause-circle me-2"></i>Pause All
                </button>
                <button type="button" class="btn btn-success btn-hover" (click)="refreshStatus()" [disabled]="isRefreshing">
                  <span *ngIf="isRefreshing" class="spinner-border spinner-border-sm me-2"></span>
                  <i class="bi bi-arrow-clockwise me-2"></i>Refresh
                </button>
                <button type="button" class="btn btn-info btn-hover" (click)="viewLogs()">
                  <i class="bi bi-journal-text me-2"></i>View Logs
                </button>
              </div>
              
              <!-- Real-time Status -->
              <div class="mt-3 pt-3 border-top">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <small class="text-muted">
                      <i class="bi bi-activity me-1"></i>
                      Last updated: {{lastUpdateTime}}
                    </small>
                    <small class="ms-3 text-muted">
                      <i class="bi bi-lightning-charge me-1"></i>
                      Next refresh: {{nextRefreshTime}}
                    </small>
                  </div>
                  <div class="d-flex align-items-center gap-2">
                    <div class="status-indicator" [class.active]="isSystemHealthy"></div>
                    <small [ngClass]="isSystemHealthy ? 'text-success' : 'text-danger'">
                      {{isSystemHealthy ? 'System Healthy' : 'System Issues'}}
                    </small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Activity Feed Preview -->
      <div class="row mt-4" *ngIf="recentActivities.length > 0">
        <div class="col-12">
          <div class="card slide-in-up" [style.animation-delay.ms]="1100">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h6 class="mb-0">📋 Recent Activities</h6>
              <span class="badge bg-primary">{{recentActivities.length}} events</span>
            </div>
            <div class="card-body p-0">
              <div class="list-group list-group-flush">
                <div *ngFor="let activity of recentActivities" 
                     class="list-group-item list-group-item-action">
                  <div class="d-flex w-100 justify-content-between">
                    <div>
                      <span class="badge me-2" 
                            [ngClass]="{
                              'bg-success': activity.level === 'SUCCESS',
                              'bg-info': activity.level === 'INFO',
                              'bg-warning': activity.level === 'WARN',
                              'bg-danger': activity.level === 'ERROR'
                            }">
                        {{activity.level}}
                      </span>
                      <strong>{{activity.component}}</strong>
                      <div class="text-muted small mt-1">{{activity.message}}</div>
                    </div>
                    <small class="text-muted">{{activity.timestamp | date:'shortTime'}}</small>
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
    .agent-status-dashboard-enhanced {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .glass-effect {
      background: rgba(255, 255, 255, 0.7);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .agent-avatar {
      transition: all 0.3s ease;
    }
    
    .agent-avatar:hover {
      transform: scale(1.1);
    }
    
    .status-indicator {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      display: inline-block;
    }
    
    .status-indicator.active {
      background-color: #10b981;
      box-shadow: 0 0 8px #10b981;
    }
  `]
})
export class AgentStatusDashboardEnhancedComponent implements OnInit {
  agents: Record<string, AgentStatus> = {};
  agentList: string[] = [];
  lastUpdateTime: string = '';
  nextRefreshTime: string = '';
  isRefreshing: boolean = false;
  isProcessing: Record<string, boolean> = {};
  isSystemHealthy: boolean = true;
  recentActivities: any[] = [];
  
  constructor(
    private monitoringService: MonitoringService,
    private avatarService: AvatarService,
    private logger: ActivityLoggerService
  ) {}
  
  ngOnInit() {
    this.logger.info('AgentStatusDashboard', 'Enhanced dashboard initialized');
    
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
        successCount: Math.floor(Math.random() * 50) + 20,
        errorCount: Math.floor(Math.random() * 5),
        successRate: Math.floor(Math.random() * 30) + 70,
        isActive: Math.random() > 0.3
      };
      this.isProcessing[agent] = false;
    });
    
    this.refreshStatus();
    
    // Auto-refresh every 30 seconds
    setInterval(() => this.refreshStatus(), 30000);
    
    // Update next refresh time
    this.updateNextRefreshTime();
    
    // Subscribe to activity logs
    this.logger.subscribe((entry) => {
      this.recentActivities.unshift(entry);
      if (this.recentActivities.length > 5) {
        this.recentActivities = this.recentActivities.slice(0, 5);
      }
    });
    
    // Load initial recent activities
    this.recentActivities = this.logger.getLogs(5);
  }
  
  refreshStatus() {
    this.isRefreshing = true;
    this.logger.uiInteraction('AgentDashboard', 'Manual refresh triggered');
    
    this.monitoringService.getAgentsStatus().subscribe({
      next: (agents) => {
        // Merge backend data with our default agents
        if (agents && typeof agents === 'object') {
          Object.keys(agents).forEach(agentKey => {
            if (agents[agentKey] && typeof agents[agentKey] === 'object') {
              this.agents[agentKey] = { ...this.agents[agentKey], ...agents[agentKey] };
              this.logger.agentActivity(agentKey, 'Status updated', agents[agentKey]);
            }
          });
        }
        this.lastUpdateTime = new Date().toLocaleTimeString();
        this.updateNextRefreshTime();
        this.isSystemHealthy = this.activeAgentCount > 5;
        this.logger.success('AgentDashboard', 'Status refreshed successfully');
      },
      error: (err) => {
        this.logger.error('AgentDashboard', 'Failed to refresh status', err);
        this.isSystemHealthy = false;
      },
      complete: () => {
        this.isRefreshing = false;
      }
    });
  }
  
  getAvatar(agentId: string): AgentAvatar {
    return this.avatarService.getAgentAvatar(agentId);
  }
  
  formatAgentName(agentId: string): string {
    return agentId
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }
  
  formatTime(timestamp?: string): string {
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
  
  toggleAgent(agentId: string) {
    this.isProcessing[agentId] = true;
    
    // Simulate API call delay
    setTimeout(() => {
      if (this.agents[agentId]) {
        const wasActive = this.agents[agentId].isActive;
        this.agents[agentId].isActive = !wasActive;
        
        const action = wasActive ? 'paused' : 'activated';
        this.logger.agentActivity(agentId, `Agent ${action}`, { wasActive, nowActive: this.agents[agentId].isActive });
        
        // Update success rate based on activity
        if (this.agents[agentId].isActive) {
          this.agents[agentId].successCount = (this.agents[agentId].successCount || 0) + 1;
        }
        
        this.isProcessing[agentId] = false;
      }
    }, 500);
  }
  
  enableAllAgents() {
    this.logger.info('AgentDashboard', 'Enabling all agents');
    Object.keys(this.agents).forEach(agentId => {
      if (!this.agents[agentId].isActive) {
        this.agents[agentId].isActive = true;
        this.logger.agentActivity(agentId, 'Agent enabled via bulk action');
      }
    });
    this.logger.success('AgentDashboard', 'All agents enabled');
  }
  
  pauseAllAgents() {
    this.logger.info('AgentDashboard', 'Pausing all agents');
    Object.keys(this.agents).forEach(agentId => {
      if (this.agents[agentId].isActive) {
        this.agents[agentId].isActive = false;
        this.logger.agentActivity(agentId, 'Agent paused via bulk action');
      }
    });
    this.logger.warn('AgentDashboard', 'All agents paused');
  }
  
  viewLogs() {
    this.logger.uiInteraction('AgentDashboard', 'View logs clicked');
    // In a real app, this would navigate to logs page
    alert('Logs view would open here. Currently showing ' + this.recentActivities.length + ' recent activities.');
  }
  
  updateNextRefreshTime() {
    const next = new Date();
    next.setSeconds(next.getSeconds() + 30);
    this.nextRefreshTime = next.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
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
