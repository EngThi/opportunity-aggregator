import os
from dotenv import load_dotenv
from supabase import create_client

load dotenv()

url = os.environ.get(SUPABASE_URL)
key = os.environ.get(SUPABASE_KEY)

def save_opportunity(data):
    # Lógica de dedup
    try:
        response = supabase.table('opportunities').insert(data).execute()
        return response
    except Exception as e:
        print(f'Erro ao salvar ou duplicata: {e}')
