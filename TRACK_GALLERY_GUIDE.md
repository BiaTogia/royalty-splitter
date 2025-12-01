# Track Gallery & Upload - User Guide

## Overview
The Track Gallery is a visual interface where users can:
- 📤 Upload audio tracks with metadata (title, duration, genre)
- 🎵 Listen to uploaded tracks with an embedded audio player
- 👥 View royalty split information
- 📊 Manage all tracks in one place

## How to Access

### 1. Navigate to the Gallery
Open your browser and go to:
```
http://localhost:8000/gallery/
```

### 2. Get an Authentication Token

> **Security update:** Browser-based access should use the server-managed session cookie (HttpOnly). The gallery prompt is legacy — do not paste or store tokens in browser `localStorage`. Use the Harmoniq frontend which authenticates via secure cookies. Tokens are still available for API clients/scripts but should not be persisted in browser storage.


On your first visit, you'll be prompted to enter your API token. You can get this by:

**Option A: Using the token endpoint**
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your_email@example.com",
    "password": "your_password"
  }'
```

Response:
```json
{
  "token": "9aef40f2dce22950c5d6bbc5a39383382ababf66",
  "user_id": 1,
  "email": "your_email@example.com"
}
```

**Option B: Using Postman**
- Method: `POST`
- URL: `http://localhost:8000/api/token/`
- Body (JSON):
```json
{
  "email": "your_email@example.com",
  "password": "your_password"
}
```

### 3. Paste Token in Prompt
When the gallery page asks for your token, paste the token value and press Enter.

## Uploading a Track

### Steps:
1. Fill in the upload form:
   - **Track Title**: Name of your track (required)
   - **Duration**: Length in minutes (required), e.g., `3.5`
   - **Genre**: Select from dropdown (required)
   - **Audio File**: Select an audio file from your computer (required)

2. Supported audio formats:
   - `.mp3` (MP3)
   - `.wav` (WAV)
   - `.flac` (FLAC)
   - `.m4a` (M4A/AAC)
   - `.aac` (AAC)
   - `.ogg` (OGG Vorbis)

3. Click **Upload Track**

4. Wait for the success message and the page will refresh automatically

5. Your track will appear in the "Your Tracks" section below

## Viewing Your Tracks

### Track Card Details:
- **Owner Badge**: Shows who uploaded the track
- **Title, Duration, Genre, Date**: Track metadata
- **Audio Player**: Built-in player with play/pause/volume controls
- **Royalty Splits**: Shows how earnings are split (if configured)

### Playing a Track:
1. Locate the track in the gallery
2. Click the **Play** button in the audio player
3. Use the controls to play, pause, adjust volume, or seek

## Creating Tracks with Splits

For now, the gallery uploads tracks with you as 100% owner. To add splits:

1. After uploading, use the API directly:
```bash
curl -X PUT http://localhost:8000/api/tracks/1/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Track",
    "duration": 3.5,
    "genre": "pop",
    "splits": [
      {"user": 1, "percentage": 60},
      {"user": 2, "percentage": 40}
    ]
  }'
```

(User IDs can be obtained from `/api/users/` endpoint)

## Technical Details

### API Endpoints Used:
- `POST /api/token/` — Get authentication token
- `GET /api/tracks/` — List all tracks
- `POST /api/tracks/` — Upload a new track
- `GET /media/tracks/{filename}` — Access uploaded audio files

### How It Works:
1. **Frontend**: HTML form + JavaScript (vanilla, no framework)
2. **Backend**: Django REST Framework
3. **File Storage**: Uploaded files stored in `/media/tracks/` directory
4. **Authentication**: Token-based (stored in browser's `localStorage`)

### File Structure:
```
royalty_splitter/
├── templates/
│   └── track_gallery.html      # Gallery UI
├── api/
│   ├── views_ui.py             # View to serve gallery
│   ├── auth_views.py           # Token endpoint
│   └── urls.py                 # Routes
├── media/
│   └── tracks/                 # Uploaded audio files
└── royalty_splitter/
    └── urls.py                 # Main routes
```

## Troubleshooting

### Token Prompt Keeps Appearing
- Make sure you entered the token correctly
- Token must start with the actual hex string (not "Token ...")
- Try clearing browser cache and localStorage

### Upload Fails
- Check file format (must be a supported audio format)
- Check file size (Django default is 2.6 MB)
- Make sure duration is a valid number
- Title and genre are required

### Can't Play Audio
- Audio file must have been uploaded successfully (check API response)
- Try a different browser
- Check browser console (F12) for errors

### Can't Get Token
- Make sure you've created a user account first via `/api/users/` POST
- Email and password must match exactly
- Check that user is active in admin

## Example Workflow

### 1. Create a User
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice",
    "email": "alice@example.com",
    "password": "securepassword123",
    "country": "USA"
  }'
```

### 2. Get Token
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "securepassword123"
  }'
# Returns: {"token": "...", "user_id": 1, "email": "alice@example.com"}
```

### 3. Open Gallery
- Go to `http://localhost:8000/gallery/`
- Paste token when prompted

### 4. Upload a Track
- Fill form with track details
- Select an audio file
- Click Upload
- Track appears in gallery with player

### 5. Listen
- Click Play in the audio player
- Enjoy! 🎵

## Notes

- Tracks are associated with the user who uploads them
- File uploads are stored in `media/tracks/` subdirectory by timestamp/ID
- Uploaded files are served at `/media/tracks/{filename}`
- In production, use a proper file storage backend (S3, etc.)
- Royalty calculations use duration × genre rate (configurable in serializers)

---

For API documentation, see `/api/` or check the DRF browsable API interface.
