import discord
from discord import app_commands, ui
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

load_dotenv()

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
            await interaction.followup.send(f"❌ Error exporting {label}. Please try again.", ephemeral=True)

    @ui.button(label="Copy Gemini Key", style=discord.ButtonStyle.secondary, emoji="🔑")
    async def copy_gemini(self, interaction: discord.Interaction, button: ui.Button):
        await self._handle_export(interaction, "gemini_key", "Gemini Key")

    @ui.button(label="Copy OpenRouter Key", style=discord.ButtonStyle.secondary, emoji="🌐")
    async def copy_openrouter(self, interaction: discord.Interaction, button: ui.Button):
        await self._handle_export(interaction, "openrouter_key", "OpenRouter Key")

    @ui.button(label="Copy Profile", style=discord.ButtonStyle.secondary, emoji="📝")
    async def copy_profile(self, interaction: discord.Interaction, button: ui.Button):
        await self._handle_export(interaction, "profile_md", "Markdown Profile")

    @ui.button(label="Export All (JSON)", style=discord.ButtonStyle.primary, emoji="📦")
    async def export_all(self, interaction: discord.Interaction, button: ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
            u = get_user_keys(self.user_id)
            import json
            data = json.dumps(u, indent=2)
            await interaction.followup.send(f"**Full Configuration Export:**\n```json\n{data}\n```", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

class OpportunityActionView(ui.View):
    def __init__(self, opp_data):
        super().__init__(timeout=None)
        self.opp_data = opp_data

    @ui.button(label="Copy Match Info", style=discord.ButtonStyle.secondary, emoji="📋")
    async def copy_info(self, interaction: discord.Interaction, button: ui.Button):
        try:
            text = f"🚀 **{self.opp_data['title']}**\n🎯 **Match:** {self.opp_data['score']}%\n🧠 **Verdict:** {self.opp_data['rationale']}\n🔗 **Link:** {self.opp_data['url']}"
            # Se for muito grande para mensagem simples, manda em bloco de código
            if len(text) > 1900:
                await interaction.response.send_message(f"**Opportunity Data:**\n```markdown\n{text[:1900]}\n```", ephemeral=True)
            else:
                await interaction.response.send_message(f"**Copyable Opportunity Data:**\n>>> {text}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error copying data: {e}", ephemeral=True)

# --- BOT LOGIC ---

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
        print("❌ Error: DISCORD_TOKEN missing in .env")
        return False
    return True

def fetch_top_opportunities_sync(user_id=None):
    all_opps = []
    print(f"📡 Syncing opportunities for user {user_id}...")
    try:
        all_opps.extend(fetch_mlh())
        all_opps.extend(fetch_tabnews())
        all_opps.extend(fetch_devpost())
        all_opps.extend(fetch_hackclub())
        all_opps.extend(fetch_github_jobs())
    except Exception as e:
        print(f"⚠️ Scraping error: {e}")

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
        await interaction.followup.send("⚠️ No opportunities found at the moment.")
        return

    strategy_embed = discord.Embed(title="🧠 Today's Strategic Recommendation", description=strategy, color=0x3498db)
    await interaction.followup.send(embed=strategy_embed)

    for opp in top:
        sc = "🟢" if opp['score'] > 75 else "🟡" if opp['score'] > 50 else "🔴"
        title = f"{sc} {opp['score']}% - {opp['title'][:200]}"
        rationale = opp['rationale']
        embed = discord.Embed(title=title, color=0x2ecc71 if opp['score'] > 75 else 0xf1c40f)
        if len(rationale) <= 1000:
            embed.description = f"{rationale}\n\n[→ Access Opportunity]({opp['url']})"
        else:
            embed.description = rationale[:1000] + "..."
            embed.add_field(name="└─ Continuation", value=f"...{rationale[1000:2000]}\n\n[→ Access Opportunity]({opp['url']})", inline=False)
        view = OpportunityActionView(opp)
        await interaction.channel.send(embed=embed, view=view)

@client.tree.command(name="config_profile", description="Set your personal Markdown profile for AI matching")
async def config_profile(interaction: discord.Interaction, profile_md: str):
    save_user_profile(str(interaction.user.id), profile_md)
    await interaction.response.send_message("✅ Your Markdown profile has been saved!", ephemeral=True)

@client.tree.command(name="config_model", description="Configure AI Engine: Select Provider and set Model ID")
@app_commands.choices(provider=[
    app_commands.Choice(name="Google Gemini", value="gemini"),
    app_commands.Choice(name="OpenRouter", value="openrouter"),
    app_commands.Choice(name="Default (Hierarchy Reset)", value="default")
])
async def config_model(interaction: discord.Interaction, provider: app_commands.Choice[str], model_id: str = "default"):
    await interaction.response.defer(ephemeral=True)
    u_keys = get_user_keys(str(interaction.user.id))
    current_key = u_keys.get(f"{provider.value}_key") or (config.get_gemini_key() if provider.value == "gemini" else config.get_openrouter_key())
    
    if provider.value == "default":
        clear_user_setting(str(interaction.user.id), "model")
        await interaction.followup.send("✅ AI Engine reset to **Default Hierarchy**.", ephemeral=True)
        return

    if not current_key:
        await interaction.followup.send(f"❌ Error: No API Key found for **{provider.name}**. Use `/config_{provider.value}` first.", ephemeral=True)
        return

    loop = asyncio.get_event_loop()
    if provider.value == "gemini":
        available_models = await loop.run_in_executor(None, config.fetch_available_google_models, current_key)
    else:
        available_models = await loop.run_in_executor(None, config.fetch_available_openrouter_models, current_key)

    if model_id not in available_models:
        await interaction.followup.send(f"⚠️ **Model Not Found:** The ID `{model_id}` was not detected.\n💡 Check [AI Studio](https://aistudio.google.com/) or [OpenRouter](https://openrouter.ai/models).", ephemeral=True)
        return

    cost_warning = ""
    if provider.value == "openrouter" and not model_id.endswith(":free"):
        cost_warning = "\n⚠️ **Note:** Paid model selected."
    elif provider.value == "gemini" and "pro" in model_id.lower():
        cost_warning = "\n⚠️ **Note:** Gemini Pro requires GCP Billing."

    save_user_model(str(interaction.user.id), f"{provider.value}:{model_id}")
    await interaction.followup.send(f"✅ AI engine configured!\n**Provider:** {provider.name}\n**Model ID:** `{model_id}`{cost_warning}", ephemeral=True)

@client.tree.command(name="config_gemini", description="Set your own Gemini API Key (Private Validation)")
async def config_gemini(interaction: discord.Interaction, key: str):
    await interaction.response.defer(ephemeral=True)
    if not key.startswith("AIza"):
        await interaction.followup.send("❌ Invalid Format: Gemini keys start with 'AIza'.", ephemeral=True)
        return
    loop = asyncio.get_event_loop()
    models = await loop.run_in_executor(None, config.fetch_available_google_models, key)
    if not models:
        await interaction.followup.send("❌ Connection Failed: Key restricted or invalid.", ephemeral=True)
        return
    save_user_key(str(interaction.user.id), "gemini", key)
    await interaction.followup.send(f"✅ Success! Found {len(models)} available models.", ephemeral=True)

@client.tree.command(name="config_openrouter", description="Set your own OpenRouter API Key (Private Validation)")
async def config_or(interaction: discord.Interaction, key: str):
    await interaction.response.defer(ephemeral=True)
    if not key.startswith("sk-"):
        await interaction.followup.send("❌ Invalid Format: OpenRouter keys start with 'sk-'.", ephemeral=True)
        return
    loop = asyncio.get_event_loop()
    models = await loop.run_in_executor(None, config.fetch_available_openrouter_models, key)
    if not models:
        await interaction.followup.send("❌ Connection Failed: Key rejected.", ephemeral=True)
        return
    save_user_key(str(interaction.user.id), "openrouter", key)
    await interaction.followup.send(f"✅ Success! {len(models)} models detected.", ephemeral=True)

@client.tree.command(name="view_config", description="View your current API keys and profile (Private)")
async def view_config(interaction: discord.Interaction):
    u = get_user_keys(str(interaction.user.id))
    if not u:
        await interaction.response.send_message("❌ No configuration saved.", ephemeral=True)
        return
    def mask(k): return f"{k[:4]}...{k[-4:]}" if k else "Not Set"
    embed = discord.Embed(title="⚙️ Your Bot Configuration", color=0x9b59b6)
    embed.add_field(name="📍 Gemini Key", value=f"`{mask(u.get('gemini_key'))}`", inline=True)
    embed.add_field(name="📍 OpenRouter Key", value=f"`{mask(u.get('openrouter_key'))}`", inline=True)
    embed.add_field(name="📝 Markdown Profile", value="✅ Saved" if u.get('profile_md') else "❌ Not Set", inline=False)
    view = ExportConfigButtons(str(interaction.user.id))
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

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
    view = OpportunityActionView({"title": "Manual Analysis", "score": score, "rationale": rationale, "url": "N/A"})
    await interaction.followup.send(embed=embed, view=view)

@client.tree.command(name="models", description="Check live AI models availability")
async def models_cmd(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    u_keys = get_user_keys(str(interaction.user.id))
    loop = asyncio.get_event_loop()
    google_models = await loop.run_in_executor(None, config.fetch_available_google_models, u_keys.get("gemini_key"))
    or_models = await loop.run_in_executor(None, config.fetch_available_openrouter_models, u_keys.get("openrouter_key"))
    embed = discord.Embed(title="🤖 Live AI Models", color=0x3498db)
    source_info = "Using custom keys" if u_keys.get("gemini_key") or u_keys.get("openrouter_key") else "Using default keys"
    embed.set_footer(text=f"{source_info} · Built for efficiency 🚌")
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
    embed = discord.Embed(title="🏴‍☠️ Hack Club — You Ship, We Ship", description="Build anything and get rewarded. No excuses.", color=0xEC3750)
    if ysws:
        embed.add_field(name="🎯 Active YSWS Programs", value="\u200b", inline=False)
        for p in ysws:
            desc = (p["description"][:100] + "...") if len(p["description"]) > 100 else p["description"]
            embed.add_field(name=p["title"][:250], value=f"{desc}\n[→ Access]({p['url']})", inline=True)
    if events:
        event_list = []
        for e in events:
            title_clean = e['title'].replace('[HC Event] ','').replace('[HC AMA] ','')[:50]
            line = f"• [{title_clean}]({e['url']})"
            if e.get("cal"): line += f" [📅]({e['cal']})"
            if e.get("youtube"): line += f" [▶️]({e['youtube']})"
            event_list.append(line)
        embed.add_field(name="📅 Upcoming Events", value="\n".join(event_list) or "No upcoming events.", inline=False)
    embed.add_field(name="🔗 Quick Links", value="[ysws.hackclub.com](https://ysws.hackclub.com) · [events.hackclub.com](https://events.hackclub.com)", inline=False)
    embed.set_footer(text="Hack Club · nonprofit for teen hackers")
    embed.set_thumbnail(url="https://assets.hackclub.com/icon-rounded.png")
    await interaction.followup.send(embed=embed)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    await client.change_presence(activity=discord.Game(name="/opportunities"))

if __name__ == "__main__":
    if validate_env():
        client.run(DISCORD_TOKEN)
