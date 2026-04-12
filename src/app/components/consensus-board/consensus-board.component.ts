import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MonitoringService, ConsensusVote } from '../../services/monitoring.service';

@Component({
  selector: 'app-consensus-board',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="consensus-board">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h6 class="mb-0">Latest Consensus Votes</h6>
        <div class="btn-group btn-group-sm" role="group">
          <button type="button" class="btn btn-outline-success" 
                  [class.active]="filterDecision === 'BUY'" (click)="filterDecision = 'BUY'">BUY</button>
          <button type="button" class="btn btn-outline-danger" 
                  [class.active]="filterDecision === 'SELL'" (click)="filterDecision = 'SELL'">SELL</button>
          <button type="button" class="btn btn-outline-warning" 
                  [class.active]="filterDecision === 'HOLD'" (click)="filterDecision = 'HOLD'">HOLD</button>
          <button type="button" class="btn btn-outline-secondary" 
                  [class.active]="filterDecision === ''" (click)="filterDecision = ''">ALL</button>
        </div>
      </div>
      
      <div class="row">
        <div *ngFor="let vote of filteredVotes" class="col-md-6 col-lg-4 mb-3">
          <div class="card h-100" [ngClass]="getVoteCardClass(vote)">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h6 class="mb-0">{{vote.symbol}}</h6>
              <span class="badge" [ngClass]="getDecisionBadgeClass(vote)">
                {{vote.finalDecision}}
              </span>
            </div>
            <div class="card-body">
              <div class="mb-2">
                <small class="text-muted">Confidence:</small>
                <div class="progress" style="height: 8px;">
                  <div class="progress-bar" [ngClass]="getConfidenceBarClass(vote.confidence)"
                       [style.width.%]="vote.confidence * 100">
                  </div>
                </div>
                <div class="text-end small">{{(vote.confidence * 100).toFixed(1)}}%</div>
              </div>
              
              <div class="row small">
                <div class="col-6">
                  <div class="text-success">
                    <strong>{{countAgents(vote.agentsInFavor)}}</strong>
                    <div>In Favor</div>
                  </div>
                </div>
                <div class="col-6">
                  <div class="text-danger">
                    <strong>{{countAgents(vote.agentsAgainst)}}</strong>
                    <div>Against</div>
                  </div>
                </div>
              </div>
              
              <div class="mt-2">
                <small class="text-muted">Vote:</small>
                <div>{{vote.agentsVoted}}/{{vote.totalAgents || 10}} agents voted</div>
              </div>
              
              <div *ngIf="vote.priceAtDecision" class="mt-2">
                <small class="text-muted">Price at decision:</small>
                <div>{{vote.priceAtDecision.toFixed(2)}}</div>
              </div>
              
              <div *ngIf="vote.reasoning" class="mt-2 small text-muted">
                <em>"{{vote.reasoning.substring(0, 80)}}..."</em>
              </div>
            </div>
            <div class="card-footer text-muted small">
              {{formatTime(vote.timestamp)}}
            </div>
          </div>
        </div>
        
        <div *ngIf="filteredVotes.length === 0" class="col-12">
          <div class="text-center text-muted py-4">
            No consensus votes to display
          </div>
        </div>
      </div>
      
      <div class="d-flex justify-content-between align-items-center mt-3">
        <small class="text-muted">Showing {{filteredVotes.length}} consensus votes</small>
        <button class="btn btn-sm btn-outline-secondary" (click)="loadVotes()">
          Refresh
        </button>
      </div>
    </div>
  `,
  styles: [`
    .consensus-board {
      font-size: 0.875rem;
    }
    .card.buy-card {
      border-left: 4px solid #198754;
    }
    .card.sell-card {
      border-left: 4px solid #dc3545;
    }
    .card.hold-card {
      border-left: 4px solid #ffc107;
    }
    .btn-group .btn.active {
      color: white;
    }
    .btn-group .btn-outline-success.active {
      background-color: #198754;
    }
    .btn-group .btn-outline-danger.active {
      background-color: #dc3545;
    }
    .btn-group .btn-outline-warning.active {
      background-color: #ffc107;
      color: #000;
    }
    .btn-group .btn-outline-secondary.active {
      background-color: #6c757d;
    }
  `]
})
export class ConsensusBoardComponent implements OnInit {
  votes: ConsensusVote[] = [];
  filteredVotes: ConsensusVote[] = [];
  filterDecision: string = '';
  
  constructor(private monitoringService: MonitoringService) {}
  
  ngOnInit() {
    this.loadVotes();
    
    // Subscribe to real-time updates
    this.monitoringService.consensusVote$.subscribe(vote => {
      this.votes.unshift(vote);
      if (this.votes.length > 20) {
        this.votes = this.votes.slice(0, 20);
      }
      this.applyFilter();
    });
  }
  
  loadVotes() {
    this.monitoringService.getConsensusVotes().subscribe({
      next: (votes) => {
        this.votes = votes.slice(0, 20); // Limit to 20 most recent
        this.applyFilter();
      },
      error: (err) => console.error('Failed to load consensus votes:', err)
    });
  }
  
  applyFilter() {
    if (this.filterDecision) {
      this.filteredVotes = this.votes.filter(
        v => v.finalDecision === this.filterDecision
      );
    } else {
      this.filteredVotes = this.votes;
    }
  }
  
  getVoteCardClass(vote: ConsensusVote): string {
    switch(vote.finalDecision) {
      case 'BUY': return 'buy-card';
      case 'SELL': return 'sell-card';
      case 'HOLD': return 'hold-card';
      default: return '';
    }
  }
  
  getDecisionBadgeClass(vote: ConsensusVote): string {
    switch(vote.finalDecision) {
      case 'BUY': return 'bg-success';
      case 'SELL': return 'bg-danger';
      case 'HOLD': return 'bg-warning text-dark';
      default: return 'bg-secondary';
    }
  }
  
  getConfidenceBarClass(confidence: number): string {
    if (confidence >= 0.8) return 'bg-success';
    if (confidence >= 0.6) return 'bg-warning';
    return 'bg-danger';
  }
  
  countAgents(agentsString: string): number {
    if (!agentsString) return 0;
    try {
      const agents = JSON.parse(agentsString);
      return Array.isArray(agents) ? agents.length : 1;
    } catch {
      return agentsString.split(',').filter(a => a.trim()).length;
    }
  }
  
  formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
}