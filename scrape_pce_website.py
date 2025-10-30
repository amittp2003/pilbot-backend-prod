"""
Web Scraper for Pillai College of Engineering Website
Automatically fetches and updates latest information from www.pce.ac.in
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse
import time

class PCEWebScraper:
    def __init__(self, base_url="https://www.pce.ac.in"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.scraped_data = []
        
    def is_valid_url(self, url):
        """Check if URL is from PCE domain"""
        parsed = urlparse(url)
        return parsed.netloc == 'www.pce.ac.in' or parsed.netloc == 'pce.ac.in'
    
    def scrape_page(self, url):
        """Scrape content from a single page"""
        try:
            print(f"Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else url
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            
            if main_content:
                content = main_content.get_text(separator=' ', strip=True)
            else:
                content = soup.get_text(separator=' ', strip=True)
            
            # Clean up content
            content = ' '.join(content.split())
            
            return {
                'url': url,
                'title': title_text,
                'content': content[:5000],  # Limit content length
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def scrape_important_sections(self):
        """Scrape key sections of PCE website"""
        important_urls = [
            # Main pages
            f"{self.base_url}/",
            f"{self.base_url}/about-us",
            f"{self.base_url}/academics",
            f"{self.base_url}/admissions",
            f"{self.base_url}/placements",
            f"{self.base_url}/facilities",
            f"{self.base_url}/research",
            f"{self.base_url}/departments",
            
            # Department pages
            f"{self.base_url}/departments/computer-engineering",
            f"{self.base_url}/departments/information-technology",
            f"{self.base_url}/departments/electronics-telecommunication",
            f"{self.base_url}/departments/mechanical-engineering",
            f"{self.base_url}/departments/artificial-intelligence",
            
            # Other important sections
            f"{self.base_url}/contact",
            f"{self.base_url}/news-events",
            f"{self.base_url}/library",
            f"{self.base_url}/student-activities",
        ]
        
        results = []
        for url in important_urls:
            data = self.scrape_page(url)
            if data:
                results.append(data)
                time.sleep(1)  # Be respectful to the server
        
        return results
    
    def save_to_json(self, data, filename):
        """Save scraped data to JSON file"""
        filepath = os.path.join('chatbotdata', filename)
        os.makedirs('chatbotdata', exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved to {filepath}")
    
    def scrape_and_save(self):
        """Main function to scrape and save data"""
        print("=" * 80)
        print("PCE Website Scraper - Starting...")
        print("=" * 80)
        
        # Scrape important sections
        scraped_data = self.scrape_important_sections()
        
        if scraped_data:
            # Save to JSON
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"website_scraped_{timestamp}.json"
            self.save_to_json(scraped_data, filename)
            
            print("\n" + "=" * 80)
            print(f"✅ Successfully scraped {len(scraped_data)} pages")
            print("=" * 80)
            
            return scraped_data
        else:
            print("❌ No data scraped")
            return []

if __name__ == "__main__":
    scraper = PCEWebScraper()
    scraped_data = scraper.scrape_and_save()
    
    print(f"\nScraped {len(scraped_data)} pages from PCE website")
    print("Next step: Run 'python load_general_data.py' to update Pinecone with new data")
