import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Carrega as variáveis do arquivo .env
load_dotenv()

# Pega o token do bot
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde 'Olá!' quando o comando /start é enviado."""
    await update.message.reply_text("Olá! Sou o Opportunity Aggregator Bot. 🤖\nEnvie /ping para testar minha latência.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde 'Pong' para testar se o bot está vivo."""
    await update.message.reply_text("Teste para o Flavortown : 🤖 🎂")

if __name__ == '__main__':
    if not TOKEN:
        print("❌ Erro: A variável TELEGRAM_BOT_TOKEN não foi encontrada no .env")
        exit(1)

    print("🤖 Iniciando o bot...")
    application = ApplicationBuilder().token(TOKEN).build()

    # Adiciona os comandos que o bot entende
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", ping))

    print("✅ Bot rodando! Pressione Ctrl+C para parar.")
    # Roda o bot até você apertar Ctrl+C
    application.run_polling()
