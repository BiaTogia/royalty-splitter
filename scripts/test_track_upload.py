# Django test script to create a user, token and POST to /api/tracks/
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'royalty_splitter.settings')
django.setup()

from rest_framework.test import APIClient
from backend.models import UserAccount
from rest_framework.authtoken.models import Token

# Create test user
email = 'apitest_user@example.com'
UserAccount.objects.filter(email=email).delete()
user = UserAccount.objects.create_user(email=email, name='API Test', password='password123')
# Create token
Token.objects.filter(user=user).delete()
token = Token.objects.create(user=user)
print('Created user id:', user.id)
print('Token:', token.key)

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

# Prepare multipart data; splits sent as JSON string
splits = json.dumps([{"user": user.id, "percentage": 100.0}])

data = {
    'title': 'API Test Track',
    'duration': '3.5',
    'genre': 'pop',
    'splits': splits,
}

resp = client.post('/api/tracks/', data, format='multipart')
print('Status code:', resp.status_code)
try:
    print('Response data:', resp.data)
except Exception:
    print('Response content:', resp.content)
