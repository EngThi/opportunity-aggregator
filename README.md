# Opportunity Aggregator 🚀

An intelligent system to centralize and rank academic and tech opportunities using AI. Built to solve the problem of fragmented information, allowing users to find the best-fit hackathons, scholarships, and jobs in seconds.

## Core Features
*   **Multi-Source Scraping:** Real-time data from Devpost (API), MLH, TabNews, and GitHub Jobs.
*   **AI Match Scoring:** Uses Gemini 3.1 Flash to compare opportunities against a local `user_profile.md`.
*   **Resilient Architecture:** Multi-tier fallback system (Google Gemini -> OpenRouter) to bypass quota limits.
*   **Discord Integration:** Slash commands for searching, analyzing text, and viewing daily top matches.
*   **Persistence:** Local SQLite database for fast, offline-ready queries.

## Deployment on VM
The project is optimized to run in containerized environments (Docker), making it easy to host alongside other services like OmniLab.

### Using Docker Compose
```bash
docker-compose up -d --build
```

### Manual Setup
1. Create environment: `python3 -m venv .venv && source .venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the bot: `python bot.py`

## Commands
*   `/opportunities` - List the top 5 matches found today.
*   `/match` - Update your skills and get a new analysis.
*   `/analyze` - Paste any text to get an instant AI match score.
*   `/models` - Check which AI models are currently responsive.

## Project Context
This project was developed in short bursts during daily bus commutes, focusing on maximum code efficiency and high-utility output for students and developers.

---
**Status:** Functional Super MVP | **Developer:** EngThi 🚌⚡
