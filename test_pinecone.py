"""
Quick test script to populate Pinecone with sample data for testing deployment
Run this before deploying to ensure your Pinecone setup works
"""

import os
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🚀 Starting Pinecone test data upload...")
    
    # Get HuggingFace token
    hf_token = os.getenv('HF_TOKEN')
    if not hf_token:
        print("❌ Error: HF_TOKEN not found in .env file")
        print("Please add your HuggingFace token to the .env file")
        return
    
    print(f"✓ Using HuggingFace token: {hf_token[:10]}...")
    
    # Initialize
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    
    # Initialize embeddings with token
    print("📥 Downloading embedding model (this may take a moment)...")
    embeddings = HuggingFaceEmbeddings(
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # Sample PCE General Information
    general_data = [
        "Pillai College of Engineering (PCE) is an autonomous engineering college located in New Panvel, Navi Mumbai, Maharashtra, India.",
        "PCE offers undergraduate B.Tech programs in Computer Engineering, Information Technology, Electronics and Telecommunication, Mechanical Engineering, and Artificial Intelligence & Data Science.",
        "The college has state-of-the-art laboratories, modern infrastructure, a well-stocked library, and sports facilities.",
        "PCE admissions are based on MHT-CET scores for Maharashtra candidates and JEE Main scores for all India candidates.",
        "The college has an active Training and Placement Cell that conducts campus recruitment drives. Major recruiters include TCS, Infosys, Wipro, L&T, and many more.",
        "PCE offers postgraduate programs including M.Tech in Computer Engineering and MBA.",
        "The college organizes technical festivals like 'Credenz' and cultural events throughout the year.",
        "PCE has various student clubs including coding club, robotics club, cultural committee, and sports committee.",
        "The faculty at PCE consists of experienced professors and industry experts who provide quality education.",
        "PCE is affiliated to the University of Mumbai and approved by AICTE (All India Council for Technical Education).",
    ]
    
    # Sample Navigation Data
    navigation_data = [
        "The main reception is located at the entrance of the college building. From reception, the Computer Engineering department is on the 3rd floor.",
        "The library is located on the 2nd floor. It is accessible from the main staircase near the reception area.",
        "The canteen is situated on the ground floor, near the left wing of the main building. It serves breakfast, lunch, and snacks.",
        "Computer labs are located on the 3rd and 4th floors. Lab 301 and 302 are on the 3rd floor, Labs 401-404 are on the 4th floor.",
        "The auditorium is located on the ground floor, accessible through the main corridor. It can accommodate 500 students.",
        "The sports ground and outdoor facilities are located behind the main building. The indoor sports complex is adjacent to the ground floor.",
        "The placement cell office is located on the 2nd floor, room number 201, near the HOD cabins.",
        "Administrative offices including the Principal's office and Examination department are on the 1st floor.",
        "The IT department is located on the 5th floor. Take the main elevator or stairs from reception.",
        "Parking facilities are available at the entrance. Student parking is on the left side, staff parking on the right side.",
    ]
    
    # Upload to General Index
    try:
        print("\n📚 Uploading to pilbot-general index...")
        gen_index = pc.Index('pilbot-general')
        
        vectors = []
        for i, text in enumerate(general_data):
            print(f"  Processing document {i+1}/{len(general_data)}...")
            embedding = embeddings.embed_query(text)
            vectors.append({
                'id': f'general_doc_{i}',
                'values': embedding,
                'metadata': {'text': text, 'category': 'general'}
            })
        
        gen_index.upsert(vectors=vectors)
        print(f"✅ Uploaded {len(vectors)} vectors to pilbot-general")
    except Exception as e:
        print(f"❌ Error uploading to general index: {e}")
    
    # Upload to Navigation Index
    try:
        print("\n🗺️  Uploading to pilbot-navigation index...")
        nav_index = pc.Index('pilbot-navigation')
        
        vectors = []
        for i, text in enumerate(navigation_data):
            print(f"  Processing document {i+1}/{len(navigation_data)}...")
            embedding = embeddings.embed_query(text)
            vectors.append({
                'id': f'nav_doc_{i}',
                'values': embedding,
                'metadata': {'text': text, 'category': 'navigation'}
            })
        
        nav_index.upsert(vectors=vectors)
        print(f"✅ Uploaded {len(vectors)} vectors to pilbot-navigation")
    except Exception as e:
        print(f"❌ Error uploading to navigation index: {e}")
    
    print("\n🎉 Test data upload complete!")
    print("\nNext steps:")
    print("1. Run test_query.py to verify the data")
    print("2. Proceed with deployment (see QUICK_DEPLOY.md)")

if __name__ == "__main__":
    main()
