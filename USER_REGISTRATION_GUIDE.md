# User Registration System - Complete Analysis & Fixes

## Problem Summary
The user registration endpoint was not working properly due to multiple issues:
1. Permission conflicts between two user viewsets
2. Weak validation in the serializer
3. APPEND_SLASH setting preventing POST requests without trailing slashes
4. Potential routing conflicts

## Solutions Applied

### 1. **Disabled APPEND_SLASH** ✅
**File:** `royalty_splitter/settings.py`
- Added `APPEND_SLASH = False` to prevent Django from redirecting POST requests
- Allows POST to `/api/users` (no trailing slash) without 500 errors

### 2. **Enhanced UserRegisterSerializer** ✅
**File:** `api/serializers/user.py`
- Added email uniqueness validation
- Added name validation (cannot be empty)
- Set password minimum length to 8 characters
- Made country field optional

### 3. **Fixed UserViewSet Permissions** ✅
**File:** `api/viewsets/user.py`
- Allow anonymous access for user registration (create action)
- Require authentication for other actions (list, retrieve, update, delete)
- Uses `UserRegisterSerializer` for user creation
- Uses `UserAccountSerializer` for other operations

### 4. **Architecture Confirmation** ✅
**Key Points:**
- Only `api/urls.py` is included in main `royalty_splitter/urls.py`
- Backend has its own router in `backend/urls.py` but it's NOT registered in main urls
- This prevents routing conflicts
- User signals in `backend/signals.py` auto-creates a Wallet when a UserAccount is created

## How to Test

### Using Postman:

**1. Register a New User**
- **Method:** POST
- **URL:** `http://localhost:8000/api/users/` (note the trailing slash)
- **Headers:** 
  - `Content-Type: application/json`
- **Body (JSON):**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "country": "USA"
}
```
- **Expected Response:** 201 Created
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "country": "USA"
}
```

**2. Verify Wallet was Created**
- Get auth token first (you'll need to implement login/token endpoint)
- **Method:** GET
- **URL:** `http://localhost:8000/api/wallets/1/`
- **Headers:** 
  - `Authorization: Token <your_token>`
- **Expected Response:** Wallet with balance = 0

### Using cURL:

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "password": "securepassword456",
    "country": "Canada"
  }'
```

## Field Requirements

| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| name | String | Yes | Cannot be empty |
| email | String | Yes | Must be unique, valid email format |
| password | String | Yes | Minimum 8 characters |
| country | String | No | Can be blank |

## What Happens After Registration

1. User is created in database
2. Password is automatically hashed using Django's authentication system
3. A Wallet is automatically created for the user (via signal)
4. User can now authenticate using their email and password
5. User can access authenticated endpoints

## Related Endpoints

Once registered, users can access:

- `GET /api/users/` - List all users (requires auth)
- `GET /api/users/{id}/` - Get user details (requires auth)
- `PUT /api/users/{id}/` - Update user (requires auth)
- `DELETE /api/users/{id}/` - Delete user (requires auth)
- `POST /api/tracks/` - Create a track (requires auth)
- `POST /api/wallets/` - Create wallet (requires auth)
- etc.

## Troubleshooting

### Error: "This email is already registered."
- Solution: Use a different email address that hasn't been registered yet

### Error: "Name cannot be empty."
- Solution: Provide a valid name (non-empty string)

### Error: "Ensure this field has at least 8 characters."
- Solution: Use a password with at least 8 characters

### Error: "POST /api/users HTTP/1.1 500"
- Solution: Make sure you have `APPEND_SLASH = False` in settings.py (already applied)

### Error: "404 Not Found"
- Solution: Ensure you're using the correct URL with trailing slash: `/api/users/`

## Files Modified

1. `royalty_splitter/settings.py` - Added APPEND_SLASH = False
2. `api/serializers/user.py` - Enhanced UserRegisterSerializer validation
3. `api/viewsets/user.py` - Improved permissions and documentation

## No Changes Needed In

- `backend/models.py` - UserAccount model is correct
- `backend/signals.py` - Wallet auto-creation is working
- `api/urls.py` - Routing is correct
- `royalty_splitter/urls.py` - Main URL configuration is correct
