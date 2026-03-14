import os
import asyncio
import random
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from src import database, scorer, config
from src.sources import devpost, mlh, tabnews, github_jobs

load_dotenv()
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bem-vindo ao Opportunity Aggregator!\n\n"
        "Comandos:\n"
        "/search <termo> - Busca nas fontes\n"
        "/today - Oportunidades novas de hoje\n"
        "/match - Ver compatibilidade com suas skills\n"
        "/models - Fetch and list real-time available models"
    )

async def list_models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fetches and lists real-time available models from both Google and OpenRouter.
    """
    await update.message.reply_text("🔎 Fetching live models from APIs... Please wait.")
    
    # Run fetch in threads to avoid blocking
    google_models = await asyncio.to_thread(config.fetch_available_google_models)
    or_models = await asyncio.to_thread(config.fetch_available_openrouter_models)
    
    text = "🤖 **Real-time Available Models**\n\n"
    
    text += "📍 **Google Gemini API:**\n"
    if google_models:
        # Show top 10 to avoid huge messages
        text += ", ".join(google_models[:10]) + (f" (+{len(google_models)-10})" if len(google_models)>10 else "")
    else:
        text += "None found or key error."
        
    text += "\n\n📍 **OpenRouter API:**\n"
    if or_models:
        # Filter for free ones or just show top 10
        free_models = [m for m in or_models if ":free" in m]
        text += "🆓 **Free:** " + ", ".join(free_models[:5]) + "\n"
        text += "💎 **All:** " + ", ".join(or_models[:5]) + "..."
    else:
        text += "None found or key error."
        
    text += "\n\nTo set a specific model as default, update `src/config.py`."
    await update.message.reply_text(text, parse_mode="Markdown")

# ... (keep other functions: search, today, match_command, handle_message as they were)

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /search <linguagem/termo>")
        return
    keyword = context.args[0]
    results = database.search_opportunities(keyword)
    if not results:
        await update.message.reply_text("Nenhuma oportunidade encontrada localmente.")
        return
    text = f"🔍 **Resultados para '{keyword}':**\n\n"
    for r in results[:5]:
        text += f"📌 {r['title']}\n🔗 {r['url']}\n\n"
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = database.get_today_opportunities()
    if not results:
        await update.message.reply_text("Nada novo por hoje. Rode o scraper em breve!")
        return
    text = "📅 **Novas de Hoje:**\n\n"
    for r in results[:5]:
        text += f"📌 {r['title']}\n🔗 {r['url']}\n\n"
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

async def match_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Quais são suas principais skills? (Ex: Python, React, AWS)")
    context.user_data['waiting_skills'] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_skills'):
        skills = update.message.text
        await update.message.reply_text("🤖 Calculando seus matches via AI Hierarchy...")
        import sqlite3
        conn = sqlite3.connect(database.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT title, description, url FROM opportunities ORDER BY created_at DESC LIMIT 10")
        opps = cursor.fetchall()
        conn.close()
        matches = []
        for title, desc, url in opps:
            score = scorer.calculate_match_score(f"{title} {desc}", skills)
            matches.append({"title": title, "url": url, "score": score})
        matches = sorted(matches, key=lambda x: x['score'], reverse=True)[:3]
        text = "🎯 **Seus Top 3 Matches:**\n\n"
        for m in matches:
            text += f"⭐ **{m['score']}%** - {m['title']}\n🔗 {m['url']}\n\n"
        await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)
        context.user_data['waiting_skills'] = False

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("today", today))
    application.add_handler(CommandHandler("match", match_command))
    application.add_handler(CommandHandler("models", list_models))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot iniciado!")
    application.run_polling()
