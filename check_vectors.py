from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

# Check general index
gen_idx = pc.Index(os.getenv('GEN_INDEX'))
gen_stats = gen_idx.describe_index_stats()
print(f"✅ General Index: {gen_stats['total_vector_count']} vectors")

# Check navigation index
nav_idx = pc.Index(os.getenv('NAV_INDEX'))
nav_stats = nav_idx.describe_index_stats()
print(f"✅ Navigation Index: {nav_stats['total_vector_count']} vectors")

# Sample a query to see what's actually retrievable
from sentence_transformers import SentenceTransformer

embeddings = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Test query
test_query = "What programs does PCE offer?"
query_vector = embeddings.encode(test_query).tolist()

results = gen_idx.query(vector=query_vector, top_k=3, include_metadata=True)

print(f"\n📋 Sample results for '{test_query}':")
for i, match in enumerate(results['matches'], 1):
    print(f"\n{i}. Score: {match['score']:.3f}")
    print(f"   Text preview: {match['metadata']['text'][:200]}...")
