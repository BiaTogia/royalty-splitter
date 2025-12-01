# Postman Guide - Getting Splits Data

## Overview
A **Split** represents how royalties for a track are distributed among different users. Each split defines:
- Which track it belongs to
- Which user gets a share
- What percentage of royalties they get (0-100%)

## Getting Splits - Multiple Methods

### Method 1: Get ALL Splits (List)

**Endpoint:**
```
GET http://localhost:8000/api/splits/
```

**Headers:**
```
Authorization: Token YOUR_AUTH_TOKEN
Content-Type: application/json
```

**Postman Steps:**
1. Create a new GET request
2. URL: `http://localhost:8000/api/splits/`
3. Go to **Headers** tab
4. Add:
   - Key: `Authorization` | Value: `Token 9aef40f2dce22950c5d6bbc5a39383382ababf66`
   - Key: `Content-Type` | Value: `application/json`
5. Click **Send**

**Response (200 OK):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "track_id": 1,
      "user": 1,
      "user_email": "alice@example.com",
      "percentage": 60.0
    },
    {
      "id": 2,
      "track_id": 1,
      "user": 2,
      "user_email": "bob@example.com",
      "percentage": 40.0
    }
  ]
}
```

---

### Method 2: Get Specific Split by ID

**Endpoint:**
```
GET http://localhost:8000/api/splits/{id}/
```

**Example:**
```
GET http://localhost:8000/api/splits/1/
```

**Postman Steps:**
1. Create a new GET request
2. URL: `http://localhost:8000/api/splits/1/`
3. Add same headers as above
4. Click **Send**

**Response (200 OK):**
```json
{
  "id": 1,
  "track_id": 1,
  "user": 1,
  "user_email": "alice@example.com",
  "percentage": 60.0
}
```

---

### Method 3: Get Splits for a Specific Track

**Endpoint:**
```
GET http://localhost:8000/api/splits/?track_id={id}
```

**Example:**
```
GET http://localhost:8000/api/splits/?track_id=1
```

**Postman Steps:**
1. Create a new GET request
2. URL: `http://localhost:8000/api/splits/`
3. Go to **Params** tab
4. Add:
   - Key: `track_id` | Value: `1`
5. Add headers
6. Click **Send**

**Response (200 OK):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "track_id": 1,
      "user": 1,
      "user_email": "alice@example.com",
      "percentage": 60.0
    },
    {
      "id": 2,
      "track_id": 1,
      "user": 2,
      "user_email": "bob@example.com",
      "percentage": 40.0
    }
  ]
}
```

---

### Method 4: Get Splits for a Specific User

**Endpoint:**
```
GET http://localhost:8000/api/splits/?user_id={id}
```

**Example:**
```
GET http://localhost:8000/api/splits/?user_id=1
```

**Postman Steps:**
1. Create a new GET request
2. URL: `http://localhost:8000/api/splits/`
3. Go to **Params** tab
4. Add:
   - Key: `user_id` | Value: `1`
5. Add headers
6. Click **Send**

---

### Method 5: Get Track WITH Its Splits

**Better approach:** Get a track which includes all its splits

**Endpoint:**
```
GET http://localhost:8000/api/tracks/{id}/
```

**Example:**
```
GET http://localhost:8000/api/tracks/1/
```

**Postman Steps:**
1. Create a new GET request
2. URL: `http://localhost:8000/api/tracks/1/`
3. Add headers with token
4. Click **Send**

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "My Song",
  "duration": 3.5,
  "genre": "pop",
  "release_date": "2025-11-29",
  "nft_id": null,
  "owner": 1,
  "owner_email": "alice@example.com",
  "file": "http://localhost:8000/media/tracks/my_song.mp3",
  "streams": [],
  "splits": [
    {
      "id": 1,
      "track_id": 1,
      "user": 1,
      "user_email": "alice@example.com",
      "percentage": 60.0
    },
    {
      "id": 2,
      "track_id": 1,
      "user": 2,
      "user_email": "bob@example.com",
      "percentage": 40.0
    }
  ],
  "royalties": []
}
```

---

## Creating a Split

**Endpoint:**
```
POST http://localhost:8000/api/splits/
```

**Headers:**
```
Authorization: Token YOUR_AUTH_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "track": 1,
  "user": 2,
  "percentage": 40
}
```

**Postman Steps:**
1. Create a new POST request
2. URL: `http://localhost:8000/api/splits/`
3. Go to **Headers** tab - add token & content-type
4. Go to **Body** tab - select **raw** - select **JSON**
5. Paste the JSON body above
6. Click **Send**

**Response (201 Created):**
```json
{
  "id": 2,
  "track_id": 1,
  "user": 2,
  "user_email": "bob@example.com",
  "percentage": 40
}
```

---

## Updating a Split

**Endpoint:**
```
PUT http://localhost:8000/api/splits/{id}/
```

**Example:**
```
PUT http://localhost:8000/api/splits/1/
```

**Headers:**
```
Authorization: Token YOUR_AUTH_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "track": 1,
  "user": 1,
  "percentage": 75
}
```

**Postman Steps:**
1. Create a new PUT request
2. URL: `http://localhost:8000/api/splits/1/`
3. Add headers
4. Go to **Body** - raw - JSON
5. Paste body with new percentage
6. Click **Send**

---

## Deleting a Split

**Endpoint:**
```
DELETE http://localhost:8000/api/splits/{id}/
```

**Example:**
```
DELETE http://localhost:8000/api/splits/1/
```

**Headers:**
```
Authorization: Token YOUR_AUTH_TOKEN
```

**Postman Steps:**
1. Create a new DELETE request
2. URL: `http://localhost:8000/api/splits/1/`
3. Add token header
4. Click **Send**

**Response (204 No Content):**
```
(empty response)
```

---

## Split Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Split record ID |
| `track_id` | Integer | ID of the track |
| `user` | Integer | ID of the user getting share |
| `user_email` | String | Email of the user (read-only) |
| `percentage` | Float | Royalty percentage (0-100) |

---

## Complete Workflow Example

### Step 1: Get All Tracks
```
GET http://localhost:8000/api/tracks/
Authorization: Token YOUR_TOKEN
```

### Step 2: View Splits for Track #1
```
GET http://localhost:8000/api/tracks/1/
Authorization: Token YOUR_TOKEN
```
(See all splits in the `splits` array)

### Step 3: Create New Split for Track #1
```
POST http://localhost:8000/api/splits/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "track": 1,
  "user": 3,
  "percentage": 25
}
```

### Step 4: Update Split #1 Percentage
```
PUT http://localhost:8000/api/splits/1/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "track": 1,
  "user": 1,
  "percentage": 50
}
```

### Step 5: Verify Track Splits Updated
```
GET http://localhost:8000/api/tracks/1/
Authorization: Token YOUR_TOKEN
```
(Check splits array to confirm)

---

## Important Rules

1. **Percentages must sum to 100%** for a track's total splits
2. **Each user can only have ONE split per track** (unique_together constraint)
3. **Percentage range**: 0-100 (validated)
4. **Required fields**: `track`, `user`, `percentage`
5. **Authentication required** for all split operations

---

## Common Errors

### 401 Unauthorized
**Problem:** Missing or invalid token
**Solution:** Check `Authorization: Token YOUR_TOKEN` header

### 400 Bad Request
```json
{
  "percentage": ["Ensure this value is less than or equal to 100."]
}
```
**Solution:** Percentage must be 0-100

### 400 Bad Request - Duplicate
```json
{
  "non_field_errors": ["Track-User combination must be unique"]
}
```
**Solution:** User already has a split for this track; update instead

### 404 Not Found
**Problem:** Split or Track doesn't exist
**Solution:** Check the ID is correct

---

## Quick Copy-Paste Commands (cURL)

### Get All Splits
```bash
curl -X GET http://localhost:8000/api/splits/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Get Track with Splits
```bash
curl -X GET http://localhost:8000/api/tracks/1/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Create Split
```bash
curl -X POST http://localhost:8000/api/splits/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "track": 1,
    "user": 2,
    "percentage": 40
  }'
```

### Update Split
```bash
curl -X PUT http://localhost:8000/api/splits/1/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "track": 1,
    "user": 1,
    "percentage": 75
  }'
```

### Delete Split
```bash
curl -X DELETE http://localhost:8000/api/splits/1/ \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## Tips

- **Use Postman environment variables** to store `TOKEN` value for reuse
- **Use track GET endpoint** to see splits (easier than filtering splits endpoint)
- **Postman Collections** can be created to save these requests for repeated use
- **View splits in raw JSON** or **formatted** using Postman's display options
