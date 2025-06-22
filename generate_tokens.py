#!/usr/bin/env python3
"""
OneLife Translation - Token Generator
Generate access tokens for QR codes and NFC tags
"""
import os
import hmac
import hashlib
import datetime
from urllib.parse import quote

def generate_tokens():
    """Generate valid access tokens"""
    # Get auth secret (use same as in api.py)
    auth_secret = os.getenv('AUTH_SECRET', 'onelife-church-spanish-2024')
    
    # Base tokens
    base_tokens = [
        'onelife-spanish-access',  # Main token
        'church-translation-2024',  # Alternative token
    ]
    
    # Add time-based tokens (weekly rotation)
    current_week = datetime.datetime.now().isocalendar()[1]
    weekly_token = f"week-{current_week}-2024"
    base_tokens.append(weekly_token)
    
    print("🔐 OneLife Translation - Access Tokens")
    print("=" * 50)
    print(f"Auth Secret: {auth_secret}")
    print(f"Current Week: {current_week}")
    print()
    
    print("📋 Available Tokens:")
    print("-" * 30)
    
    all_tokens = []
    
    for i, token in enumerate(base_tokens, 1):
        # Create HMAC hash for secure version
        hashed = hmac.new(
            auth_secret.encode(),
            token.encode(),
            hashlib.sha256
        ).hexdigest()[:16]  # Take first 16 chars for shorter URL
        
        print(f"{i}. Plain: {token}")
        print(f"   Hashed: {hashed}")
        print()
        
        all_tokens.extend([token, hashed])
    
    print("🔗 Sample URLs for QR Codes:")
    print("-" * 30)
    
    base_url = "https://your-app-name.vercel.app"  # Replace with your actual Vercel URL
    
    for i, token in enumerate(['onelife-spanish-access', base_tokens[2]], 1):  # Show main token and weekly token
        encoded_token = quote(token)
        url = f"{base_url}?token={encoded_token}"
        print(f"{i}. {url}")
        print()
    
    print("📱 Instructions:")
    print("-" * 30)
    print("1. Replace 'your-app-name.vercel.app' with your actual Vercel URL")
    print("2. Use any of the tokens above in your QR codes")
    print("3. Weekly tokens automatically rotate every week")
    print("4. For extra security, use the hashed versions")
    print("5. Add ?token=YOUR_TOKEN to your URLs")
    print()
    print("💡 Example QR Code Content:")
    print(f"   {base_url}?token=onelife-spanish-access")
    print()
    print("⚠️  Security Notes:")
    print("- Keep tokens private")
    print("- Rotate tokens regularly")
    print("- Consider setting AUTH_SECRET environment variable")
    print("- Remove /auth/tokens endpoint in production")

if __name__ == "__main__":
    generate_tokens() 