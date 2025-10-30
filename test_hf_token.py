import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv('HF_TOKEN')

print(f"Token loaded: {HF_TOKEN[:10]}..." if HF_TOKEN else "No token found")
print(f"Token length: {len(HF_TOKEN) if HF_TOKEN else 0}")

# Try a simple, always-available model
try:
    client = InferenceClient('gpt2', token=HF_TOKEN)
    response = client.text_generation("Hello", max_new_tokens=20)
    print(f"\n✅ Success! Response: {response[:50]}...")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nThe token might be invalid or expired.")
    print("Please generate a new token at: https://huggingface.co/settings/tokens")
