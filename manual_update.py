"""
Manual Update Script
Run this script manually whenever you want to update the chatbot with latest PCE website data
"""

import subprocess
import sys

print("=" * 80)
print("PILBOT MANUAL UPDATE")
print("=" * 80)
print("\nThis will:")
print("  1. Scrape the latest data from www.pce.ac.in")
print("  2. Update the Pinecone knowledge base")
print("  3. Restart the backend server (if running)")
print("\n" + "=" * 80)

# Step 1: Scrape ALL website pages
print("\n📡 Step 1: Scraping ALL PCE website pages...")
print("   (This includes: Student Council, Departments, Placements, Events, etc.)")
result = subprocess.run([sys.executable, 'scrape_all_pce_pages.py'])

if result.returncode != 0:
    print("❌ Scraping failed!")
    sys.exit(1)

# Step 2: Load scraped data into Pinecone
print("\n🔄 Step 2: Loading scraped data into Pinecone...")
result = subprocess.run([sys.executable, 'load_scraped_data.py'])

if result.returncode != 0:
    print("❌ Update failed!")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ UPDATE COMPLETED SUCCESSFULLY!")
print("=" * 80)
print("\nThe chatbot now has the latest information from PCE website.")
print("If the server is running, it will auto-reload with new data.")
print("=" * 80)
