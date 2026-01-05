#!/usr/bin/env python
"""
Quick script to create a new OAuth application for AOC
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lego.settings')
django.setup()

from lego.apps.oauth.models import APIApplication
from lego.apps.users.models import User

# New OAuth app credentials
client_id = 'aoc_leaderboard_client_id_12345'
client_secret = 'aoc_leaderboard_secret_67890_abcdefghijklmnop'

print("=" * 60)
print("AOC OAuth Application Setup")
print("=" * 60)

# Check if it already exists
if APIApplication.objects.filter(client_id=client_id).exists():
    print(f"\n✓ OAuth app with client_id '{client_id}' already exists!")
    app = APIApplication.objects.get(client_id=client_id)
    print(f"\nApplication Details:")
    print(f"  Name: {app.name}")
    print(f"  Description: {app.description}")
    print(f"  Redirect URIs: {app.redirect_uris}")
    print(f"  Client ID: {app.client_id}")
    print(f"  Client Secret: {app.client_secret}")
    print(f"  Grant Type: {app.authorization_grant_type}")
    print(f"  Client Type: {app.client_type}")
else:
    # Get the first user (admin)
    user = User.objects.first()
    if not user:
        print("ERROR: No users found in database!")
        print("Please run: python manage.py load_fixtures --development")
        sys.exit(1)

    # Create the new OAuth application
    app = APIApplication.objects.create(
        client_id=client_id,
        client_secret=client_secret,
        user=user,
        redirect_uris='http://localhost:5173/auth/callback',
        client_type='public',
        authorization_grant_type='authorization-code',
        name='Advent of Code Leaderboard',
        description='Abakus Advent of Code Leaderboard Integration',
        skip_authorization=False
    )

    print("\n✓ Successfully created new OAuth application!")
    print(f"\nApplication Details:")
    print(f"  Name: {app.name}")
    print(f"  Description: {app.description}")
    print(f"  Client ID: {app.client_id}")
    print(f"  Client Secret: {app.client_secret}")
    print(f"  Redirect URIs: {app.redirect_uris}")

print("\n" + "=" * 60)
print("Next Steps:")
print("=" * 60)
print("\n1. Your aoc-abakus-sv/.env should have:")
print(f"   ABAKUS_CLIENT_ID={app.client_id}")
print(f"   ABAKUS_CLIENT_SECRET={app.client_secret}")
print("\n2. Restart your lego server to load the new 'aoc' scope")
print("\n3. Test the OAuth flow in aoc-abakus-sv")
print("\n" + "=" * 60)

# Check for existing OAuth apps
print("\nAll OAuth Applications in Database:")
print("-" * 60)
for app in APIApplication.objects.all():
    print(f"  • {app.name} (ID: {app.client_id[:20]}...)")
print("-" * 60)
