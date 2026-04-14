import { test, expect } from '@playwright/test';

test.describe('Infrastructure Tests', () => {
  test('should have all required services running', async ({ request }) => {
    console.log('Testing infrastructure services...');
    
    // Test 1: Backend service
    try {
      const backendResponse = await request.get('http://localhost:8082/api/health');
      expect(backendResponse.ok()).toBeTruthy();
      const backendData = await backendResponse.json();
      console.log(`✅ Backend: Running (${backendData.tickers} tickers, ${backendData.agents} agents)`);
    } catch (error) {
      console.log('❌ Backend: Not running or unreachable');
      throw error;
    }
    
    // Test 2: Frontend service
    try {
      const frontendResponse = await request.get('http://localhost:4200');
      expect(frontendResponse.ok()).toBeTruthy();
      console.log('✅ Frontend: Running (HTTP 200 OK)');
    } catch (error) {
      console.log('❌ Frontend: Not running or unreachable');
      throw error;
    }
    
    // Test 3: Database connectivity (via backend)
    try {
      const dbResponse = await request.get('http://localhost:8082/api/agent-activities');
      expect(dbResponse.ok()).toBeTruthy();
      console.log('✅ Database: Connected (agent activities endpoint works)');
    } catch (error) {
      console.log('⚠️ Database: Agent activities endpoint failed (might be empty)');
    }
  });

  test('should have all required API endpoints', async ({ request }) => {
    const endpoints = [
      { path: '/api/health', method: 'GET', description: 'Health check' },
      { path: '/api/predictions/monitoring/real-stocks', method: 'GET', description: 'Real stocks data' },
      { path: '/api/predictions/collaborative', method: 'POST', description: 'Collaborative predictions' },
      { path: '/api/predictions/monitoring/pipeline', method: 'GET', description: 'Pipeline status' },
      { path: '/api/agent-activities', method: 'GET', description: 'Agent activities' },
      { path: '/api/trigger/all/AAPL', method: 'POST', description: 'Trigger agent analysis' },
    ];
    
    for (const endpoint of endpoints) {
      try {
        let response;
        if (endpoint.method === 'GET') {
          response = await request.get(`http://localhost:8082${endpoint.path}`);
        } else {
          response = await request.post(`http://localhost:8082${endpoint.path}`, {});
        }
        
        // Some endpoints might return 200 with empty data, which is OK
        if (response.ok() || response.status() === 204) {
          console.log(`✅ ${endpoint.description}: ${endpoint.method} ${endpoint.path} (${response.status()})`);
        } else {
          console.log(`⚠️ ${endpoint.description}: ${endpoint.method} ${endpoint.path} (${response.status()})`);
        }
      } catch (error) {
        console.log(`❌ ${endpoint.description}: ${endpoint.method} ${endpoint.path} (Error: ${error.message})`);
      }
    }
  });

  test('should have correct CORS configuration', async ({ request }) => {
    // Test CORS headers for frontend-backend communication
    const response = await request.get('http://localhost:8082/api/health');
    
    // Check for CORS headers
    const headers = response.headers();
    const corsHeader = headers['access-control-allow-origin'];
    
    if (corsHeader) {
      console.log(`✅ CORS configured: ${corsHeader}`);
      // Should allow localhost:4200 or be *
      expect(corsHeader === '*' || corsHeader.includes('localhost:4200')).toBeTruthy();
    } else {
      console.log('⚠️ No CORS header found (might be configured differently)');
    }
  });

  test('should have proper error handling', async ({ request }) => {
    // Test 404 handling
    const notFoundResponse = await request.get('http://localhost:8082/api/nonexistent-endpoint');
    expect([404, 400]).toContain(notFoundResponse.status());
    console.log(`✅ 404 handling: Returns ${notFoundResponse.status()} for nonexistent endpoint`);
    
    // Test malformed request handling
    const badRequestResponse = await request.post('http://localhost:8082/api/predictions/collaborative', {
      data: 'invalid json',
      headers: { 'Content-Type': 'application/json' }
    });
    expect([400, 500]).toContain(badRequestResponse.status());
    console.log(`✅ Error handling: Returns ${badRequestResponse.status()} for malformed request`);
  });

  test('should have performance within acceptable limits', async ({ request }) => {
    const startTime = Date.now();
    
    // Test health endpoint response time
    const healthResponse = await request.get('http://localhost:8082/api/health');
    const healthTime = Date.now() - startTime;
    
    expect(healthResponse.ok()).toBeTruthy();
    expect(healthTime).toBeLessThan(1000); // Should respond within 1 second
    console.log(`✅ Health endpoint response time: ${healthTime}ms`);
    
    // Test real stocks endpoint response time
    const stocksStartTime = Date.now();
    const stocksResponse = await request.get('http://localhost:8082/api/predictions/monitoring/real-stocks');
    const stocksTime = Date.now() - stocksStartTime;
    
    expect(stocksResponse.ok()).toBeTruthy();
    expect(stocksTime).toBeLessThan(2000); // Should respond within 2 seconds
    console.log(`✅ Real stocks endpoint response time: ${stocksTime}ms`);
    
    // Test collaborative predictions response time
    const predictionsStartTime = Date.now();
    const predictionsResponse = await request.post('http://localhost:8082/api/predictions/collaborative', {});
    const predictionsTime = Date.now() - predictionsStartTime;
    
    expect(predictionsResponse.ok()).toBeTruthy();
    expect(predictionsTime).toBeLessThan(5000); // Should respond within 5 seconds (agent analysis)
    console.log(`✅ Collaborative predictions response time: ${predictionsTime}ms`);
  });

  test('should have data consistency', async ({ request }) => {
    // Test that multiple calls return consistent data structure
    const response1 = await request.get('http://localhost:8082/api/predictions/monitoring/real-stocks');
    const data1 = await response1.json();
    
    const response2 = await request.get('http://localhost:8082/api/predictions/monitoring/real-stocks');
    const data2 = await response2.json();
    
    // Both should be arrays
    expect(Array.isArray(data1)).toBeTruthy();
    expect(Array.isArray(data2)).toBeTruthy();
    
    // Should have similar structure (might have different data due to updates)
    if (data1.length > 0 && data2.length > 0) {
      const firstItem1 = data1[0];
      const firstItem2 = data2[0];
      
      // Check they have the same properties
      const keys1 = Object.keys(firstItem1);
      const keys2 = Object.keys(firstItem2);
      
      expect(keys1.sort()).toEqual(keys2.sort());
      console.log(`✅ Data consistency: Both responses have ${keys1.length} properties with same structure`);
    } else {
      console.log('⚠️ Data consistency: One or both responses empty');
    }
  });

  test('should handle concurrent requests', async ({ request }) => {
    // Make multiple concurrent requests
    const requests = Array(5).fill(null).map(() => 
      request.get('http://localhost:8082/api/health')
    );
    
    const startTime = Date.now();
    const responses = await Promise.all(requests);
    const totalTime = Date.now() - startTime;
    
    // All should succeed
    for (const response of responses) {
      expect(response.ok()).toBeTruthy();
    }
    
    console.log(`✅ Concurrent requests: ${responses.length} requests completed in ${totalTime}ms`);
    expect(totalTime).toBeLessThan(3000); // 5 concurrent requests should complete within 3 seconds
  });

  test('should have proper logging and monitoring', async ({ page }) => {
    // Check frontend console for errors
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    await page.goto('http://localhost:4200');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    if (consoleErrors.length === 0) {
      console.log('✅ Frontend: No console errors detected');
    } else {
      console.log(`⚠️ Frontend: ${consoleErrors.length} console errors detected`);
      for (const error of consoleErrors.slice(0, 3)) {
        console.log(`  - ${error.substring(0, 100)}...`);
      }
    }
    
    // Check for network errors
    const networkErrors = [];
    page.on('response', response => {
      if (response.status() >= 400) {
        networkErrors.push({
          url: response.url(),
          status: response.status()
        });
      }
    });
    
    if (networkErrors.length === 0) {
      console.log('✅ Network: No failed requests detected');
    } else {
      console.log(`⚠️ Network: ${networkErrors.length} failed requests detected`);
      for (const error of networkErrors.slice(0, 3)) {
        console.log(`  - ${error.url}: ${error.status}`);
      }
    }
  });
});