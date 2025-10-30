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


from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEmbeddings
from huggingface_hub import InferenceClient
import os
import pinecone
import requests
from groq import Groq
from services import email_service
from dotenv import load_dotenv
load_dotenv()


# Environment variables
HF_TOKEN = os.getenv('HF_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
HOSTS= os.environ['HOSTS']
PINECONE_API_KEY=os.environ['PINECONE_API_KEY']
GEN_INDEX=os.environ['GEN_INDEX']
NAV_INDEX=os.environ['NAV_INDEX']

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize Pinecone
pinecone_c = pinecone.Pinecone(api_key=PINECONE_API_KEY)
gen_index= pinecone_c.Index(GEN_INDEX)
nav_index = pinecone_c.Index(NAV_INDEX)


TEMPLATE = '''
You are an AI assistant EXCLUSIVELY for Pillai College of Engineering (PCE). You MUST ONLY use information from the context provided below.

CRITICAL RULES:
1. ONLY answer using facts from the Context below - DO NOT use any external knowledge
2. If the Context doesn't contain the answer, say: "I don't have that specific information in my database. Please contact PCE directly or visit www.pce.ac.in"
3. For greetings, respond warmly but then ask how you can help with PCE information
4. Be specific and detailed when information IS available in the context
5. Include specific data like numbers, dates, names when they appear in the context

Context from PCE Database:
{summaries}

User Question: {question}

Instructions:
- Extract ALL relevant details from the context
- Be comprehensive - include programs, departments, facilities, contacts, etc.
- Use exact names, numbers, and details from the context
- If context has lists or multiple items, include them all
- Never make up information that's not in the context

Answer based ONLY on the context above:'''
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
    query_vector = embeddings.embed_query(question)
    # Increased top_k to get more relevant information
    query_results = vectorstore.query(vector=query_vector, top_k=10, include_metadata=True)
    
    # Format context with scores to prioritize most relevant info
    doc_summaries = '\n\n'.join([
        f"[Relevance: {match['score']:.2f}] {match['metadata']['text']}" 
        for match in query_results['matches'] if match['score'] > 0.3  # Filter low relevance
    ])
    
    if not doc_summaries:
        return "I don't have specific information about that in my database. Please contact PCE directly or visit www.pce.ac.in for more details."
    
    answer = query_llama(question, doc_summaries, prmt_TEM)
    return answer

def query_with_template_and_sources_NAV(question, vectorstore, prmt_TEM):
    """Query navigation with detailed context"""
    query_vector = embeddings.embed_query(question)
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

# Embeddings model
embeddings=HuggingFaceEmbeddings()

# CORS Middleware - Allow multiple origins
allowed_origins = HOSTS.split(',') if ',' in HOSTS else [HOSTS] if HOSTS != '*' else ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if HOSTS != '*' else ['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

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

# Pydantic Model for Request
class ChatRequest(BaseModel):
    message: str
    user_name: str = ""
    email: str = ""

class Message(BaseModel):
    text: str
    sender: str
    topic: str

class EmailRequest(BaseModel):
    message: str
    email: str

@app.post("/chat/general")
async def chat(request: ChatRequest):
    try:

        # Generate Response
        response = query_with_template_and_sources(request.message, gen_index, TEMPLATE)
        return {
            "reply": response,
            # "intent": intent
        }
    
    except Exception as e:
        return {
            "reply": f"An error occurred: {str(e)}",
            "intent": "Error"
        }
    
@app.post("/chat/academics")
def handle_academics_query(request: ChatRequest):
    # Academics-specific logic
    print(request.message)
    return {"reply": request.message}

@app.post("/chat/campus-nav")
def handle_campus_life_query(request: ChatRequest):
    # Campus life specific logic
    
    try:
        if nav_index is None:
            raise Exception("Navigation store not initialized")


        nav_response=query_with_template_and_sources_NAV(request.message, nav_index, Nav_prompt)
        # print(nav_response)

        return {"reply": nav_response}
    
    except Exception as e:
        return {
            "reply": f"An error occurred: {str(e)}",
            "intent": "Error"
        }

@app.post("/chat/admissions")
def handle_admissions_query(message: str):
    # Admissions-specific logic
    return {"reply": "Admissions-related response"}

@app.post('/chat/mail')
def handle_sending_mail(request: EmailRequest):
    try:
        user = request.email.split('@')[0]
        print(f"📧 Mail request received - To: {request.email}, Message: {request.message[:50]}...")
        
        email_service.sendEmail(request.email, user, request.message)
        
        return {
            'reply': f"✅ Email sent successfully to {request.email}! Check your inbox.",
            'success': True
        }
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Email failed: {error_msg}")
        return {
            'reply': f"❌ Failed to send email. Error: {error_msg}. Please check your email configuration.",
            'success': False
        }