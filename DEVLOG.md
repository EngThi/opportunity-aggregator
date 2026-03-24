# DEVLOG: Bus Commutes & High-Tier AI 🚌⚡

Building this wasn't about sitting in a comfy chair. It was about coding in short bursts between bus stops, turning a basic script into a full-blown career assistant.

## The "Super MVP" Progress:

### 1. The Brain (Multi-Tier AI)
I didn't just plug in an API. I built a **resilient hierarchy**:
- **Primary:** Gemini 3 Flash (The latest/fastest).
- **Secondary:** Fallback to Gemini 2.5/2.0.
- **Last Resort:** OpenRouter (Gemma Free) via fallback.
- *Result:* The bot calculates a "Match Score" (0-100%) against user skills. It basically never fails.

### 2. Live Data Flow
Spaghetti code is gone. Everything is modular now:
- **Devpost API:** Snagging hackathons in real-time.
- **MLH:** Dynamic parsing of global events.
- **TabNews:** Tech news via RSS.
- **GitHub Jobs:** Issues tagged for hiring.
- **SQLite:** Fast, local persistence. No cloud latency here.

### 3. Real-Time Discovery
I built a `/models` command that doesn't use a hardcoded list. It talks **directly** to Google and OpenRouter APIs to see what's actually available. If a new model drops today, the bot sees it.

### 4. QA & Automation
- **Tests:** 5 core tests covering scrapers, DB deduplication, and AI scoring.
- **CI/CD:** GitHub Actions set up to test every push.
- **Scheduler:** `main.py` is the pulse, syncing everything daily.

## Personal Flex:
Context matters. This was built by a student during daily commutes. High efficiency, modular architecture, and bleeding-edge AI—all from a smartphone hotspot on a moving bus.

---
**Project Page:** [flavortown.hackclub.com/projects/10278](https://flavortown.hackclub.com/projects/10278)
