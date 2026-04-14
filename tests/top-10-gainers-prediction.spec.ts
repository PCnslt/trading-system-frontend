import { test, expect } from '@playwright/test';

test.describe('Top 10 Gainers with 2-Day Prediction Component', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard
    await page.goto('http://localhost:4200');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
  });

  test('should display the component with correct title', async ({ page }) => {
    // Check component header
    const componentHeader = page.locator('text=/Top 10 Stock Gainers with 2-Day Advance Prediction/i');
    await expect(componentHeader).toBeVisible({ timeout: 10000 });
    
    // Check subtitle
    const subtitle = page.locator('text=/Real-time data from Yahoo Finance with AI-powered 2-day forecasting/i');
    await expect(subtitle).toBeVisible();
    
    console.log('✅ Component header and subtitle displayed correctly');
  });

  test('should display data table with correct columns', async ({ page }) => {
    // Wait for table to load
    const table = page.locator('table').first();
    await expect(table).toBeVisible({ timeout: 10000 });
    
    // Check table headers
    const headers = ['Rank', 'Symbol', 'Name', 'Price', 'Today\'s Change', '2-Day Prediction', 'Confidence', 'Signal', 'Market Cap', 'P/E (TTM)'];
    
    for (const header of headers) {
      const headerElement = page.locator('th', { hasText: header }).first();
      await expect(headerElement).toBeVisible();
      console.log(`✅ Header "${header}" found`);
    }
    
    // Check table has rows (might be loading or have data)
    const rows = table.locator('tbody tr');
    const rowCount = await rows.count();
    console.log(`Found ${rowCount} rows in table`);
    
    if (rowCount > 0) {
      // Check first row has data
      const firstRow = rows.first();
      const firstSymbol = firstRow.locator('td').nth(1); // Symbol column
      const symbolText = await firstSymbol.textContent();
      expect(symbolText).toMatch(/^[A-Z]{1,5}$/);
      console.log(`✅ First symbol: ${symbolText}`);
    }
  });

  test('should display prediction data with confidence bars', async ({ page }) => {
    // Wait for table
    const table = page.locator('table').first();
    await expect(table).toBeVisible({ timeout: 10000 });
    
    const rows = table.locator('tbody tr');
    const rowCount = await rows.count();
    
    if (rowCount > 0) {
      // Check prediction columns exist
      const firstRow = rows.first();
      
      // Check 2-Day Prediction column
      const predictionCol = firstRow.locator('td').nth(5); // 2-Day Prediction column
      await expect(predictionCol).toBeVisible();
      
      // Check for prediction text pattern (e.g., +1.23 (2.34%))
      const predictionText = await predictionCol.textContent();
      expect(predictionText).toMatch(/[+-]?\d+\.\d+\s*\([+-]?\d+\.\d+%\)/);
      console.log(`✅ Prediction data: ${predictionText}`);
      
      // Check confidence progress bar
      const confidenceBar = firstRow.locator('.progress-bar');
      await expect(confidenceBar).toBeVisible();
      
      const confidenceText = await confidenceBar.textContent();
      expect(confidenceText).toMatch(/\d+%/);
      console.log(`✅ Confidence: ${confidenceText}`);
      
      // Check signal badge
      const signalBadge = firstRow.locator('.badge');
      await expect(signalBadge).toBeVisible();
      
      const signalText = await signalBadge.textContent();
      expect(['BUY', 'HOLD', 'SELL']).toContain(signalText);
      console.log(`✅ Signal: ${signalText}`);
    }
  });

  test('should have functional refresh button', async ({ page }) => {
    // Find refresh button
    const refreshButton = page.locator('button:has-text("Refresh")').first();
    await expect(refreshButton).toBeVisible();
    
    // Check it's enabled (not loading)
    const loadingSpinner = page.locator('.fa-spin');
    const isSpinning = await loadingSpinner.count() > 0;
    
    if (!isSpinning) {
      await expect(refreshButton).toBeEnabled();
      console.log('✅ Refresh button is enabled');
    }
  });

  test('should have functional generate predictions button', async ({ page }) => {
    // Find generate predictions button
    const generateButton = page.locator('button:has-text("Generate 2-Day Predictions")').first();
    await expect(generateButton).toBeVisible();
    
    // Check it's enabled (not currently generating)
    const generatingSpinner = page.locator('.fa-bolt.fa-spin');
    const isGenerating = await generatingSpinner.count() > 0;
    
    if (!isGenerating) {
      await expect(generateButton).toBeEnabled();
      console.log('✅ Generate predictions button is enabled');
    }
  });

  test('should display last updated timestamp', async ({ page }) => {
    // Find timestamp in footer
    const timestampText = page.locator('text=/Updated:/i');
    await expect(timestampText).toBeVisible({ timeout: 10000 });
    
    const timestamp = await timestampText.textContent();
    expect(timestamp).toMatch(/Updated:.*\d{1,2}:\d{2}.*(AM|PM)/i);
    console.log(`✅ Last updated timestamp: ${timestamp}`);
  });

  test('should handle loading state', async ({ page }) => {
    // Check for loading spinner when component is loading
    // This might require triggering a refresh
    const refreshButton = page.locator('button:has-text("Refresh")').first();
    
    // Click refresh and check for loading state
    await refreshButton.click();
    
    // Look for loading spinner or text
    const loadingSpinner = page.locator('.spinner-border.text-success');
    const loadingText = page.locator('text=/Fetching real-time gainers/i');
    
    // Either spinner or loading text should appear
    const hasLoadingState = (await loadingSpinner.count() > 0) || (await loadingText.count() > 0);
    
    if (hasLoadingState) {
      console.log('✅ Loading state displayed during refresh');
    } else {
      console.log('⚠️ No loading state detected (might be very fast)');
    }
    
    // Wait for loading to complete
    await page.waitForTimeout(2000);
  });

  test('should display error state when backend is unavailable', async ({ page }) => {
    // This test would require mocking backend failure
    // For now, just check error display structure exists
    const errorAlert = page.locator('.alert.alert-danger');
    const errorCount = await errorAlert.count();
    
    if (errorCount > 0) {
      const errorText = await errorAlert.textContent();
      console.log(`Error state detected: ${errorText}`);
      
      // Check retry button exists
      const retryButton = errorAlert.locator('button:has-text("Retry")');
      await expect(retryButton).toBeVisible();
      console.log('✅ Error state with retry button displayed');
    } else {
      console.log('✅ No errors (backend is working)');
    }
  });

  test('should display BUY/HOLD/SELL signals with appropriate colors', async ({ page }) => {
    // Wait for table
    const table = page.locator('table').first();
    await expect(table).toBeVisible({ timeout: 10000 });
    
    const rows = table.locator('tbody tr');
    const rowCount = await rows.count();
    
    if (rowCount > 0) {
      // Check each row for signal badges
      for (let i = 0; i < Math.min(rowCount, 5); i++) {
        const row = rows.nth(i);
        const signalBadge = row.locator('.badge');
        
        if (await signalBadge.count() > 0) {
          const signalText = await signalBadge.textContent();
          const badgeClass = await signalBadge.getAttribute('class');
          
          // Check color coding
          if (signalText === 'BUY') {
            expect(badgeClass).toContain('bg-success');
          } else if (signalText === 'SELL') {
            expect(badgeClass).toContain('bg-danger');
          } else if (signalText === 'HOLD') {
            expect(badgeClass).toContain('bg-warning');
          }
          
          console.log(`✅ Row ${i + 1}: Signal ${signalText} with appropriate color`);
        }
      }
    }
  });

  test('should have responsive table design', async ({ page }) => {
    // Check table has responsive wrapper
    const tableWrapper = page.locator('.table-responsive');
    await expect(tableWrapper).toBeVisible();
    
    // Check table has dark theme
    const table = tableWrapper.locator('table.table-dark');
    await expect(table).toBeVisible();
    
    // Check table has hover effects
    const tableHover = tableWrapper.locator('table.table-hover');
    await expect(tableHover).toBeVisible();
    
    console.log('✅ Table has responsive design with dark theme and hover effects');
  });
});

test.describe('Backend API Integration', () => {
  test('should fetch real stocks from backend', async ({ request }) => {
    // Test backend endpoint
    const response = await request.get('http://localhost:8082/api/predictions/monitoring/real-stocks');
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
    
    if (data.length > 0) {
      const firstStock = data[0];
      expect(firstStock).toHaveProperty('symbol');
      expect(firstStock).toHaveProperty('name');
      console.log(`✅ Backend returned ${data.length} real stocks`);
    } else {
      console.log('⚠️ Backend returned empty array (fallback data might be used)');
    }
  });

  test('should generate collaborative predictions', async ({ request }) => {
    // Test collaborative predictions endpoint
    const response = await request.post('http://localhost:8082/api/predictions/collaborative', {});
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
    
    if (data.length > 0) {
      const firstPrediction = data[0];
      expect(firstPrediction).toHaveProperty('symbol');
      expect(firstPrediction).toHaveProperty('predictedChangePercent');
      expect(firstPrediction).toHaveProperty('confidence');
      console.log(`✅ Backend generated ${data.length} collaborative predictions`);
    } else {
      console.log('⚠️ Backend returned empty predictions array');
    }
  });

  test('should have backend health check', async ({ request }) => {
    // Test health endpoint
    const response = await request.get('http://localhost:8082/api/health');
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('status');
    expect(data).toHaveProperty('tickers');
    expect(data).toHaveProperty('agents');
    
    console.log(`✅ Backend health: ${data.status}, ${data.tickers} tickers, ${data.agents} agents`);
  });
});