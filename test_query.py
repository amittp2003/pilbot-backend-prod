"""
Test query script to verify Pinecone setup is working
"""

import os
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_query(index, query, index_name):
    print(f"\n{'='*60}")
    print(f"Testing {index_name}")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"{'-'*60}")
    
    embeddings = HuggingFaceEmbeddings()
    query_vector = embeddings.embed_query(query)
    results = index.query(vector=query_vector, top_k=3, include_metadata=True)
    
    if not results['matches']:
        print("❌ No results found! Make sure you've uploaded data.")
        return
    
    print("\nTop 3 Results:")
    for i, match in enumerate(results['matches'], 1):
        print(f"\n{i}. Score: {match['score']:.4f}")
        print(f"   Text: {match['metadata']['text'][:200]}...")

def main():
    print("🔍 Testing Pinecone Queries...")
    
    # Initialize
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    
    # Test General Index
    try:
        gen_index = pc.Index('pilbot-general')
        test_query(
            gen_index,
            "Tell me about Pillai College of Engineering",
            "General Information Index"
        )
        
        test_query(
            gen_index,
            "What courses does PCE offer?",
            "General Information Index"
        )
    except Exception as e:
        print(f"❌ Error with general index: {e}")
    
    # Test Navigation Index
    try:
        nav_index = pc.Index('pilbot-navigation')
        test_query(
            nav_index,
            "Where is the library?",
            "Navigation Index"
        )
        
        test_query(
            nav_index,
            "How do I get to the canteen?",
            "Navigation Index"
        )
    except Exception as e:
        print(f"❌ Error with navigation index: {e}")
    
    print(f"\n{'='*60}")
    print("✅ Query tests complete!")
    print("\nIf you see relevant results above, your Pinecone setup is working!")
    print("You can now proceed with deployment.")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
