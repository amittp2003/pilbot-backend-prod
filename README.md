# 🤖 Pilbot - AI Chatbot for Pillai College of Engineering

Complete AI-powered chatbot with **878+ knowledge vectors**, auto-updating web scraper, and RAG (Retrieval Augmented Generation) using Groq AI + Pinecone.

---

## ✨ Features

- **878 Knowledge Vectors**: 290 original PCE data + 588 web-scraped pages
- **Smart RAG System**: Retrieves top 10 results with relevance filtering
- **Auto-Updates**: Scrapes 34+ PCE website pages daily
- **Campus Navigation**: 71 detailed location entries across 5 floors
- **Email Integration**: Send responses directly to email
- **4 AI Models**: Automatic fallback (llama-3.1-8b-instant, llama-3.3-70b-versatile, etc.)
- **Premium UI**: Perplexity-inspired dark theme with cyan/blue/black/grey

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd pilbot_backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:
```env
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
GEN_INDEX=pilbot-general
NAV_INDEX=pilbot-navigation
HOSTS=http://localhost:3000
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

### 3. Load Data

```bash
# Load original PCE data
python load_general_data.py
python load_navigation_data.py

# Scrape latest website data (24 pages, 253K chars)
python manual_update.py
```

### 4. Run Backend

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Frontend Setup

```bash
cd pilbot-frontend
npm install
npm start  # Runs on http://localhost:3000
```

---

## 🔄 Auto-Update System

### Manual Update (Anytime)
```bash
python manual_update.py
```
Scrapes all 34 PCE pages and updates Pinecone (takes ~2 minutes)

### Automated Updates
Already configured in `auto_update_system.py`:
- **Daily**: 2:00 AM
- **Weekly**: Sunday 3:00 AM

Pages auto-scraped:
- Student Council, Activities, Scholarships
- All 6 Engineering Departments (Computer, IT, EXTC, ECS, Mechanical, Automobile)
- Admissions, Placements, Research
- Events, News, Announcements
- Infrastructure (Library, Hostel, Sports, Canteen)
- About, Leadership, Contact, IQAC, NAAC, NBA

---

## 📊 System Status

**Current Data:**
- Pinecone Vectors: **878** (290 base + 588 web)
- Navigation Entries: **71** (5 floors)
- Web Pages Scraped: **24**
- Total Characters: **253,133**
- Tables Extracted: **157**

**Check System:**
```bash
python check_system.py
```

**Check Specific Query:**
```bash
python test_student_council.py  # Example test script
```

---

## 🛠️ Tech Stack

**Backend:**
- FastAPI 0.115.6
- Groq AI 0.33.0 (llama-3.1-8b-instant)
- Pinecone 6.0.1 (768-dim vectors)
- Sentence Transformers (all-mpnet-base-v2)
- BeautifulSoup4 4.14.2 (web scraping)
- LangChain 1.0.3

**Frontend:**
- React 18.3.1
- TailwindCSS 3.4.13
- Framer Motion 11.11.1
- Axios 1.7.7

---

## 📁 Key Files

```
pilbot_backend/
├── main.py                       # FastAPI app with RAG
├── load_general_data.py          # Load 290 base vectors
├── load_navigation_data.py       # Load 71 navigation entries
├── scrape_all_pce_pages.py       # Scrape 34 PCE pages
├── load_scraped_data.py          # Load web data to Pinecone
├── manual_update.py              # Manual update trigger
├── auto_update_system.py         # Scheduled auto-updates
├── check_system.py               # System status checker
├── chatbotdata/                  # 41 JSON files (original)
├── navigation/                   # 5 JSON files (floors)
└── chatbotdata/web_scraped/      # 24 scraped pages

pilbot-frontend/
├── src/ChatInterfacePremium.js   # Premium UI component
└── .env                          # REACT_APP_API_URL
```

---

## 🧪 Test It

Go to http://localhost:3000 and try:

1. **"Tell me about student council"**
   → Shows members with names, positions, years

2. **"What programs does PCE offer?"**
   → Lists all B.Tech programs with details

3. **"Where is the library?"**
   → S302, Third Floor, S Wing with directions

4. **"What is the placement process?"**
   → Complete placement guide (34K chars!)

---

## 🚀 Deployment

### Backend (Render.com)
1. Push to GitHub
2. Create Web Service on Render
3. Add environment variables
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)
1. Update `REACT_APP_API_URL` to Render URL
2. Push to GitHub
3. Import project on Vercel
4. Add environment variable
5. Deploy

---

## 📈 Results

**AI Accuracy Improvements:**
- Increased retrieval: 5→10 (general), 3→5 (navigation)
- Relevance filtering: score > 0.3
- Lower temperature: 0.7→0.3 (more factual)
- Increased tokens: 500→800 (comprehensive answers)
- Strengthened prompts to use ONLY context

**Student Council Example:**
- Before: Score 0.524 (wrong data - Academic Council)
- After: Score 0.806 (correct data with member names!)

---

## 🔧 Troubleshooting

**Backend won't start:**
```bash
cd pilbot_backend
venv\Scripts\activate
python check_system.py
```

**No data in Pinecone:**
```bash
python load_general_data.py
python load_navigation_data.py
python manual_update.py
```

**Frontend can't connect:**
- Check `.env` has correct API URL
- Verify backend is running on port 8000
- Check CORS settings in `main.py`

---

## 📝 License

MIT License - Feel free to use for your portfolio!

---

## 🙌 Credits

Built for Pillai College of Engineering
- Groq AI for fast, free inference
- Pinecone for vector database
- PCE website for data source
