from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

try:
    models = client.models.list()
    print('\n✅ Available Groq Models:')
    print('=' * 50)
    for m in models.data:
        if m.active:
            print(f'  ✓ {m.id}')
    print('=' * 50)
except Exception as e:
    print(f'Error: {e}')
