import os
import json
import pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone
PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
NAV_INDEX = os.environ['NAV_INDEX']

pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
nav_index = pc.Index(NAV_INDEX)

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Load all navigation JSON files
navigation_files = [
    'navigation/ground.json',
    'navigation/first.json',
    'navigation/second-floor.json',
    'navigation/third-floor.json',
    'navigation/fourth-floor.json'
]

print("=" * 80)
print("Loading PCE Navigation Data into Pinecone")
print("=" * 80)

all_navigation_data = []
doc_id = 0

for nav_file in navigation_files:
    print(f"\n📂 Processing: {nav_file}")
    
    with open(nav_file, 'r') as f:
        data = json.load(f)
    
    floor_name = data.get('floor', 'Unknown Floor')
    college_name = data.get('college_name', 'Pillai College of Engineering')
    
    # Process each wing
    for wing_key, wing_data in data.get('wings', {}).items():
        wing_name = wing_data.get('name', f'{wing_key} Wing')
        
        # Process each room
        for room in wing_data.get('rooms', []):
            room_number = room.get('room_number', '')
            room_name = room.get('name', '')
            room_type = room.get('type', '')
            nearby = ', '.join(room.get('nearby', []))
            
            # Create comprehensive text entry
            text_parts = [
                f"{room_name} is located at {room_number} on the {floor_name} in {wing_name} of {college_name}.",
                f"Type: {room_type}."
            ]
            
            # Add directions
            if 'directions' in room:
                for direction_key, direction_text in room['directions'].items():
                    text_parts.append(f"Directions ({direction_key.replace('_', ' ')}): {direction_text}")
            
            if nearby:
                text_parts.append(f"Nearby locations: {nearby}.")
            
            full_text = ' '.join(text_parts)
            
            all_navigation_data.append({
                'id': f'nav_{doc_id}',
                'text': full_text,
                'floor': floor_name,
                'wing': wing_name,
                'room_number': room_number,
                'room_name': room_name,
                'type': room_type
            })
            
            doc_id += 1
    
    print(f"   ✓ Loaded {len(data.get('wings', {}))} wings")

print(f"\n📊 Total navigation entries: {len(all_navigation_data)}")
print("\n🔄 Deleting old navigation data...")

# Delete all existing vectors
try:
    nav_index.delete(delete_all=True)
    print("   ✓ Old data cleared")
except Exception as e:
    print(f"   ⚠ Warning: {e}")

print("\n🚀 Uploading new navigation data to Pinecone...")

# Batch upload
batch_size = 100
for i in range(0, len(all_navigation_data), batch_size):
    batch = all_navigation_data[i:i + batch_size]
    
    # Generate embeddings
    texts = [item['text'] for item in batch]
    vectors = embeddings.embed_documents(texts)
    
    # Prepare upsert data
    upsert_data = []
    for j, item in enumerate(batch):
        upsert_data.append({
            'id': item['id'],
            'values': vectors[j],
            'metadata': {
                'text': item['text'],
                'floor': item['floor'],
                'wing': item['wing'],
                'room_number': item['room_number'],
                'room_name': item['room_name'],
                'type': item['type']
            }
        })
    
    # Upsert to Pinecone
    nav_index.upsert(vectors=upsert_data)
    print(f"   ✓ Uploaded batch {i//batch_size + 1}: {len(batch)} entries")

print("\n" + "=" * 80)
print("✅ Navigation data successfully loaded!")
print("=" * 80)

# Verify
stats = nav_index.describe_index_stats()
print(f"\n📈 Total vectors in index: {stats['total_vector_count']}")
print(f"📊 Dimension: {stats['dimension']}")

# Test query
print("\n🧪 Testing navigation query...")
test_query = "Where is the library?"
query_vector = embeddings.embed_query(test_query)
results = nav_index.query(vector=query_vector, top_k=3, include_metadata=True)

print(f"\nTest query: '{test_query}'")
print("-" * 80)
for i, match in enumerate(results['matches'], 1):
    print(f"\n{i}. Score: {match['score']:.4f}")
    print(f"   Room: {match['metadata'].get('room_name', 'N/A')}")
    print(f"   Location: {match['metadata'].get('room_number', 'N/A')} - {match['metadata'].get('floor', 'N/A')}")
    print(f"   Details: {match['metadata'].get('text', 'N/A')[:200]}...")

print("\n" + "=" * 80)
print("🎉 All done! Your navigation system is ready.")
print("=" * 80)
