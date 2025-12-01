# Frontend-Backend Integration: Visual Guide

---

## Complete System Architecture

```
                           USER
                            │
                            ▼
        ┌──────────────────────────────────────────┐
        │      NEXT.JS FRONTEND (Port 3000)        │
        ├──────────────────────────────────────────┤
        │                                          │
        │  Pages:                                  │
        │  ├─ Login       ──► AuthContext         │
        │  ├─ Register    ──► AuthContext         │
        │  ├─ Dashboard   ──► AppDataContext      │
        │  ├─ Tracks      ──► AppDataContext      │
        │  ├─ Profile     ──► AuthContext         │
        │  └─ History     ──► AppDataContext      │
        │                                          │
        │  Services (api.js):                      │
        │  ├─ authAPI                             │
        │  ├─ trackAPI                            │
        │  ├─ splitAPI                            │
        │  ├─ walletAPI                           │
        │  ├─ payoutAPI                           │
        │  └─ royaltyAPI                          │
        │                                          │
        │  Storage:                                │
        │  └─ localStorage: auth_token            │
        │                                          │
        └────────────────┬─────────────────────────┘
                         │
                         │ HTTPS REST API
                         │ Header: Authorization: Token {jwt}
                         │
        ┌────────────────▼─────────────────────────┐
        │    DJANGO REST FRAMEWORK (Port 8000)    │
        ├──────────────────────────────────────────┤
        │                                          │
        │  Authentication:                         │
        │  ├─ /api/token/           (POST)        │
        │  └─ /api/register/        (POST)        │
        │                                          │
        │  User:                                   │
        │  ├─ /api/users/me/        (GET)         │
        │  └─ /api/users/{id}/      (PUT)         │
        │                                          │
        │  Tracks:                                 │
        │  ├─ /api/tracks/          (GET,POST)    │
        │  ├─ /api/tracks/{id}/     (GET,DELETE)  │
        │  └─ /api/tracks/{id}/download/ (GET)    │
        │                                          │
        │  Splits:                                 │
        │  ├─ /api/splits/          (GET,POST)    │
        │  ├─ /api/splits/{id}/     (PUT,DELETE)  │
        │  └─ /api/splits/?track=X  (GET filter)  │
        │                                          │
        │  Wallets:                                │
        │  ├─ /api/wallets/me/      (GET)         │
        │  ├─ /api/wallets/{id}/    (GET,PUT)     │
        │  └─ /api/wallets/         (GET)         │
        │                                          │
        │  Payouts:                                │
        │  ├─ /api/payouts/         (GET,POST)    │
        │  ├─ /api/payouts/{id}/    (GET,PUT)     │
        │  └─ /api/payouts/summary/ (GET)         │
        │                                          │
        │  Royalties:                              │
        │  ├─ /api/royalties/       (GET)         │
        │  └─ /api/royalties/?track=X (GET filter)│
        │                                          │
        │  Admin:                                  │
        │  ├─ /admin/               (Django)      │
        │  └─ /api/docs/            (Swagger)     │
        │                                          │
        └────────────────┬─────────────────────────┘
                         │
                         │ Django ORM
                         │
        ┌────────────────▼─────────────────────────┐
        │    POSTGRESQL DATABASE (Port 5432)      │
        ├──────────────────────────────────────────┤
        │                                          │
        │  Core Tables:                            │
        │  ├─ auth_user             (Users)       │
        │  ├─ backend_wallet        (Balances)    │
        │  ├─ backend_track         (Tracks)      │
        │  ├─ backend_split         (Splits)      │
        │  ├─ backend_royalty       (Royalties)   │
        │  ├─ backend_payout        (Payouts)     │
        │  └─ backend_siem          (Events)      │
        │                                          │
        │  Relationships:                          │
        │  ├─ User ──1:1──► Wallet               │
        │  ├─ User ──1:M──► Track                │
        │  ├─ Track ──1:M──► Split               │
        │  ├─ Track ──1:M──► Royalty             │
        │  ├─ Royalty ──1:M──► Payout            │
        │  └─ User ──1:M──► Payout               │
        │                                          │
        └──────────────────────────────────────────┘
```

---

## User Registration Flow

```
┌─────────────────┐
│  User Visits    │
│  /register      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Register Form (Next.js Page)           │
│  - Name input                           │
│  - Email input                          │
│  - Password input                       │
│  - Submit button                        │
└────────┬────────────────────────────────┘
         │
         │ User fills form & clicks submit
         │
         ▼
┌─────────────────────────────────────────┐
│  Form Validation (Frontend)             │
│  - Check fields not empty               │
│  - Check password length                │
│  - Check email format                   │
└────────┬────────────────────────────────┘
         │
         ▼ POST /api/register/
         │ Body: {name, email, password}
         │
┌────────▼──────────────────────────────────┐
│  Django Backend                           │
│  1. Validate email not duplicate          │
│  2. Hash password (Django)                │
│  3. Create User object                    │
│  4. Create Wallet for user                │
│  5. Generate JWT token                    │
│  6. Save to PostgreSQL                    │
└────────┬──────────────────────────────────┘
         │
         ▼ Response: {token, user_id, email}
         │
┌────────▼──────────────────────────────────┐
│  Frontend Receives Response               │
│  1. Store token in localStorage           │
│  2. Set user context                      │
│  3. Redirect to /dashboard                │
└─────────────────────────────────────────┘
```

---

## Track Creation & Royalty Distribution Flow

```
┌──────────────────────┐
│  User at /tracks     │
│  Clicks "Upload New" │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Track Upload Form                   │
│  - Title: "My Song"                  │
│  - Duration: 10 (minutes)            │
│  - Genre: "Electronic"               │
│  - Splits:                           │
│    • User A: 50%                     │
│    • User B: 30%                     │
│    • User C: 20%                     │
└──────────┬──────────────────────────┘
           │
           │ Validate: 50+30+20 = 100% ✓
           │
           ▼ POST /api/tracks/
           │ FormData: {title, duration, genre}
           │
┌──────────▼──────────────────────────┐
│  Backend: Create Track               │
│  1. Validate track data              │
│  2. Save to PostgreSQL               │
│  3. Return: {id: 1, title, duration} │
└──────────┬──────────────────────────┘
           │
           ▼ POST /api/splits/
           │ For each collaborator:
           │ {track_id: 1, user: "userB@email.com", percentage: 30}
           │
┌──────────▼──────────────────────────┐
│  Backend: Create Splits              │
│  1. Validate percentage (0-100)      │
│  2. Find users by email              │
│  3. Create Split objects             │
│  4. Save to PostgreSQL               │
└──────────┬──────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Now track exists in database!       │
│  Ready for royalty distribution      │
└──────────┬───────────────────────────┘
           │
           │ (Manual backend trigger)
           │ Django shell:
           │ >>> distribute_royalty_for_track(track)
           │
           ▼
┌──────────────────────────────────────┐
│  Backend: Calculate Royalties        │
│  1. Get track duration: 10 minutes   │
│  2. Calculate: 10 × $10/min = $100   │
│  3. Deduct 2% fee: $100 × 0.98 = $98│
│  4. For each split:                  │
│     • User A: $100 × 0.5 × 0.98 = $49│
│     • User B: $100 × 0.3 × 0.98 = $29.40
│     • User C: $100 × 0.2 × 0.98 = $19.60
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Backend: Update Wallets             │
│  1. Get each user's wallet           │
│  2. wallet.balance += user_share     │
│  3. Save to PostgreSQL               │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Backend: Create Payouts             │
│  1. For each user, create Payout     │
│  2. Amount: their share ($49, $29.40, $19.60)
│  3. Status: 1 (Pending)              │
│  4. Save to PostgreSQL               │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Database State:                     │
│  ✓ Wallet.balance updated            │
│  ✓ Payout records created (Pending)  │
│  ✓ Royalty record created            │
│  ✓ All users have money earned!      │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Frontend (Dashboard)                │
│  1. Polls GET /api/wallets/me/       │
│  2. Sees wallet.balance = $49        │
│  3. Polls GET /api/payouts/          │
│  4. Sees payout status = Pending     │
│  5. Dashboard updates automatically! │
└──────────────────────────────────────┘
```

---

## Payout Confirmation Flow

```
┌──────────────────────────┐
│  Payouts Created         │
│  Status: PENDING         │
│  Amount: $49, $29.40, $19.60
└──────────┬───────────────┘
           │
           │ (Admin confirms via Swagger UI)
           │ http://localhost:8000/api/docs/
           │
           ▼ PUT /api/payouts/{id}/
           │ Body: {
           │   status: 2,
           │   blockchain_txn_id: "0x123abc..."
           │ }
           │
┌──────────▼─────────────────────────┐
│  Backend: Update Payout             │
│  1. Check admin auth                │
│  2. Set status = 2 (Confirmed)      │
│  3. Set blockchain_txn_id           │
│  4. Save to PostgreSQL              │
└──────────┬──────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Frontend Polls (Every 30 seconds)   │
│  GET /api/payouts/                  │
│  Response: status = 2 (Confirmed)   │
│  Dashboard displays: "✓ Confirmed"   │
│  Shows blockchain TXN ID             │
└──────────────────────────────────────┘
```

---

## Data Model Relationships

```
┌──────────────┐
│    User      │
├──────────────┤
│ id           │
│ email        │◄─────────────┐
│ password     │              │
│ name         │              │
│ created_at   │              │
└──────────────┘              │ 1:1
       │                      │
       │ 1:1                  │
       ▼                      │
┌──────────────┐    ┌────────▼───────┐
│   Wallet     │    │  Auth Token    │
├──────────────┤    ├────────────────┤
│ id           │    │ user_id        │
│ user_id      │    │ token (JWT)    │
│ balance      │    │ created_at     │
│ address      │    │ expires_at     │
└──────────────┘    └────────────────┘
       │
       │ 1:M
       ▼
┌──────────────────┐
│   Payout         │
├──────────────────┤
│ id               │
│ wallet_id        │
│ amount           │
│ status (1,2)     │
│ blockchain_txn_id│
│ created_at       │
└──────────────────┘


┌──────────────┐
│    Track     │
├──────────────┤
│ id           │
│ owner_id     │◄─────┐
│ title        │      │
│ duration     │      │ 1:M
│ genre        │      │
│ file_url     │      │
│ created_at   │      │
└──────────────┘      │
       │              │
       │ 1:M      ┌───┴─────────┐
       ▼          │   User      │
┌──────────────┐  ├─────────────┤
│    Split     │  │ id          │
├──────────────┤  │ email       │
│ id           │  └─────────────┘
│ track_id     │
│ user_id      │
│ percentage   │
├──────────────┤
│ Total Splits │
│ per track    │
│ must = 100%  │
└──────────────┘
       │
       │ 1:M
       ▼
┌──────────────────┐
│   Royalty        │
├──────────────────┤
│ id               │
│ track_id         │
│ total_earning    │
│ platform_fee     │
│ created_at       │
└──────────────────┘
```

---

## API Call Sequence Diagram

```
FRONTEND                        BACKEND
   │                               │
   │──── POST /api/register/ ─────→│
   │    {name, email, password}    │
   │                               │ Create User + Wallet
   │                               │ Hash password
   │                               │ Generate token
   │←─── 201 {token, user_id} ─────│
   │                               │
   │ [Store token in localStorage] │
   │                               │
   │──── GET /api/users/me/ ──────→│
   │    Header: Authorization      │
   │                               │ Validate token
   │←─── 200 {user data} ──────────│
   │                               │
   │──── POST /api/tracks/ ───────→│
   │    FormData: track data       │
   │                               │ Validate + Store
   │←─── 201 {track_id, ...} ─────│
   │                               │
   │──── POST /api/splits/ ───────→│
   │    For each collaborator      │
   │                               │ Validate splits
   │←─── 201 {split data} ────────│
   │                               │
   │ [Waits 30 seconds]            │
   │                               │
   │──── GET /api/wallets/me/ ────→│
   │                               │ Query database
   │←─── 200 {balance, ...} ──────│
   │                               │
   │──── GET /api/payouts/ ───────→│
   │                               │ Query database
   │←─── 200 [{payout1, ...}] ────│
   │                               │
   │ [Dashboard updates]           │
   │                               │
```

---

## Error Handling Flow

```
Frontend API Call
       │
       ▼
┌──────────────────┐
│  Response OK?    │
└────┬────────────┬┘
     │            │
    YES           NO
     │            │
     ▼            ▼
┌──────────┐  ┌─────────────────┐
│ Parse    │  │ Is 4xx/5xx?     │
│ JSON     │  └────┬────────┬────┘
│          │       │        │
│ Return   │      YES       NO
│ data     │       │        │
└──────────┘       ▼        ▼
                  ┌────┐  ┌────┐
                  │500 │  │401 │
                  │    │  │    │
                  ▼    ▼  ▼    ▼
               Show error message
               to user via Toast
               notification

               For 401: Logout user
               For 404: Show "Not found"
               For 500: Show "Server error"
```

---

## Database State After Complete Flow

```
BEFORE:
┌──────────────────┐
│  Empty Database  │
│  (schema only)   │
└──────────────────┘

AFTER (Complete Workflow):

Users:
┌──────┬───────────────┬─────────────────────┐
│ id   │ email         │ created_at          │
├──────┼───────────────┼─────────────────────┤
│ 1    │ artist1@ex.com│ 2025-11-30 10:00:00 │
│ 2    │ artist2@ex.com│ 2025-11-30 10:00:30 │
│ 3    │ artist3@ex.com│ 2025-11-30 10:00:45 │
└──────┴───────────────┴─────────────────────┘

Wallets:
┌──────┬─────────┬────────────────────┐
│ id   │ balance │ user_id            │
├──────┼─────────┼────────────────────┤
│ 1    │ $49.00  │ 1 (artist1)        │
│ 2    │ $29.40  │ 2 (artist2)        │
│ 3    │ $19.60  │ 3 (artist3)        │
└──────┴─────────┴────────────────────┘

Tracks:
┌──────┬────────────────────┬──────────┬──────────┐
│ id   │ title              │ duration │ owner_id │
├──────┼────────────────────┼──────────┼──────────┤
│ 1    │ Collaborative Song │ 10 min   │ 1        │
└──────┴────────────────────┴──────────┴──────────┘

Splits:
┌──────┬──────────┬─────────┬──────────────┐
│ id   │ track_id │ user_id │ percentage   │
├──────┼──────────┼─────────┼──────────────┤
│ 1    │ 1        │ 1       │ 50%          │
│ 2    │ 1        │ 2       │ 30%          │
│ 3    │ 1        │ 3       │ 20%          │
└──────┴──────────┴─────────┴──────────────┘
Total = 100% ✓

Royalties:
┌──────┬──────────┬──────────────┬──────────────┐
│ id   │ track_id │ total_earning│ platform_fee │
├──────┼──────────┼──────────────┼──────────────┤
│ 1    │ 1        │ $100.00      │ $2.00 (2%)   │
└──────┴──────────┴──────────────┴──────────────┘

Payouts:
┌──────┬──────────┬──────────┬────────┬─────────────────┐
│ id   │ wallet_id│ amount   │ status │ blockchain_txn_id│
├──────┼──────────┼──────────┼────────┼─────────────────┤
│ 1    │ 1        │ $49.00   │ 2      │ 0x123abc...     │
│ 2    │ 2        │ $29.40   │ 2      │ 0x456def...     │
│ 3    │ 3        │ $19.60   │ 2      │ 0x789ghi...     │
└──────┴──────────┴──────────┴────────┴─────────────────┘
(1=Pending, 2=Confirmed)

TOTAL FLOW:
• 3 users created
• 1 track created  
• 3 splits configured
• $100 royalty earned
• $98 distributed ($2 platform fee)
• 3 payouts created + confirmed
• All users have money in wallet
• All transactions recorded on blockchain
```

---

## Current Status Dashboard

```
┌─────────────────────────────────────────────────┐
│         INTEGRATION STATUS: ✅ COMPLETE         │
├─────────────────────────────────────────────────┤
│                                                 │
│  COMPLETED ✓                                    │
│  ├─ API Service Layer (api.js)                 │
│  ├─ Authentication Integration                  │
│  ├─ Track Management Integration               │
│  ├─ Split Management Integration               │
│  ├─ Wallet Sync Integration                    │
│  ├─ Payout Display Integration                 │
│  ├─ Dashboard Real Data                        │
│  ├─ Token Management                           │
│  ├─ Error Handling                             │
│  ├─ Auto-polling (30 seconds)                  │
│  └─ Documentation (5 guides)                   │
│                                                 │
│  TESTED ✓                                       │
│  ├─ User Registration                          │
│  ├─ User Login                                 │
│  ├─ Track Creation                             │
│  ├─ Split Configuration                        │
│  ├─ Royalty Distribution                       │
│  ├─ Wallet Updates                             │
│  ├─ Payout Creation                            │
│  ├─ Payout Confirmation                        │
│  ├─ Multi-User Scenario                        │
│  └─ End-to-End Flow                            │
│                                                 │
│  READY FOR                                      │
│  ✓ Testing                                      │
│  ✓ Deployment                                   │
│  ✓ Production Use                              │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

**Created:** November 30, 2025  
**Status:** ✅ COMPLETE & TESTED  
**Ready For:** Live Testing
