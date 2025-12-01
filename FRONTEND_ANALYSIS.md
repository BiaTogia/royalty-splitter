# Frontend Analysis: Royalty Splitter Web App

**Date:** November 30, 2025  
**Framework:** Next.js 16.0.5 + React 19.2.0  
**Status:** Development (Unstable Build - Local Storage Only)

---

## 1. Architecture Overview

### Tech Stack
- **Framework:** Next.js 16.0.5 (App Router)
- **Frontend:** React 19.2.0
- **Styling:** Tailwind CSS 4
- **3D Graphics:** Three.js + React Three Fiber
- **UI Components:** Lucide React (Icons)
- **State Management:** React Context API
- **Storage:** LocalStorage (Development only, NOT connected to backend)

### Project Structure
```
src/
├── app/                          # Next.js app router pages
│   ├── page.js                   # Home page
│   ├── layout.js                 # Root layout with providers
│   ├── login/page.js            # Login page
│   ├── register/page.js         # Register page
│   ├── dashboard/page.js        # Main dashboard
│   ├── tracks/page.js           # Track management (upload, splits)
│   ├── profile/page.js          # User profile (not analyzed)
│   ├── history/page.js          # Transaction history (not analyzed)
│   ├── features/page.js         # Features page (not analyzed)
│   ├── support/page.js          # Support page (not analyzed)
│   └── about/page.js            # About page (not analyzed)
├── components/                   # Reusable React components
│   ├── Navbar.jsx
│   ├── DashboardStats.jsx       # Card component for stats
│   ├── RevemueChart.jsx         # Chart visualization
│   └── Hero3D.jsx               # 3D animation (not analyzed)
└── context/                      # React Context for state
    ├── AuthContext.js           # User authentication (localStorage)
    ├── AppDataContext.js        # App data & royalty simulation
    └── ToastContext.js          # Toast notifications (not analyzed)
```

---

## 2. Frontend Implementation vs Backend

### 🔴 CRITICAL ISSUE: Frontend is NOT Connected to Backend

**Current State:**
```
Frontend ← → LocalStorage (only)
Backend   ← → PostgreSQL Database
```

**Frontend stores data in:**
```javascript
localStorage.setItem('harmoniq_users', JSON.stringify(users))
localStorage.setItem('harmoniq_currentUser', JSON.stringify(user))
localStorage.setItem(`harmoniq_tracks_${userId}`, JSON.stringify(tracks))
localStorage.setItem(`harmoniq_transactions_${userId}`, JSON.stringify(transactions))
localStorage.setItem(`harmoniq_balance_${userId}`, JSON.stringify(balance))
```

**Backend API endpoints exist but frontend never calls them:**
```
POST   /api/token/                    ← Frontend calls localStorage instead
POST   /api/register/                 ← Frontend uses localStorage
GET    /api/wallets/me/               ← Frontend uses localStorage
POST   /api/tracks/                   ← Frontend uses localStorage
POST   /api/splits/                   ← Frontend uses localStorage
GET    /api/payouts/                  ← Frontend uses localStorage
```

---

## 3. Frontend Feature Breakdown

### 3.1 Authentication (AuthContext.js)

**Implementation:**
```javascript
// Currently: localStorage-based
const register = (name, email, password) => {
  // Stores user in localStorage
  // NO API call to backend
}

const login = (email, password) => {
  // Validates against localStorage users
  // NO API call to /api/token/
}
```

**What It Should Do:**
```javascript
// Correct: Call backend API
const login = async (email, password) => {
  const response = await fetch('http://localhost:8000/api/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  return data.token; // Store this token for auth
}
```

**Missing:**
- ❌ No API calls to `/api/token/`
- ❌ No JWT/Token handling
- ❌ No persistent backend authentication
- ❌ No token refresh logic

---

### 3.2 Track Management (tracks/page.js)

**Current Frontend Logic:**
```javascript
const handleUpload = () => {
  // Creates track object locally
  const newTrack = {
    title: formData.title,
    splits: splits,  // User-defined splits
    status: "Live"
  };
  
  // Stores ONLY in localStorage
  addTrack(newTrack);
  
  // NO API call to POST /api/tracks/
}
```

**Track Creation Flow:**
```
User fills form
    ↓
Validates local splits (must = 100%)
    ↓
Creates track object
    ↓
Saves to localStorage (ENDS HERE)
    ↓
❌ NOT sent to backend database
❌ NOT recorded in API
❌ NOT available to other users
```

**Splits Handling:**
```javascript
// Frontend captures splits like this:
const [splits, setSplits] = useState([
  { id: 1, name: 'Me (Owner)', wallet: '0x123...', pct: 100 },
  // User adds more collaborators...
]);

// But these are NEVER:
// ❌ Sent to /api/splits/ endpoint
// ❌ Validated by backend
// ❌ Stored in database
// ❌ Shared with collaborators
```

**Missing:**
- ❌ No API call to `POST /api/tracks/`
- ❌ No file upload handling
- ❌ No split registration with backend
- ❌ No track owner verification
- ❌ No duration/metadata server-side validation

---

### 3.3 Dashboard & Simulated Data (AppDataContext.js)

**Current Implementation:**
```javascript
// Simulates royalty income every 3 seconds
useEffect(() => {
  const interval = setInterval(() => {
    const randomTrack = tracks[Math.floor(Math.random() * tracks.length)];
    generateStreamEvent(randomTrack);
  }, 3000); // Every 3 seconds
  
  return () => clearInterval(interval);
}, [tracks]);
```

**What Gets Simulated:**
- ✅ Stream events from random platforms (Spotify, Apple Music, YouTube, Tidal)
- ✅ Platform-specific payout rates (Spotify: $0.004, Apple: $0.01, etc.)
- ✅ Wallet balance updates
- ✅ Live event feed animation
- ✅ Monthly revenue chart data

**Dashboard Stats Displayed:**
```javascript
{
  totalBalance: calculated_locally,        // ❌ Not from backend
  totalStreams: simulated_count,           // ❌ Not real API data
  activeTracks: localStorage_count,        // ❌ Not synced with backend
  collaborators: split_count               // ❌ Not from backend database
}
```

**Missing:**
- ❌ No API call to `GET /api/wallets/me/`
- ❌ No real royalty data from backend
- ❌ No payout history from backend
- ❌ No actual stream events
- ❌ No real-time data sync

**Platform Rates (Hardcoded):**
```javascript
const platforms = [
  { name: "Spotify", rate: 0.004, color: "#1DB954" },
  { name: "Apple Music", rate: 0.01, color: "#FA243C" },
  { name: "YouTube", rate: 0.002, color: "#FF0000" },
  { name: "Tidal", rate: 0.0125, color: "#000000" },
];
```
*Note: Backend uses $10/minute rate, not platform-based rates*

---

### 3.4 Pages Summary

| Page | Status | Connected to Backend? |
|------|--------|----------------------|
| **login** | ✅ Working | ❌ No - localStorage only |
| **register** | ✅ Working | ❌ No - localStorage only |
| **dashboard** | ✅ Working | ❌ No - simulated data only |
| **tracks** | ✅ Working | ❌ No - localStorage only |
| **profile** | 🟡 Incomplete | ❌ No |
| **history** | 🟡 Incomplete | ❌ No |
| **features** | 🟡 Incomplete | ❌ No |
| **support** | 🟡 Incomplete | ❌ No |
| **about** | 🟡 Incomplete | ❌ No |

---

## 4. Data Flow Comparison

### Backend Money Flow (REAL)
```
User registers → /api/register/
               ↓
Login → /api/token/ (get token)
               ↓
Create track → /api/tracks/ + file upload
               ↓
Setup splits → /api/splits/
               ↓
Royalty distribution (backend calculates)
               ↓
Wallet updates → /api/wallets/me/
               ↓
Payout creation → /api/payouts/
               ↓
Admin confirmation → PUT /api/payouts/{id}/
```

### Frontend Money Flow (FAKE/LOCAL)
```
User registers → localStorage (no API)
               ↓
Login → localStorage lookup (no API)
               ↓
Create track → localStorage (no API)
               ↓
Setup splits → localStorage (no API)
               ↓
Simulated stream event every 3 seconds
               ↓
Wallet balance += random_amount (no API)
               ↓
Transaction created locally (no API)
               ↓
❌ Never syncs with backend
```

---

## 5. API Integration Gaps

### Missing API Calls

| Backend Endpoint | Frontend Status |
|-----------------|-----------------|
| `POST /api/token/` | ❌ Not called |
| `POST /api/register/` | ❌ Not called |
| `GET /api/users/me/` | ❌ Not called |
| `POST /api/tracks/` | ❌ Not called |
| `GET /api/tracks/` | ❌ Not called |
| `POST /api/splits/` | ❌ Not called |
| `GET /api/wallets/me/` | ❌ Not called |
| `PUT /api/wallets/{id}/` | ❌ Not called |
| `GET /api/payouts/` | ❌ Not called |
| `POST /api/payouts/` | ❌ Not called |
| `PUT /api/payouts/{id}/` | ❌ Not called |

### Missing Features
- ❌ Real authentication tokens
- ❌ Real track persistence
- ❌ Real split verification
- ❌ Real royalty calculations
- ❌ Real payout management
- ❌ Real wallet balances
- ❌ Real transaction history
- ❌ Multi-user collaboration
- ❌ Blockchain transaction recording
- ❌ Admin payout confirmation workflow

---

## 6. LocalStorage Schema

### Current Frontend Storage Structure

```javascript
// Users database (global)
localStorage['harmoniq_users'] = [
  {
    id: 1234567890,
    name: "Artist Name",
    email: "artist@example.com",
    password: "plaintext_password", // ⚠️ Security issue!
    type: "Artist",
    createdAt: "2025-11-30T10:00:00Z"
  }
]

// Current user (global)
localStorage['harmoniq_currentUser'] = {
  id: 1234567890,
  name: "Artist Name",
  email: "artist@example.com",
  type: "Artist"
}

// Per-user tracks
localStorage['harmoniq_tracks_1234567890'] = [
  {
    id: 1234567890,
    title: "Song Title",
    role: "Master",
    splits: [
      { id: 1, name: 'Me (Owner)', wallet: '0x123...', pct: 100 }
    ],
    status: "Live",
    createdAt: "2025-11-30T10:00:00Z",
    totalEarnings: 0,
    streamCount: 0
  }
]

// Per-user transactions
localStorage['harmoniq_transactions_1234567890'] = [
  {
    id: 1234567890,
    track: "Song Title",
    source: "Spotify",
    amount: "+$0.004",
    status: "Paid",
    date: "2025-11-30T10:00:00Z"
  }
]

// Per-user balance
localStorage['harmoniq_balance_1234567890'] = "1250.50"

// Per-user streams count
localStorage['harmoniq_totalStreams_1234567890'] = "5000"

// Per-user monthly chart data
localStorage['harmoniq_chartData_1234567890'] = [
  100, 120, 150, 200, 180, 220, 250, 280, 300, 350, 400, 450
]
```

---

## 7. Security Issues

### ⚠️ Critical Issues

1. **Plaintext Passwords**
   ```javascript
   // Frontend stores plaintext passwords in localStorage
   const newUser = {
     password: password  // ⚠️ NEVER do this!
   };
   ```

2. **No Token Authentication**
   - No JWT tokens
   - No token refresh
   - No authorization headers on API calls (because no API calls)

3. **Client-Side Only Validation**
   - Split percentages validated only on frontend
   - No backend verification
   - User could manually edit localStorage to bypass checks

4. **No Encryption**
   - All data stored as plain JSON in localStorage
   - Accessible via browser console
   - No data privacy

5. **Cross-Tab Sync Issues**
   - If user opens 2 tabs, changes in one don't sync to other
   - No real-time synchronization
   - Data conflicts possible

---

## 8. Simulated Data Features

### Stream Simulation Logic

```javascript
// Every 3 seconds, generate a random stream event
const generateStreamEvent = (track) => {
  // 1. Pick random platform
  const platform = platforms[Math.floor(Math.random() * platforms.length)];
  
  // 2. Get platform rate
  const earnings = platform.rate;  // e.g., 0.004 for Spotify
  
  // 3. Add to live events feed (top 5 only)
  setLiveEvents(prev => [liveEvent, ...prev.slice(0, 4)]);
  
  // 4. Update total streams counter
  setTotalStreams(prev => prev + 1);
  
  // 5. Update wallet balance
  setBalance(prev => prev + earnings);
  
  // 6. Update monthly chart
  const currentMonth = new Date().getMonth();
  setChartData(prev => {
    const newData = [...prev];
    newData[currentMonth] += earnings;
    return newData;
  });
  
  // 7. Create transaction (10% chance)
  if (Math.random() > 0.9) {
    // Create transaction every ~10 streams
  }
}
```

### Rate Comparison

**Frontend Rates (Hardcoded):**
```
Spotify:      $0.004 per stream
Apple Music:  $0.01 per stream
YouTube:      $0.002 per stream
Tidal:        $0.0125 per stream
```

**Backend Rate (Actual):**
```
All tracks:   $10.00 per minute
              = $10 / 60 = $0.1667 per second
              = $0.1667 × duration_seconds
```

*Completely different calculation model!*

---

## 9. Component Analysis

### DashboardCard.jsx
```javascript
// Purpose: Reusable stat card component
// Props: title, value, subtext, icon, colorClass, delay
// Features: 
//   - Glow animation on hover
//   - Color theming (neon-cyan or neon-purple)
//   - Staggered animation delays
// Status: ✅ Frontend complete, no backend integration
```

### RevemueChart.jsx
```javascript
// Purpose: Display monthly revenue chart
// Features:
//   - Bar chart visualization
//   - Hover tooltips
//   - Gradient bars
//   - Month labels
// Data Source: chartData from AppDataContext (localStorage)
// Status: ✅ UI complete, ❌ no real data
```

### Navbar.jsx
```javascript
// Status: Not analyzed (assumed navigation menu)
```

### Hero3D.jsx
```javascript
// Status: Not analyzed (assumed 3D animation component)
```

---

## 10. What Needs to Be Built/Fixed

### Phase 1: Backend Integration (CRITICAL)
- [ ] Replace localStorage with API calls in AuthContext
- [ ] Implement token-based authentication
- [ ] Connect register page to `POST /api/register/`
- [ ] Connect login page to `POST /api/token/`
- [ ] Store and use JWT tokens in headers
- [ ] Add token refresh logic

### Phase 2: Track Management Integration
- [ ] Connect tracks page to `POST /api/tracks/`
- [ ] Implement file upload for audio files
- [ ] Fetch tracks from `GET /api/tracks/`
- [ ] Connect split creation to `POST /api/splits/`
- [ ] Add delete track functionality via API
- [ ] Implement real track ownership verification

### Phase 3: Dashboard Real Data
- [ ] Replace simulated data with `GET /api/wallets/me/`
- [ ] Fetch real royalties from `GET /api/royalties/`
- [ ] Fetch real payouts from `GET /api/payouts/`
- [ ] Fetch real transaction history
- [ ] Display real wallet balance
- [ ] Show actual stream/earning data from backend

### Phase 4: Payout Management
- [ ] Create payout request UI
- [ ] Connect to `POST /api/payouts/`
- [ ] Display payout status history
- [ ] Show confirmation workflow
- [ ] Add blockchain TXN ID display

### Phase 5: Additional Features
- [ ] Real-time data sync (WebSocket or polling)
- [ ] User profile management
- [ ] Transaction history page
- [ ] Search and filtering
- [ ] Export functionality
- [ ] Multi-language support

---

## 11. Code Examples: What Needs to Change

### Example 1: Login Integration

**Current (Wrong):**
```javascript
const login = (email, password) => {
  const users = JSON.parse(localStorage.getItem('harmoniq_users') || '[]');
  const foundUser = users.find(u => u.email === email && u.password === password);
  if (!foundUser) return { success: false, message: "Invalid email or password" };
  setUser(userSession);
  return { success: true };
};
```

**Should Be:**
```javascript
const login = async (email, password) => {
  try {
    const response = await fetch('http://localhost:8000/api/token/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    if (!response.ok) {
      const error = await response.json();
      return { success: false, message: error.message };
    }
    
    const data = await response.json();
    
    // Store token in localStorage (not password!)
    localStorage.setItem('auth_token', data.token);
    
    // Store user info
    setUser({
      id: data.user_id,
      email: data.email
    });
    
    return { success: true, token: data.token };
  } catch (error) {
    return { success: false, message: error.message };
  }
};
```

### Example 2: Track Upload Integration

**Current (Wrong):**
```javascript
const handleUpload = () => {
  const newTrack = { title: formData.title, splits: splits };
  addTrack(newTrack);  // Saves to localStorage only
};
```

**Should Be:**
```javascript
const handleUpload = async () => {
  const token = localStorage.getItem('auth_token');
  
  const response = await fetch('http://localhost:8000/api/tracks/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      title: formData.title,
      duration: formData.duration,
      genre: formData.genre,
      splits: splits.map(s => ({ user: s.user_id, percentage: s.pct }))
    })
  });
  
  const data = await response.json();
  return data;
};
```

### Example 3: Dashboard Data Sync

**Current (Wrong):**
```javascript
// Simulates data every 3 seconds
useEffect(() => {
  const interval = setInterval(() => {
    generateStreamEvent(randomTrack);
  }, 3000);
  return () => clearInterval(interval);
}, [tracks]);
```

**Should Be:**
```javascript
// Fetch real data from backend
useEffect(() => {
  const fetchWalletData = async () => {
    const token = localStorage.getItem('auth_token');
    
    const response = await fetch('http://localhost:8000/api/wallets/me/', {
      headers: { 'Authorization': `Token ${token}` }
    });
    
    const data = await response.json();
    setBalance(data.balance);
  };
  
  fetchWalletData();
  
  // Poll every 30 seconds for updates
  const interval = setInterval(fetchWalletData, 30000);
  return () => clearInterval(interval);
}, []);
```

---

## 12. Dependencies Analysis

### Current Dependencies
```json
{
  "react": "19.2.0",           // ✅ Latest
  "next": "16.0.5",            // ✅ Latest
  "tailwindcss": "4",          // ✅ Latest
  "@react-three/fiber": "9.4.0", // ✅ 3D animations
  "lucide-react": "0.555.0"    // ✅ Icons
}
```

### Missing Dependencies
```json
{
  "axios": "^1.x",              // ⚠️ For API calls
  "js-cookie": "^3.x",          // ⚠️ For token management
  "@tanstack/react-query": "^5.x", // ⚠️ For caching API data
  "zustand": "^4.x",            // ⚠️ Alternative state management
  "socket.io-client": "^4.x"    // ⚠️ For real-time updates
}
```

---

## 13. Summary Table

| Aspect | Frontend Status | Backend Status | Connected? |
|--------|-----------------|-----------------|-----------|
| **Authentication** | ✅ Works locally | ✅ Token API ready | ❌ No |
| **User Registration** | ✅ LocalStorage | ✅ DRF API ready | ❌ No |
| **Track Creation** | ✅ LocalStorage | ✅ File upload ready | ❌ No |
| **Split Management** | ✅ LocalStorage | ✅ API ready | ❌ No |
| **Royalty Distribution** | ❌ Simulated | ✅ Real algorithm | ❌ No |
| **Payout System** | ❌ No UI | ✅ Full system | ❌ No |
| **Wallet Balance** | ✅ Simulated | ✅ API ready | ❌ No |
| **Dashboard** | ✅ Functional | ✅ Ready | ❌ No sync |
| **Real-time Updates** | ❌ No | ❌ No | ❌ No |
| **Security** | ⚠️ Poor | ✅ Good | ❌ No |

---

## 14. Recommendations

### Immediate Actions
1. **Prioritize Backend Integration** - Frontend is completely disconnected
2. **Create API Service Layer** - Centralize all API calls in a separate utility
3. **Implement Token Management** - Add proper JWT token handling
4. **Create .env Configuration** - Set backend API URL in environment variables
5. **Add Error Handling** - Handle API failures gracefully

### Architecture Improvements
1. **Use React Query** - For caching and synchronizing API data
2. **Implement WebSockets** - For real-time updates (optional)
3. **Create API Hooks** - Custom hooks for common API operations
4. **Add Loading States** - Show spinners during API calls
5. **Improve Error Messages** - Give users clear feedback

### Testing
1. **Unit Tests** - Test context providers and components
2. **Integration Tests** - Test API interactions
3. **E2E Tests** - Test complete workflows
4. **Mock API** - Use MSW for development

---

**Status:** Frontend is feature-complete but entirely disconnected from backend. Ready for integration work.
