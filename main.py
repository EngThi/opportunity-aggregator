import sys
import os
import time
import schedule
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sources.mlh import fetch_mlh
from sources.tabnews import fetch_tabnews
from sources.devpost import fetch_devpost
from sources.hackclub import fetch_hackclub
from sources.github_jobs import fetch_github_jobs
from scorer import AIScorer
from database import save_opportunity, init_db
from src import notifier

load_dotenv()

def run_aggregator():
    print(f"\n🚀 [{time.strftime('%H:%M:%S')}] Starting Smart Sync...")
    init_db()
    
    all_opportunities = []
    
    print("📡 Scraping sources...")
    try: all_opportunities.extend(fetch_mlh())
    except: print("⚠️ MLH Error")
    
    try: all_opportunities.extend(fetch_tabnews())
    except: print("⚠️ TabNews Error")
    
    try: all_opportunities.extend(fetch_devpost())
    except: print("⚠️ Devpost Error")

    try: all_opportunities.extend(fetch_github_jobs())
    except: print("⚠️ GitHub Jobs Error")

    try: all_opportunities.extend(fetch_hackclub())
    except: print("⚠️ Hack Club Error")

    print(f"✅ Total found: {len(all_opportunities)}")

    print("🧠 Scoring with Gemini 3...")
    scorer = AIScorer() # Uses system profile/keys
    scored_opportunities = []
    
    # Process the 20 most recent
    for opp in all_opportunities[:20]:
        print(f"   🧐 Analyzing: {opp['title'][:50]}...")
        score, rationale = scorer.score_opportunity(opp)
        opp['score'] = score
        opp['rationale'] = rationale
        scored_opportunities.append(opp)

    print("💾 Saving to Database...")
    save_opportunity(scored_opportunities)

    # 4. Proactive Alerts (Elite Radar)
    print("📡 Checking for elite opportunities (>90%)...")
    alerts_sent = 0
    for opp in scored_opportunities:
        if opp.get('score', 0) >= 90:
            notifier.send_proactive_alert(opp)
            alerts_sent += 1
    
    print(f"✨ Sync completed. {alerts_sent} alerts triggered.")

if __name__ == "__main__":
    # First run
    run_aggregator()
    
    # Schedule every 6 hours
    schedule.every(6).hours.do(run_aggregator)
    
    print("\n⏰ Scheduler ACTIVE. Running every 6 hours.")
    while True:
        schedule.run_pending()
        time.sleep(60)
