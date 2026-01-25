import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def save_opportunity(data):
    # Lógica de dedup
    try:
        response = supabase.table('opportunities').insert(data).execute()
        return response
    except Exception as e:
        print(f'Erro ao salvar ou duplicata: {e}')

if __name__ == "__main__":
    print(f"Supabase URL: {url}")
    # Não vamos printar a chave por segurança, mas verificamos se ela existe
    if url and key:
        print("✅ Configurações do Supabase encontradas!")
    else:
        print("❌ Faltam configurações no arquivo .env")
