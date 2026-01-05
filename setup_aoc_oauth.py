#!/usr/bin/env python
"""
Setup script for AOC OAuth application in any environment (dev, staging, production)

Usage:
  python setup_aoc_oauth.py --env dev --redirect http://localhost:5173/auth/callback
  python setup_aoc_oauth.py --env staging --redirect https://aoc.abakus.no/auth/callback
  python setup_aoc_oauth.py --env production --redirect https://aoc.abakus.no/auth/callback
"""
import os
import sys
import django
import argparse
import secrets

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lego.settings')
django.setup()

from lego.apps.oauth.models import APIApplication
from lego.apps.users.models import User


def generate_secure_credentials():
    """Generate cryptographically secure client credentials"""
    client_id = f"aoc_{secrets.token_urlsafe(32)}"
    client_secret = secrets.token_urlsafe(64)
    return client_id, client_secret


def setup_oauth_app(redirect_uri, use_existing=False):
    """
    Set up or update the AOC OAuth application

    Args:
        redirect_uri: The redirect URI for the OAuth callback
        use_existing: If True, update existing app instead of creating new one
    """
    app_name = 'Advent of Code Leaderboard'

    print("=" * 70)
    print(f"Setting up OAuth Application: {app_name}")
    print("=" * 70)

    # Check if app already exists
    existing_app = APIApplication.objects.filter(name=app_name).first()

    if existing_app and not use_existing:
        print(f"\nAn OAuth app named '{app_name}' already exists!")
        print(f"\nExisting Application Details:")
        print(f"  Client ID: {existing_app.client_id}")
        print(f"  Redirect URI: {existing_app.redirect_uris}")

        response = input("\nDo you want to update it? (yes/no): ").lower()
        if response != 'yes':
            print("Aborted.")
            return existing_app

        # Update existing app
        existing_app.redirect_uris = redirect_uri
        existing_app.save()
        print("\n✓ Updated existing OAuth application!")
        return existing_app

    elif existing_app and use_existing:
        # Update existing app
        existing_app.redirect_uris = redirect_uri
        existing_app.save()
        print("\n✓ Updated existing OAuth application!")
        return existing_app

    else:
        # Create new app
        user = User.objects.first()
        if not user:
            print("ERROR: No users found in database!")
            print("Please create at least one user first.")
            sys.exit(1)

        # Generate secure credentials
        client_id, client_secret = generate_secure_credentials()

        app = APIApplication.objects.create(
            client_id=client_id,
            client_secret=client_secret,
            user=user,
            redirect_uris=redirect_uri,
            client_type='public',
            authorization_grant_type='authorization-code',
            name=app_name,
            description='Abakus Advent of Code Leaderboard Integration',
            skip_authorization=False
        )

        print("\n✓ Successfully created new OAuth application!")
        return app


def main():
    parser = argparse.ArgumentParser(
        description='Setup AOC OAuth application for different environments'
    )
    parser.add_argument(
        '--env',
        choices=['dev', 'staging', 'production'],
        default='dev',
        help='Environment to configure (dev, staging, production)'
    )
    parser.add_argument(
        '--redirect',
        required=True,
        help='Redirect URI for OAuth callback (e.g., http://localhost:5173/auth/callback)'
    )
    parser.add_argument(
        '--update',
        action='store_true',
        help='Update existing app instead of creating new one'
    )

    args = parser.parse_args()

    print(f"\nEnvironment: {args.env.upper()}")
    print(f"Redirect URI: {args.redirect}")
    print()

    # Setup the OAuth app
    app = setup_oauth_app(args.redirect, use_existing=args.update)

    # Display results
    print("\n" + "=" * 70)
    print("OAuth Application Details")
    print("=" * 70)
    print(f"\n  Name: {app.name}")
    print(f"  Description: {app.description}")
    print(f"  Client ID: {app.client_id}")
    print(f"  Client Secret: {app.client_secret}")
    print(f"  Redirect URI: {app.redirect_uris}")
    print(f"  Grant Type: {app.authorization_grant_type}")

    # Environment-specific instructions
    print("\n" + "=" * 70)
    print(f"Configuration for {args.env.upper()} Environment")
    print("=" * 70)

    if args.env == 'dev':
        api_url = 'http://localhost:8000'
    elif args.env == 'staging':
        api_url = 'https://staging.abakus.no'  # Replace with actual staging URL
    else:  # production
        api_url = 'https://abakus.no'

    print(f"\nAdd these to your aoc-abakus-sv .env file:\n")
    print(f"ABAKUS_API_URL={api_url}")
    print(f"ABAKUS_CLIENT_ID={app.client_id}")
    print(f"ABAKUS_CLIENT_SECRET={app.client_secret}")
    print(f"ABAKUS_REDIRECT_URI={args.redirect}")

    print("\n" + "=" * 70)
    print("Next Steps")
    print("=" * 70)
    print("\n1. Add the environment variables above to your .env file")
    print("2. Restart your aoc-abakus-sv application")
    print("3. Test the OAuth flow")

    if args.env in ['staging', 'production']:
        print("\n  IMPORTANT for staging/production:")
        print("   - Make sure lego is running and accessible at the API URL")
        print("   - Ensure the redirect URI is accessible from the internet")
        print("   - The 'aoc' scope must be configured in lego settings")
        print("   - OAuth authentication.py must allow 'aoc' scope")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
