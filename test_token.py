"""
Test if your HuggingFace token works
"""
from huggingface_hub import login

# Paste your token here directly (temporarily for testing)
token = input("Paste your HuggingFace token here: ").strip()

if not token or token == "your_huggingface_token_here":
    print("❌ You need to paste your actual token!")
    exit(1)

print(f"🔑 Testing token: {token[:10]}...")

try:
    login(token=token)
    print("✅ Token is VALID! Your HuggingFace login works!")
    print(f"\nNow update your .env file with:")
    print(f"HF_TOKEN={token}")
except Exception as e:
    print(f"❌ Token is INVALID: {e}")
    print("\nPlease:")
    print("1. Go to https://huggingface.co/settings/tokens")
    print("2. Create a NEW token")
    print("3. Run this script again")
