import os
from dotenv import load_dotenv
load_dotenv(override=True)

import discord
from discord import app_commands, ui
import asyncio
import sys
import json
import sqlite3

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sources.mlh import fetch_mlh
from sources.tabnews import fetch_tabnews
from sources.devpost import fetch_devpost
from sources.hackclub import fetch_hackclub
from sources.github_jobs import fetch_github_jobs
from scorer import AIScorer
from database import save_opportunity, init_db, save_user_key, get_user_keys, save_user_profile, save_user_model, clear_user_setting, get_opportunity_by_id
import config

# --- CONFIGURATION ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")

# --- UI COMPONENTS ---

class ExportConfigButtons(ui.View):
    """Persistent view for user settings management"""
    def __init__(self, user_id=None):
        super().__init__(timeout=None)
        self.user_id = str(user_id) if user_id else None

    async def _handle_export(self, interaction: discord.Interaction, key_name, label):
        try:
            await interaction.response.defer(ephemeral=True)
            uid = self.user_id or str(interaction.user.id)
            u = get_user_keys(uid)
            val = u.get(key_name)
            if not val:
                await interaction.followup.send(f"❌ {label} is not set.", ephemeral=True)
                return
            code_block = "markdown" if key_name == "profile_md" else ""
            await interaction.followup.send(f"**Your {label}:**\n```{code_block}\n{val}\n```", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Export error: {e}", ephemeral=True)

    @ui.button(label="Copy Gemini Key", style=discord.ButtonStyle.secondary, emoji="🔑", custom_id="persistent_copy_gemini")
    async def copy_gemini(self, interaction: discord.Interaction, button: ui.Button):
        await self._handle_export(interaction, "gemini_key", "Gemini Key")

    @ui.button(label="Copy OpenRouter Key", style=discord.ButtonStyle.secondary, emoji="🌐", custom_id="persistent_copy_or")
    async def copy_openrouter(self, interaction: discord.Interaction, button: ui.Button):
        await self._handle_export(interaction, "openrouter_key", "OpenRouter Key")

    @ui.button(label="Copy Profile", style=discord.ButtonStyle.secondary, emoji="📝", custom_id="persistent_copy_profile")
    async def copy_profile(self, interaction: discord.Interaction, button: ui.Button):
        await self._handle_export(interaction, "profile_md", "Markdown Profile")

    @ui.button(label="Export All (JSON)", style=discord.ButtonStyle.primary, emoji="📦", custom_id="persistent_export_all")
    async def export_all(self, interaction: discord.Interaction, button: ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
            uid = self.user_id or str(interaction.user.id)
            u = get_user_keys(uid)
            data = json.dumps(u, indent=2)
            await interaction.followup.send(f"**Full Configuration Export:**\n```json\n{data}\n```", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

# --- BOT LOGIC ---

class OpportunityBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.add_view(ExportConfigButtons())
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
        print("❌ Error: DISCORD_TOKEN missing in .env")
        return False
    return True

def fetch_top_opportunities_sync(user_id=None):
    all_opps = []
    try:
        all_opps.extend(fetch_mlh())
        all_opps.extend(fetch_tabnews())
        all_opps.extend(fetch_devpost())
        all_opps.extend(fetch_hackclub())
        all_opps.extend(fetch_github_jobs())
    except: pass

    scorer = AIScorer(user_id=user_id)
    scored = []
    for opp in all_opps[:15]:
        score, rationale = scorer.score_opportunity(opp)
        opp["score"] = score
        opp["rationale"] = rationale
        scored.append(opp)

    init_db()
    save_opportunity(scored)
    return sorted(scored, key=lambda x: x["score"], reverse=True)[:5], scorer.generate_daily_strategy(scored[:5])

@client.tree.command(name="opportunities", description="Top 5 personalized matches using your AI profile")
async def opportunities_cmd(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    loop = asyncio.get_event_loop()
    top, strategy = await loop.run_in_executor(None, fetch_top_opportunities_sync, str(interaction.user.id))

    if not top:
        await interaction.followup.send("⚠️ No opportunities found.")
        return

    strategy_embed = discord.Embed(title="🧠 Strategic Recommendation", description=strategy, color=0x3498db)
    await interaction.followup.send(embed=strategy_embed)

    for opp in top:
        sc = "🟢" if opp['score'] > 75 else "🟡" if opp['score'] > 50 else "🔴"
        title = f"{sc} {opp['score']}% - {opp['title'][:200]}"
        embed = discord.Embed(title=title, color=0x2ecc71 if opp['score'] > 75 else 0xf1c40f)
        
        rationale = opp['rationale']
        if len(rationale) <= 1000:
            embed.description = f"{rationale}\n\n[→ Access Opportunity]({opp['url']})"
        else:
            embed.description = rationale[:1000] + "..."
            embed.add_field(name="└─ Continuation", value=f"...{rationale[1000:2000]}\n\n[→ Access Opportunity]({opp['url']})", inline=False)
        
        await interaction.channel.send(embed=embed)

@client.tree.command(name="config_profile", description="Set your personal Markdown profile")
async def config_profile(interaction: discord.Interaction, profile_md: str):
    save_user_profile(str(interaction.user.id), profile_md)
    await interaction.response.send_message("✅ Profile saved!", ephemeral=True)

@client.tree.command(name="config_model", description="Configure AI Engine")
@app_commands.choices(provider=[
    app_commands.Choice(name="Google Gemini", value="gemini"),
    app_commands.Choice(name="OpenRouter", value="openrouter"),
    app_commands.Choice(name="Default", value="default")
])
async def config_model(interaction: discord.Interaction, provider: app_commands.Choice[str], model_id: str = "default"):
    await interaction.response.defer(ephemeral=True)
    if provider.value == "default":
        clear_user_setting(str(interaction.user.id), "model")
        await interaction.followup.send("✅ Reset to default.", ephemeral=True)
        return
    save_user_model(str(interaction.user.id), f"{provider.value}:{model_id}")
    await interaction.followup.send(f"✅ Set to `{model_id}`", ephemeral=True)

@client.tree.command(name="config_gemini", description="Set Gemini Key")
async def config_gemini(interaction: discord.Interaction, key: str):
    await interaction.response.defer(ephemeral=True)
    save_user_key(str(interaction.user.id), "gemini", key)
    await interaction.followup.send("✅ Gemini Key saved.", ephemeral=True)

@client.tree.command(name="config_openrouter", description="Set OpenRouter Key")
async def config_or(interaction: discord.Interaction, key: str):
    await interaction.response.defer(ephemeral=True)
    save_user_key(str(interaction.user.id), "openrouter", key)
    await interaction.followup.send("✅ OpenRouter Key saved.", ephemeral=True)

@client.tree.command(name="view_config", description="View your settings")
async def view_config(interaction: discord.Interaction):
    u = get_user_keys(str(interaction.user.id))
    if not u:
        await interaction.response.send_message("❌ No config.", ephemeral=True)
        return
    mask = lambda k: f"{k[:4]}...{k[-4:]}" if k else "Not Set"
    embed = discord.Embed(title="⚙️ Configuration", color=0x9b59b6)
    embed.add_field(name="📍 Gemini", value=f"`{mask(u.get('gemini_key'))}`", inline=True)
    embed.add_field(name="📍 OpenRouter", value=f"`{mask(u.get('openrouter_key'))}`", inline=True)
    embed.add_field(name="📝 Profile", value="✅ Saved" if u.get('profile_md') else "❌ Not Set", inline=False)
    await interaction.response.send_message(embed=embed, view=ExportConfigButtons(str(interaction.user.id)), ephemeral=True)

@client.tree.command(name="clear_config", description="Delete settings")
@app_commands.choices(item=[
    app_commands.Choice(name="Gemini Key", value="gemini"),
    app_commands.Choice(name="OpenRouter Key", value="openrouter"),
    app_commands.Choice(name="Markdown Profile", value="profile"),
    app_commands.Choice(name="Everything", value="all")
])
async def clear_config(interaction: discord.Interaction, item: app_commands.Choice[str]):
    clear_user_setting(str(interaction.user.id), item.value)
    await interaction.response.send_message(f"✅ Cleared {item.name}.", ephemeral=True)

@client.tree.command(name="analyze", description="AI analysis for text")
async def analyze_cmd(interaction: discord.Interaction, text: str):
    await interaction.response.defer(thinking=True)
    scorer = AIScorer(user_id=str(interaction.user.id))
    score, rationale = scorer.score_opportunity({"title": "Manual", "description": text})
    embed = discord.Embed(title="🧠 Analysis", color=0x2ecc71 if score > 75 else 0xf1c40f)
    embed.add_field(name="Score", value=f"**{score}%**", inline=True)
    embed.add_field(name="Verdict", value=rationale, inline=False)
    await interaction.followup.send(embed=embed)

@client.tree.command(name="models", description="Check AI availability")
async def models_cmd(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    u_keys = get_user_keys(str(interaction.user.id))
    g_models = config.fetch_available_google_models(u_keys.get("gemini_key"))
    embed = discord.Embed(title="🤖 AI Models", description=f"Found {len(g_models)} Gemini models.", color=0x3498db)
    await interaction.followup.send(embed=embed)

@client.tree.command(name="hackclub", description="🔥 Hack Club events")
async def hackclub_cmd(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    items = fetch_hackclub()
    embed = discord.Embed(title="🏴‍☠️ Hack Club", color=0xEC3750)
    for p in items[:5]:
        embed.add_field(name=p["title"][:100], value=f"[→ Access]({p['url']})", inline=True)
    await interaction.followup.send(embed=embed)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    await client.change_presence(activity=discord.Game(name="/opportunities"))

if __name__ == "__main__":
    if validate_env():
        client.run(DISCORD_TOKEN)
