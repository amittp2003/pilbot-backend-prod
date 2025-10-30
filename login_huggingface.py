"""
Login to HuggingFace to enable model downloads
"""
import os
from dotenv import load_dotenv
from huggingface_hub import login

# Load environment variables
load_dotenv()

hf_token = os.getenv('HF_TOKEN')

if not hf_token:
    print("❌ Error: HF_TOKEN not found in .env file")
    exit(1)

print("🔑 Logging in to HuggingFace...")
print(f"   Using token: {hf_token[:10]}...")

try:
    login(token=hf_token)
    print("✅ Successfully logged in to HuggingFace!")
    print("   You can now run test_pinecone.py")
except Exception as e:
    print(f"❌ Login failed: {e}")
