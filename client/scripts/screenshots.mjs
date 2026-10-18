// Capture the README screenshots from a running app.
//
//   docker compose up --build -d          (or uvicorn on :8000 with client_build/ present)
//   python scripts/seed.py                (demo users and posts)
//   npm run screenshots                   (from client/; BASE_URL=http://host:port to point elsewhere)
//
// Writes PNGs to assets/screenshots/ at desktop (1440x900) and phone (390x844) sizes.
// page.screenshot creates the folder if it is missing.
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const BASE_URL = (process.env.BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '');
const OUT_DIR = fileURLToPath(new URL('../../assets/screenshots/', import.meta.url));

const viewports = {
  desktop: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
  phone: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
};

async function capture(browser, name, options) {
  const context = await browser.newContext(options);
  const page = await context.newPage();
  await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  await page.locator('.card').first().waitFor();

  await page.screenshot({ path: `${OUT_DIR}users-${name}.png`, fullPage: name === 'phone' });

  await page.getByRole('button', { name: 'Blogs' }).click();
  await page.locator('.blog-content').first().waitFor();
  // Let the 0.3s tab transition finish and drop the hover state so the shot shows the settled UI
  await page.mouse.move(0, 0);
  await page.waitForTimeout(500);
  await page.screenshot({ path: `${OUT_DIR}blogs-${name}.png`, fullPage: name === 'phone' });

  await context.close();
}

async function captureApiDocs(browser) {
  const context = await browser.newContext(viewports.desktop);
  const page = await context.newPage();
  await page.goto(`${BASE_URL}/docs`, { waitUntil: 'networkidle' });
  await page.locator('.opblock').first().waitFor();
  await page.screenshot({ path: `${OUT_DIR}api-docs-desktop.png` });
  await context.close();
}

const browser = await chromium.launch();
try {
  // Each capture has its own browser context, so they run in parallel
  await Promise.all([
    ...Object.entries(viewports).map(([name, options]) => capture(browser, name, options)),
    captureApiDocs(browser),
  ]);
} finally {
  await browser.close();
}
console.log(`Screenshots written to ${OUT_DIR}`);
