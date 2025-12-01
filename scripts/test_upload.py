#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'royalty_splitter.settings')
django.setup()

from rest_framework.test import APIClient
from backend.models import UserAccount
from rest_framework.authtoken.models import Token
import json
from io import BytesIO

# Create test user
email = 'upload_test@example.com'
UserAccount.objects.filter(email=email).delete()
user = UserAccount.objects.create_user(email=email, name='Upload Test', password='password123')
Token.objects.filter(user=user).delete()
token = Token.objects.create(user=user)

print(f"✓ Created test user: {email}")
print(f"✓ Token: {token.key}")

# Create test file
test_audio = BytesIO(b'fake mp3 data for testing')
test_audio.name = 'test.mp3'

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

# Try to upload
splits = json.dumps([{"user": user.id, "percentage": 100.0}])
response = client.post('/api/tracks/', {
    'title': 'Test Upload Track',
    'duration': '3.5',
    'genre': 'pop',
    'file': test_audio,
    'splits': splits,
}, format='multipart')

print(f"\nUpload Response Status: {response.status_code}")
if response.status_code == 201:
    print("✓ Upload successful!")
    print(f"Track ID: {response.data.get('id')}")
    print(f"Track Title: {response.data.get('title')}")
    print(f"Owner: {response.data.get('owner_email')}")
    print(f"File stored at: {response.data.get('file')}")
else:
    print("✗ Upload failed")
    print(f"Response: {response.data}")
