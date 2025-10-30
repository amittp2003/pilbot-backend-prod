import os
import pinecone
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone
PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
NAV_INDEX = os.environ['NAV_INDEX']

pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
nav_index = pc.Index(NAV_INDEX)

# Query to get some sample navigation data
print("\n=== Current Navigation Data in Pinecone ===\n")

# Get index stats
stats = nav_index.describe_index_stats()
print(f"Total vectors: {stats['total_vector_count']}")
print(f"Dimension: {stats['dimension']}\n")

# Fetch some sample vectors
results = nav_index.query(
    vector=[0.0] * 768,  # Dummy vector to get any results
    top_k=10,
    include_metadata=True
)

print("Sample navigation entries:")
print("=" * 80)
for i, match in enumerate(results['matches'], 1):
    print(f"\n{i}. Score: {match['score']:.4f}")
    print(f"   ID: {match['id']}")
    if 'metadata' in match and match['metadata']:
        print(f"   Text: {match['metadata'].get('text', 'N/A')}")
    print("-" * 80)
