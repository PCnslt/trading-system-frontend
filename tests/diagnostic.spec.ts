import { test, expect } from '@playwright/test';

test('Diagnostic: Check what\'s actually on the page', async ({ page }) => {
  await page.goto('http://localhost:4200');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);
  
  // Take screenshot
  await page.screenshot({ path: 'test-results/diagnostic-screenshot.png', fullPage: true });
  
  // Log page title
  const title = await page.title();
  console.log(`Page title: ${title}`);
  
  // Log all h1-h6 elements
  for (let i = 1; i <= 6; i++) {
    const headers = page.locator(`h${i}`);
    const count = await headers.count();
    console.log(`h${i} elements: ${count}`);
    
    for (let j = 0; j < Math.min(count, 5); j++) {
      const text = await headers.nth(j).textContent();
      console.log(`  h${i}[${j}]: ${text}`);
    }
  }
  
  // Log all tables
  const tables = page.locator('table');
  const tableCount = await tables.count();
  console.log(`Tables on page: ${tableCount}`);
  
  for (let i = 0; i < tableCount; i++) {
    const table = tables.nth(i);
    const tableHtml = await table.innerHTML();
    console.log(`Table ${i} HTML (first 500 chars): ${tableHtml.substring(0, 500)}...`);
  }
  
  // Check for specific elements
  const topGainers = page.locator('text=/Top.*Gainer/i');
  const topGainersCount = await topGainers.count();
  console.log(`Elements matching "Top.*Gainer": ${topGainersCount}`);
  
  // Check console for errors
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });
  
  await page.reload();
  await page.waitForLoadState('networkidle');
  
  console.log(`Console errors: ${consoleErrors.length}`);
  if (consoleErrors.length > 0) {
    console.log('First 3 errors:', consoleErrors.slice(0, 3));
  }
});