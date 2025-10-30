import requests
from bs4 import BeautifulSoup
import json

# Scrape the student council page
url = "https://www.pce.ac.in/students/student-council/"
print(f"🔍 Fetching: {url}")
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(response.content, 'html.parser')

# Print page title to verify we got the page
print(f"📄 Page title: {soup.title.string if soup.title else 'No title'}")

# Try multiple selectors for content
main_content = (
    soup.find('main') or 
    soup.find('article') or 
    soup.find('div', class_='entry-content') or
    soup.find('div', id='content') or
    soup.find('div', class_='content')
)

print(f"🔍 Found main content: {main_content is not None}")

if main_content:
    # Get all text
    text_content = main_content.get_text(separator='\n', strip=True)
    
    # Clean up
    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
    clean_text = '\n'.join(lines)
    
    # Create structured data
    student_council_data = {
        "title": "Student Council | Pillai College of Engineering",
        "url": url,
        "content": clean_text,
        "sections": {}
    }
    
    # Try to find sections
    headings = main_content.find_all(['h1', 'h2', 'h3', 'h4'])
    for heading in headings:
        heading_text = heading.get_text(strip=True)
        # Get content until next heading
        content = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ['h1', 'h2', 'h3', 'h4']:
                break
            content.append(sibling.get_text(strip=True))
        
        if content:
            student_council_data["sections"][heading_text] = ' '.join(content)
    
    # Save to JSON
    output_file = 'chatbotdata/student_council.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(student_council_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Scraped and saved student council data to {output_file}")
    print(f"\n📄 Preview of content ({len(clean_text)} characters):")
    print(clean_text[:500])
    print("\n...")
    print(f"\n📊 Found {len(student_council_data['sections'])} sections")
    for section in student_council_data['sections'].keys():
        print(f"  - {section}")
else:
    print("❌ Could not find main content")
