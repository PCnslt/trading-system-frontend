import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MonitoringService, AgentActivity } from '../../services/monitoring.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-agent-activity-feed',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="activity-feed">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h6 class="mb-0">Real-time Agent Activities</h6>
        <div class="form-group mb-0" style="width: 200px;">
          <select class="form-select form-select-sm" [(ngModel)]="selectedAgent" (change)="filterActivities()">
            <option value="">All Agents</option>
            <option *ngFor="let agent of agents" [value]="agent">{{agent}}</option>
          </select>
        </div>
      </div>
      
      <div class="table-responsive">
        <table class="table table-sm table-hover">
          <thead>
            <tr>
              <th scope="col">Time</th>
              <th scope="col">Agent</th>
              <th scope="col">Task</th>
              <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let activity of filteredActivities" 
                [class.table-success]="activity.status === 'success'"
                [class.table-danger]="activity.status === 'error'"
                [class.table-warning]="activity.status === 'pending'">
              <td class="text-nowrap">{{formatTime(activity.timestamp)}}</td>
              <td>
                <span class="badge bg-primary">{{activity.agentId}}</span>
              </td>
              <td class="text-truncate" style="max-width: 200px;" title="{{activity.task}}">
                {{activity.task}}
              </td>
              <td>
                <span [class]="getStatusBadgeClass(activity.status)">
                  {{activity.status}}
                </span>
              </td>
            </tr>
            <tr *ngIf="filteredActivities.length === 0">
              <td colspan="4" class="text-center text-muted py-3">
                No activities to display
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="d-flex justify-content-between align-items-center mt-3">
        <small class="text-muted">Showing {{filteredActivities.length}} activities</small>
        <button class="btn btn-sm btn-outline-secondary" (click)="loadActivities()">
          Refresh
        </button>
      </div>
    </div>
  `,
  styles: [`
    .activity-feed {
      font-size: 0.875rem;
    }
    .table th, .table td {
      padding: 0.5rem;
    }
  `]
})
export class AgentActivityFeedComponent implements OnInit {
  activities: AgentActivity[] = [];
  filteredActivities: AgentActivity[] = [];
  agents: string[] = [];
  selectedAgent: string = '';
  
  constructor(private monitoringService: MonitoringService) {}
  
  ngOnInit() {
    this.loadActivities();
    this.loadAgents();
    
    // Subscribe to real-time updates
    this.monitoringService.agentActivity$.subscribe(activity => {
      this.activities.unshift(activity);
      if (this.activities.length > 50) {
        this.activities = this.activities.slice(0, 50);
      }
      this.filterActivities();
    });
  }
  
  loadActivities() {
    console.log('AgentActivityFeed: Loading activities...');
    this.monitoringService.getAgentActivities().subscribe({
      next: (activities) => {
        console.log('AgentActivityFeed: Received', activities?.length, 'activities');
        console.log('First activity:', activities?.[0]);
        this.activities = activities.slice(0, 50); // Limit to 50 most recent
        this.filterActivities();
      },
      error: (err) => {
        console.error('AgentActivityFeed: Failed to load activities:', err);
        console.error('Error details:', err.message, err.status, err.url);
      }
    });
  }
  
  loadAgents() {
    this.monitoringService.getAgentActivities().subscribe({
      next: (activities) => {
        const agentSet = new Set(activities.map(a => a.agentId));
        this.agents = Array.from(agentSet).sort();
      },
      error: (err) => console.error('Failed to load agents:', err)
    });
  }
  
  filterActivities() {
    if (this.selectedAgent) {
      this.filteredActivities = this.activities.filter(
        a => a.agentId === this.selectedAgent
      );
    } else {
      this.filteredActivities = this.activities;
    }
  }
  
  formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }
  
  getStatusBadgeClass(status: string): string {
    switch(status) {
      case 'success': return 'badge bg-success';
      case 'error': return 'badge bg-danger';
      case 'pending': return 'badge bg-warning text-dark';
      default: return 'badge bg-secondary';
    }
  }
}