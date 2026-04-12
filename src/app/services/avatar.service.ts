import { Injectable } from '@angular/core';

export interface AgentAvatar {
  id: string;
  name: string;
  role: string;
  avatarUrl: string;
  color: string;
  emoji: string;
  description: string;
}

@Injectable({
  providedIn: 'root'
})
export class AvatarService {
  private agentAvatars: AgentAvatar[] = [
    {
      id: 'technical-analyst',
      name: 'Alex Chen',
      role: 'Technical Analyst',
      avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=technical&backgroundColor=4f46e5',
      color: '#4f46e5',
      emoji: '📈',
      description: 'Charts, patterns, RSI, MACD expert'
    },
    {
      id: 'fundamental-analyst',
      name: 'Dr. Sarah Johnson',
      role: 'Fundamental Analyst',
      avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=fundamental&backgroundColor=10b981',
      color: '#10b981',
      emoji: '📊',
      description: 'P/E ratios, margins, valuation specialist'
    },
    {
      id: 'sentiment-analyst',
      name: 'Marcus Lee',
      role: 'Sentiment Analyst',
      avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=sentiment&backgroundColor=f59e0b',
      color: '#f59e0b',
      emoji: '😊',
      description: 'News sentiment, social media trends'
    },
    {
      id: 'macro-analyst',
      name: 'James Wilson',
      role: 'Macro Analyst',
      avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=macro&backgroundColor=8b5cf6',
      color: '#8b5cf6',
      emoji: '🌍',
      description: 'Economic indicators, interest rates, geopolitics'
    },
    {
      id: 'crypto-analyst',
      name: 'Crypto Max',
      role: 'Crypto Analyst',
      avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=crypto&backgroundColor=6366f1',
      color: '#6366f1',
      emoji: '₿',
      description: 'Blockchain, DeFi, crypto markets'
    },
    {
      id: 'options-analyst',
      name: 'Options Olivia',
      role: 'Options Analyst',
      avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=options&backgroundColor=ec4899',
      color: '#ec4899',
      emoji: '📉',
      description: 'Options chains, volatility, Greeks'
    },
    {
      id: 'risk-analyst',
      name: 'Risk Rachel',
      role: 'Risk Analyst',
      avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=risk&backgroundColor=ef4444',
      color: '#ef4444',
      emoji: '⚠️',
      description: 'Risk assessment, position sizing, stop-loss'
    },
    {
      id: 'quant-analyst',
      name: 'Quant Quinn',
      role: 'Quant Analyst',
      avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=quant&backgroundColor=3b82f6',
      color: '#3b82f6',
      emoji: '🧮',
      description: 'Algorithmic models, statistical analysis'
    },
    {
      id: 'sector-analyst',
      name: 'Sector Sam',
      role: 'Sector Analyst',
      avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=sector&backgroundColor=14b8a6',
      color: '#14b8a6',
      emoji: '🏢',
      description: 'Industry trends, sector rotation'
    },
    {
      id: 'compliance-analyst',
      name: 'Compliance Chris',
      role: 'Compliance Analyst',
      avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=compliance&backgroundColor=6b7280',
      color: '#6b7280',
      emoji: '⚖️',
      description: 'Regulatory compliance, trading rules'
    }
  ];

  getAgentAvatar(agentId: string): AgentAvatar {
    const avatar = this.agentAvatars.find(a => a.id === agentId);
    if (avatar) {
      return avatar;
    }
    
    // Default avatar for unknown agents
    return {
      id: agentId,
      name: this.formatAgentName(agentId),
      role: this.formatAgentRole(agentId),
      avatarUrl: `https://api.dicebear.com/7.x/avataaars/svg?seed=${agentId}&backgroundColor=6b7280`,
      color: '#6b7280',
      emoji: '🤖',
      description: 'AI Trading Agent'
    };
  }

  getAllAvatars(): AgentAvatar[] {
    return this.agentAvatars;
  }

  private formatAgentName(agentId: string): string {
    return agentId
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  private formatAgentRole(agentId: string): string {
    const name = this.formatAgentName(agentId);
    return name + ' Analyst';
  }

  getStatusColor(status: string): string {
    switch(status?.toLowerCase()) {
      case 'active': return '#10b981';
      case 'inactive': return '#ef4444';
      case 'processing': return '#f59e0b';
      case 'error': return '#dc2626';
      default: return '#6b7280';
    }
  }

  getStatusEmoji(status: string): string {
    switch(status?.toLowerCase()) {
      case 'active': return '✅';
      case 'inactive': return '⏸️';
      case 'processing': return '🔄';
      case 'error': return '❌';
      default: return '❓';
    }
  }
}