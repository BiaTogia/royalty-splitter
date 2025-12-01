# Authentication Guide - Royalty Splitter API

## Quick Start

> **Security update (recommended):** Browser-based access now uses secure server-managed sessions. The backend sets an HttpOnly session cookie on successful login/register and also issues a CSRF cookie. Browser frontends must use `fetch(..., { credentials: 'include' })` and must NOT store authentication tokens or plaintext passwords in `localStorage`.
>
> Token-based authentication remains available for non-browser API clients (scripts, CLI, server-to-server). If you must use tokens for automation, store them securely on the host (e.g., environment variables, secret manager) and never persist them in a browser environment.


### 1. Browser (Recommended) — Session-Based Flow

**Endpoint:** `POST /api/token/` (or `POST /api/register/` for new accounts)

- The endpoint authenticates the user and creates a Django session on the server side.
- The response sets an HttpOnly session cookie and a CSRF cookie. The response body does NOT contain a token.
- From the frontend, make subsequent requests with credentials included:

```javascript
fetch('/api/tracks/', {
  method: 'GET',
  credentials: 'include'
})
```

- For state-changing requests (POST/PUT/DELETE), include the CSRF token from the `csrftoken` cookie as the `X-CSRFToken` header.

```javascript
fetch('/api/tracks/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: JSON.stringify({ /* ... */ })
})
```

(Frontend note: the Harmoniq frontend already performs these steps — it uses `credentials: 'include'` and attaches `X-CSRFToken` for unsafe requests.)

---

### 2. Non-Browser Clients — Token-Based Flow

Use this flow for scripts, CLI tools, or server-to-server integrations where cookies are not appropriate.

**Endpoint:** `POST /api/token/`

**Request:**
```bash
POST http://localhost:8000/api/token/
Content-Type: application/json

{
  "email": "yourname@example.com",
  "password": "YourSecurePassword123"
}
```

**Response:**
```json
{
  "token": "f6fbf4d30866479402bbece353494b34b9f8e08e",
  "user_id": 1,
  "email": "yourname@example.com"
}
```

Notes:
- Store tokens securely outside the browser (e.g., env vars, secret store).
- Use tokens in the header: `Authorization: Token YOUR_TOKEN_HERE`.
- Tokens are intended for non-browser automation only.

---



---

## Using Your Token

### In Swagger UI
1. Open **http://localhost:8000/api/docs/**
2. Click the **🔒 Authorize** button (top right)
3. Enter your token in the format: `Token YOUR_TOKEN_HERE`
   ```
   Token f6fbf4d30866479402bbece353494b34b9f8e08e
   ```
4. Click **Authorize**
5. Now all requests will include your token automatically!

### In cURL
```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
  http://localhost:8000/api/payouts/
```

### In Postman
1. Create a new request
2. Go to the **Authorization** tab
3. Select type: **API Key**
4. Key: `Authorization`
5. Value: `Token YOUR_TOKEN_HERE`
6. Add to: **Header**
7. Send your request

### In JavaScript/Fetch
```javascript
const token = 'YOUR_TOKEN_HERE';

fetch('http://localhost:8000/api/payouts/', {
  method: 'GET',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Test User (Already Created)

You can use this test account to try the API:

- **Email:** `test@example.com`
- **Password:** `test123456`
- **Token:** `f6fbf4d30866479402bbece353494b34b9f8e08e`
- **Wallet Balance:** $0.00

### Example Request
```bash
curl -H "Authorization: Token f6fbf4d30866479402bbece353494b34b9f8e08e" \
  http://localhost:8000/api/payouts/
```

---

## Payout Endpoints (Require Authentication)

### 1. List Your Payouts
```
GET /api/payouts/
Authorization: Token YOUR_TOKEN
```

**Response:**
```json
[
  {
    "id": 1,
    "amount": "150.00",
    "txn_date": "2025-11-29T19:50:00Z",
    "status": 1,
    "status_name": "Pending",
    "blockchain_txn_id": null
  }
]
```

### 2. Create a Payout
```
POST /api/payouts/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "amount": "50.00",
  "status": 1
}
```

**Response:** `201 Created`
```json
{
  "id": 2,
  "amount": "50.00",
  "txn_date": "2025-11-29T19:51:00Z",
  "status": 1,
  "status_name": "Pending",
  "blockchain_txn_id": null
}
```

### 3. Get Payout Details
```
GET /api/payouts/1/
Authorization: Token YOUR_TOKEN
```

### 4. Update Payout
```
PUT /api/payouts/1/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "amount": "75.00",
  "status": 1
}
```

### 5. Delete Payout
```
DELETE /api/payouts/1/
Authorization: Token YOUR_TOKEN
```

### 6. Get All Your Payouts
```
GET /api/payouts/my_payouts/
Authorization: Token YOUR_TOKEN
```

### 7. Get Payout Summary
```
GET /api/payouts/summary/
Authorization: Token YOUR_TOKEN
```

**Response:**
```json
{
  "total_payouts": 5,
  "total_amount": "250.00",
  "wallet_balance": "750.00"
}
```

---

## Error Responses

### 401 Unauthorized - Missing Token
```
{
  "detail": "Authentication credentials were not provided."
}
```
**Fix:** Add your token to the Authorization header

### 401 Unauthorized - Invalid Token
```
{
  "detail": "Invalid token."
}
```
**Fix:** Use the correct token from `/api/token/` endpoint

### 400 Bad Request - Invalid Payout Amount
```
{
  "amount": ["Payout amount must be positive."]
}
```
**Fix:** Enter an amount between $1.00 and $999,999.99

### 400 Bad Request - Insufficient Balance
```
{
  "non_field_errors": ["Insufficient balance. Wallet balance: 50.00, Payout amount: 500"]
}
```
**Fix:** Your wallet doesn't have enough balance for this payout

### 404 Not Found - User Wallet Doesn't Exist
```
{
  "error": "User wallet does not exist"
}
```
**Fix:** Contact support to create a wallet for your account

---

## Token Management

### Reset Your Token
If your token is compromised, get a new one by calling `/api/token/` again with your credentials. A new token will be created.

### Token Information
Tokens are:
- **Unique per user** - Each user has one token
- **Persistent** - Same token every time you authenticate
- **Secure** - Never share your token with others
- **Format** - 40 character hex string

---

## Common Issues

### Q: I get "Unauthorized" when using Swagger
**A:** You need to click the **Authorize** button and enter your token in the format: `Token YOUR_TOKEN_HERE` (with the word "Token" before it)

### Q: My token isn't working
**A:** Make sure you're using the format: `Token YOUR_TOKEN_HERE` (with space and "Token" prefix)

### Q: I forgot my token
**A:** Call `POST /api/token/` with your email/password again to get your token

### Q: Can I have multiple tokens?
**A:** No, each user has one token. Calling `/api/token/` again returns the same token

### Q: Is my token exposed in Swagger?
**A:** Yes, Swagger displays your token. Use a temporary test account if security is a concern. In production, use HTTPS and manage tokens carefully.

---

## Next Steps

1. Get your token from `/api/token/`
2. Authorize in Swagger using the **Authorize** button
3. Start testing the Payout endpoints!

**API Documentation:** http://localhost:8000/api/docs/
