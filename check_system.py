"""
System Status Checker for Pilbot
Verifies all components are working correctly
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("PILBOT SYSTEM STATUS CHECK")
print("=" * 80)

# Check environment variables
print("\n📋 Environment Variables:")
print("-" * 80)

required_vars = ['GROQ_API_KEY', 'PINECONE_API_KEY', 'GEN_INDEX', 'NAV_INDEX']
optional_vars = ['EMAIL_ADDRESS', 'EMAIL_PASSWORD', 'HOSTS']

all_good = True
for var in required_vars:
    value = os.getenv(var)
    if value:
        masked = value[:8] + '...' if len(value) > 8 else '***'
        print(f"✓ {var}: {masked}")
    else:
        print(f"✗ {var}: NOT SET")
        all_good = False

for var in optional_vars:
    value = os.getenv(var)
    if value:
        print(f"✓ {var}: SET")
    else:
        print(f"⚠ {var}: NOT SET (optional)")

# Check Pinecone connection
print("\n📊 Pinecone Status:")
print("-" * 80)
try:
    import pinecone
    PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
    GEN_INDEX = os.environ['GEN_INDEX']
    NAV_INDEX = os.environ['NAV_INDEX']
    
    pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
    
    # Check general index
    gen_index = pc.Index(GEN_INDEX)
    gen_stats = gen_index.describe_index_stats()
    print(f"✓ General Index ({GEN_INDEX}):")
    print(f"  - Vectors: {gen_stats['total_vector_count']}")
    print(f"  - Dimension: {gen_stats['dimension']}")
    
    # Check navigation index
    nav_index = pc.Index(NAV_INDEX)
    nav_stats = nav_index.describe_index_stats()
    print(f"✓ Navigation Index ({NAV_INDEX}):")
    print(f"  - Vectors: {nav_stats['total_vector_count']}")
    print(f"  - Dimension: {nav_stats['dimension']}")
    
except Exception as e:
    print(f"✗ Pinecone Error: {e}")
    all_good = False

# Check Groq connection
print("\n🤖 Groq AI Status:")
print("-" * 80)
try:
    from groq import Groq
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    if GROQ_API_KEY:
        client = Groq(api_key=GROQ_API_KEY)
        models = client.models.list()
        active_models = [m for m in models.data if m.active]
        print(f"✓ Groq API Connected")
        print(f"  - Available models: {len(active_models)}")
        print(f"  - Primary model: llama-3.1-8b-instant")
    else:
        print("✗ Groq API Key not set")
        all_good = False
        
except Exception as e:
    print(f"✗ Groq Error: {e}")
    all_good = False

# Check data files
print("\n📁 Data Files:")
print("-" * 80)

navigation_files = [
    'navigation/ground.json',
    'navigation/first.json',
    'navigation/second-floor.json',
    'navigation/third-floor.json',
    'navigation/fourth-floor.json'
]

chatbot_dir = 'chatbotdata/'

nav_count = 0
for file in navigation_files:
    if os.path.exists(file):
        nav_count += 1

if nav_count == 5:
    print(f"✓ Navigation files: {nav_count}/5")
else:
    print(f"⚠ Navigation files: {nav_count}/5 (some missing)")

if os.path.exists(chatbot_dir):
    json_files = [f for f in os.listdir(chatbot_dir) if f.endswith('.json')]
    print(f"✓ Chatbot data files: {len(json_files)}")
else:
    print(f"✗ Chatbot data directory not found")
    all_good = False

# Check Python packages
print("\n📦 Python Packages:")
print("-" * 80)

required_packages = [
    'fastapi',
    'uvicorn',
    'groq',
    'pinecone',
    'langchain_huggingface',
    'langchain',
    'dotenv'
]

for package in required_packages:
    try:
        __import__(package.replace('-', '_'))
        print(f"✓ {package}")
    except ImportError:
        print(f"✗ {package} - NOT INSTALLED")
        all_good = False

# Final summary
print("\n" + "=" * 80)
if all_good:
    print("✅ ALL SYSTEMS OPERATIONAL!")
    print("\nYou can now start the server:")
    print("  python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000")
else:
    print("⚠️  SOME ISSUES DETECTED")
    print("\nPlease fix the issues marked with ✗ before running the server.")
print("=" * 80)
