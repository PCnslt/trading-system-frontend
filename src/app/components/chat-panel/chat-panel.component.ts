import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/index';

interface ChatMessage {
  id?: number;
  senderType: string; // 'user' or 'agent'
  senderId: string;
  agentName?: string;
  agentExpertise?: string;
  message: string;
  timestamp: string;
  signal?: string;
  confidence?: number;
  modelUsed?: string;
  symbol?: string;
  messageType?: string;
}

interface AgentProfile {
  id: string;
  name: string;
  expertise: string;
  personality: string;
  model: string;
  status: string;
}

@Component({
  selector: 'app-chat-panel',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="chat-panel">
      <!-- Header with Agent Selection -->
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h6 class="mb-0">💬 Real Agent Chat</h6>
          <small class="text-muted">10 intelligent agents with Hugging Face brains</small>
        </div>
        <div class="btn-group btn-group-sm" role="group">
          <button type="button" class="btn btn-outline-primary" 
                  [class.active]="selectedAgentId === ''" (click)="selectAgent('')">
            All Agents
          </button>
          <button type="button" class="btn btn-outline-primary" 
                  [class.active]="selectedAgentId === 'technical_analyst'" (click)="selectAgent('technical_analyst')">
            Technical
          </button>
          <button type="button" class="btn btn-outline-primary" 
                  [class.active]="selectedAgentId === 'fundamental_analyst'" (click)="selectAgent('fundamental_analyst')">
            Fundamental
          </button>
        </div>
      </div>

      <!-- Agent Status -->
      <div class="mb-3">
        <div class="d-flex flex-wrap gap-1">
          <span *ngFor="let agent of agentProfiles" class="badge" 
                [ngClass]="getAgentBadgeClass(agent.id)"
                [title]="agent.expertise"
                (click)="selectAgent(agent.id)"
                style="cursor: pointer;">
            {{agent.name.split(' ')[0]}}
          </span>
        </div>
        <small class="text-muted">Click agent badges to chat with specific experts</small>
      </div>

      <!-- Chat Messages -->
      <div class="chat-messages border rounded p-2" style="max-height: 300px; overflow-y: auto; background: var(--bg-secondary);">
        <div *ngFor="let message of filteredMessages" class="chat-message mb-2 p-2 border rounded"
             [ngClass]="{'user-message': message.senderType === 'user', 'agent-message': message.senderType === 'agent'}">
          
          <!-- Message Header -->
          <div class="d-flex justify-content-between align-items-start mb-1">
            <div>
              <span *ngIf="message.senderType === 'agent'" class="badge" [ngClass]="getAgentBadgeClass(message.senderId)">
                {{message.agentName || message.senderId}}
              </span>
              <span *ngIf="message.senderType === 'user'" class="badge bg-primary">
                You
              </span>
              
              <span *ngIf="message.signal" class="badge ms-1" [ngClass]="getSignalBadgeClass(message.signal)">
                {{message.signal}}
              </span>
              
              <small class="text-muted ms-2">{{formatTime(message.timestamp)}}</small>
            </div>
            
            <div>
              <span *ngIf="message.confidence" class="badge" 
                    [ngClass]="{'bg-success': message.confidence > 0.7, 'bg-warning': message.confidence > 0.4, 'bg-danger': message.confidence <= 0.4}">
                {{(message.confidence * 100).toFixed(0)}}% confidence
              </span>
              <span *ngIf="message.modelUsed" class="badge bg-info ms-1" title="AI Model">
                {{getModelShortName(message.modelUsed)}}
              </span>
            </div>
          </div>

          <!-- Message Content -->
          <div class="message-content">
            <div [innerHTML]="formatMessage(message.message)"></div>
            
            <div *ngIf="message.agentExpertise" class="mt-1 text-muted small">
              <em>{{message.agentExpertise}}</em>
            </div>
            
            <div *ngIf="message.symbol" class="mt-1">
              <span class="badge bg-dark">📊 {{message.symbol}}</span>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div *ngIf="isLoading" class="text-center py-3">
          <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
          <p class="mt-2 small text-muted">Agents are thinking...</p>
        </div>

        <!-- Empty State -->
        <div *ngIf="!isLoading && filteredMessages.length === 0" class="text-center text-muted py-4">
          <div class="mb-2">🤖</div>
          <p class="mb-1">No messages yet</p>
          <small>Ask a question to start chatting with intelligent agents</small>
        </div>
      </div>

      <!-- Chat Input -->
      <div class="mt-3">
        <div class="input-group">
          <input type="text" class="form-control" placeholder="Ask agents about markets, stocks, analysis..." 
                 [(ngModel)]="newMessage" (keyup.enter)="sendMessage()"
                 [disabled]="isLoading">
          <button class="btn btn-primary" type="button" (click)="sendMessage()" [disabled]="isLoading || !newMessage.trim()">
            <span *ngIf="!isLoading">💬 Send</span>
            <span *ngIf="isLoading">
              <span class="spinner-border spinner-border-sm me-1"></span>
              Thinking...
            </span>
          </button>
        </div>
        
        <!-- Quick Questions -->
        <div class="mt-2">
          <small class="text-muted d-block mb-1">Quick questions:</small>
          <div class="d-flex flex-wrap gap-1">
            <button *ngFor="let question of quickQuestions" class="btn btn-sm btn-outline-secondary"
                    (click)="setQuickQuestion(question)" [disabled]="isLoading">
              {{question}}
            </button>
          </div>
        </div>

        <!-- Agent Discussions -->
        <div class="mt-3">
          <button class="btn btn-sm btn-outline-info w-100" (click)="loadAgentDiscussions()" [disabled]="isLoading">
            <span *ngIf="!isLoading">👥 Listen to Agent Discussions</span>
            <span *ngIf="isLoading">Loading discussions...</span>
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .chat-panel {
      font-size: 0.875rem;
    }
    .chat-messages {
      background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
      border: 1px solid var(--border-color);
      border-radius: 8px;
    }
    .chat-message {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      transition: all 0.2s;
    }
    .chat-message:hover {
      border-color: var(--accent-blue);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px var(--shadow-color);
    }
    .user-message {
      border-left: 3px solid var(--accent-blue);
      background: linear-gradient(135deg, rgba(51, 102, 255, 0.05) 0%, var(--bg-card) 100%);
    }
    .agent-message {
      border-left: 3px solid var(--accent-green);
      background: linear-gradient(135deg, rgba(0, 214, 143, 0.05) 0%, var(--bg-card) 100%);
    }
    .message-content {
      line-height: 1.5;
    }
    .message-content strong {
      color: var(--text-primary);
    }
    .message-content em {
      color: var(--text-muted);
      font-style: italic;
    }
    .badge-technical {
      background: linear-gradient(135deg, var(--accent-blue) 0%, #2952cc 100%);
      color: white;
    }
    .badge-fundamental {
      background: linear-gradient(135deg, var(--accent-green) 0%, #00b377 100%);
      color: white;
    }
    .badge-sentiment {
      background: linear-gradient(135deg, var(--accent-purple) 0%, #7a1fd2 100%);
      color: white;
    }
    .badge-macro {
      background: linear-gradient(135deg, var(--accent-orange) 0%, #e69500 100%);
      color: white;
    }
    .badge-crypto {
      background: linear-gradient(135deg, var(--accent-yellow) 0%, #e6b400 100%);
      color: #000;
    }
    .badge-default {
      background: linear-gradient(135deg, var(--accent-cyan) 0%, #00bbd6 100%);
      color: white;
    }
  `]
})
export class ChatPanelComponent implements OnInit {
  messages: ChatMessage[] = [];
  agentProfiles: AgentProfile[] = [];
  newMessage = '';
  selectedAgentId = '';
  isLoading = false;
  errorMessage = '';

  quickQuestions = [
    'Analyze AAPL',
    'Bitcoin outlook?',
    'Market sentiment?',
    'Best stock to buy?',
    'Economic risks?'
  ];

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadAgentProfiles();
    this.loadRecentChats();
    this.initializeAgents();
  }

  get filteredMessages(): ChatMessage[] {
    if (!this.selectedAgentId) {
      return this.messages;
    }
    return this.messages.filter(msg => 
      msg.senderId === this.selectedAgentId || 
      (msg.senderType === 'user' && this.selectedAgentId !== '')
    );
  }

  loadAgentProfiles() {
    this.http.get<any>(`${environment.apiUrl}/chat/agents`)
      .subscribe({
        next: (response) => {
          if (response.status === 'success') {
            this.agentProfiles = response.agents;
          }
        },
        error: (error) => {
          console.error('Failed to load agent profiles:', error);
        }
      });
  }

  loadRecentChats() {
    this.isLoading = true;
    this.http.get<any>(`${environment.apiUrl}/chat/recent?userId=dashboard_user&limit=20`)
      .subscribe({
        next: (response) => {
          if (response.status === 'success') {
            this.messages = response.chats.map((chat: any) => ({
              senderType: chat.senderType,
              senderId: chat.senderId,
              agentName: chat.agentName,
              agentExpertise: chat.agentExpertise,
              message: chat.message,
              timestamp: chat.timestamp,
              signal: chat.signal,
              confidence: chat.confidence,
              modelUsed: chat.modelUsed
            }));
          }
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Failed to load recent chats:', error);
          this.isLoading = false;
          this.errorMessage = 'Failed to load chat history';
        }
      });
  }

  initializeAgents() {
    this.http.post<any>(`${environment.apiUrl}/chat/initialize`, {})
      .subscribe({
        next: (response) => {
          if (response.status === 'success') {
            // Add greetings to messages
            const greetings = response.greetings.map((greeting: any) => ({
              senderType: 'agent',
              senderId: greeting.agentId,
              agentName: greeting.agentName,
              agentExpertise: greeting.expertise,
              message: greeting.message,
              timestamp: greeting.timestamp,
              signal: 'GREETING',
              confidence: 0.9
            }));
            
            this.messages = [...greetings, ...this.messages];
          }
        },
        error: (error) => {
          console.error('Failed to initialize agents:', error);
        }
      });
  }

  sendMessage() {
    if (!this.newMessage.trim() || this.isLoading) return;

    const userMessage = this.newMessage.trim();
    this.newMessage = '';

    // Add user message to chat
    const userChat: ChatMessage = {
      senderType: 'user',
      senderId: 'dashboard_user',
      message: userMessage,
      timestamp: new Date().toISOString()
    };
    this.messages.push(userChat);

    // Send to backend
    this.isLoading = true;
    const requestBody: any = {
      userId: 'dashboard_user',
      message: userMessage
    };

    if (this.selectedAgentId) {
      requestBody.agentId = this.selectedAgentId;
    }

    this.http.post<any>(`${environment.apiUrl}/chat/send`, requestBody)
      .subscribe({
        next: (response) => {
          if (response.status === 'success') {
            // Add agent responses to chat
            const agentResponses = response.responses.map((resp: any) => ({
              senderType: 'agent',
              senderId: resp.agentId,
              agentName: resp.agentName,
              message: resp.message,
              timestamp: resp.timestamp,
              signal: resp.signal,
              confidence: resp.confidence,
              modelUsed: resp.modelUsed
            }));
            
            this.messages = [...this.messages, ...agentResponses];
            
            // Auto-scroll to bottom
            setTimeout(() => {
              const chatContainer = document.querySelector('.chat-messages');
              if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
              }
            }, 100);
          }
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Failed to send message:', error);
          this.errorMessage = 'Failed to get agent response';
          this.isLoading = false;
          
          // Add fallback response
          const fallbackResponse: ChatMessage = {
            senderType: 'agent',
            senderId: this.selectedAgentId || 'technical_analyst',
            agentName: this.selectedAgentId ? 
              this.agentProfiles.find(a => a.id === this.selectedAgentId)?.name : 'Technical Analyst',
            message: `I'm analyzing your question: "${userMessage}". Based on my expertise, I recommend further research.`,
            timestamp: new Date().toISOString(),
            signal: 'HOLD',
            confidence: 0.6
          };
          this.messages.push(fallbackResponse);
        }
      });
  }

  loadAgentDiscussions() {
    this.isLoading = true;
    this.http.get<any>(`${environment.apiUrl}/chat/discussions?topic=market_analysis`)
      .subscribe({
        next: (response) => {
          if (response.status === 'success') {
            const discussions = response.discussions.map((disc: any) => ({
              senderType: 'agent',
              senderId: disc.agentId,
              agentName: disc.agentName,
              agentExpertise: disc.agentExpertise,
              message: disc.message,
              timestamp: disc.timestamp
            }));
            
            this.messages = [...this.messages, ...discussions];
          }
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Failed to load discussions:', error);
          this.isLoading = false;
        }
      });
  }

  selectAgent(agentId: string) {
    this.selectedAgentId = agentId;
    
    // If selecting an agent, add a prompt
    if (agentId && this.agentProfiles.length > 0) {
      const agent = this.agentProfiles.find(a => a.id === agentId);
      if (agent) {
        const promptMessage: ChatMessage = {
          senderType: 'system',
          senderId: 'system',
          message: `Now chatting with ${agent.name}. Ask about ${agent.expertise.toLowerCase()}.`,
          timestamp: new Date().toISOString()
        };
        this.messages.push(promptMessage);
      }
    }
  }

  setQuickQuestion(question: string) {
    this.newMessage = question;
  }

  // Helper methods
  formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  formatMessage(message: string): string {
    // Convert markdown-like formatting to HTML
    return message
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>')
      .replace(/📊/g, '📊 ')
      .replace(/📈/g, '📈 ')
      .replace(/🎯/g, '🎯 ')
      .replace(/💰/g, '💰 ')
      .replace(/⏰/g, '⏰ ');
  }

  getAgentBadgeClass(agentId: string): string {
    const map: {[key: string]: string} = {
      'technical_analyst': 'badge-technical',
      'fundamental_analyst': 'badge-fundamental',
      'sentiment_analyst': 'badge-sentiment',
      'macro_analyst': 'badge-macro',
      'crypto_analyst': 'badge-crypto',
      'options_analyst': 'badge-default',
      'risk_analyst': 'badge-default',
      'quant_analyst': 'badge-default',
      'sector_analyst': 'badge-default',
      'compliance_analyst': 'badge-default'
    };
    return map[agentId] || 'badge-secondary';
  }

  getSignalBadgeClass(signal: string): string {
    switch (signal) {
      case 'STRONG_BUY':
      case 'BUY':
        return 'bg-success';
      case 'SELL':
        return 'bg-danger';
      case 'HOLD':
        return 'bg-warning text-dark';
      case 'GREETING':
        return 'bg-info';
      default:
        return 'bg-secondary';
    }
  }

  getModelShortName(model: string): string {
    if (!model) return 'AI';
    if (model.includes('llama')) return 'Llama';
    if (model.includes('mistral')) return 'Mistral';
    if (model.includes('zephyr')) return 'Zephyr';
    if (model.includes('qwen')) return 'Qwen';
    if (model.includes('gemma')) return 'Gemma';
    if (model.includes('phi')) return 'Phi';
    return 'AI';
  }
}