"""
Comprehensive PCE Website Scraper
Scrapes all important pages and saves to JSON files
"""
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import os

class ComprehensivePCEScraper:
    def __init__(self):
        self.base_url = "https://www.pce.ac.in"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        self.scraped_data = []
        
        # Comprehensive list of important PCE pages
        self.pages_to_scrape = {
            # Student Pages
            "Student Council": "/students/student-council/",
            "Student Achievements": "/students/student-achievements/",
            "Student Activities": "/students/student-activities/",
            "Student Clubs": "/students/student-clubs/",
            "Anti Ragging": "/students/anti-ragging/",
            "Scholarships": "/students/scholarships/",
            "Student Grievance": "/students/student-grievance/",
            
            # Departments
            "Computer Engineering": "/academics/bachelors/computer-engineering/",
            "IT Engineering": "/academics/bachelors/information-technology/",
            "EXTC Engineering": "/academics/bachelors/electronics-telecommunication-engineering/",
            "ECS Engineering": "/academics/bachelors/electronics-computer-science/",
            "Mechanical Engineering": "/academics/bachelors/mechanical-engineering/",
            "Automobile Engineering": "/academics/bachelors/automobile-engineering/",
            
            # Admissions
            "Admissions": "/academics/admissions/",
            "Fee Structure": "/academics/admissions/fee-structure/",
            
            # Placements
            "Placements Overview": "/placements/",
            "Placement Statistics": "/placements/placement-statistics/",
            "Training Programs": "/placements/training-programs/",
            
            # Facilities
            "Library": "/about/infrastructure-and-facilities/library/",
            "Hostel": "/about/infrastructure-and-facilities/hostel-facility/",
            "Sports": "/about/infrastructure-and-facilities/sports-facilities/",
            "Canteen": "/about/infrastructure-and-facilities/canteen/",
            
            # Research & Innovation
            "Research": "/research/",
            "IIC": "/iic/",
            "Innovation Cell": "/innovation-cell/",
            
            # Events & News
            "News": "/news/",
            "Events": "/events/",
            "Announcements": "/students/announcements/",
            
            # About
            "About Institute": "/about/the-institute/",
            "Leadership": "/about/leadership/",
            "Contact": "/about/contact/",
            
            # IQAC
            "IQAC": "/iqac/",
            "NAAC": "/accreditation/naac/",
            "NBA": "/accreditation/nba/",
        }
    
    def clean_text(self, text):
        """Clean and normalize text"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        # Remove excessive whitespace
        cleaned = '\n'.join(lines)
        # Remove multiple consecutive blank lines
        while '\n\n\n' in cleaned:
            cleaned = cleaned.replace('\n\n\n', '\n\n')
        return cleaned
    
    def scrape_page(self, page_name, page_path):
        """Scrape a single page"""
        url = f"{self.base_url}{page_path}"
        print(f"🔍 Scraping: {page_name}")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Try multiple content selectors
            content = (
                soup.find('main') or 
                soup.find('article') or 
                soup.find('div', class_='entry-content') or
                soup.find('div', id='content') or
                soup.find('div', class_='content') or
                soup.find('body')
            )
            
            if content:
                # Extract text
                text = content.get_text(separator='\n', strip=True)
                cleaned_text = self.clean_text(text)
                
                # Extract tables if present
                tables = []
                for table in content.find_all('table'):
                    table_data = []
                    for row in table.find_all('tr'):
                        row_data = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                        if any(row_data):  # Skip empty rows
                            table_data.append(row_data)
                    if table_data:
                        tables.append(table_data)
                
                data = {
                    "page_name": page_name,
                    "url": url,
                    "scraped_at": datetime.now().isoformat(),
                    "text_content": cleaned_text,
                    "tables": tables,
                    "character_count": len(cleaned_text)
                }
                
                print(f"   ✅ Success: {len(cleaned_text)} characters, {len(tables)} tables")
                return data
            else:
                print(f"   ⚠️  No content found")
                return None
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return None
    
    def scrape_all(self):
        """Scrape all pages"""
        print("="*80)
        print("🚀 COMPREHENSIVE PCE WEBSITE SCRAPER")
        print("="*80)
        print(f"Total pages to scrape: {len(self.pages_to_scrape)}\n")
        
        successful = 0
        failed = 0
        
        for page_name, page_path in self.pages_to_scrape.items():
            data = self.scrape_page(page_name, page_path)
            if data:
                self.scraped_data.append(data)
                successful += 1
            else:
                failed += 1
            
            # Be respectful - wait between requests
            time.sleep(1)
        
        print("\n" + "="*80)
        print(f"✅ Scraping Complete!")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        print("="*80)
    
    def save_to_json(self):
        """Save all scraped data to individual JSON files"""
        output_dir = "chatbotdata/web_scraped"
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n💾 Saving {len(self.scraped_data)} files to {output_dir}/")
        
        # Save each page as a separate file
        for data in self.scraped_data:
            # Create safe filename
            safe_name = data['page_name'].lower().replace(' ', '_').replace('/', '_')
            filename = f"{output_dir}/{safe_name}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ {filename}")
        
        # Also save a combined file
        combined_file = f"{output_dir}/_all_pages_combined.json"
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump({
                "scraped_at": datetime.now().isoformat(),
                "total_pages": len(self.scraped_data),
                "pages": self.scraped_data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n   📦 Combined file: {combined_file}")
        print(f"\n✅ All data saved successfully!")
    
    def get_summary(self):
        """Print summary of scraped data"""
        total_chars = sum(data['character_count'] for data in self.scraped_data)
        total_tables = sum(len(data['tables']) for data in self.scraped_data)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total pages: {len(self.scraped_data)}")
        print(f"   Total characters: {total_chars:,}")
        print(f"   Total tables: {total_tables}")
        print(f"   Average chars/page: {total_chars//len(self.scraped_data):,}")

if __name__ == "__main__":
    scraper = ComprehensivePCEScraper()
    scraper.scrape_all()
    scraper.save_to_json()
    scraper.get_summary()
    
    print("\n" + "="*80)
    print("🎯 NEXT STEP: Run 'python load_scraped_data.py' to add to Pinecone")
    print("="*80)
