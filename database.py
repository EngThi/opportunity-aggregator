import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def save_opportunity(data):
    """
    Saves an opportunity to Supabase using upsert on the 'url' field to prevent duplicates.
    Expects 'data' to be a list of dictionaries or a single dictionary.
    """
    try:
        # Assumes 'url' is the unique identifier in the Supabase table
        response = supabase.table('opportunities').upsert(data, on_conflict='url').execute()
        return response
    except Exception as e:
        print(f'Erro ao salvar ou fazer upsert: {e}')
        return None

def get_latest_opportunities(limit=5):
    """
    Retrieves the latest opportunities from Supabase.
    """
    try:
        response = supabase.table('opportunities').select("*").order('created_at', descending=True).limit(limit).execute()
        return response.data
    except Exception as e:
        print(f'Erro ao buscar oportunidades: {e}')
        return []

if __name__ == "__main__":
    print(f"Supabase URL: {url}")
    # Não vamos printar a chave por segurança, mas verificamos se ela existe
    if url and key:
        print("✅ Configurações do Supabase encontradas!")
    else:
        print("❌ Faltam configurações no arquivo .env")
