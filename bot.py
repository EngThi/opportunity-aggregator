import discord
from discord import app_commands
import asyncio
import os
import sys
from dotenv import load_dotenv

# Adiciona o diretório src ao path para importações
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

load_dotenv()

from sources.mlh import fetch_mlh
from sources.tabnews import fetch_tabnews
from sources.devpost import fetch_devpost
from scorer import AIScorer
from database import save_opportunity, init_db

# --- CONFIGURAÇÃO ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")

class OpportunityBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

client = OpportunityBot()

def validate_env():
    """Valida se as chaves essenciais estão presentes"""
    required = ["DISCORD_TOKEN", "GEMINI_API_KEY"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        print(f"❌ Erro: Variáveis faltando no .env: {', '.join(missing)}")
        return False
    return True

def fetch_top_opportunities_sync():
    all_opps = []
    print("📡 Coletando oportunidades em background...")
    try:
        all_opps.extend(fetch_mlh())
        all_opps.extend(fetch_tabnews())
        all_opps.extend(fetch_devpost())
    except Exception as e:
        print(f"⚠️ Erro no scraping: {e}")

    scorer = AIScorer()
    scored = []
    # Processa as 10 mais recentes para ser rápido
    for opp in all_opps[:10]:
        score, rationale = scorer.score_opportunity(opp)
        opp["score"] = score
        opp["rationale"] = rationale
        scored.append(opp)

    init_db()
    save_opportunity(scored)
    return sorted(scored, key=lambda x: x["score"], reverse=True)[:5]

@client.tree.command(name="opportunities", description="Top 5 oportunidades personalizadas via IA")
async def opportunities_cmd(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    
    loop = asyncio.get_event_loop()
    top = await loop.run_in_executor(None, fetch_top_opportunities_sync)

    if not top:
        await interaction.followup.send("⚠️ Nenhuma oportunidade disponível no momento.")
        return

    embed = discord.Embed(
        title="🚀 Top Opportunites for You",
        description="I've analyzed the web and found these matches based on your profile.",
        color=0x2ecc71 # Verde
    )

    for opp in top:
        score_color = "🟢" if opp['score'] > 75 else "🟡" if opp['score'] > 50 else "🔴"
        embed.add_field(
            name=f"{score_color} {opp['score']}% - {opp['title'][:50]}",
            value=f"**Source:** {opp['source']}\n{opp['rationale'][:150]}...\n[View Link]({opp['url']})",
            inline=False
        )
    
    embed.set_footer(text="Opportunity Aggregator · Built for the bus commute 🚌")
    await interaction.followup.send(embed=embed)

@client.tree.command(name="analyze", description="Análise instantânea de qualquer texto de vaga")
async def analyze_cmd(interaction: discord.Interaction, text: str):
    await interaction.response.defer(thinking=True)
    
    scorer = AIScorer()
    mock_opp = {"title": "Custom Job", "description": text, "source": "Manual"}
    score, rationale = scorer.score_opportunity(mock_opp)
    
    color = 0x2ecc71 if score > 75 else 0xf1c40f if score > 50 else 0xe74c3c
    embed = discord.Embed(title="🧠 Match Analysis", color=color)
    embed.add_field(name="Score", value=f"**{score}%**", inline=True)
    embed.add_field(name="Veredito", value=rationale, inline=False)
    
    await interaction.followup.send(embed=embed)

@client.event
async def on_ready():
    print(f"✅ Logado como {client.user} (ID: {client.user.id})")
    await client.change_presence(activity=discord.Game(name="/opportunities"))

if __name__ == "__main__":
    if validate_env():
        client.run(DISCORD_TOKEN)
