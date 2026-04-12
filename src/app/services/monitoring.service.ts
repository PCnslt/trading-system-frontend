import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, Subject, BehaviorSubject } from 'rxjs';
import { Client, IMessage } from '@stomp/stompjs';
import * as SockJS from 'sockjs-client';
import { environment } from '../../environments/index';

export interface AgentActivity {
  id: number;
  agentId: string;
  timestamp: string;
  task: string;
  activityType: string;
  inputData: string;
  outputData: string;
  reasoning: string;
  status: string;
  durationMs: number;
  symbol: string;
}

export interface ChatMessage {
  id: number;
  sender: string;
  receiver: string;
  timestamp: string;
  message: string;
  context: string;
  messageType: string;
  confidence: number;
  symbol: string;
}

export interface ConsensusVote {
  id: number;
  timestamp: string;
  symbol: string;
  agentsInFavor: string;
  agentsAgainst: string;
  confidence: number;
  finalDecision: string;
  totalAgents: number;
  agentsVoted: number;
  reasoning: string;
  priceAtDecision: number;
}

export interface TradeRecommendation {
  id: number;
  timestamp: string;
  symbol: string;
  entryRange: string;
  target: string;
  stopLoss: string;
  positionSize: number;
  confidence: number;
  rationale: string;
  recommendedBy: string;
  status: string;
  currentPrice: number;
  potentialPnl: number;
  riskRewardRatio: number;
}

export interface PriceHistoryData {
  symbol: string;
  period: string;
  source: string;
  labels: string[];
  prices: number[];
  volumes: number[];
  indicators: {
    rsi: number[];
    macdLine: number[];
    macdSignal: number[];
    macdHistogram: number[];
  };
  timestamp: string;
  data_points: number;
}

export interface AgentStatus {
  lastActivity: string;
  lastActivityTime: string;
  lastStatus: string;
  successCount: number;
  errorCount: number;
  successRate: number;
  isActive: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class MonitoringService {
  private baseUrl = environment.apiUrl;
  private stompClient!: Client;
  
  private agentActivitySubject = new Subject<AgentActivity>();
  private chatMessageSubject = new Subject<ChatMessage>();
  private consensusVoteSubject = new Subject<ConsensusVote>();
  private tradeRecommendationSubject = new Subject<TradeRecommendation>();
  private connectionStatusSubject = new BehaviorSubject<boolean>(false);
  
  agentActivity$ = this.agentActivitySubject.asObservable();
  chatMessage$ = this.chatMessageSubject.asObservable();
  consensusVote$ = this.consensusVoteSubject.asObservable();
  tradeRecommendation$ = this.tradeRecommendationSubject.asObservable();
  connectionStatus$ = this.connectionStatusSubject.asObservable();

  constructor(private http: HttpClient) {
    this.initWebSocket();
  }

  private initWebSocket() {
    console.log('Initializing WebSocket connection to:', environment.wsUrl);
    try {
      const socket = new SockJS(environment.wsUrl);
      console.log('SockJS socket created');
      
      this.stompClient = new Client({
        webSocketFactory: () => socket,
        debug: (str: string) => console.log('STOMP: ' + str),
        reconnectDelay: 5000,
        heartbeatIncoming: 4000,
        heartbeatOutgoing: 4000
      });

      this.stompClient.onConnect = (frame: any) => {
        console.log('WebSocket connected successfully:', frame);
        this.connectionStatusSubject.next(true);
        
        this.stompClient.subscribe('/topic/agent-activities', (message: IMessage) => {
          console.log('Received agent activity:', message.body);
          const activity = JSON.parse(message.body).activity;
          this.agentActivitySubject.next(activity);
        });
        
        this.stompClient.subscribe('/topic/chat', (message: IMessage) => {
          const chatMsg = JSON.parse(message.body).message;
          this.chatMessageSubject.next(chatMsg);
        });
        
        this.stompClient.subscribe('/topic/consensus', (message: IMessage) => {
          const vote = JSON.parse(message.body).vote;
          this.consensusVoteSubject.next(vote);
        });
        
        this.stompClient.subscribe('/topic/trade-recommendations', (message: IMessage) => {
          const recommendation = JSON.parse(message.body).recommendation;
          this.tradeRecommendationSubject.next(recommendation);
        });
      };

      this.stompClient.onStompError = (frame: any) => {
        console.error('STOMP error:', frame.headers['message'], frame.body);
      };

      this.stompClient.onWebSocketError = (event: any) => {
        console.error('WebSocket error:', event);
      };

      this.stompClient.onDisconnect = () => {
        console.log('WebSocket disconnected');
        this.connectionStatusSubject.next(false);
      };

      this.stompClient.activate();
      console.log('STOMP client activation requested');
    } catch (error) {
      console.error('Failed to initialize WebSocket:', error);
    }
  }

  // Agent Activities
  getAgentActivities(params?: any): Observable<AgentActivity[]> {
    console.log('MonitoringService: Fetching agent activities from', `${this.baseUrl}/agent-activities`);
    return this.http.get<AgentActivity[]>(`${this.baseUrl}/agent-activities`, { params });
  }

  createAgentActivity(activity: Partial<AgentActivity>): Observable<any> {
    return this.http.post(`${this.baseUrl}/agent-activities`, activity);
  }

  // Chat Messages
  getChatMessages(params?: any): Observable<ChatMessage[]> {
    return this.http.get<ChatMessage[]>(`${this.baseUrl}/chat`, { params });
  }

  createChatMessage(message: Partial<ChatMessage>): Observable<any> {
    return this.http.post(`${this.baseUrl}/chat`, message);
  }

  // Consensus Votes
  getConsensusVotes(params?: any): Observable<ConsensusVote[]> {
    return this.http.get<ConsensusVote[]>(`${this.baseUrl}/consensus`, { params });
  }

  getLatestConsensus(symbol?: string): Observable<any> {
    let params = new HttpParams();
    if (symbol) {
      params = params.set('symbol', symbol);
    }
    return this.http.get(`${this.baseUrl}/consensus/latest`, { params });
  }

  // Trade Recommendations
  getTradeRecommendations(params?: any): Observable<TradeRecommendation[]> {
    return this.http.get<TradeRecommendation[]>(`${this.baseUrl}/trade-recommendations`, { params });
  }

  getActiveRecommendations(): Observable<TradeRecommendation[]> {
    return this.http.get<TradeRecommendation[]>(`${this.baseUrl}/trade-recommendations/active`);
  }

  // Monitoring Stats
  getMonitoringStats(): Observable<any> {
    return this.http.get(`${this.baseUrl}/monitoring/stats`);
  }

  getAgentsStatus(): Observable<Record<string, AgentStatus>> {
    return this.http.get<Record<string, AgentStatus>>(`${this.baseUrl}/monitoring/agents/status`);
  }

  getHealth(): Observable<any> {
    return this.http.get(`${this.baseUrl}/monitoring/health`);
  }

  getPriceHistory(symbol: string, period: string = '30 days'): Observable<PriceHistoryData> {
    return this.http.get<PriceHistoryData>(`${this.baseUrl}/monitoring/price-history/${symbol}`, {
      params: { period }
    });
  }
}