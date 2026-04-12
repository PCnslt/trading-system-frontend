import { Injectable } from '@angular/core';

export interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'INFO' | 'WARN' | 'ERROR' | 'DEBUG' | 'SUCCESS';
  component: string;
  message: string;
  data?: any;
  agentId?: string;
  userId?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ActivityLoggerService {
  private logs: LogEntry[] = [];
  private maxLogs = 1000;
  private listeners: ((entry: LogEntry) => void)[] = [];

  constructor() {
    // Log service initialization
    this.info('ActivityLoggerService', 'Logger service initialized');
  }

  private generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  private addLog(entry: LogEntry) {
    this.logs.unshift(entry); // Add to beginning for reverse chronological order
    
    // Keep only maxLogs entries
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(0, this.maxLogs);
    }
    
    // Notify listeners
    this.listeners.forEach(listener => listener(entry));
    
    // Also log to console in development
    if (!environment.production) {
      const consoleMethod = entry.level === 'ERROR' ? 'error' : 
                           entry.level === 'WARN' ? 'warn' : 
                           entry.level === 'DEBUG' ? 'debug' : 'log';
      console[consoleMethod](`[${entry.component}] ${entry.message}`, entry.data || '');
    }
  }

  info(component: string, message: string, data?: any, agentId?: string) {
    const entry: LogEntry = {
      id: this.generateId(),
      timestamp: new Date(),
      level: 'INFO',
      component,
      message,
      data,
      agentId
    };
    this.addLog(entry);
  }

  success(component: string, message: string, data?: any, agentId?: string) {
    const entry: LogEntry = {
      id: this.generateId(),
      timestamp: new Date(),
      level: 'SUCCESS',
      component,
      message,
      data,
      agentId
    };
    this.addLog(entry);
  }

  warn(component: string, message: string, data?: any, agentId?: string) {
    const entry: LogEntry = {
      id: this.generateId(),
      timestamp: new Date(),
      level: 'WARN',
      component,
      message,
      data,
      agentId
    };
    this.addLog(entry);
  }

  error(component: string, message: string, data?: any, agentId?: string) {
    const entry: LogEntry = {
      id: this.generateId(),
      timestamp: new Date(),
      level: 'ERROR',
      component,
      message,
      data,
      agentId
    };
    this.addLog(entry);
  }

  debug(component: string, message: string, data?: any, agentId?: string) {
    const entry: LogEntry = {
      id: this.generateId(),
      timestamp: new Date(),
      level: 'DEBUG',
      component,
      message,
      data,
      agentId
    };
    this.addLog(entry);
  }

  // Agent-specific logging
  agentActivity(agentId: string, action: string, data?: any) {
    this.info(`Agent:${agentId}`, action, data, agentId);
  }

  agentError(agentId: string, error: string, data?: any) {
    this.error(`Agent:${agentId}`, error, data, agentId);
  }

  agentSuccess(agentId: string, action: string, data?: any) {
    this.success(`Agent:${agentId}`, action, data, agentId);
  }

  // UI interactions
  uiInteraction(component: string, action: string, data?: any) {
    this.debug(`UI:${component}`, action, data);
  }

  // Backend API calls
  apiCall(method: string, endpoint: string, status: number, duration?: number) {
    const level = status >= 400 ? 'ERROR' : status >= 300 ? 'WARN' : 'SUCCESS';
    const message = `${method} ${endpoint} - ${status}${duration ? ` (${duration}ms)` : ''}`;
    
    const entry: LogEntry = {
      id: this.generateId(),
      timestamp: new Date(),
      level,
      component: 'API',
      message,
      data: { method, endpoint, status, duration }
    };
    this.addLog(entry);
  }

  // Get logs
  getLogs(limit?: number): LogEntry[] {
    return limit ? this.logs.slice(0, limit) : [...this.logs];
  }

  getLogsByComponent(component: string): LogEntry[] {
    return this.logs.filter(log => log.component.includes(component));
  }

  getLogsByAgent(agentId: string): LogEntry[] {
    return this.logs.filter(log => log.agentId === agentId);
  }

  getLogsByLevel(level: LogEntry['level']): LogEntry[] {
    return this.logs.filter(log => log.level === level);
  }

  // Clear logs
  clearLogs() {
    this.logs = [];
    this.info('ActivityLoggerService', 'Logs cleared');
  }

  // Subscribe to new logs
  subscribe(listener: (entry: LogEntry) => void) {
    this.listeners.push(listener);
    return () => {
      const index = this.listeners.indexOf(listener);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  // Get statistics
  getStats() {
    const total = this.logs.length;
    const byLevel = this.logs.reduce((acc, log) => {
      acc[log.level] = (acc[log.level] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    const byComponent = this.logs.reduce((acc, log) => {
      const key = log.component.split(':')[0]; // Get main component
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    return {
      total,
      byLevel,
      byComponent,
      oldest: this.logs[this.logs.length - 1]?.timestamp,
      newest: this.logs[0]?.timestamp
    };
  }
}

// Import environment for production check
import { environment } from '../../environments/index';