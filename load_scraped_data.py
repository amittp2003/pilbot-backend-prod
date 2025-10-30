"""
Load all web-scraped data into Pinecone
"""
import json
import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Initialize
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('GEN_INDEX'))
embeddings = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Text splitter for chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=200,
    length_function=len,
)

def load_scraped_files():
    """Load all scraped JSON files"""
    scraped_dir = "chatbotdata/web_scraped"
    
    if not os.path.exists(scraped_dir):
        print(f"❌ Directory not found: {scraped_dir}")
        print("   Run 'python scrape_all_pce_pages.py' first!")
        return []
    
    files = [f for f in os.listdir(scraped_dir) if f.endswith('.json') and not f.startswith('_')]
    print(f"📁 Found {len(files)} scraped files\n")
    
    all_data = []
    for filename in files:
        filepath = os.path.join(scraped_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_data.append(data)
    
    return all_data

def create_chunks_from_scraped_data(scraped_data):
    """Create text chunks from scraped pages"""
    all_chunks = []
    
    for page_data in scraped_data:
        page_name = page_data['page_name']
        url = page_data['url']
        content = page_data['text_content']
        
        print(f"📄 Processing: {page_name}")
        print(f"   Content length: {len(content)} characters")
        
        # Create chunks
        chunks = text_splitter.split_text(content)
        print(f"   Created: {len(chunks)} chunks")
        
        # Add metadata to each chunk
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                'text': chunk,
                'source': page_name,
                'url': url,
                'chunk_index': i,
                'total_chunks': len(chunks)
            })
        
        # Also process tables if present
        if page_data.get('tables'):
            for table_idx, table in enumerate(page_data['tables']):
                # Convert table to text
                table_text = f"Table from {page_name}:\n"
                for row in table:
                    table_text += " | ".join(row) + "\n"
                
                all_chunks.append({
                    'text': table_text,
                    'source': f"{page_name} (Table {table_idx+1})",
                    'url': url,
                    'chunk_index': 0,
                    'total_chunks': 1
                })
    
    return all_chunks

def upload_to_pinecone(chunks):
    """Upload chunks to Pinecone"""
    print(f"\n🚀 Uploading {len(chunks)} chunks to Pinecone...")
    
    batch_size = 100
    total_uploaded = 0
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        
        # Create vectors
        vectors = []
        for j, chunk in enumerate(batch):
            vector_id = f"scraped_{i+j}_{datetime.now().strftime('%Y%m%d')}"
            embedding = embeddings.encode(chunk['text']).tolist()
            
            vectors.append({
                'id': vector_id,
                'values': embedding,
                'metadata': {
                    'text': chunk['text'],
                    'source': chunk['source'],
                    'url': chunk['url'],
                    'chunk_index': chunk['chunk_index'],
                    'scraped_date': datetime.now().isoformat()
                }
            })
        
        # Upload batch
        index.upsert(vectors=vectors)
        total_uploaded += len(vectors)
        print(f"   ✅ Uploaded batch {i//batch_size + 1}: {total_uploaded}/{len(chunks)} chunks")
    
    print(f"\n✅ Upload complete! {total_uploaded} chunks added to Pinecone")

def main():
    print("="*80)
    print("📊 LOADING WEB-SCRAPED DATA INTO PINECONE")
    print("="*80)
    
    # Load scraped data
    scraped_data = load_scraped_files()
    if not scraped_data:
        return
    
    print(f"\n✅ Loaded {len(scraped_data)} pages")
    
    # Create chunks
    print("\n" + "="*80)
    print("🔪 CREATING CHUNKS")
    print("="*80 + "\n")
    
    chunks = create_chunks_from_scraped_data(scraped_data)
    
    print("\n" + "="*80)
    print(f"📦 Total chunks created: {len(chunks)}")
    print("="*80)
    
    # Upload to Pinecone
    upload_to_pinecone(chunks)
    
    # Check final stats
    stats = index.describe_index_stats()
    print("\n" + "="*80)
    print(f"📊 PINECONE INDEX STATS")
    print(f"   Total vectors: {stats['total_vector_count']}")
    print("="*80)
    
    print("\n✅ ALL DONE! Your chatbot now has the latest PCE website data!")

if __name__ == "__main__":
    main()
