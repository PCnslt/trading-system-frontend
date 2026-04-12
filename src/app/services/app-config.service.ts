import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AppConfigService {
  private config = {
    apiUrl: 'http://localhost:8082/api',
    wsUrl: 'http://localhost:8082/ws-monitoring',
    production: false
  };

  get apiUrl(): string {
    return this.config.apiUrl;
  }

  get wsUrl(): string {
    return this.config.wsUrl;
  }

  get production(): boolean {
    return this.config.production;
  }

  get environment() {
    return this.config;
  }
}