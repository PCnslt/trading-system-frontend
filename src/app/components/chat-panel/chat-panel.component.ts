import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MonitoringService, ChatMessage } from '../../services/monitoring.service';

@Component({
  selector: 'app-chat-panel',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="chat-panel">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h6 class="mb-0">Agent Communications</h6>
        <div class="btn-group btn-group-sm" role="group">
          <button type="button" class="btn btn-outline-primary" 
                  [class.active]="filterType === ''" (click)="filterType = ''">All</button>
          <button type="button" class="btn btn-outline-primary" 
                  [class.active]="filterType === 'reasoning'" (click)="filterType = 'reasoning'">Reasoning</button>
          <button type="button" class="btn btn-outline-primary" 
                  [class.active]="filterType === 'alert'" (click)="filterType = 'alert'">Alerts</button>
        </div>
      </div>
      
      <div class="chat-messages" style="max-height: 300px; overflow-y: auto;">
        <div *ngFor="let message of filteredMessages" class="chat-message mb-2 p-2 border rounded">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <span class="badge bg-info">{{message.sender}}</span>
              <span class="text-muted ms-2">→</span>
              <span class="badge bg-secondary ms-1">{{message.receiver}}</span>
              <small class="text-muted ms-2">{{formatTime(message.timestamp)}}</small>
            </div>
            <span *ngIf="message.confidence" class="badge" 
                  [ngClass]="{'bg-success': message.confidence > 0.7, 'bg-warning': message.confidence > 0.4, 'bg-danger': message.confidence <= 0.4}">
              {{(message.confidence * 100).toFixed(0)}}%
            </span>
          </div>
          <div class="mt-1">
            <strong>{{message.messageType || 'message'}}:</strong> {{message.message}}
          </div>
          <div *ngIf="message.context" class="mt-1 text-muted small">
            <em>Context: {{message.context}}</em>
          </div>
          <div *ngIf="message.symbol" class="mt-1">
            <span class="badge bg-primary">Symbol: {{message.symbol}}</span>
          </div>
        </div>
        <div *ngIf="filteredMessages.length === 0" class="text-center text-muted py-3">
          No chat messages to display
        </div>
      </div>
      
      <div class="mt-3">
        <div class="input-group input-group-sm">
          <span class="input-group-text">Quick Send</span>
          <input type="text" class="form-control" placeholder="Message..." [(ngModel)]="newMessage" (keyup.enter)="sendTestMessage()">
          <button class="btn btn-outline-primary" type="button" (click)="sendTestMessage()">Send</button>
        </div>
        <small class="text-muted">Test chat functionality (simulated)</small>
      </div>
    </div>
  `,
  styles: [`
    .chat-panel {
      font-size: 0.875rem;
    }
    .chat-message {
      background-color: #f8f9fa;
      border-left: 3px solid #0d6efd;
    }
    .chat-message.alert {
      border-left-color: #dc3545;
      background-color: #fff5f5;
    }
    .chat-message.reasoning {
      border-left-color: #198754;
      background-color: #f0fff4;
    }
    .btn-group .btn.active {
      background-color: #0d6efd;
      color: white;
    }
  `]
})
export class ChatPanelComponent implements OnInit {
  messages: ChatMessage[] = [];
  filteredMessages: ChatMessage[] = [];
  filterType: string = '';
  newMessage: string = '';
  
  constructor(private monitoringService: MonitoringService) {}
  
  ngOnInit() {
    this.loadMessages();
    
    // Subscribe to real-time updates
    this.monitoringService.chatMessage$.subscribe(message => {
      this.messages.unshift(message);
      if (this.messages.length > 30) {
        this.messages = this.messages.slice(0, 30);
      }
      this.applyFilter();
    });
  }
  
  loadMessages() {
    this.monitoringService.getChatMessages().subscribe({
      next: (messages) => {
        this.messages = messages.slice(0, 30); // Limit to 30 most recent
        this.applyFilter();
      },
      error: (err) => console.error('Failed to load chat messages:', err)
    });
  }
  
  applyFilter() {
    if (this.filterType) {
      this.filteredMessages = this.messages.filter(
        m => m.messageType === this.filterType
      );
    } else {
      this.filteredMessages = this.messages;
    }
  }
  
  formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  
  sendTestMessage() {
    if (!this.newMessage.trim()) return;
    
    const testMessage: Partial<ChatMessage> = {
      sender: 'test_agent',
      receiver: 'monitoring_dashboard',
      message: this.newMessage,
      messageType: 'test',
      timestamp: new Date().toISOString(),
      confidence: 0.8
    };
    
    this.monitoringService.createChatMessage(testMessage).subscribe({
      next: () => {
        this.newMessage = '';
      },
      error: (err) => console.error('Failed to send test message:', err)
    });
  }
}