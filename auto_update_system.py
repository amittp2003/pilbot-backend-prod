"""
Automated Update System for Pilbot
Periodically checks PCE website for updates and refreshes the knowledge base
"""

import schedule
import time
import subprocess
import os
from datetime import datetime
from scrape_pce_website import PCEWebScraper

def update_knowledge_base():
    """Complete update workflow"""
    print("\n" + "=" * 80)
    print(f"PILBOT AUTO-UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Step 1: Scrape ALL website pages comprehensively
        print("\n📡 Step 1: Scraping ALL PCE website pages...")
        result = subprocess.run(
            ['python', 'scrape_all_pce_pages.py'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode != 0:
            print("⚠️ Scraping failed. Skipping update.")
            print(result.stderr)
            return
        
        # Step 2: Load scraped data into Pinecone
        print("\n🔄 Step 2: Loading scraped data into Pinecone...")
        result = subprocess.run(
            ['python', 'load_scraped_data.py'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            print("✅ Knowledge base updated successfully!")
            print(result.stdout)
        else:
            print("❌ Error updating knowledge base:")
            print(result.stderr)
        
        print("\n" + "=" * 80)
        print("Update completed!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error during update: {e}")

def run_scheduler():
    """Run the scheduled update system"""
    print("=" * 80)
    print("PILBOT AUTO-UPDATE SCHEDULER")
    print("=" * 80)
    print("\nScheduled updates:")
    print("  - Daily at 2:00 AM")
    print("  - Weekly on Sunday at 3:00 AM")
    print("\nPress Ctrl+C to stop")
    print("=" * 80)
    
    # Schedule daily update at 2 AM
    schedule.every().day.at("02:00").do(update_knowledge_base)
    
    # Schedule weekly deep update on Sunday at 3 AM
    schedule.every().sunday.at("03:00").do(update_knowledge_base)
    
    # Run once immediately on startup
    update_knowledge_base()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")
