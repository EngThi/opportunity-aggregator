import schedule
import time
import os
from src import database, notifier
from src.sources import devpost, mlh, tabnews, github_jobs
from dotenv import load_dotenv

load_dotenv()

def job():
    print("🚀 Iniciando tarefa diária de sincronização...")
    
    all_opps = []
    all_opps.extend(devpost.fetch_devpost())
    all_opps.extend(mlh.fetch_mlh())
    all_opps.extend(tabnews.fetch_tabnews())
    all_opps.extend(github_jobs.fetch_github_jobs())
    
    saved_count = database.save_opportunity(all_opps)
    print(f"✅ Sincronização concluída. {saved_count} novas oportunidades salvas.")
    
    # Notificar um chat_id padrão se configurado (opcional)
    admin_chat_id = os.environ.get("ADMIN_CHAT_ID")
    if admin_chat_id:
        today_opps = database.get_today_opportunities()
        notifier.send_telegram_digest(admin_chat_id, today_opps)

if __name__ == "__main__":
    # Executa uma vez ao iniciar
    job()
    
    # Agenda para rodar todo dia às 09:00
    schedule.every().day.at("09:00").do(job)
    
    print("⏳ Scheduler ativo. Rodando job diariamente às 09:00.")
    while True:
        schedule.run_pending()
        time.sleep(60)
