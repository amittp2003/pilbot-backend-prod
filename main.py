# from fastapi import FastAPI, Request, Body
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from huggingface_hub import InferenceClient
# import faiss
# import pickle
# import os
# from dotenv import load_dotenv
# import mail
# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_community.vectorstores import FAISS
# from langchain import LLMChain
# from langchain_community.utilities import GoogleSearchAPIWrapper
# from langchain.tools import Tool
# from langchain.agents import initialize_agent
# from langchain_huggingface import HuggingFaceEndpoint

# # Load the pre-trained index and vector store
# index = faiss.read_index("index_PCE.index")
# with open("faiss_PCE.pkl", "rb") as fp:
#     store = pickle.load(fp)
# store.index = index

# nav_index = faiss.read_index("index_nav.index")
# with open("faiss_nav.pkl", "rb") as f:
#     nav_store = pickle.load(f)
# nav_store.index = nav_index

# load_dotenv()

# # Hugging Face Configuration
# HF_TOKEN = os.getenv('HF_TOKEN')


# # Templates
# # TEMPLATE = """
# # You are a chatbot assistant for Pillai College of Engineering, designed to provide information about student services and college-related inquiries. 
# # UNDERSTAND THE USER QUERY AND RESPOND ACCORDINGLY. USER MAY GREET SOMETIME LIKE 'HELLO', 'HEY HI'. EVERYTIME IT IS NOT NECESSARY TO REFER THE RETRIVED DOCS TO RESPOND THE QUERY.

# # Guidelines:
# # 1. **If unsure**: Respond with, "Sorry, I'm not sure about the answer. Please visit the website for further assistance."
# # 2. **No fabricated answers**: Avoid making up responses; only provide verified information.
# # 3. **Clarifying unclear queries**: If the user's question is unclear, kindly ask for clarification or additional context.

# # **Examples**
# # Human: Hello
# # Chatbot: Hello! How may I assist you today?

# # Human: what's the weather today?
# # Chatbot: Sorry for the inconvience, but I can help you with information regarding the PCE.


# # ---------
# # {summaries}
# # ---------
# # Human: {question}
# # Chatbot: 
# # """

# TEMPLATE = '''
# You are a chatbot assistant for Pillai College of Engineering, designed to provide information about student services and college-related inquiries.

# Guidelines:
# 1. If unsure: Respond with "Sorry, I'm not sure about the answer. Please visit the website for further assistance."
# 2. No fabricated answers: Only provide verified information from the given context
# 3. For unclear queries: Ask for clarification

# Context: {summaries}
# Question: {question}


# Examples:
# Human: Hello
# Chatbot: Hi! How can I assist you with PCE-related information today?

# Remember to:
# - Keep responses concise and relevant to the query
# - Don't dump all available information at once
# - Match the formality level of the user's query
# '''
# # Intent and Reframe Templates
# INTENT_TEMPLATE = '''
# Classify the intent of the user query as "Broad" if it is a general request or "Specific" if it asks for detailed information or "Mail" if it asks to mail the information.

# Query: "{user_query}"

# Intent:
# '''

# REFRAME_TEMPLATE = '''
# You are an AI tasked with reframing questions for clarity and conciseness.

# **Example**
# QUESTION: Heyy
# REFRAMED QUESTION: Hey 

# QUESTION: computer engineering
# REFRAMED QUESTION: give me syllabus of computer engineering

# User Question: {user_question}
# Reframed Question:
# '''
# # Nav_prompt='''
# # You are an AI assitant that answers to questions asked regarding CAMPUS NAVIGATION ONLY!!. You are developed to assist with navigation in PCE campus. When user query is about welcome respond accordingly. IF THE CONTEXT RELATED TO THE QUERY IS NOT SUFFICIENT SIMPLY SAY "Sorry for inconvience Iam not able answer your query!!"  

# Nav_prompt = '''
# You are a helpful navigation assistant that answers to questions asked regarding CAMPUS NAVIGATION ONLY!!. You are developed to assist with navigation in PCE campus. Using the provided context about rooms and locations, 
# give clear, step-by-step directions. Whenever the query is about navigation format your response in this structure else respond accordingly:

# Current Location: [Extract or infer current location from context Else guide from Reception]
# Destination: [Destination being asked about]
# Route:
# 1. [First step]
# 2. [Second step]
# ...

# Nearby Facilities [to Destination]:
# - [List relevant nearby rooms/facilities]

# Context: {summaries}
# Question: {question}

# Remember to:
# - Say Sorry If no appropriate context is available
# - Keep directions concise and clear
# - Mention room numbers when available
# - Include relevant landmarks
# - List nearby facilities at the end

# Answer:'''

# # Utility Functions
# # def generate_prompt(question, retrieved_docs, prmt_TEM):
# #     doc_summaries = "\n".join([f"CONTENT: {doc.page_content}" for doc in retrieved_docs])
# #     prompt = prmt_TEM.format(question=question, summaries=doc_summaries)
# #     return prompt

# def query_llama(question,  doc_summaries, prmt_TEM, repo_id='mistralai/Mistral-7B-Instruct-v0.3'):
#     # llm=HuggingFaceEndpoint(repo_id=repo_id,)

#     # prompt=PromptTemplate(input_variables=["summaries", "question"], template=prmt_TEM)
#     # chain = prompt | llm | StrOutputParser()
#     # resp= chain.invoke({"summaries": summaries, "question":question})
    
#     # llm_chain=LLMChain(llm, prompt)
#     # response=llm.invoke(prompt)
#     # response=llm_chain.run()
    
#     prompt = prmt_TEM.format(question=question, summaries=doc_summaries)
#     client = InferenceClient(repo_id, token=HF_TOKEN)
#     response = client.chat_completion(
#         messages=[{"role": "user", "content": prompt}],
#         max_tokens=500,
#         stream=False
#     )
#     return response['choices'][0]['message']['content']
#     # return resp


# def query_with_template_and_sources(question, vectorstore, prmt_TEM):
#     docs = vectorstore.similarity_search(question, k=2)
#     doc_summaries = "\n".join([f"CONTENT: {doc.page_content}" for doc in docs])
#     # prompt = generate_prompt(question, docs, prmt_TEM)
#     answer = query_llama(question, doc_summaries, prmt_TEM)
#     return answer

# def query_with_template_and_sources_NAV(question, vectorstore, prmt_TEM):
#     doc_summaries = vectorstore.similarity_search(question, k=2)
#     # doc_summaries = "\n".join([f"CONTENT: {doc.page_content}" for doc in docs])
#     # prompt = generate_prompt(question, docs, prmt_TEM)
#     answer = query_llama(question, doc_summaries, prmt_TEM)
#     return answer

# # FastAPI Application
# app = FastAPI()

# # CORS Middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Pydantic Model for Request
# class ChatRequest(BaseModel):
#     message: str
#     user_name: str = ""
#     email: str = ""

# class Message(BaseModel):
#     text: str
#     sender: str
#     topic: str

# @app.post("/chat/general")
# async def chat(request: ChatRequest):
#     try:
#         # Determine Intent
#         # intent = query_llama(
#         #     INTENT_TEMPLATE.format(user_query=request.message)
#         # )
#         # print(intent)

#         # # Reframe Question
#         # reframed_question = query_llama(
#         #     REFRAME_TEMPLATE.format(user_question=request.message)
#         # )
#         # print(reframed_question)

#         # Generate Response
#         response = query_with_template_and_sources(request.message, store, TEMPLATE)

#         # Optional: Send Email if Intent is Mail
#         # if intent.strip().lower() == "mail":
#         #     # Assuming you'll import or define the mail sending function
#         #     import mail
#         #     mail.sendEmail(request.email, request.user_name, response)

#         return {
#             "reply": response,
#             # "intent": intent
#         }
    
#     except Exception as e:
#         return {
#             "reply": f"An error occurred: {str(e)}",
#             "intent": "Error"
#         }
    
# @app.post("/chat/academics")
# def handle_academics_query(request: ChatRequest):
#     # Academics-specific logic
#     print(request.message)
#     return {"reply": request.message}

# @app.post("/chat/campus-nav")
# def handle_campus_life_query(request: ChatRequest):
#     # Campus life specific logic
    
#     try:
#         if nav_store is None:
#             raise Exception("Navigation store not initialized")


#         nav_response=query_with_template_and_sources_NAV(request.message, nav_store, Nav_prompt)
#         # print(nav_response)

#         return {"reply": nav_response}
    
#     except Exception as e:
#         return {
#             "reply": f"An error occurred: {str(e)}",
#             "intent": "Error"
#         }

# @app.post("/chat/admissions")
# def handle_admissions_query(message: str):
#     # Admissions-specific logic
#     return {"reply": "Admissions-related response"}

# @app.post('/chat/mail')
# def handle_sending_mail(message: Message, email: str = Body(...)):
#     user= email.split('@')[0]
#     print("Iam here", message.text,email)
#     mail.sendEmail(email, user, message.text)

#     return {'reply': "Mail sent"}


from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from langchain_huggingface import HuggingFaceEmbeddings
import os
import gc  # Garbage collector for memory optimization
import pinecone
from groq import Groq
from services import email_service
from middleware import RateLimiter, sanitize_input, get_client_ip
from dotenv import load_dotenv
load_dotenv()

# Initialize rate limiter
rate_limiter = RateLimiter(
    requests_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', 30)),
    requests_per_hour=int(os.getenv('RATE_LIMIT_PER_HOUR', 200))
)


# Environment variables
HF_TOKEN = os.getenv('HF_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
HOSTS = os.getenv('HOSTS', '*')  # Default to wildcard if not set
PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
GEN_INDEX = os.environ['GEN_INDEX']
NAV_INDEX = os.environ['NAV_INDEX']

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize Pinecone
pinecone_c = pinecone.Pinecone(api_key=PINECONE_API_KEY)
gen_index= pinecone_c.Index(GEN_INDEX)
nav_index = pinecone_c.Index(NAV_INDEX)


TEMPLATE = '''
You are PilBot, a friendly AI assistant for Pillai College of Engineering (PCE). You're here to help students like a helpful friend!

YOUR PERSONALITY:
- Friendly, warm, and conversational
- Helpful and encouraging
- Use casual, student-friendly language
- Smart and knowledgeable about both PCE specifically AND general college/engineering topics

HOW TO ANSWER:
1. **For PCE-specific questions** (admissions, fees, programs, campus, etc.):
   - PRIORITIZE the Context below if it has relevant info
   - If context is incomplete, use your general knowledge to fill gaps
   - Always cite when you're using official PCE data vs. general knowledge

2. **For general questions** (greetings, "who are you", "how are you", etc.):
   - Respond naturally using your own intelligence
   - Introduce yourself as PilBot, the PCE assistant
   - Be warm and welcoming

3. **For questions OUTSIDE PCE scope** (weather, sports, entertainment, etc.):
   - Politely redirect: "Haha, I wish I could help with that, but I'm specifically here for PCE-related stuff! 😅 Ask me about admissions, courses, campus facilities, or anything about engineering!"

4. **When context has [No specific PCE database matches]**:
   - Still answer if you have general knowledge relevant to PCE/engineering
   - Be honest that you're using general knowledge, not official PCE data
   - Example: "Based on general engineering college standards (I don't have PCE's exact data on this), typically..."

Context from PCE Database:
{summaries}

Student's Question: {question}

Remember: 
- Use BOTH the context AND your own intelligence
- Be specific when you have PCE data, helpful when you don't
- Always friendly and student-focused!

Answer:'''
# Intent and Reframe Templates
INTENT_TEMPLATE = '''
Classify the intent of the user query as "Broad" if it is a general request or "Specific" if it asks for detailed information or "Mail" if it asks to mail the information.

Query: "{user_query}"

Intent:
'''

Nav_prompt = '''
You are a navigation assistant for Pillai College of Engineering (PCE) campus. You MUST ONLY use the location information from the context provided below.

CRITICAL RULES:
1. ONLY use location details from the Context below
2. If the location is not in the context, say: "I don't have information about that location. Please check with the reception."
3. Extract ALL details: room numbers, floor, wing, nearby facilities, and exact directions
4. Always include specific room numbers and directions from the context

Context from PCE Campus Navigation Database:
{summaries}

User Question: {question}

For navigation questions, provide this structure:
📍 Location: [Room number and name from context]
🏢 Floor & Wing: [Exact floor and wing from context]  
🚶 Directions: [Exact directions from context]
🏠 Nearby: [List nearby rooms/facilities from context]

IMPORTANT: Use ONLY the exact information from the context above. Include all specific details like room numbers, floor names, and step-by-step directions that appear in the context.

Answer:'''

def query_llama(question, doc_summaries, prmt_TEM, repo_id='llama-3.1-8b-instant'):
    """
    Query LLM using Groq API - Ultra-fast and free inference
    """
    prompt = prmt_TEM.format(question=question, summaries=doc_summaries)
    
    # Groq models to try in order (verified available models as of Oct 2025)
    models_to_try = [
        'llama-3.1-8b-instant',          # Meta Llama 3.1 8B - Fastest & free
        'llama-3.3-70b-versatile',       # Meta Llama 3.3 70B - Most capable
        'qwen/qwen3-32b',                # Qwen 3 32B - Powerful alternative
        'openai/gpt-oss-20b',            # GPT OSS 20B - Good fallback
    ]
    
    for model_id in models_to_try:
        try:
            # Use Groq API (super fast!)
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an AI assistant EXCLUSIVELY for Pillai College of Engineering (PCE). 

CRITICAL INSTRUCTIONS:
1. ONLY use information from the context provided in the user's message
2. Extract and include ALL relevant details: numbers, names, dates, programs, departments, facilities
3. Be comprehensive - if the context lists multiple items, include them ALL
4. NEVER add information not present in the context
5. If information is not in the context, clearly state: "I don't have that information in my database"
6. Be specific and detailed when information IS available
7. Use exact terminology and names from the context

Respond in a friendly, professional manner while strictly following these rules."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=model_id,
                temperature=0.3,  # Lower temperature for more factual, less creative responses
                max_tokens=800,  # Increased for more comprehensive answers
                top_p=0.9,  # More focused on high-probability tokens
                stream=False
            )
            
            # Extract the response
            result = chat_completion.choices[0].message.content.strip()
            
            if result and len(result) > 10:  # If we got a valid response
                print(f"✓ Success with Groq model: {model_id}")
                return result
                
        except Exception as e:
            error_msg = str(e)[:100]
            print(f"Groq model {model_id} failed: {error_msg}")
            continue  # Try next model
    
    # If all models fail, return a context-aware response
    print("All Groq models failed, using fallback response")
    return generate_fallback_response(question, doc_summaries)


def generate_fallback_response(question, doc_summaries):
    """
    Generate a simple response based on retrieved documents when AI models are unavailable
    """
    if not doc_summaries or doc_summaries.strip() == '':
        return "I apologize, but I couldn't find relevant information to answer your question. The AI service is currently experiencing issues. Please try asking about:\n- College programs and courses\n- Admission procedures\n- Campus facilities\n- Student activities"
    
    # Extract key information from summaries
    lines = doc_summaries.split('\n')
    relevant_info = []
    for line in lines[:3]:  # Take first 3 matches
        if 'Content:' in line:
            content = line.replace('Content:', '').strip()
            if content:
                relevant_info.append(content)
    
    if relevant_info:
        return f"Based on available information:\n\n" + "\n\n".join(relevant_info) + "\n\nNote: The AI assistant is currently unavailable, so this is a direct excerpt from our database."
    
    return "I found some information but the AI service is temporarily unavailable. Please try again in a moment, or contact the college directly for immediate assistance."


def query_with_template_and_sources(question, vectorstore, prmt_TEM):    
    """Query general knowledge with more context for comprehensive answers"""
    
    query_lower = question.lower().strip()
    
    # Handle simple greetings with quick response (no AI needed)
    greeting_keywords = ['hello', 'hi', 'hey', 'hii', 'helo', 'hola']
    if any(query_lower == greet or query_lower == greet + '!' for greet in greeting_keywords):
        return "Hey there! 👋 I'm PilBot, your friendly assistant for Pillai College of Engineering! I can help you with:\n\n✨ Admissions & eligibility\n📚 Courses & programs\n🏫 Campus facilities & navigation\n🎓 Student activities & events\n\nWhat would you like to know about PCE?"
    
    # For ALL other queries, do vector search first
    query_vector = get_embeddings().embed_query(question)
    query_results = vectorstore.query(vector=query_vector, top_k=10, include_metadata=True)
    
    # Get relevant context (even if low relevance, still include it)
    doc_summaries = '\n\n'.join([
        f"[Relevance: {match['score']:.2f}] {match['metadata']['text']}" 
        for match in query_results['matches'] if match['score'] > 0.25  # Lower threshold to include more context
    ])
    
    # If no context at all, provide empty context but still let AI respond
    if not doc_summaries:
        doc_summaries = "[No specific PCE database matches found for this query]"
    
    # ALWAYS call the AI - let it use both its knowledge AND the context
    answer = query_llama(question, doc_summaries, prmt_TEM)
    return answer

def query_with_template_and_sources_NAV(question, vectorstore, prmt_TEM):
    """Query navigation with detailed context"""
    query_vector = get_embeddings().embed_query(question)
    # Get more navigation options
    query_results = vectorstore.query(vector=query_vector, top_k=5, include_metadata=True)
    
    # Format with all metadata for navigation
    doc_summaries = '\n\n'.join([
        f"[Match Score: {match['score']:.2f}]\n{match['metadata']['text']}" 
        for match in query_results['matches'] if match['score'] > 0.25
    ])
    
    if not doc_summaries:
        return "I don't have information about that location. Please check with the reception or visit www.pce.ac.in/campus-map for more details."
    
    answer = query_llama(question, doc_summaries, prmt_TEM)
    return answer

# FastAPI Application
app = FastAPI()

# Lazy-load embeddings to save memory (OPTIMIZED)
_embeddings = None

def get_embeddings():
    """Lazy-load embeddings model with maximum optimization"""
    global _embeddings
    if _embeddings is None:
        # Using original all-mpnet-base-v2 (best quality) with aggressive optimization
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            model_kwargs={'device': 'cpu'}
            # Removed encode_kwargs to avoid argument conflicts
        )
        gc.collect()
    return _embeddings

# CORS Middleware - Allow multiple origins
if HOSTS == '*':
    allowed_origins = ['*']
    print("⚠️ CORS: Allowing ALL origins (wildcard mode)")
else:
    allowed_origins = [origin.strip() for origin in HOSTS.split(',')]
    print(f"✅ CORS: Allowing specific origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Force garbage collection after startup to free memory
@app.on_event("startup")
async def startup_event():
    """Run garbage collection on startup to minimize memory usage"""
    gc.collect()
    print("✅ Startup complete - Memory optimized")

# Health Check Endpoint
@app.get("/")
async def root():
    return {
        "status": "alive",
        "message": "Pilbot API is running",
        "version": "1.0.0",
        "endpoints": [
            "/chat/general",
            "/chat/academics", 
            "/chat/campus-nav",
            "/chat/admissions",
            "/chat/mail"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Pydantic Model for Request with validation
class ChatRequest(BaseModel):
    message: str
    user_name: str = ""
    email: str = ""
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v) > 2000:
            raise ValueError('Message too long (max 2000 characters)')
        # Sanitize input
        return sanitize_input(v)
    
    @validator('email')
    def validate_email(cls, v):
        if v and len(v) > 100:
            raise ValueError('Email too long')
        return sanitize_input(v) if v else ""
    
    @validator('user_name')
    def validate_user_name(cls, v):
        if v and len(v) > 100:
            raise ValueError('Name too long')
        return sanitize_input(v) if v else ""

class Message(BaseModel):
    text: str
    sender: str
    topic: str

class EmailRequest(BaseModel):
    message: str
    email: str

@app.post("/chat/general")
async def chat(request: ChatRequest, http_request: Request):
    # Rate limiting
    client_ip = get_client_ip(http_request)
    if rate_limiter.is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    
    try:
        # Generate Response
        response = query_with_template_and_sources(request.message, gen_index, TEMPLATE)
        gc.collect()  # Free memory after processing
        return {
            "reply": response,
        }
    
    except Exception as e:
        # Log error internally but don't expose details to user
        print(f"Error in /chat/general: {str(e)}")  # Use proper logging in production
        gc.collect()  # Free memory even on error
        return {
            "reply": "I'm having trouble processing your request right now. Please try again in a moment.",
            "intent": "Error"
        }
    
@app.post("/chat/academics")
def handle_academics_query(request: ChatRequest, http_request: Request):
    # Rate limiting
    client_ip = get_client_ip(http_request)
    if rate_limiter.is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    
    try:
        # Generate Response using general index for academic queries
        response = query_with_template_and_sources(request.message, gen_index, TEMPLATE)
        gc.collect()  # Free memory
        return {
            "reply": response
        }
    except Exception as e:
        print(f"Error in /chat/academics: {str(e)}")
        gc.collect()
        return {
            "reply": "I'm having trouble processing your request right now. Please try again in a moment.",
            "intent": "Error"
        }

@app.post("/chat/campus-nav")
def handle_campus_life_query(request: ChatRequest, http_request: Request):
    # Rate limiting
    client_ip = get_client_ip(http_request)
    if rate_limiter.is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    
    try:
        if nav_index is None:
            raise Exception("Navigation store not initialized")

        nav_response=query_with_template_and_sources_NAV(request.message, nav_index, Nav_prompt)
        gc.collect()  # Free memory
        return {"reply": nav_response}
    
    except Exception as e:
        print(f"Error in /chat/campus-nav: {str(e)}")
        gc.collect()
        return {
            "reply": "I'm having trouble processing your request right now. Please try again in a moment.",
            "intent": "Error"
        }

@app.post("/chat/admissions")
def handle_admissions_query(request: ChatRequest, http_request: Request):
    # Rate limiting
    client_ip = get_client_ip(http_request)
    if rate_limiter.is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    
    try:
        # Generate Response using general index for admissions queries
        response = query_with_template_and_sources(request.message, gen_index, TEMPLATE)
        gc.collect()  # Free memory
        return {
            "reply": response
        }
    except Exception as e:
        print(f"Error in /chat/admissions: {str(e)}")
        gc.collect()
        return {
            "reply": "I'm having trouble processing your request right now. Please try again in a moment.",
            "intent": "Error"
        }

@app.post('/chat/mail')
def handle_sending_mail(request: EmailRequest, http_request: Request):
    # Stricter rate limiting for email (more expensive operation)
    client_ip = get_client_ip(http_request)
    if rate_limiter.is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    
    try:
        # Sanitize email input
        sanitized_email = sanitize_input(request.email, max_length=100)
        sanitized_message = sanitize_input(request.message, max_length=2000)
        
        user = sanitized_email.split('@')[0]
        print(f"📧 Mail request received - To: {sanitized_email}, Message: {sanitized_message[:50]}...")
        
        email_service.sendEmail(sanitized_email, user, sanitized_message)
        
        return {
            'reply': f"✅ Email sent successfully to {sanitized_email}! Check your inbox.",
            'success': True
        }
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Email failed: {error_msg}")
        return {
            'reply': f"❌ Failed to send email. Error: {error_msg}. Please check your email configuration.",
            'success': False
        }