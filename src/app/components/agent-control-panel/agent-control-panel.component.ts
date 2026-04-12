import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { environment } from '../../../environments/index';

interface TriggerResponse {
  status: string;
  message: string;
  activity?: any;
  gatewayResponse?: any;
  successCount?: number;
  errorCount?: number;
  results?: any;
  symbol?: string;
  timestamp?: string;
}

@Component({
  selector: 'app-agent-control-panel',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="agent-control-panel">
      <div class="card">
        <div class="card-header bg-primary text-white">
          <h5 class="mb-0">🎮 Agent Control Panel</h5>
        </div>
        <div class="card-body">
          <!-- Symbol Input -->
          <div class="row mb-3">
            <div class="col-md-6">
              <label for="symbol" class="form-label">Symbol</label>
              <input type="text" class="form-control" id="symbol" [(ngModel)]="symbol" 
                     placeholder="e.g., AAPL, TSLA, BTC">
            </div>
            <div class="col-md-6">
              <label for="agent" class="form-label">Agent</label>
              <select class="form-select" id="agent" [(ngModel)]="selectedAgent">
                <option value="">Select Agent</option>
                <option *ngFor="let agent of agents" [value]="agent.value">{{agent.label}}</option>
              </select>
            </div>
          </div>
          
          <!-- Trigger Buttons -->
          <div class="row mb-3">
            <div class="col-md-12">
              <div class="btn-group" role="group">
                <button type="button" class="btn btn-primary" 
                        (click)="triggerSingleAgent()"
                        [disabled]="!selectedAgent || !symbol">
                  Trigger {{selectedAgent || 'Agent'}}
                </button>
                <button type="button" class="btn btn-success" 
                        (click)="triggerAllAgents()"
                        [disabled]="!symbol">
                  Trigger All 10 Agents
                </button>
                <button type="button" class="btn btn-outline-secondary" 
                        (click)="clearLogs()">
                  Clear Logs
                </button>
              </div>
            </div>
          </div>
          
          <!-- Quick Symbol Buttons -->
          <div class="row mb-3">
            <div class="col-md-12">
              <div class="btn-group" role="group">
                <span class="me-2">Quick Symbols:</span>
                <button type="button" class="btn btn-sm btn-outline-primary" 
                        (click)="setSymbol('AAPL')">AAPL</button>
                <button type="button" class="btn btn-sm btn-outline-primary" 
                        (click)="setSymbol('TSLA')">TSLA</button>
                <button type="button" class="btn btn-sm btn-outline-primary" 
                        (click)="setSymbol('MSFT')">MSFT</button>
                <button type="button" class="btn btn-sm btn-outline-primary" 
                        (click)="setSymbol('NVDA')">NVDA</button>
                <button type="button" class="btn btn-sm btn-outline-primary" 
                        (click)="setSymbol('BTC')">BTC</button>
              </div>
            </div>
          </div>
          
          <!-- Status & Logs -->
          <div class="row">
            <div class="col-md-12">
              <div class="card">
                <div class="card-header">
                  <h6 class="mb-0">Trigger Logs</h6>
                </div>
                <div class="card-body" style="max-height: 300px; overflow-y: auto;">
                  <div *ngIf="logs.length === 0" class="text-muted">No triggers yet.</div>
                  <div *ngFor="let log of logs" class="log-entry mb-2">
                    <div class="d-flex justify-content-between">
                      <span class="fw-bold">{{log.timestamp}}</span>
                      <span class="badge" [ngClass]="log.status === 'success' ? 'bg-success' : 'bg-danger'">
                        {{log.status}}
                      </span>
                    </div>
                    <div class="small">{{log.message}}</div>
                    <div *ngIf="log.agent" class="small text-muted">Agent: {{log.agent}}, Symbol: {{log.symbol}}</div>
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
    .agent-control-panel {
      font-size: 0.875rem;
    }
    .log-entry {
      padding: 0.5rem;
      border-left: 3px solid #dee2e6;
      background-color: #f8f9fa;
    }
    .log-entry.success {
      border-left-color: #198754;
    }
    .log-entry.error {
      border-left-color: #dc3545;
    }
  `]
})
export class AgentControlPanelComponent implements OnInit {
  symbol: string = 'AAPL';
  selectedAgent: string = 'technical';
  logs: Array<{
    timestamp: string;
    message: string;
    status: string;
    agent?: string;
    symbol?: string;
  }> = [];
  
  agents = [
    { value: 'technical', label: 'Technical Analyst' },
    { value: 'fundamental', label: 'Fundamental Analyst' },
    { value: 'sentiment', label: 'Sentiment Analyst' },
    { value: 'macro', label: 'Macro Analyst' },
    { value: 'crypto', label: 'Crypto Analyst' },
    { value: 'options', label: 'Options Analyst' },
    { value: 'risk', label: 'Risk Analyst' },
    { value: 'quant', label: 'Quant Analyst' },
    { value: 'sector', label: 'Sector Analyst' },
    { value: 'compliance', label: 'Compliance Analyst' }
  ];

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.addLog('Control panel initialized', 'info');
  }

  triggerSingleAgent() {
    console.log('Triggering single agent:', this.selectedAgent, this.symbol);
    if (!this.selectedAgent || !this.symbol) {
      this.addLog('Please select an agent and enter a symbol', 'error');
      return;
    }
    
    const url = `${environment.apiUrl}/trigger/${this.selectedAgent}/${this.symbol}`;
    this.addLog(`Triggering ${this.selectedAgent} for ${this.symbol}...`, 'info');
    
    this.http.post<TriggerResponse>(url, {}).subscribe({
      next: (response) => {
        this.addLog(`Success: ${response.message}`, 'success', this.selectedAgent, this.symbol);
        console.log('Trigger response:', response);
      },
      error: (error: HttpErrorResponse) => {
        const message = error.error?.message || error.message || 'Unknown error';
        this.addLog(`Error: ${message}`, 'error', this.selectedAgent, this.symbol);
        console.error('Trigger error:', error);
      }
    });
  }

  triggerAllAgents() {
    if (!this.symbol) {
      this.addLog('Please enter a symbol', 'error');
      return;
    }
    
    const url = `${environment.apiUrl}/trigger/all/${this.symbol}`;
    this.addLog(`Triggering all 10 agents for ${this.symbol}...`, 'info');
    
    this.http.post<TriggerResponse>(url, {}).subscribe({
      next: (response) => {
        this.addLog(`All agents triggered: ${response.successCount || 0} success, ${response.errorCount || 0} errors`, 
                   'success', 'all', this.symbol);
        console.log('Trigger all response:', response);
      },
      error: (error: HttpErrorResponse) => {
        const message = error.error?.message || error.message || 'Unknown error';
        this.addLog(`Error: ${message}`, 'error', 'all', this.symbol);
        console.error('Trigger all error:', error);
      }
    });
  }

  setSymbol(symbol: string) {
    this.symbol = symbol;
    this.addLog(`Symbol set to ${symbol}`, 'info');
  }

  clearLogs() {
    this.logs = [];
    this.addLog('Logs cleared', 'info');
  }

  private addLog(message: string, status: 'success' | 'error' | 'info', agent?: string, symbol?: string) {
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    this.logs.unshift({ timestamp, message, status, agent, symbol });
    // Keep only last 20 logs
    if (this.logs.length > 20) {
      this.logs = this.logs.slice(0, 20);
    }
  }
}