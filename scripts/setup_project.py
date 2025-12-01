import os
import sys
import django
from django.conf import settings
from django.core.management import call_command
from django.contrib.auth import get_user_model

# Setup Django environment
sys.path.append('/code')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'royalty_splitter.settings')
django.setup()

from rest_framework.authtoken.models import Token
from backend.models import UserAccount, Track, Wallet, Royalty, Split, Payout, PayoutStatus, Role, SeverityLevel, SIEM_Event

def setup():
    print("--- Applying Migrations ---")
    call_command('migrate')

    print("\n--- Creating Roles & Statuses ---")
    admin_role, _ = Role.objects.get_or_create(role_name="Admin")
    artist_role, _ = Role.objects.get_or_create(role_name="Artist")
    manager_role, _ = Role.objects.get_or_create(role_name="Manager")
    
    PayoutStatus.objects.get_or_create(status_name="Pending")
    PayoutStatus.objects.get_or_create(status_name="Completed")
    PayoutStatus.objects.get_or_create(status_name="Failed")

    SeverityLevel.objects.get_or_create(severity_name="Low")
    SeverityLevel.objects.get_or_create(severity_name="Medium")
    SeverityLevel.objects.get_or_create(severity_name="High")

    print("\n--- Creating Superuser ---")
    User = get_user_model()
    email = "togrul@gmail.com"
    password = "password123"
    if not User.objects.filter(email=email).exists():
        user = User.objects.create_superuser(email=email, name="togrul", password=password)
        print(f"Superuser created: {email}")
    else:
        user = User.objects.get(email=email)
        print(f"Superuser already exists: {email}")

    print("\n--- Generating Token ---")
    token, created = Token.objects.get_or_create(user=user)
    print(f"Token: {token.key}")

    print("\n--- Populating Initial Data ---")
    # Create a regular user (Artist)
    artist_email = "artist@example.com"
    if not User.objects.filter(email=artist_email).exists():
        artist_user = User.objects.create_user(email=artist_email, name="Artist User", password="password123", role=artist_role)
        print(f"Artist user created: {artist_email}")
    else:
        artist_user = User.objects.get(email=artist_email)

    # Create Track
    track, created = Track.objects.get_or_create(
        title="My First Hit",
        defaults={
            "duration": 180.5,
            "release_date": "2023-01-01",
            "owner": artist_user
        }
    )
    if created:
        print(f"Track created: {track.title}")
    else:
        print(f"Track already exists: {track.title}")

    # Create Wallet
    wallet, created = Wallet.objects.get_or_create(
        user=artist_user,
        defaults={"balance": 1000.00}
    )
    print(f"Wallet verified for {artist_user.email}")

    # Create Royalty
    royalty, created = Royalty.objects.get_or_create(
        track=track,
        defaults={"total_earning": 500.00, "distribution_date": "2023-02-01"}
    )
    print(f"Royalty verified for {track.title}")

    # Create Split
    split, created = Split.objects.get_or_create(
        track=track,
        user=artist_user,
        defaults={"percentage": 100.0}
    )
    print(f"Split verified: 100% to {artist_user.email}")

    # Create Payout
    payout_status = PayoutStatus.objects.get(status_name="Pending")
    payout, created = Payout.objects.get_or_create(
        wallet=wallet,
        amount=100.00,
        status=payout_status
    )
    print(f"Payout verified: {payout.amount}")

    print("\n--- Setup Complete ---")
    print(f"SUPERUSER_EMAIL={email}")
    print(f"SUPERUSER_PASSWORD={password}")
    print(f"TOKEN={token.key}")

if __name__ == "__main__":
    setup()
