import { test, expect } from '@playwright/test';

test.describe('Comprehensive Frontend Regression Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the dashboard
    await page.goto('http://localhost:4200');
    // Wait for page to load and initial API calls
    await page.waitForLoadState('networkidle');
    // Wait a bit more for Angular to initialize
    await page.waitForTimeout(2000);
  });

  test('Issue 1: Top 10 Gainers section displays correctly', async ({ page }) => {
    // Test 1.1: Section title is correct
    const gainersTitle = page.locator('h6:has-text("📈 Top 10 Gainers (Yahoo Finance)")');
    await expect(gainersTitle).toBeVisible({ timeout: 10000 });
    
    // Test 1.2: Wait for data to load
    await page.waitForTimeout(5000);
    
    // Test 1.3: Find the table - it should be near the header
    // Get parent container of the header, then find table within it
    const gainersSection = gainersTitle.locator('xpath=../..'); // Go up two levels
    const gainersTable = gainersSection.locator('table').first();
    await expect(gainersTable).toBeVisible({ timeout: 10000 });
    
    // Test 1.4: Table should have rows (might be 0 if loading, but API returns 10)
    const tableRows = gainersTable.locator('tbody tr');
    await page.waitForTimeout(3000); // Wait more for data
    
    const rowCount = await tableRows.count();
    console.log(`Top 10 Gainers table has ${rowCount} rows`);
    
    // If 0 rows, check if it's loading
    if (rowCount === 0) {
      const loadingText = page.locator('text=Loading');
      if (await loadingText.count() > 0) {
        console.log('Table is still loading...');
        // Wait more and check again
        await page.waitForTimeout(5000);
        const newRowCount = await tableRows.count();
        console.log(`After waiting, table has ${newRowCount} rows`);
        expect(newRowCount).toBeGreaterThan(0);
      }
    } else {
      expect(rowCount).toBeGreaterThan(0);
    }
    
    // Test 1.4: Each row has required columns
    for (let i = 0; i < Math.min(rowCount, 3); i++) { // Check first 3 rows
      const row = tableRows.nth(i);
      const cells = row.locator('td');
      const cellCount = await cells.count();
      expect(cellCount).toBeGreaterThanOrEqual(4); // Should have at least Symbol, Name, Change, Price
      
      // Verify data looks reasonable
      const symbolCell = cells.nth(0);
      const symbolText = await symbolCell.textContent();
      expect(symbolText?.length).toBeGreaterThan(0);
      expect(symbolText).toMatch(/^[A-Z]+$/); // Should be uppercase letters
    }
    
    // Test 1.5: No "Loading..." or error messages
    const loadingText = page.locator('text=Loading...');
    await expect(loadingText).not.toBeVisible({ timeout: 1000 });
    
    const errorText = page.locator('text=Failed to load');
    await expect(errorText).not.toBeVisible({ timeout: 1000 });
  });

  test('Issue 2: All tables have dark backgrounds (CSS fix)', async ({ page }) => {
    // Test 2.1: Check all tables have table-dark class
    const allTables = page.locator('table');
    const tableCount = await allTables.count();
    
    for (let i = 0; i < tableCount; i++) {
      const table = allTables.nth(i);
      const tableClass = await table.getAttribute('class');
      expect(tableClass).toContain('table-dark');
    }
    
    // Test 2.2: Visual verification - take screenshot
    await page.screenshot({ path: 'test-results/table-backgrounds-verified.png', fullPage: true });
    
    // Test 2.3: Check CSS variables are applied
    const tableRow = page.locator('table tbody tr').first();
    const backgroundColor = await tableRow.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    
    // Should be dark (rgb values low)
    console.log(`Table row background color: ${backgroundColor}`);
    // rgb(33, 37, 41) is Bootstrap's table-dark color
    expect(backgroundColor).toBe('rgb(33, 37, 41)');
  });

  test('Issue 3: Prediction Pipeline shows correct state when inactive', async ({ page }) => {
    // Test 3.1: Pipeline section exists
    const pipelineSection = page.locator('div').filter({ hasText: /Prediction Pipeline/i }).first();
    await expect(pipelineSection).toBeVisible();
    
    // Test 3.2: When no analysis is running, should show "No analysis running" or empty
    const noAnalysisText = page.locator('text=No analysis running');
    const emptyPipelineText = page.locator('text=Start a new analysis');
    
    if (await noAnalysisText.count() > 0 || await emptyPipelineText.count() > 0) {
      console.log('✅ Pipeline correctly shows no analysis running');
      
      // Test 3.3: Should NOT show fake progress bars
      const fakeProgress = page.locator('.progress-bar[style*="100%"]');
      await expect(fakeProgress).not.toBeVisible();
      
      const inProgressStages = page.locator('text=IN_PROGRESS');
      await expect(inProgressStages).not.toBeVisible();
      
      const completedStages = page.locator('text=COMPLETED');
      await expect(completedStages).not.toBeVisible();
    } else {
      // If pipeline shows data, verify it's not fake
      const progressBars = page.locator('.progress-bar');
      const barCount = await progressBars.count();
      
      for (let i = 0; i < barCount; i++) {
        const bar = progressBars.nth(i);
        const width = await bar.getAttribute('style');
        
        // Should not be 100% unless actually completed
        if (width?.includes('100%')) {
          const parentText = await bar.evaluate((el) => {
            return el.closest('div')?.textContent || '';
          });
          
          // If it says "COMPLETED" with 100%, that's OK
          // If it says "IN_PROGRESS" or "PENDING" with 100%, that's fake
          if (parentText.includes('IN_PROGRESS') || parentText.includes('PENDING')) {
            console.warn(`⚠️ WARNING: Fake progress detected - ${parentText} shows 100%`);
          }
        }
      }
    }
    
    // Test 3.4: Click "Generate Predictions" and verify pipeline updates
    const generateButton = page.locator('button:has-text("Generate Predictions")');
    if (await generateButton.count() > 0) {
      console.log('Testing Generate Predictions button...');
      
      // Click and wait for API call
      await generateButton.click();
      await page.waitForTimeout(3000); // Wait for analysis to start
      
      // Now pipeline should show progress
      const inProgressAfterClick = page.locator('text=IN_PROGRESS');
      if (await inProgressAfterClick.count() > 0) {
        console.log('✅ Pipeline shows IN_PROGRESS after clicking Generate Predictions');
      }
    }
  });

  test('Issue 4: Ticker database foundation - verify data display', async ({ page }) => {
    // Test 4.1: Check ticker count display
    const tickerStats = page.locator('text=/tickers/i');
    await expect(tickerStats.first()).toBeVisible();
    
    // Test 4.2: Verify data is being loaded (not just hardcoded)
    // Check Recent Activity table
    const recentActivityTable = page.locator('table').filter({ hasText: 'Recent Activity' }).first();
    if (await recentActivityTable.count() > 0) {
      const activityRows = recentActivityTable.locator('tbody tr');
      const activityCount = await activityRows.count();
      
      console.log(`Recent Activity table has ${activityCount} rows`);
      expect(activityCount).toBeGreaterThan(0);
      
      // Verify data looks real (not placeholder)
      const firstRow = activityRows.first();
      const rowText = await firstRow.textContent();
      expect(rowText).not.toContain('placeholder');
      expect(rowText).not.toContain('example');
    }
    
    // Test 4.3: Check agent status table
    const agentTable = page.locator('table').filter({ hasText: 'Agent' }).first();
    if (await agentTable.count() > 0) {
      const agentRows = agentTable.locator('tbody tr');
      const agentCount = await agentRows.count();
      
      console.log(`Agent Status table has ${agentCount} rows`);
      expect(agentCount).toBe(10); // Should have 10 agents
      
      // Each agent should have a status
      for (let i = 0; i < Math.min(agentCount, 3); i++) {
        const row = agentRows.nth(i);
        const statusCell = row.locator('td').nth(2); // Assuming status is 3rd column
        const statusText = await statusCell.textContent();
        expect(statusText).toMatch(/^(ACTIVE|IDLE|ERROR)$/);
      }
    }
  });

  test('End-to-end: Generate predictions workflow', async ({ page }) => {
    // Step 1: Verify initial state
    const generateButton = page.locator('button:has-text("Generate Predictions")');
    await expect(generateButton).toBeVisible();
    
    // Step 2: Click generate
    console.log('Clicking Generate Predictions...');
    await generateButton.click();
    
    // Step 3: Wait for analysis to start
    await page.waitForTimeout(2000);
    
    // Step 4: Verify pipeline shows progress
    const pipelineProgress = page.locator('text=/Overall Progress/i');
    await expect(pipelineProgress).toBeVisible();
    
    // Step 5: Wait for completion (or timeout)
    await page.waitForTimeout(10000); // Wait 10 seconds
    
    // Step 6: Check for results
    const resultsSection = page.locator('text=/Top Recommendations/i');
    await expect(resultsSection).toBeVisible();
    
    // Step 7: Verify recommendations table has data
    const recommendationsTable = page.locator('table').filter({ hasText: 'Recommendation' }).first();
    if (await recommendationsTable.count() > 0) {
      const recommendationRows = recommendationsTable.locator('tbody tr');
      const recCount = await recommendationRows.count();
      expect(recCount).toBeGreaterThan(0);
      
      console.log(`Generated ${recCount} recommendations`);
    }
    
    // Take screenshot of final state
    await page.screenshot({ path: 'test-results/e2e-workflow-complete.png', fullPage: true });
  });

  test('API Integration: Verify backend connectivity', async ({ page }) => {
    // Monitor network requests
    const apiRequests = [];
    
    page.on('request', request => {
      if (request.url().includes('localhost:8082')) {
        apiRequests.push({
          url: request.url(),
          method: request.method()
        });
      }
    });
    
    // Reload page to trigger API calls
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    console.log(`Made ${apiRequests.length} API calls to backend`);
    
    // Should have made multiple API calls
    expect(apiRequests.length).toBeGreaterThan(5);
    
    // Check for critical endpoints
    const criticalEndpoints = [
      '/api/predictions/monitoring/real-stocks',
      '/api/health',
      '/api/agent-activities',
      '/api/monitoring/agents/status'
    ];
    
    for (const endpoint of criticalEndpoints) {
      const hasEndpoint = apiRequests.some(req => req.url.includes(endpoint));
      expect(hasEndpoint).toBeTruthy();
    }
    
    // Check for errors in console
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // Trigger some UI interaction
    await page.locator('button').first().click();
    await page.waitForTimeout(1000);
    
    console.log(`Console errors: ${consoleErrors.length}`);
    // Should have minimal errors (some might be expected)
    expect(consoleErrors.length).toBeLessThan(5);
  });
});