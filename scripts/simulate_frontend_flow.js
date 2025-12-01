// Simulate frontend flow: register -> obtain token -> fetch wallet, tracks, payouts
// Usage: node simulate_frontend_flow.js

(async () => {
  const API_BASE = process.env.API_BASE || 'http://localhost:8000';
  const rand = Math.floor(Math.random() * 100000);
  const email = `auto_test_${rand}@example.com`;
  const password = 'password123';
  const name = 'Auto Test User';

  const headersJSON = { 'Content-Type': 'application/json' };

  try {
    console.log('1) Registering user:', email);
    let res = await fetch(`${API_BASE}/api/register/`, {
      method: 'POST',
      headers: headersJSON,
      body: JSON.stringify({ email, password, name })
    });
    const regBody = await safeParse(res);
    console.log('  register status:', res.status);
    console.log('  register body:', regBody);

    console.log('2) Obtaining token...');
    res = await fetch(`${API_BASE}/api/token/`, {
      method: 'POST',
      headers: headersJSON,
      body: JSON.stringify({ email, password })
    });
    const tokenBody = await safeParse(res);
    console.log('  token status:', res.status);
    console.log('  token body:', tokenBody);
    const token = tokenBody?.token;
    if (!token) throw new Error('No token returned');

    const authHeaders = { Authorization: `Token ${token}` };

    console.log('3) Fetching wallet (me)...');
    res = await fetch(`${API_BASE}/api/wallets/me/`, { method: 'GET', headers: authHeaders });
    const walletBody = await safeParse(res);
    console.log('  wallet status:', res.status);
    console.log('  wallet body:', walletBody);

    console.log('4) Fetching tracks...');
    res = await fetch(`${API_BASE}/api/tracks/`, { method: 'GET', headers: authHeaders });
    const tracksBody = await safeParse(res);
    console.log('  tracks status:', res.status);
    console.log('  tracks body length:', Array.isArray(tracksBody) ? tracksBody.length : typeof tracksBody);

    console.log('5) Fetching payouts...');
    res = await fetch(`${API_BASE}/api/payouts/`, { method: 'GET', headers: authHeaders });
    const payoutsBody = await safeParse(res);
    console.log('  payouts status:', res.status);
    console.log('  payouts body length:', Array.isArray(payoutsBody) ? payoutsBody.length : typeof payoutsBody);

    console.log('\nSimulation complete.');
  } catch (err) {
    console.error('Simulation error:', err);
  }

  async function safeParse(res) {
    const ct = res.headers.get('content-type') || '';
    try {
      if (ct.includes('application/json')) return await res.json();
      return await res.text();
    } catch (e) {
      return await res.text().catch(() => null);
    }
  }
})();
