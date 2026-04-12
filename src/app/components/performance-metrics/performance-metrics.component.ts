import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MonitoringService } from '../../services/monitoring.service';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';

@Component({
  selector: 'app-performance-metrics',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  template: `
    <div class="performance-metrics">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h6 class="mb-0">Performance Metrics</h6>
        <div class="btn-group btn-group-sm" role="group">
          <button type="button" class="btn btn-outline-primary" 
                  [class.active]="timeRange === '24h'" (click)="setTimeRange('24h')">24h</button>
          <button type="button" class="btn btn-outline-primary" 
                  [class.active]="timeRange === '7d'" (click)="setTimeRange('7d')">7d</button>
          <button type="button" class="btn btn-outline-primary" 
                  [class.active]="timeRange === '30d'" (click)="setTimeRange('30d')">30d</button>
        </div>
      </div>
      
      <div class="row g-3">
        <div class="col-md-6">
          <div class="card">
            <div class="card-header py-2">
              <h6 class="mb-0">Success Rate Trend</h6>
            </div>
            <div class="card-body">
              <canvas baseChart
                [data]="successRateChartData"
                [type]="successRateChartType"
                [options]="successRateChartOptions">
              </canvas>
            </div>
          </div>
        </div>
        
        <div class="col-md-6">
          <div class="card">
            <div class="card-header py-2">
              <h6 class="mb-0">Activity Distribution</h6>
            </div>
            <div class="card-body">
              <canvas baseChart
                [data]="activityChartData"
                [type]="activityChartType"
                [options]="activityChartOptions">
              </canvas>
            </div>
          </div>
        </div>
      </div>
      
      <div class="row mt-3">
        <div class="col-md-4">
          <div class="card text-center">
            <div class="card-body">
              <div class="display-6">{{metrics.totalActivities || 0}}</div>
              <div class="text-muted small">Total Activities</div>
            </div>
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="card text-center">
            <div class="card-body">
              <div class="display-6" [ngClass]="{'text-success': metrics.avgSuccessRate >= 80, 'text-warning': metrics.avgSuccessRate >= 60, 'text-danger': metrics.avgSuccessRate < 60}">
                {{(metrics.avgSuccessRate || 0).toFixed(1)}}%
              </div>
              <div class="text-muted small">Avg Success Rate</div>
            </div>
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="card text-center">
            <div class="card-body">
              <div class="display-6">{{metrics.activeAgents || 0}}/10</div>
              <div class="text-muted small">Active Agents</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="mt-3">
        <button class="btn btn-sm btn-outline-primary w-100" (click)="refreshMetrics()">
          Refresh Metrics
        </button>
      </div>
    </div>
  `,
  styles: [`
    .performance-metrics {
      font-size: 0.875rem;
    }
    .btn-group .btn.active {
      background-color: #0d6efd;
      color: white;
    }
  `]
})
export class PerformanceMetricsComponent implements OnInit {
  timeRange: string = '24h';
  metrics: any = {};
  
  // Success Rate Chart
  successRateChartData: ChartData<'line'> = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        data: [65, 72, 78, 75, 80, 82, 85],
        label: 'Success Rate',
        borderColor: '#198754',
        backgroundColor: 'rgba(25, 135, 84, 0.1)',
        fill: true,
        tension: 0.3
      }
    ]
  };
  
  successRateChartType: ChartType = 'line';
  
  successRateChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: (value) => value + '%'
        }
      }
    }
  };
  
  // Activity Chart
  activityChartData: ChartData<'bar'> = {
    labels: ['Technical', 'Fundamental', 'Sentiment', 'Macro', 'Crypto', 'Risk', 'Options', 'Quant', 'Sector', 'Compliance'],
    datasets: [
      {
        data: [120, 95, 85, 70, 60, 55, 50, 45, 40, 35],
        label: 'Activities',
        backgroundColor: [
          '#0d6efd', '#198754', '#ffc107', '#dc3545',
          '#6f42c1', '#fd7e14', '#20c997', '#0dcaf0',
          '#6610f2', '#d63384'
        ]
      }
    ]
  };
  
  activityChartType: ChartType = 'bar';
  
  activityChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };
  
  constructor(private monitoringService: MonitoringService) {}
  
  ngOnInit() {
    this.refreshMetrics();
    
    // Auto-refresh every 60 seconds
    setInterval(() => this.refreshMetrics(), 60000);
  }
  
  setTimeRange(range: string) {
    this.timeRange = range;
    this.refreshMetrics();
  }
  
  refreshMetrics() {
    // Load system stats
    this.monitoringService.getMonitoringStats().subscribe({
      next: (stats) => {
        this.metrics = stats;
      },
      error: (err) => console.error('Failed to load metrics:', err)
    });
    
    // Load agent status for active count
    this.monitoringService.getAgentsStatus().subscribe({
      next: (agents) => {
        const activeCount = Object.values(agents).filter(a => a.isActive).length;
        this.metrics.activeAgents = activeCount;
      },
      error: (err) => console.error('Failed to load agent status:', err)
    });
    
    // Update charts with simulated data (in real app, this would come from API)
    this.updateChartData();
  }
  
  updateChartData() {
    // Simulate different data based on time range
    let labels: string[];
    let data: number[];
    
    switch(this.timeRange) {
      case '24h':
        labels = Array.from({length: 24}, (_, i) => `${i}:00`);
        data = Array.from({length: 24}, () => Math.floor(Math.random() * 20) + 75);
        break;
      case '7d':
        labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        data = [65, 72, 78, 75, 80, 82, 85];
        break;
      case '30d':
        labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
        data = [70, 75, 78, 82];
        break;
      default:
        labels = [];
        data = [];
    }
    
    this.successRateChartData = {
      labels,
      datasets: [
        {
          data,
          label: 'Success Rate',
          borderColor: '#198754',
          backgroundColor: 'rgba(25, 135, 84, 0.1)',
          fill: true,
          tension: 0.3
        }
      ]
    };
    
    // Update activity chart with random data
    this.activityChartData = {
      labels: ['Technical', 'Fundamental', 'Sentiment', 'Macro', 'Crypto', 'Risk', 'Options', 'Quant', 'Sector', 'Compliance'],
      datasets: [
        {
          data: Array.from({length: 10}, () => Math.floor(Math.random() * 100) + 30),
          label: 'Activities',
          backgroundColor: [
            '#0d6efd', '#198754', '#ffc107', '#dc3545',
            '#6f42c1', '#fd7e14', '#20c997', '#0dcaf0',
            '#6610f2', '#d63384'
          ]
        }
      ]
    };
  }
}