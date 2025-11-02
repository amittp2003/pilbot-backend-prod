"""
CRITICAL: Re-index Pinecone with MiniLM model to match backend

This script converts your existing Pinecone data to use the smaller
all-MiniLM-L6-v2 model instead of all-mpnet-base-v2.

This is REQUIRED because we changed the embedding model to fit in 512MB RAM.
"""

from langchain_huggingface import HuggingFaceEmbeddings
import pinecone
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize new embeddings model (same as backend now uses)
print("🔄 Loading MiniLM embeddings model (80MB)...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'batch_size': 1, 'show_progress_bar': True}
)

# Connect to Pinecone
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
GEN_INDEX = os.getenv('GEN_INDEX')
NAV_INDEX = os.getenv('NAV_INDEX')

pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
gen_index = pc.Index(GEN_INDEX)
nav_index = pc.Index(NAV_INDEX)

print(f"✅ Connected to Pinecone indexes: {GEN_INDEX}, {NAV_INDEX}")

# Load your original data
print("\n📂 Loading original data files...")

def load_all_json_files():
    """Load all JSON files from chatbotdata folder"""
    import glob
    data = []
    json_files = glob.glob('chatbotdata/*.json')
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                if isinstance(content, list):
                    data.extend(content)
                elif isinstance(content, dict):
                    data.append(content)
                print(f"  ✓ Loaded {file_path}")
        except Exception as e:
            print(f"  ✗ Error loading {file_path}: {e}")
    
    return data

# Load general data
general_data = load_all_json_files()
print(f"📊 Loaded {len(general_data)} general documents")

# Load navigation data
nav_data = []
nav_files = ['navigation/first.json', 'navigation/ground.json', 'navigation/second-floor.json', 
             'navigation/third-floor.json', 'navigation/fourth-floor.json']
for nav_file in nav_files:
    try:
        with open(nav_file, 'r', encoding='utf-8') as f:
            nav_content = json.load(f)
            if isinstance(nav_content, list):
                nav_data.extend(nav_content)
            elif isinstance(nav_content, dict):
                nav_data.append(nav_content)
            print(f"  ✓ Loaded {nav_file}")
    except Exception as e:
        print(f"  ✗ Error loading {nav_file}: {e}")

print(f"📊 Loaded {len(nav_data)} navigation documents")

# Re-index General data
print("\n🔄 Re-indexing GENERAL data with MiniLM embeddings...")
gen_vectors = []
for i, doc in enumerate(general_data):
    if i % 50 == 0:
        print(f"  Processing {i}/{len(general_data)}...")
    
    text = doc.get('text', '') or doc.get('content', '') or str(doc)
    if text:
        embedding = embeddings.embed_query(text)
        gen_vectors.append({
            'id': f'gen_{i}',
            'values': embedding,
            'metadata': {'text': text[:1000]}  # Limit metadata size
        })

# Upsert in batches
print(f"📤 Uploading {len(gen_vectors)} vectors to {GEN_INDEX}...")
batch_size = 100
for i in range(0, len(gen_vectors), batch_size):
    batch = gen_vectors[i:i+batch_size]
    gen_index.upsert(vectors=batch)
    print(f"  ✓ Uploaded batch {i//batch_size + 1}/{(len(gen_vectors)//batch_size) + 1}")

print(f"✅ General index updated!")

# Re-index Navigation data
print("\n🔄 Re-indexing NAVIGATION data with MiniLM embeddings...")
nav_vectors = []
for i, doc in enumerate(nav_data):
    if i % 10 == 0:
        print(f"  Processing {i}/{len(nav_data)}...")
    
    text = doc.get('text', '') or doc.get('content', '') or str(doc)
    if text:
        embedding = embeddings.embed_query(text)
        nav_vectors.append({
            'id': f'nav_{i}',
            'values': embedding,
            'metadata': {'text': text[:1000]}
        })

print(f"📤 Uploading {len(nav_vectors)} vectors to {NAV_INDEX}...")
for i in range(0, len(nav_vectors), batch_size):
    batch = nav_vectors[i:i+batch_size]
    nav_index.upsert(vectors=batch)
    print(f"  ✓ Uploaded batch {i//batch_size + 1}/{(len(nav_vectors)//batch_size) + 1}")

print(f"✅ Navigation index updated!")

print("\n🎉 RE-INDEXING COMPLETE!")
print("Your Pinecone now uses MiniLM embeddings compatible with 512MB RAM backend!")
print("\nYou can now deploy to Render and it should work within 512MB limit.")
