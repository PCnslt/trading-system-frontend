import { test, expect } from '@playwright/test';

test('Check Top 10 Gainers table specifically', async ({ page }) => {
  await page.goto('http://localhost:4200');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(5000); // Wait longer for data to load
  
  // Find the Top 10 Gainers table
  const gainersHeader = page.locator('h6:has-text("📈 Top 10 Gainers (Yahoo Finance)")');
  await expect(gainersHeader).toBeVisible();
  
  // Get the table after this header
  const gainersTable = gainersHeader.locator('..').locator('table').first();
  await expect(gainersTable).toBeVisible();
  
  // Count rows in tbody
  const tableRows = gainersTable.locator('tbody tr');
  const rowCount = await tableRows.count();
  console.log(`Top 10 Gainers table has ${rowCount} rows in tbody`);
  
  // Check each row
  for (let i = 0; i < rowCount; i++) {
    const row = tableRows.nth(i);
    const cells = row.locator('td');
    const cellCount = await cells.count();
    console.log(`Row ${i}: ${cellCount} cells`);
    
    if (cellCount > 0) {
      const symbolCell = cells.nth(0);
      const symbolText = await symbolCell.textContent();
      console.log(`  Symbol: ${symbolText}`);
    }
  }
  
  // Also check the API directly
  const apiResponse = await page.request.get('http://localhost:8082/api/predictions/monitoring/real-stocks');
  const apiData = await apiResponse.json();
  console.log(`API returns ${apiData.totalStocks} stocks: ${apiData.stocks.map(s => s.symbol).join(', ')}`);
  
  // The table should match API data
  expect(rowCount).toBe(apiData.totalStocks);
});