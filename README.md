# Opportunity Aggregator

An intelligent automation engine designed to centralize, analyze, and rank academic and professional opportunities. The system acts as a personalized radar, filtering through fragmented data sources to deliver high-signal matches directly to the user.

## Project Origin
Developed primarily during daily bus commutes, this project focuses on high-utility output and resource efficiency. It solves the "information overload" problem by delegating the initial screening of hackathons and grants to a multi-tiered AI architecture.

![Bot Interface Showcase](assets/bot_showcase.png)

## Core Capabilities

### 1. Autonomous Data Ingestion
The system synchronizes data from multiple high-signal platforms:
*   **Devpost API:** Global hackathons and project-based competitions.
*   **Hack Club API & Scrapers:** Community events and "You Ship, We Ship" (YSWS) programs.
*   **MLH (Major League Hacking):** Official student hackathon circuit.
*   **TabNews RSS:** Community-driven tech insights and grants.

### 2. Multi-Tiered AI Scoring
To ensure 24/7 reliability and bypass API quotas, the engine uses a hierarchical scoring logic:
*   **Primary:** Gemini 3.1 Flash-Lite (Fast, direct reasoning).
*   **Secondary:** Gemini 1.5 Flash (Direct API fallback).
*   **Tertiary:** OpenRouter Bridge (Access to Llama/Gemma free models).

### 3. Proactive Radar Alerts
Instead of a passive search, the system runs a background analyzer that triggers real-time Discord Webhook alerts when an opportunity matches >90% of the user's profile.

![Proactive Alerta Example](assets/radar_alerts.png)

## Architecture

*   **Language:** Python 3.11+
*   **Interface:** Discord (Slash Commands)
*   **Database:** SQLite (Local persistence for offline analysis)
*   **Deployment:** Containerized via Docker for Hack Club VM environments.

## Setup & Deployment

### Credentials
The system requires a `.env` file with the following keys:
```env
DISCORD_TOKEN=your_bot_token
GEMINI_API_KEY=your_google_key
DISCORD_WEBHOOK_URL=your_channel_webhook
OPENROUTER_API_KEY=optional_fallback_key
```

### 24/7 Deployment (Docker)
The project is optimized for low-resource environments (VPS/VM):
```bash
docker-compose up -d --build
```

### Manual Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python bot.py
```

## Commands
*   `/opportunities` - Displays the top 5 curated matches for the current cycle.
*   `/hackclub` - Dedicated panel for active YSWS programs and community events.
*   `/analyze` - Real-time AI analysis for external text or job descriptions.
*   `/config_gemini` - (BYOK) Allows users to provide their own API keys for personal scaling.

---
**Developer:** EngThi | **Status:** Stable MVP v1.0
