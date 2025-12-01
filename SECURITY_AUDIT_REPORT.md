# Security Audit Report - Harmoniq Royalty Splitter

**Date:** December 1, 2025  
**Severity Summary:** 🔴 7 Critical | 🟠 5 High | 🟡 4 Medium | 🟢 2 Low

---

## 🔴 CRITICAL ISSUES

### 1. **Hardcoded Secret Key & Credentials in Settings** (CRITICAL)
**Location:** `royalty_splitter/settings.py` lines 25, 130-135

**Issues:**
```python
# ❌ INSECURE - Hardcoded secret key
SECRET_KEY = "django-insecure-(3^9pm=j#13&w07ovwf5*@2hs-0c$##dl-2f&0=co4ye-m1#z4"

# ❌ INSECURE - Hardcoded database credentials
'PASSWORD': os.environ.get('POSTGRES_PASSWORD', '1234qax'),  # Default fallback!
```

**Risk:** 
- Secret key compromises token signing for all users
- Database credentials in default fallback allow unauthorized access
- Code exposed on GitHub = immediate compromise

**Recommendations:**
```python
# ✅ SECURE - Use environment variables only
from django.core.management.utils import get_random_secret_key

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set")

# ✅ For production, enforce environment variable
'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
if not os.environ.get('POSTGRES_PASSWORD'):
    raise ValueError("POSTGRES_PASSWORD must be set")
```

---

### 2. **Debug Mode Enabled in Production** (CRITICAL)
**Location:** `royalty_splitter/settings.py` line 27

**Issue:**
```python
DEBUG = True  # ❌ NEVER in production!
```

**Risk:**
- Leaks full stack traces with sensitive paths and code
- Exposes environment variables in error pages
- Detailed SQL queries visible to attackers
- Database structure exposed

**Recommendation:**
```python
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
```

---

### 3. **Auth Token Stored in Plain localStorage** (CRITICAL)
**Location:** `Harmoniq/src/context/AuthContext.js`, `Harmoniq/src/services/api.js`

**Issue:**
```javascript
// ❌ INSECURE - Token in plain text localStorage
export const setAuthToken = (token) => {
  localStorage.setItem('auth_token', token);  // Accessible to XSS attacks!
};

// ❌ Retrieved and used in headers
const getToken = () => localStorage.getItem('auth_token');
const headers = { 'Authorization': `Token ${token}` };
```

**Risk:**
- XSS attacks can steal token: `localStorage.getItem('auth_token')`
- Token persists after logout (if not cleared)
- No expiration, token remains valid indefinitely
- Token visible in JavaScript debugger

**Recommendation:**
- Use **httpOnly cookies** (inaccessible to JavaScript)
- Implement token expiration & refresh tokens
- Set `secure` flag for HTTPS only
- Set `sameSite=Strict` to prevent CSRF

---

### 4. **Password Stored in Plain Text (localStorage)** (CRITICAL)
**Location:** `Harmoniq/src/context/AuthContext.js` lines 22-24, 67

**Issue:**
```javascript
// ❌ INSECURE - Password saved to localStorage
const newUser = {
  password,  // Plain text in browser storage!
  // ...
};
localStorage.setItem('harmoniq_users', JSON.stringify(users));  // Includes password!

// ❌ Later used in plaintext comparison
const foundUser = users.find(u => u.email === email && u.password === password);
```

**Risk:**
- Passwords exposed if device is compromised
- Local storage is accessible to any script
- No hashing or encryption
- Browser DevTools shows all passwords

**Recommendation:**
- **NEVER** store passwords client-side
- Use backend authentication ONLY
- Remove password handling from AuthContext completely
- Backend MUST hash passwords with bcrypt/Argon2

---

### 5. **No CSRF Protection for State-Changing Operations** (CRITICAL)
**Location:** Django MIDDLEWARE - `cors_middleware` before CSRF middleware

**Issue:**
```python
# ❌ CORS before CSRF means credentials allowed from any origin
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # ← BEFORE CSRF!
    "django.middleware.csrf.CsrfViewMiddleware",
]
```

**Risk:**
- CORS middleware processes requests before CSRF validation
- POST/PUT/DELETE requests vulnerable to CSRF attacks
- Attacker site can make authenticated requests on behalf of user

**Recommendation:**
```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",  # After CORS
    # ... rest
]

# Add CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Enforce CSRF for API
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'CSRF_FAILURE_VIEW': 'api.views.csrf_failure',  # Custom handler
}
```

---

### 6. **No Rate Limiting on Auth Endpoints** (CRITICAL)
**Location:** `api/auth_views.py` lines 43, 87

**Issue:**
```python
@api_view(['POST'])
@permission_classes([AllowAny])
def get_auth_token(request):  # ❌ No rate limit!
    # Can brute force passwords

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):  # ❌ No rate limit!
    # Can create infinite accounts
```

**Risk:**
- Brute force password attacks (millions of attempts)
- Account enumeration
- Registration spam / DOS attack
- No account lockout after failed attempts

**Recommendation:**
```python
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class AuthThrottle(AnonRateThrottle):
    scope = 'auth'
    rate = '5/minute'  # 5 attempts per minute per IP

# In settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'auth': '5/minute',
    }
}

# Apply to endpoints
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthThrottle])
def get_auth_token(request):
    # Now rate limited
```

---

### 7. **Frontend Register Password Validation Too Weak** (CRITICAL)
**Location:** `Harmoniq/src/app/register/page.js` line 16-18

**Issue:**
```javascript
// ❌ Only checks length >= 6!
if (formData.password.length < 6) {
    return addToast("Password too short", "error");
}
```

**Risk:**
- Backend validates 8 chars minimum, frontend only 6 (inconsistent!)
- Simple passwords like "123456" accepted
- No complexity requirements (uppercase, numbers, symbols)
- Weak passwords vulnerable to dictionary attacks

**Recommendation:**
```javascript
const validatePassword = (password) => {
  const requirements = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    numbers: /\d/.test(password),
    special: /[!@#$%^&*]/.test(password),
  };
  return requirements;
};

if (formData.password.length < 8 || 
    !/[A-Z]/.test(formData.password) ||
    !/\d/.test(formData.password)) {
  return addToast("Password must be 8+ chars with uppercase & number", "error");
}
```

---

## 🟠 HIGH SEVERITY ISSUES

### 8. **No Input Validation on File Uploads** (HIGH)
**Location:** `Harmoniq/src/app/tracks/page.js` (file upload handler)

**Issue:**
```javascript
// Only checks MIME type (easily spoofed)
if (!file.type.startsWith('image/')) {
    return addToast("Select image", "error");
}
// Size check only on frontend (can be bypassed)
if (file.size > 50 * 1024 * 1024) {}
```

**Risk:**
- MIME type can be spoofed by attacker
- Malicious files labeled as images (e.g., .exe with image/ MIME)
- Large files DOS the server (no backend validation)
- No file extension validation

**Recommendation:**
```javascript
// Frontend validation (user experience)
const validateFile = (file) => {
  const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
  const MAX_SIZE = 5 * 1024 * 1024;
  const ALLOWED_EXT = ['.jpg', '.jpeg', '.png', '.webp'];
  
  if (!ALLOWED_TYPES.includes(file.type)) return false;
  if (file.size > MAX_SIZE) return false;
  
  const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
  if (!ALLOWED_EXT.includes(ext)) return false;
  
  return true;
};

// Backend validation (CRITICAL - in Django):
from django.core.files.uploadedfile import UploadedFile
import magic  # python-magic for real MIME type

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_image(request):
    file = request.FILES.get('profile_image')
    
    # Size limit
    if file.size > 5 * 1024 * 1024:
        return Response({'error': 'File too large'}, status=400)
    
    # Real MIME type check
    mime = magic.from_buffer(file.read(1024), mime=True)
    if mime not in ['image/jpeg', 'image/png', 'image/webp']:
        return Response({'error': 'Invalid file type'}, status=400)
    
    # Scan with antivirus if available
    # clamscan(file.path)
```

---

### 9. **No Authentication on Public Endpoints** (HIGH)
**Location:** `Harmoniq/src/app/tracks/page.js`, `Harmoniq/src/app/profile/page.js`

**Issue:**
- Profile endpoint shows user data without ownership check
- Track data endpoint returns all user tracks
- No verification that requester = resource owner

**Risk:**
- User A can see User B's profile by changing URL
- User A can download User B's tracks
- User A can see financial data of User B

**Recommendation:**
```python
# In backend viewsets
class TrackViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        # Only return tracks owned by current user
        return Track.objects.filter(owner=self.request.user)

class ProfileViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get', 'put'])
    def me(self, request):
        # Only return current user's profile
        if request.user != requested_user:
            return Response({'error': 'Forbidden'}, status=403)
```

---

### 10. **No Input Sanitization on User Inputs** (HIGH)
**Location:** Multiple pages (name, email, track title)

**Issue:**
```javascript
// No sanitization before storing or displaying
const [name, setName] = useState(formData.name);  // Could contain XSS
```

**Risk:**
- XSS injection via name/email fields
- HTML injection in track titles
- JavaScript execution in user data display

**Recommendation:**
```javascript
import DOMPurify from 'dompurify';

// Sanitize user input
const sanitizeName = (name) => DOMPurify.sanitize(name);

// On backend - Django
from django.utils.html import escape
from rest_framework.validators import ValidationError

def validate_name(value):
    clean_name = escape(value)  # Escape HTML
    if len(clean_name) < 2 or len(clean_name) > 100:
        raise ValidationError("Name must be 2-100 chars")
```

---

### 11. **No HTTPS Enforcement** (HIGH)
**Location:** `royalty_splitter/settings.py`, Docker setup

**Issue:**
- Development runs on HTTP only
- No SECURE_SSL_REDIRECT
- No HSTS headers
- Cookies not marked SECURE

**Risk:**
- Man-in-the-middle attacks
- Token/credentials intercepted on public WiFi
- Session hijacking possible

**Recommendation:**
```python
# In settings.py for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Strict-Transport-Security header
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Frontend should also enforce HTTPS
    # Update next.config.mjs
```

---

### 12. **Exposed API Documentation** (HIGH)
**Location:** `royalty_splitter/settings.py` line 63

**Issue:**
```python
'SERVE_INCLUDE_SCHEMA': False,  # ✅ Good, but...
# If True, would expose full API schema with field names
```

**Risk:**
- Full API structure exposed (even if False, can be discovered)
- Endpoint enumeration
- Information disclosure

**Recommendation:**
- Keep `SERVE_INCLUDE_SCHEMA: False`
- Use `.env` to control schema exposure
- Implement IP whitelist for admin/schema endpoints

---

## 🟡 MEDIUM SEVERITY ISSUES

### 13. **No Account Lockout After Failed Login** (MEDIUM)
**Location:** `api/auth_views.py` lines 57-71

**Issue:**
```python
# ❌ No account lockout
def get_auth_token(request):
    try:
        user = UserAccount.objects.get(email=email)
        if user.check_password(password):  # ✓ Correct
            # Success
        else:
            return Response({'error': 'Invalid credentials'})  # ❌ No lockout
```

**Risk:**
- Unlimited brute force attempts
- No notifications to user of failed attempts
- Account takeover after enough attempts

**Recommendation:**
```python
from django.contrib.auth.models import update_last_login
from datetime import timedelta
from django.utils import timezone

class FailedLoginAttempt(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    attempted_at = models.DateTimeField(auto_now_add=True)

def get_auth_token(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    try:
        user = UserAccount.objects.get(email=email)
        
        # Check if locked out
        recent_attempts = FailedLoginAttempt.objects.filter(
            user=user,
            attempted_at__gte=timezone.now() - timedelta(minutes=15)
        ).count()
        
        if recent_attempts >= 5:
            return Response(
                {'error': 'Too many attempts. Try again in 15 minutes.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        if user.check_password(password):
            # Clear failed attempts
            FailedLoginAttempt.objects.filter(user=user).delete()
            # ... return token
        else:
            FailedLoginAttempt.objects.create(user=user)
            return Response({'error': 'Invalid credentials'}, status=401)
            
    except UserAccount.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=401)
```

---

### 14. **No OAuth2 / Social Login** (MEDIUM)
**Issue:** Only email/password auth, no 2FA, no social providers

**Recommendation:**
```bash
pip install social-auth-app-django
# Add Google, GitHub OAuth providers
# Implement backup codes for 2FA
```

---

### 15. **Insufficient Error Handling** (MEDIUM)
**Location:** Multiple API endpoints

**Issue:**
```python
# ❌ Generic error might leak info
except Exception as e:
    return Response({'error': str(e)})  # Exposes implementation details
```

**Recommendation:**
```python
# ✅ Log internally, return generic message
import logging
logger = logging.getLogger(__name__)

try:
    # ... code
except Exception as e:
    logger.error(f"Auth error: {e}", exc_info=True)
    return Response(
        {'error': 'Authentication failed'},
        status=status.HTTP_401_UNAUTHORIZED
    )
```

---

### 16. **No CORS Origin Whitelist Strict Enough** (MEDIUM)
**Location:** `royalty_splitter/settings.py` line 182-187

**Issue:**
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",      # ✓ Good
    "http://127.0.0.1:3000",      # Duplicate
    "http://localhost:3001",      # Old frontend
    "http://127.0.0.1:3001",      # Duplicate
]
CORS_ALLOW_CREDENTIALS = True  # ⚠️ Allows credentials with CORS
```

**Risk:**
- Allows credentials from any whitelisted origin
- Old frontend included unnecessarily

**Recommendation:**
```python
# Use environment-specific CORS
import os

CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

# Only allow credentials from specific origins
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
```

---

## 🟢 LOW SEVERITY ISSUES

### 17. **No Security Headers** (LOW)
**Location:** Django middleware

**Issue:**
- Missing X-Content-Type-Options
- Missing X-Frame-Options
- Missing Content-Security-Policy
- Missing Referrer-Policy

**Recommendation:**
```python
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "cdn.jsdelivr.net"),
    "style-src": ("'self'", "'unsafe-inline'"),
    "img-src": ("'self'", "data:", "https:"),
}

SECURE_CONTENT_SECURITY_POLICY_REPORT_ONLY = not DEBUG

SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
X_CONTENT_TYPE_OPTIONS = "nosniff"
REFERRER_POLICY = "strict-origin-when-cross-origin"
```

---

### 18. **No Logging / Audit Trail** (LOW)
**Location:** Django logging configuration

**Issue:**
- No security event logging
- No audit trail for sensitive operations
- Hard to detect breaches or attacks

**Recommendation:**
```python
# Add logging for security events
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/security.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
        },
    },
    'loggers': {
        'security': {
            'handlers': ['security'],
            'level': 'WARNING',
        },
    },
}

# Log failed logins, unauthorized access, etc.
```

---

## Summary & Action Items

### Immediate Actions (Before Production):
1. ✅ Move credentials to environment variables (.env file)
2. ✅ Disable DEBUG mode
3. ✅ Implement httpOnly cookies for auth tokens
4. ✅ Remove password handling from frontend
5. ✅ Add rate limiting to auth endpoints
6. ✅ Implement CSRF protection properly
7. ✅ Add input validation & sanitization

### Short Term (Week 1):
- Implement file upload backend validation
- Add account lockout mechanism
- Enable HTTPS & HSTS
- Add security headers
- Implement logging & monitoring

### Medium Term (Month 1):
- Implement 2FA support
- Add OAuth2 social login
- Implement token refresh mechanism
- Add vulnerability scanning in CI/CD
- Security audit by third party

### Long Term (Ongoing):
- Regular penetration testing
- Keep dependencies updated
- Monitor security advisories
- User education on security best practices

---

**Risk Level:** 🔴 **CRITICAL** - Not ready for production with real user data  
**Estimated Fix Time:** 2-3 weeks for all issues  
**Recommendation:** Fix critical issues before any public/production deployment
