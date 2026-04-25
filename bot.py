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
from sources.hackclub import fetch_hackclub
from scorer import AIScorer
from database import save_opportunity, init_db, save_user_key
import config

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
            print(f"✅ Commands synced to guild: {GUILD_ID}")
        else:
            await self.tree.sync()
            print("✅ Commands synced globally")

client = OpportunityBot()

def validate_env():
    if not os.getenv("DISCORD_TOKEN"):
        print("❌ Erro: DISCORD_TOKEN faltando no .env")
        return False
    return True

def fetch_top_opportunities_sync(user_id=None):
    all_opps = []
    print(f"📡 Coletando oportunidades para user {user_id}...")
    try:
        all_opps.extend(fetch_mlh())
        all_opps.extend(fetch_tabnews())
        all_opps.extend(fetch_devpost())
        all_opps.extend(fetch_hackclub())
    except Exception as e:
        print(f"⚠️ Erro no scraping: {e}")

    # Usa o Scorer com as chaves do usuário (se existirem)
    scorer = AIScorer(user_id=user_id)
    scored = []
    for opp in all_opps[:10]:
        score, rationale = scorer.score_opportunity(opp)
        opp["score"] = score
        opp["rationale"] = rationale
        scored.append(opp)

    init_db()
    save_opportunity(scored)
    return sorted(scored, key=lambda x: x["score"], reverse=True)[:5]

@client.tree.command(name="opportunities", description="Top 5 oportunidades com seu perfil e sua chave de API")
async def opportunities_cmd(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    loop = asyncio.get_event_loop()
    top = await loop.run_in_executor(None, fetch_top_opportunities_sync, str(interaction.user.id))

    if not top:
        await interaction.followup.send("⚠️ Nenhuma oportunidade disponível.")
        return

    embed = discord.Embed(title="🚀 Your Personalized Matches", color=0x2ecc71)
    for opp in top:
        sc = "🟢" if opp['score'] > 75 else "🟡" if opp['score'] > 50 else "🔴"
        embed.add_field(name=f"{sc} {opp['score']}% - {opp['title'][:50]}", value=f"{opp['rationale'][:150]}...\n[Link]({opp['url']})", inline=False)
    
    await interaction.followup.send(embed=embed)

@client.tree.command(
    name="hackclub",
    description="🔥 Programas YSWS ativos + eventos do Hack Club (hardware, games, arte, código)"
)
async def hackclub_cmd(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    loop = asyncio.get_event_loop()
    items = await loop.run_in_executor(None, fetch_hackclub)

    ysws = [i for i in items if i.get("type") == "ysws"][:6]
    events = [i for i in items if i.get("type") == "event"][:3]

    embed = discord.Embed(
        title="🏴‍☠️ Hack Club — You Ship, We Ship",
        description=(
            "Build **qualquer coisa** — game, hardware, arte, PCB, API — "
            "e o Hack Club te recompensa de verdade.\n"
            "Sempre tem um programa ativo. **Sem desculpa pra não shipar.**"
        ),
        color=0xEC3750  # Red do Hack Club
    )

    if ysws:
        embed.add_field(
            name="🎯 Programas YSWS Ativos",
            value="\u200b",
            inline=False
        )
        for p in ysws:
            desc = p["description"][:120]
            embed.add_field(
                name=p["title"],
                value=f"{desc}...\n[→ Acessar]({p['url']})",
                inline=True
            )

    if events:
        event_list = []
        for e in events:
            line = f"• [{e['title'].replace('[HC Event] ','').replace('[HC AMA] ','')}]({e['url']})"
            if e.get("cal"):
                line += f" [📅]({e['cal']})"
            if e.get("youtube"):
                line += f" [▶️]({e['youtube']})"
            event_list.append(line)
            
        embed.add_field(
            name="📅 Próximos Eventos & AMAs",
            value="\n".join(event_list),
            inline=False
        )

    embed.add_field(
        name="🔗 Links rápidos",
        value=(
            "[ysws.hackclub.com](https://ysws.hackclub.com) · "
            "[events.hackclub.com](https://events.hackclub.com) · "
            "[hackclub.com/slack](https://hackclub.com/slack)"
        ),
        inline=False
    )

    embed.set_footer(text="Hack Club · nonprofit for teen hackers · #ship no Slack")
    embed.set_thumbnail(url="https://assets.hackclub.com/icon-rounded.png")

    await interaction.followup.send(embed=embed)

@client.tree.command(name="config_gemini", description="Configure sua própria Gemini API Key (Privado)")
async def config_gemini(interaction: discord.Interaction, key: str):
    save_user_key(str(interaction.user.id), "gemini", key)
    await interaction.response.send_message("✅ Sua Gemini API Key foi salva com sucesso e será usada como prioridade!", ephemeral=True)

@client.tree.command(name="config_openrouter", description="Configure sua própria OpenRouter API Key (Privado)")
async def config_or(interaction: discord.Interaction, key: str):
    save_user_key(str(interaction.user.id), "openrouter", key)
    await interaction.response.send_message("✅ Sua OpenRouter API Key foi salva com sucesso!", ephemeral=True)

@client.tree.command(name="analyze", description="Analisa um texto usando suas chaves de API")
async def analyze_cmd(interaction: discord.Interaction, text: str):
    await interaction.response.defer(thinking=True)
    scorer = AIScorer(user_id=str(interaction.user.id))
    mock_opp = {"title": "Manual Analysis", "description": text, "source": "User"}
    score, rationale = scorer.score_opportunity(mock_opp)
    
    color = 0x2ecc71 if score > 75 else 0xf1c40f
    embed = discord.Embed(title="🧠 Match Analysis", color=color)
    embed.add_field(name="Score", value=f"**{score}%**", inline=True)
    embed.add_field(name="Veredito", value=rationale, inline=False)
    await interaction.followup.send(embed=embed)

@client.tree.command(name="models", description="Check live AI models availability")
async def models_cmd(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    loop = asyncio.get_event_loop()
    google_models = await loop.run_in_executor(None, config.fetch_available_google_models)
    or_models = await loop.run_in_executor(None, config.fetch_available_openrouter_models)
    embed = discord.Embed(title="🤖 Live AI Models", color=0x3498db)
    embed.add_field(name="📍 Google Gemini", value=f"```{', '.join(google_models[:5])}...```", inline=False)
    embed.add_field(name="📍 OpenRouter", value=f"Free models: {len([m for m in or_models if ':free' in m])}", inline=False)
    await interaction.followup.send(embed=embed)

@client.event
async def on_ready():
    print(f"✅ Logado como {client.user}")
    await client.change_presence(activity=discord.Game(name="/opportunities"))

if __name__ == "__main__":
    if validate_env():
        client.run(DISCORD_TOKEN)
