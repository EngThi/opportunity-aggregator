import os
from dotenv import load_dotenv
load_dotenv(override=True)

import discord
from discord import app_commands, ui
import asyncio
import sys
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sources.mlh import fetch_mlh
from sources.tabnews import fetch_tabnews
from sources.devpost import fetch_devpost
from sources.hackclub import fetch_hackclub
from sources.github_jobs import fetch_github_jobs
from scorer import AIScorer
from database import save_opportunity, init_db, save_user_key, get_user_keys, save_user_profile, save_user_model, clear_user_setting
import config

# --- CONFIGURATION ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")

# --- UI COMPONENTS ---

class ExportConfigButtons(ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = str(user_id)

    async def _handle_export(self, interaction: discord.Interaction, key_name, label):
        try:
            await interaction.response.defer(ephemeral=True)
            u = get_user_keys(self.user_id)
            val = u.get(key_name)
            if not val:
                await interaction.followup.send(f"❌ {label} is not set.", ephemeral=True)
                return
            code_block = "markdown" if key_name == "profile_md" else ""
            await interaction.followup.send(f"**Your {label}:**\n```{code_block}\n{val}\n```", ephemeral=True)
        except Exception as e:
            print(f"❌ Export error: {e}")
            await interaction.followup.send(f"❌ Error exporting {label}.", ephemeral=True)

    @ui.button(label="Copy Gemini Key", style=discord.ButtonStyle.secondary, emoji="🔑", custom_id="copy_gemini_btn")
    async def copy_gemini(self, interaction: discord.Interaction, button: ui.Button):
        await self._handle_export(interaction, "gemini_key", "Gemini Key")

    @ui.button(label="Copy OpenRouter Key", style=discord.ButtonStyle.secondary, emoji="🌐", custom_id="copy_or_btn")
    async def copy_openrouter(self, interaction: discord.Interaction, button: ui.Button):
        await self._handle_export(interaction, "openrouter_key", "OpenRouter Key")

    @ui.button(label="Copy Profile", style=discord.ButtonStyle.secondary, emoji="📝", custom_id="copy_profile_btn")
    async def copy_profile(self, interaction: discord.Interaction, button: ui.Button):
        await self._handle_export(interaction, "profile_md", "Markdown Profile")

    @ui.button(label="Export All (JSON)", style=discord.ButtonStyle.primary, emoji="📦", custom_id="export_all_btn")
    async def export_all(self, interaction: discord.Interaction, button: ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
            u = get_user_keys(self.user_id)
            data = json.dumps(u, indent=2)
            await interaction.followup.send(f"**Full Configuration Export:**\n```json\n{data}\n```", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

class OpportunityActionView(ui.View):
    def __init__(self, opp_data):
        super().__init__(timeout=None) # Views for opportunities are ephemeral per message
        self.opp_data = opp_data

    @ui.button(label="Copy Match Info", style=discord.ButtonStyle.secondary, emoji="📋")
    async def copy_info(self, interaction: discord.Interaction, button: ui.Button):
        try:
            # Send immediate thinking state
            await interaction.response.defer(ephemeral=True)
            
            # Formatting with safety checks
            title = self.opp_data.get('title', 'N/A')
            score = self.opp_data.get('score', 0)
            rat = self.opp_data.get('rationale', 'N/A')
            url = self.opp_data.get('url', 'N/A')
            
            text = f"🚀 **{title}**\n🎯 **Match:** {score}%\n🧠 **Verdict:** {rat}\n🔗 **Link:** {url}"
            
            if len(text) > 1900:
                await interaction.followup.send(f"**Opportunity Summary:**\n```markdown\n{text[:1900]}\n```", ephemeral=True)
            else:
                await interaction.followup.send(f"**Copyable Data:**\n>>> {text}", ephemeral=True)
        except Exception as e:
            print(f"❌ Copy Error: {e}")
            try: await interaction.followup.send(f"❌ Error copying: {str(e)}", ephemeral=True)
            except: pass

# --- BOT LOGIC ---

class OpportunityBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Register Persistent Views (for config buttons)
        # Note: Opportunity views are dynamic so they don't need fixed IDs here
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
    top_5 = sorted(scored, key=lambda x: x["score"], reverse=True)[:5]
    strategy = scorer.generate_daily_strategy(top_5)
    return top_5, strategy

@client.tree.command(name="opportunities", description="Top 5 personalized matches using your AI profile")
async def opportunities_cmd(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    loop = asyncio.get_event_loop()
    top, strategy = await loop.run_in_executor(None, fetch_top_opportunities_sync, str(interaction.user.id))

    if not top:
        await interaction.followup.send("⚠️ No opportunities found.")
        return

    strategy_embed = discord.Embed(title="🧠 Today's Strategic Recommendation", description=strategy, color=0x3498db)
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
        
        await interaction.channel.send(embed=embed, view=OpportunityActionView(opp))

@client.tree.command(name="config_profile", description="Set your personal Markdown profile for AI matching")
async def config_profile(interaction: discord.Interaction, profile_md: str):
    save_user_profile(str(interaction.user.id), profile_md)
    await interaction.response.send_message("✅ Profile saved!", ephemeral=True)

@client.tree.command(name="config_model", description="Configure AI Engine: Select Provider and set Model ID")
@app_commands.choices(provider=[
    app_commands.Choice(name="Google Gemini", value="gemini"),
    app_commands.Choice(name="OpenRouter", value="openrouter"),
    app_commands.Choice(name="Default (Hierarchy Reset)", value="default")
])
async def config_model(interaction: discord.Interaction, provider: app_commands.Choice[str], model_id: str = "default"):
    await interaction.response.defer(ephemeral=True)
    from database import get_user_keys, save_user_model, clear_user_setting
    if provider.value == "default":
        clear_user_setting(str(interaction.user.id), "model")
        await interaction.followup.send("✅ AI Engine reset!", ephemeral=True)
        return

    u_keys = get_user_keys(str(interaction.user.id))
    current_key = u_keys.get(f"{provider.value}_key") or (config.get_gemini_key() if provider.value == "gemini" else config.get_openrouter_key())
    if not current_key:
        await interaction.followup.send(f"❌ No API Key for {provider.name}.", ephemeral=True)
        return

    loop = asyncio.get_event_loop()
    if provider.value == "gemini": available_models = await loop.run_in_executor(None, config.fetch_available_google_models, current_key)
    else: available_models = await loop.run_in_executor(None, config.fetch_available_openrouter_models, current_key)

    if model_id not in available_models:
        await interaction.followup.send(f"⚠️ Model `{model_id}` not found.", ephemeral=True)
        return

    save_user_model(str(interaction.user.id), f"{provider.value}:{model_id}")
    await interaction.followup.send(f"✅ AI engine set to `{model_id}`", ephemeral=True)

@client.tree.command(name="config_gemini", description="Set your own Gemini API Key (Private Validation)")
async def config_gemini(interaction: discord.Interaction, key: str):
    await interaction.response.defer(ephemeral=True)
    if not key.startswith("AIza"):
        await interaction.followup.send("❌ Invalid Format.", ephemeral=True)
        return
    loop = asyncio.get_event_loop()
    models = await loop.run_in_executor(None, config.fetch_available_google_models, key)
    if not models:
        await interaction.followup.send("❌ Key invalid.", ephemeral=True)
        return
    save_user_key(str(interaction.user.id), "gemini", key)
    await interaction.followup.send(f"✅ Success! Found {len(models)} models.", ephemeral=True)

@client.tree.command(name="config_openrouter", description="Set your own OpenRouter API Key (Private Validation)")
async def config_or(interaction: discord.Interaction, key: str):
    await interaction.response.defer(ephemeral=True)
    if not key.startswith("sk-"):
        await interaction.followup.send("❌ Invalid Format.", ephemeral=True)
        return
    loop = asyncio.get_event_loop()
    models = await loop.run_in_executor(None, config.fetch_available_openrouter_models, key)
    if not models:
        await interaction.followup.send("❌ Key rejected.", ephemeral=True)
        return
    save_user_key(str(interaction.user.id), "openrouter", key)
    await interaction.followup.send(f"✅ Success! {len(models)} models detected.", ephemeral=True)

@client.tree.command(name="view_config", description="View your current API keys and profile (Private)")
async def view_config(interaction: discord.Interaction):
    u = get_user_keys(str(interaction.user.id))
    if not u:
        await interaction.response.send_message("❌ No configuration.", ephemeral=True)
        return
    def mask(k): return f"{k[:4]}...{k[-4:]}" if k else "Not Set"
    embed = discord.Embed(title="⚙️ Configuration", color=0x9b59b6)
    embed.add_field(name="📍 Gemini Key", value=f"`{mask(u.get('gemini_key'))}`", inline=True)
    embed.add_field(name="📍 OpenRouter Key", value=f"`{mask(u.get('openrouter_key'))}`", inline=True)
    embed.add_field(name="📝 Profile", value="✅ Saved" if u.get('profile_md') else "❌ Not Set", inline=False)
    await interaction.response.send_message(embed=embed, view=ExportConfigButtons(str(interaction.user.id)), ephemeral=True)

@client.tree.command(name="clear_config", description="Delete specific parts of your configuration")
@app_commands.choices(item=[
    app_commands.Choice(name="Gemini Key", value="gemini"),
    app_commands.Choice(name="OpenRouter Key", value="openrouter"),
    app_commands.Choice(name="Markdown Profile", value="profile"),
    app_commands.Choice(name="Everything", value="all")
])
async def clear_config(interaction: discord.Interaction, item: app_commands.Choice[str]):
    clear_user_setting(str(interaction.user.id), item.value)
    await interaction.response.send_message(f"✅ Cleared: **{item.name}**", ephemeral=True)

@client.tree.command(name="analyze", description="Instant AI analysis for any opportunity text")
async def analyze_cmd(interaction: discord.Interaction, text: str):
    await interaction.response.defer(thinking=True)
    scorer = AIScorer(user_id=str(interaction.user.id))
    mock_opp = {"title": "Manual Analysis", "description": text, "source": "User"}
    score, rationale = scorer.score_opportunity(mock_opp)
    color = 0x2ecc71 if score > 75 else 0xf1c40f
    embed = discord.Embed(title="🧠 Match Analysis", color=color)
    embed.add_field(name="Match Score", value=f"**{score}%**", inline=True)
    embed.add_field(name="Verdict", value=rationale, inline=False)
    opp_for_view = {"title": "Manual Analysis", "score": score, "rationale": rationale, "url": "N/A"}
    await interaction.followup.send(embed=embed, view=OpportunityActionView(opp_for_view))

@client.tree.command(name="models", description="Check live AI models availability")
async def models_cmd(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    u_keys = get_user_keys(str(interaction.user.id))
    loop = asyncio.get_event_loop()
    google_models = await loop.run_in_executor(None, config.fetch_available_google_models, u_keys.get("gemini_key"))
    or_models = await loop.run_in_executor(None, config.fetch_available_openrouter_models, u_keys.get("openrouter_key"))
    embed = discord.Embed(title="🤖 Live AI Models", color=0x3498db)
    g_text = ", ".join(google_models[:5]) if google_models else "None"
    embed.add_field(name="📍 Google Gemini", value=f"```{g_text}...```", inline=False)
    embed.add_field(name="📍 OpenRouter", value=f"Free models: {len([m for m in or_models if ':free' in m])}", inline=False)
    await interaction.followup.send(embed=embed)

@client.tree.command(name="hackclub", description="🔥 Active YSWS programs + Hack Club events")
async def hackclub_cmd(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    loop = asyncio.get_event_loop()
    items = await loop.run_in_executor(None, fetch_hackclub)
    ysws = [i for i in items if i.get("type") == "ysws"][:6]
    events = [i for i in items if i.get("type") == "event"][:5]
    embed = discord.Embed(title="🏴‍☠️ Hack Club", description="Build anything.", color=0xEC3750)
    if ysws:
        for p in ysws:
            desc = (p["description"][:100] + "...") if len(p["description"]) > 100 else p["description"]
            embed.add_field(name=p["title"][:200], value=f"{desc}\n[→ Access]({p['url']})", inline=True)
    await interaction.followup.send(embed=embed)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    await client.change_presence(activity=discord.Game(name="/opportunities"))

if __name__ == "__main__":
    if validate_env():
        client.run(DISCORD_TOKEN)
