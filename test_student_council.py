from pinecone import Pinecone
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
gen_idx = pc.Index(os.getenv('GEN_INDEX'))
embeddings = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Test the exact query about student council
test_queries = [
    "Tell me about student council",
    "What is the student council?",
    "Who are the student council members?"
]

for query in test_queries:
    print(f"\n{'='*80}")
    print(f"🔍 Query: {query}")
    print('='*80)
    
    query_vector = embeddings.encode(query).tolist()
    results = gen_idx.query(vector=query_vector, top_k=5, include_metadata=True)
    
    print(f"\n📊 Found {len(results['matches'])} results:\n")
    
    for i, match in enumerate(results['matches'], 1):
        print(f"{i}. Score: {match['score']:.3f}")
        print(f"   Text: {match['metadata']['text'][:300]}...")
        print()
