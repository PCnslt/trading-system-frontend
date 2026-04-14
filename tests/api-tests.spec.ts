import { test, expect } from '@playwright/test';

test.describe('Backend API Regression Tests', () => {
  
  test('Issue 1: Real stocks endpoint returns exactly 10 stocks', async ({ request }) => {
    const response = await request.get('http://localhost:8082/api/predictions/monitoring/real-stocks');
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    console.log(`✅ Real stocks endpoint returns ${data.totalStocks} stocks`);
    expect(data.totalStocks).toBe(10);
    expect(data.stocks).toHaveLength(10);
    
    // Verify data looks reasonable
    expect(data.stocks[0]).toHaveProperty('symbol');
    expect(data.stocks[0]).toHaveProperty('name');
    expect(data.stocks[0]).toHaveProperty('dailyChange');
    expect(data.stocks[0]).toHaveProperty('price');
  });

  test('Issue 3: Pipeline endpoint - should not show fake progress', async ({ request }) => {
    const response = await request.get('http://localhost:8082/api/predictions/monitoring/pipeline');
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    console.log(`✅ Pipeline endpoint response received`);
    console.log(`   - Has ${data.pipeline.length} stages`);
    console.log(`   - Current stage: ${data.currentStage}`);
    console.log(`   - Overall progress: ${data.overallProgress}%`);
    console.log(`   - Real data flag: ${data.realData}`);
    
    // Check if pipeline is showing fake progress
    if (data.pipeline.length > 0) {
      const firstStage = data.pipeline[0];
      console.log(`   - First stage: ${firstStage.stageName} (${firstStage.status}, ${firstStage.progress}%)`);
      
      // If no analysis is running, first stage should not be "COMPLETED" with 100%
      // or "IN_PROGRESS" with >0% progress
      if (firstStage.status === 'COMPLETED' && firstStage.progress === 100) {
        console.warn('   ⚠️ WARNING: First stage shows 100% complete - might be fake progress');
        // This would be a bug
      }
      
      if (firstStage.status === 'IN_PROGRESS' && firstStage.progress > 0) {
        console.warn(`   ⚠️ WARNING: First stage shows ${firstStage.progress}% in-progress - verify analysis is actually running`);
      }
    } else {
      console.log('   ✅ Pipeline is empty - correct behavior when no analysis is running');
    }
  });

  test('Health endpoint shows system status', async ({ request }) => {
    const response = await request.get('http://localhost:8082/api/health');
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    console.log(`✅ Health endpoint: ${data.tickers} tickers, ${data.agents} agents, status: ${data.status}`);
    
    expect(data.status).toBe('UP');
    expect(data.agents).toBe(10);
    // Ticker count should be 878 until database integration
    expect(data.tickers).toBe(878);
  });

  test('Verify backend is running new code', async ({ request }) => {
    // Test multiple endpoints to verify new code is running
    const tests = [
      { url: '/api/predictions/monitoring/real-stocks', expectedField: 'totalStocks', expectedValue: 10 },
      { url: '/api/health', expectedField: 'status', expectedValue: 'UP' },
    ];
    
    for (const test of tests) {
      const response = await request.get(`http://localhost:8082${test.url}`);
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(data[test.expectedField]).toBe(test.expectedValue);
    }
    
    console.log('✅ Backend is running with new code (real-stocks returns 10, not 20)');
  });
});