# Opportunity Aggregator 🚀

A tool built to centralize and rank academic and tech opportunities. It automatically pulls data from various platforms and uses AI to find the best matches based on your specific profile.

## 🚌 Project Story
This project was developed in short bursts during daily bus commutes. The goal was to build something efficient that could turn a phone into a productive workstation, delegating the manual work of searching for hackathons and grants to an automated system.

![Main Showcase](assets/main_showcase.png)

## Key Features

### 1. Data Sources
The system syncs in real-time with:
*   **Devpost API:** Global hackathons and project competitions.
*   **Hack Club API:** Community events, workshops, and AMAs.
*   **Hack Club YSWS:** "You Ship, We Ship" programs for hardware and software.
*   **MLH:** Official student hackathon circuit.
*   **TabNews:** Tech community insights and research grants.

### 2. Personalized Ranking (BYOK)
The system uses a **Bring Your Own Key** approach so you can scale your own usage:
*   **Markdown Profiles:** Users can upload their own .md files to define their skills and interests.
*   **Fallback System:** It uses Gemini 3.1 Flash/Pro and automatically switches to OpenRouter (Llama/Gemma) if quotas are hit.
*   **Model Selection:** You can choose exactly which model you want to use via Discord commands.

### 3. Background Radar
Instead of searching manually, the system runs a background process:
*   **Auto-Sync:** Runs every 6 hours.
*   **Alerts:** Sends a Discord notification via Webhook whenever a high-quality match (>90%) is found.

![Radar Alerts](assets/radar_alerts.png)

## ⌨️ Commands

| Command | Description |
| :--- | :--- |
| `/opportunities` | Syncs data and lists the Top 5 matches with AI rationales. |
| `/hackclub` | Panel for Hack Club events and active programs. |
| `/analyze` | Instant analysis for any pasted job or event text. |
| `/config_profile` | Upload your Markdown profile for matching. |
| `/config_model` | Select your AI provider and Model ID. |
| `/config_gemini` | Store your Gemini API Key. |
| `/config_openrouter` | Store your OpenRouter API Key. |
| `/view_config` | See your settings and export your data. |
| `/clear_config` | Delete specific settings or wipe your data. |
| `/models` | Check which AI models are currently available. |

## 🛠️ Tech Stack

*   **Language:** Python 3.11+
*   **Interface:** Discord.py (Slash Commands & Interactive Buttons)
*   **AI:** Google GenAI & OpenAI SDK (via OpenRouter)
*   **Database:** SQLite (Local storage with auto-migrations)
*   **Testing:** Unit and Mock tests using Pytest.

![Architecture Diagram](assets/architecture_diagram.png)

## 🚀 Deployment

### Docker (Recommended)
```bash
docker-compose up -d --build
```

### Manual Setup
1. **Env:** `python -m venv .venv && source .venv/bin/activate`
2. **Deps:** `pip install -r requirements.txt`
3. **Run:** `python bot.py` and `python main.py`

## 🛡️ Privacy
*   **Local Storage:** Your API keys and profiles stay in your own SQLite database.
*   **Private Messages:** Configuration commands use ephemeral messages (only you can see them).
*   **Full Control:** You can view or delete your data at any time.

---
**Developer:** EngThi | **Status:** Stable MVP v1.0
