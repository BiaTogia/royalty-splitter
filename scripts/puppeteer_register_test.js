const puppeteer = require('puppeteer');

(async () => {
  const url = process.env.FRONTEND_URL || 'http://localhost:3000/register';
  console.log('Opening', url);

  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  const logs = [];
  page.on('console', msg => {
    const args = msg.args();
    Promise.all(args.map(a => a.jsonValue().catch(() => a.toString())))
      .then(vals => logs.push({ type: 'console', text: vals.join(' ') }));
  });

  page.on('pageerror', err => logs.push({ type: 'pageerror', error: err.message }));

  page.on('requestfailed', req => {
    logs.push({ type: 'requestfailed', url: req.url(), method: req.method(), failure: req.failure()?.errorText });
  });

  page.on('response', async res => {
    try {
      const ct = res.headers()['content-type'] || '';
      let body = '';
      if (ct.includes('application/json')) body = await res.json();
      else body = await res.text().catch(() => '');
      logs.push({ type: 'response', url: res.url(), status: res.status(), body });
    } catch (e) {
      logs.push({ type: 'response_error', url: res.url(), error: e.message });
    }
  });

  console.log('Attempting to connect to dev server at', url);
  try {
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
    console.log('Successfully loaded page');
  } catch (err) {
    console.error('Failed to load page:', err.message);
    throw err;
  }
  // small pause to allow any client-side JS to initialize
  await new Promise((res) => setTimeout(res, 1000));

  // Fill the form
  const rand = Math.floor(Math.random() * 100000);
  const email = `puppeteer_auto_${rand}@example.com`;
  const name = 'Puppeteer Test';
  const password = 'password123';

  await page.type('input[type=text]', name, { delay: 30 }).catch(() => {});
  await page.type('input[type=email]', email, { delay: 30 });
  await page.type('input[type=password]', password, { delay: 30 });

  // Submit the form and wait for network (use broader selector fallback)
  await page.waitForSelector('button[type=submit], form button, button:not([type])', { timeout: 5000 });
  await Promise.all([
    page.click('button[type=submit], form button, button:not([type])'),
    page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 20000 }).catch(() => {}),
  ]);

  // Wait a moment for responses
  await new Promise((res) => setTimeout(res, 1000));

  console.log('--- Captured logs ---');
  logs.forEach((entry, i) => {
    console.log(`#${i+1}`, JSON.stringify(entry, null, 2));
  });

  await browser.close();
  console.log('Done');
})();
