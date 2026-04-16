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

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")  # opcional, acelera registro de comandos

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def fetch_top_opportunities_sync():
    """Versão síncrona para ser rodada em thread separada"""
    all_opps = []
    print("📡 Coletando oportunidades para o Discord...")
    all_opps.extend(fetch_mlh())
    all_opps.extend(fetch_tabnews())
    all_opps.extend(fetch_devpost())

    scorer = AIScorer()
    scored = []
    # Limite de 15 para evitar rate limit e ser rápido na resposta do comando
    for opp in all_opps[:15]:
        score, rationale = scorer.score_opportunity(opp)
        opp["score"] = score
        opp["rationale"] = rationale
        scored.append(opp)

    init_db()
    save_opportunity(scored)
    return sorted(scored, key=lambda x: x["score"], reverse=True)[:5]

@tree.command(name="opportunities", description="Top 5 oportunidades do dia (hackathons, grants, jobs)")
async def opportunities_cmd(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    try:
        # Executa a coleta em uma thread separada para não travar o bot
        loop = asyncio.get_event_loop()
        top = await loop.run_in_executor(None, fetch_top_opportunities_sync)
    except Exception as e:
        print(f"❌ Erro ao buscar oportunidades: {e}")
        await interaction.followup.send("⚠️ Houve um erro ao processar as oportunidades. Tente novamente em breve.")
        return

    if not top:
        await interaction.followup.send("⚠️ Nenhuma oportunidade encontrada agora. Tente novamente em breve.")
        return

    embed = discord.Embed(
        title="🏆 Top Opportunities Today",
        description="Curated by AI · Powered by Opportunity Aggregator",
        color=0x00b4d8
    )

    for i, opp in enumerate(top, 1):
        embed.add_field(
            name=f"{i}. [{opp['score']}%] {opp['title'][:60]}",
            value=f"💡 {opp['rationale'][:150]}...\n🔗 [Link Directo]({opp['url']})",
            inline=False
        )

    embed.set_footer(text="Use /opportunities anytime to refresh")
    await interaction.followup.send(embed=embed)

@tree.command(name="analyze", description="Analisa uma oportunidade específica (cole o texto)")
@app_commands.describe(text="O título ou descrição da oportunidade que você quer analisar")
async def analyze_cmd(interaction: discord.Interaction, text: str):
    await interaction.response.defer(thinking=True)
    
    try:
        scorer = AIScorer()
        # Mock de objeto para o scorer
        mock_opp = {
            "title": "Custom Analysis",
            "description": text,
            "source": "User Input"
        }
        
        score, rationale = scorer.score_opportunity(mock_opp)
        
        embed = discord.Embed(
            title="🧠 AI Match Analysis",
            description=f"Analysis of: *{text[:100]}...*",
            color=0xfca311 if score > 70 else 0xe5e5e5
        )
        
        embed.add_field(name="Match Score", value=f"**{score}%**", inline=True)
        embed.add_field(name="Verdict", value=rationale, inline=False)
        embed.set_footer(text="Based on your user_profile.md")
        
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Erro na análise: {e}")

@client.event
async def on_ready():
    if GUILD_ID:
        guild = discord.Object(id=int(GUILD_ID))
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)
        print(f"✅ Bot online e comandos sincronizados para o servidor {GUILD_ID}")
    else:
        await tree.sync()
        print(f"✅ Bot online e comandos sincronizados globalmente")
    print(f"🤖 Conectado como {client.user}")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ Erro: DISCORD_TOKEN não encontrado no arquivo .env")
    else:
        client.run(DISCORD_TOKEN)
