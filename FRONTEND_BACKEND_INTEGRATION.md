# Frontend-Backend Integration Guide

**Status:** ✅ Backend Connected  
**Date:** November 30, 2025  
**Next.js App:** Connected to Django Backend at `http://localhost:8000`

---

## What's Been Connected

### ✅ Completed Integrations

1. **Authentication System**
   - `POST /api/token/` - Login with email & password
   - `POST /api/register/` - Register new users
   - `GET /api/users/me/` - Fetch current user profile
   - Token-based auth with Authorization headers
   - Automatic token refresh on page load

2. **Track Management**
   - `POST /api/tracks/` - Create new tracks
   - `GET /api/tracks/` - Fetch user's tracks
   - `DELETE /api/tracks/{id}/` - Delete tracks
   - Real track persistence in database

3. **Split Management**
   - `POST /api/splits/` - Create splits for tracks
   - `GET /api/splits/?track={id}` - Fetch track splits
   - Email-based user collaboration
   - Percentage validation (must sum to 100%)

4. **Wallet & Balance**
   - `GET /api/wallets/me/` - Fetch user's wallet
   - Real balance from backend
   - Auto-polling every 30 seconds
   - Displays actual earned money

5. **Payouts**
   - `GET /api/payouts/` - Fetch user's payouts
   - Displays payout history with status
   - Shows pending vs confirmed payouts
   - Real blockchain TXN IDs

6. **Dashboard**
   - Real wallet balance display
   - Actual payout counts and statuses
   - Real track counts
   - Collaborator information from splits

---

## File Changes Made

### New Files Created
```
src/services/api.js                    # Centralized API service layer
.env.local                              # Environment configuration
```

### Modified Files
```
src/context/AuthContext.js             # Now uses backend API
src/context/AppDataContext.js          # Now fetches real data
src/app/login/page.js                  # Async API calls
src/app/register/page.js               # Async API calls
src/app/dashboard/page.js              # Shows real payouts & balance
src/app/tracks/page.js                 # Uploads to backend API
```

---

## API Service Layer (`src/services/api.js`)

All API calls are centralized in this file. Key functions:

```javascript
// Authentication
authAPI.register(email, password, name)
authAPI.login(email, password)
authAPI.getCurrentUser()
authAPI.updateProfile(userData)

// Tracks
trackAPI.createTrack(formData)         // FormData with track file
trackAPI.getUserTracks()
trackAPI.deleteTrack(trackId)

// Splits
splitAPI.createSplit(trackId, splitData)
splitAPI.getTrackSplits(trackId)
splitAPI.updateSplit(splitId, splitData)

// Wallet
walletAPI.getMyWallet()
walletAPI.updateWallet(walletId, walletData)

// Payouts
payoutAPI.getMyPayouts()
payoutAPI.createPayout(payoutData)
payoutAPI.updatePayout(payoutId, payoutData)

// Utility functions
setAuthToken(token)                    // Store JWT token
clearAuthToken()                       // Remove JWT token
isAuthenticated()                      # Check if user logged in
getAuthToken()                         # Get stored token
```

---

## How to Test the Integration

### Step 1: Start Backend & Frontend

```bash
# Terminal 1: Start Django backend
cd royalty_splitter
docker-compose up

# Terminal 2: Start Next.js frontend
cd web_project-unstable-build-laman/web_project-unstable-build-laman
npm run dev
```

Frontend runs at: http://localhost:3000  
Backend runs at: http://localhost:8000

---

### Step 2: Register a New User

1. Go to http://localhost:3000/register
2. Fill in:
   - Artist Name: "Test Artist"
   - Email: "test@example.com"
   - Password: "password123"
3. Click "Initialize Dashboard"

**Behind the scenes:**
- Frontend calls `POST /api/register/`
- Backend creates user in database
- Backend returns token
- Frontend stores token in localStorage
- Frontend redirects to dashboard

---

### Step 3: Login

1. Go to http://localhost:3000/login
2. Enter email and password
3. Click "Log In"

**Behind the scenes:**
- Frontend calls `POST /api/token/`
- Backend validates credentials
- Backend returns token
- Frontend stores token and redirects

---

### Step 4: Create a Track

1. Go to http://localhost:3000/tracks
2. Click "Upload New"
3. Fill in:
   - Track Title: "My Song"
   - Duration: "5" (minutes)
   - Genre: "Electronic"
4. Configure splits:
   - Owner (you): 100%
5. Click "Create Track & Register Splits"

**Behind the scenes:**
- Frontend calls `POST /api/tracks/` with FormData
- Backend stores track in database
- Frontend calls `POST /api/splits/` for each collaborator
- Backend records split percentages
- Frontend updates local state and displays track

---

### Step 5: Check Dashboard

1. Go to http://localhost:3000/dashboard
2. See real data:
   - **Wallet Balance**: $0.00 (no royalties yet)
   - **Total Payouts**: 0 (no payouts created)
   - **Active Tracks**: 1 (your created track)
   - **Collaborators**: 0 (no splits)

**Behind the scenes:**
- Frontend calls `GET /api/wallets/me/`
- Frontend calls `GET /api/payouts/`
- Frontend calls `GET /api/tracks/`
- All data updates every 30 seconds

---

### Step 6: Create Royalties (Backend Only)

To simulate earning royalties, you need to manually trigger the backend royalty distribution:

```bash
# Enter Django shell
docker-compose exec web python manage.py shell

# Then run:
from backend.models import Track
from backend.royalty_service import distribute_royalty_for_track

track = Track.objects.get(id=1)
result = distribute_royalty_for_track(track)
print(result)
```

**What happens:**
- Backend calculates royalties
- Updates wallet balance
- Creates payouts
- Frontend dashboard auto-updates (polls every 30s)

---

### Step 7: Check Updated Balance

After creating royalties:

1. Refresh dashboard or wait 30 seconds
2. See updated:
   - **Wallet Balance**: $49.00 (your share of royalties)
   - **Total Payouts**: 1 (payout created)

---

## Architecture Diagram

```
┌─────────────────────────────────────┐
│   Next.js Frontend (localhost:3000) │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  React Components             │ │
│  │  (Login, Tracks, Dashboard)   │ │
│  └──────────────┬────────────────┘ │
│                 │                   │
│  ┌──────────────▼────────────────┐ │
│  │  Context Providers            │ │
│  │  (AuthContext, AppDataContext)│ │
│  └──────────────┬────────────────┘ │
│                 │                   │
│  ┌──────────────▼────────────────┐ │
│  │  API Service Layer            │ │
│  │  (src/services/api.js)        │ │
│  │  - authAPI                    │ │
│  │  - trackAPI                   │ │
│  │  - splitAPI                   │ │
│  │  - walletAPI                  │ │
│  │  - payoutAPI                  │ │
│  └──────────────┬────────────────┘ │
│                 │                   │
│  ┌──────────────▼────────────────┐ │
│  │  localStorage                 │ │
│  │  (auth_token only)            │ │
│  └───────────────────────────────┘ │
│                                     │
└─────────────────┬───────────────────┘
                  │
                  │ HTTP/HTTPS
                  │ REST API Calls
                  │
┌─────────────────▼───────────────────┐
│   Django Backend (localhost:8000)   │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  Django REST Framework        │ │
│  │  - /api/token/                │ │
│  │  - /api/register/             │ │
│  │  - /api/tracks/               │ │
│  │  - /api/splits/               │ │
│  │  - /api/wallets/              │ │
│  │  - /api/payouts/              │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  PostgreSQL Database          │ │
│  │  - Users                      │ │
│  │  - Tracks                     │ │
│  │  - Splits                     │ │
│  │  - Wallets                    │ │
│  │  - Payouts                    │ │
│  │  - Royalties                  │ │
│  └───────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

---

## Complete Money Flow (Frontend → Backend → Database)

```
1. USER REGISTERS
   ├─ Frontend form input
   ├─ POST /api/register/ with email, password, name
   ├─ Backend creates User + Wallet in PostgreSQL
   ├─ Backend returns token
   ├─ Frontend stores token in localStorage
   └─ Frontend redirects to dashboard

2. USER CREATES TRACK
   ├─ Frontend form input (title, duration, genre)
   ├─ POST /api/tracks/ with FormData (includes audio file)
   ├─ Backend stores Track in PostgreSQL
   ├─ POST /api/splits/ for each collaborator
   ├─ Backend stores Split records
   ├─ Backend returns track data
   └─ Frontend updates local state

3. BACKEND DISTRIBUTES ROYALTIES (manual trigger)
   ├─ Django shell: distribute_royalty_for_track(track)
   ├─ Backend calculates: duration × $10/min
   ├─ Backend deducts 2% platform fee
   ├─ Backend updates Wallet.balance for each user
   ├─ Backend creates Payout records
   └─ Database records all transactions

4. FRONTEND DISPLAYS DATA
   ├─ Frontend calls GET /api/wallets/me/
   ├─ Frontend gets real balance from database
   ├─ Frontend calls GET /api/payouts/
   ├─ Frontend displays payout history
   ├─ Frontend calls GET /api/tracks/
   ├─ Frontend displays user's tracks
   └─ Dashboard shows all real data

5. ADMIN CONFIRMS PAYOUT (via Swagger UI)
   ├─ Admin goes to http://localhost:8000/api/docs/
   ├─ Admin calls PUT /api/payouts/{id}/
   ├─ Admin sets status=2 (Confirmed)
   ├─ Admin adds blockchain_txn_id
   ├─ Backend updates Payout in database
   └─ Frontend next poll sees Confirmed status
```

---

## Environment Configuration

The `.env.local` file sets:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

This is used by the API service layer for all requests.

### For Production

Update to your production backend URL:
```
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## Error Handling

All API calls now have proper error handling:

```javascript
try {
  const result = await login(email, password);
  if (!result.success) {
    addToast(result.message, "error");  // Show error to user
  }
} catch (err) {
  addToast(err.message, "error");
}
```

Errors are caught and displayed to users with:
- Toast notifications (red error messages)
- Console logging for debugging
- Fallback error messages

---

## What Still Needs to Be Done

### Phase 2 Tasks
- [ ] Create upload UI for audio files
- [ ] Add real file upload handling
- [ ] Implement real-time notifications (WebSocket)
- [ ] Add payout request creation
- [ ] Implement blockchain confirmation workflow

### Phase 3 Tasks
- [ ] Add user profile page integration
- [ ] Implement transaction history page
- [ ] Add search and filtering
- [ ] Create admin dashboard

### Phase 4 Tasks
- [ ] Add payment gateway (Stripe, PayPal)
- [ ] Implement two-factor authentication
- [ ] Add analytics dashboard
- [ ] Create mobile-responsive design

---

## Testing Checklist

- [ ] User can register with backend
- [ ] User can login with backend
- [ ] User can create tracks with backend
- [ ] User can see their tracks on dashboard
- [ ] Dashboard shows real wallet balance
- [ ] Dashboard shows real payouts
- [ ] Track deletion works via API
- [ ] Split creation works via API
- [ ] API errors display properly to user
- [ ] Token persists on page refresh
- [ ] Auto-logout on invalid token

---

## Troubleshooting

### "Backend not connecting"
```
Error: Failed to fetch from http://localhost:8000
```
**Solution:** 
- Make sure Django backend is running: `docker-compose up`
- Check .env.local has correct API URL
- Check CORS is enabled in Django settings

### "Token not found"
```
Error: Authorization token missing
```
**Solution:**
- Try logging in again
- Check browser localStorage for `auth_token`
- Clear browser cache and try again

### "Track upload fails"
```
Error: Failed to upload track
```
**Solution:**
- Ensure you're logged in
- Check that duration field is filled
- Check track title is not empty
- Try uploading via Swagger UI to debug

### "Dashboard shows no data"
```
"No payouts yet" - "No earnings yet"
```
**Solution:**
- This is normal! Frontend shows real data
- Create a track first
- Then trigger royalty distribution via backend
- Dashboard will update on next poll (30 seconds)

---

## Key Improvements Over Old System

| Feature | Old (LocalStorage) | New (Backend API) |
|---------|-------------------|-------------------|
| **Data Persistence** | ❌ Lost on clear | ✅ Saved in database |
| **Multi-User** | ❌ Isolated per browser | ✅ Shared across users |
| **Real Data** | ❌ Simulated | ✅ Real database |
| **Collaboration** | ❌ Not possible | ✅ Email-based splits |
| **Security** | ⚠️ Plaintext passwords | ✅ Token-based auth |
| **Scalability** | ❌ Limited to browser | ✅ Unlimited |
| **Audit Trail** | ❌ None | ✅ Full history |
| **Admin Panel** | ❌ None | ✅ Swagger UI + Django admin |

---

## API Endpoints Reference

### Authentication
- `POST /api/token/` - Login
- `POST /api/register/` - Register
- `GET /api/users/me/` - Current user

### Tracks
- `GET /api/tracks/` - List user's tracks
- `POST /api/tracks/` - Create track
- `GET /api/tracks/{id}/` - Get track detail
- `DELETE /api/tracks/{id}/` - Delete track

### Splits
- `GET /api/splits/` - List splits (with ?track filter)
- `POST /api/splits/` - Create split
- `GET /api/splits/{id}/` - Get split detail
- `PUT /api/splits/{id}/` - Update split
- `DELETE /api/splits/{id}/` - Delete split

### Wallets
- `GET /api/wallets/me/` - Current user's wallet
- `GET /api/wallets/{id}/` - Get wallet
- `PUT /api/wallets/{id}/` - Update wallet

### Payouts
- `GET /api/payouts/` - List payouts
- `POST /api/payouts/` - Create payout
- `GET /api/payouts/{id}/` - Get payout
- `PUT /api/payouts/{id}/` - Update payout (admin)
- `GET /api/payouts/summary/` - Payout summary

### Royalties
- `GET /api/royalties/` - List royalties
- `GET /api/royalties/?track={id}` - Track royalties

---

**Status: ✅ CONNECTED & READY TO TEST**

Start the backend and frontend, then follow the testing steps above!
