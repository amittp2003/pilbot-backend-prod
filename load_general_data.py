import os
import json
import pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone
PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
GEN_INDEX = os.environ['GEN_INDEX']

pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
gen_index = pc.Index(GEN_INDEX)

# Initialize embeddings
print("🔄 Initializing embeddings model...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Function to recursively extract text from JSON data
def extract_text(data):
    if isinstance(data, dict):
        result = []
        for key, value in data.items():
            result.extend(extract_text(value))
        return result
    elif isinstance(data, list):
        result = []
        for item in data:
            result.extend(extract_text(item))
        return result
    elif isinstance(data, str):
        return [data]
    else:
        return []

# Function to load all JSON files from the chatbotdata folder
def load_all_json_files(folder_path):
    json_files = [file for file in os.listdir(folder_path) if file.endswith('.json')]
    
    extracted_text = []
    file_sources = {}  # Track which file each text chunk came from
    
    print(f"\n📂 Found {len(json_files)} JSON files in {folder_path}")
    
    for json_file in json_files:
        file_path = os.path.join(folder_path, json_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                texts = extract_text(data)
                
                # Store source file info
                for text in texts:
                    if text.strip():  # Only non-empty text
                        extracted_text.append(text)
                        file_sources[len(extracted_text)-1] = json_file
                
                print(f"   ✓ Loaded {json_file}: {len(texts)} entries")
                
            except json.JSONDecodeError as e:
                print(f"   ✗ Error loading {json_file}: {e}")
    
    return extracted_text, file_sources

print("=" * 80)
print("Loading PCE General Knowledge Data into Pinecone")
print("=" * 80)

# Load all JSON files
folder_path = 'chatbotdata/'
extracted_text, file_sources = load_all_json_files(folder_path)

# Combine into one large text
combined_text = '-'.join(extracted_text)
print(f"\n📊 Total text length: {len(combined_text)} characters")

# Create chunks
print("\n🔪 Creating text chunks...")
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
chunks = splitter.split_text(combined_text)
print(f"   ✓ Created {len(chunks)} chunks")

# Delete old data
print("\n🔄 Deleting old general knowledge data...")
try:
    gen_index.delete(delete_all=True)
    print("   ✓ Old data cleared")
except Exception as e:
    print(f"   ⚠ Warning: {e}")

# Upload to Pinecone in batches
print("\n🚀 Uploading to Pinecone...")
batch_size = 100

for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i + batch_size]
    
    # Generate embeddings for batch
    vectors = embeddings.embed_documents(batch)
    
    # Prepare upsert data
    upsert_data = []
    for j, (chunk, vector) in enumerate(zip(batch, vectors)):
        doc_id = i + j
        upsert_data.append({
            'id': f'gen_doc_{doc_id}',
            'values': vector,
            'metadata': {
                'text': chunk[:1000],  # Limit metadata size
                'chunk_id': doc_id,
                'source': 'general_knowledge'
            }
        })
    
    # Upsert to Pinecone
    gen_index.upsert(vectors=upsert_data)
    print(f"   ✓ Uploaded batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}: {len(batch)} chunks")

print("\n" + "=" * 80)
print("✅ General knowledge data successfully loaded!")
print("=" * 80)

# Verify
stats = gen_index.describe_index_stats()
print(f"\n📈 Total vectors in index: {stats['total_vector_count']}")
print(f"📊 Dimension: {stats['dimension']}")

# Test query
print("\n🧪 Testing general knowledge query...")
test_query = "What programs does PCE offer?"
query_vector = embeddings.embed_query(test_query)
results = gen_index.query(vector=query_vector, top_k=3, include_metadata=True)

print(f"\nTest query: '{test_query}'")
print("-" * 80)
for i, match in enumerate(results['matches'], 1):
    print(f"\n{i}. Score: {match['score']:.4f}")
    print(f"   Text: {match['metadata'].get('text', 'N/A')[:200]}...")

print("\n" + "=" * 80)
print("🎉 All done! Your general knowledge system is ready.")
print("=" * 80)
