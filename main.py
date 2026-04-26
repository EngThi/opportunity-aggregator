import os
from dotenv import load_dotenv
load_dotenv(override=True) # Ensure new config is always loaded

import sys
import time
import schedule

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
    print("\n📡 Analyzing Scores for Alerts...")
    alerts_sent = 0
    for opp in scored_opportunities:
        score = opp.get('score', 0)
        if score >= 90:
            print(f"   🔥 ELITE FOUND: {opp['title']} ({score}%)")
            notifier.send_proactive_alert(opp)
            alerts_sent += 1
        elif score >= 70:
            print(f"   🟡 Strong Match: {opp['title']} ({score}%)")
        else:
            print(f"   ⚪ Low Match: {opp['title']} ({score}%)")
    
    print(f"\n✨ Sync completed. {alerts_sent} alerts triggered.")
    
    # Notifica se não encontrou nada de elite nesta rodada
    if alerts_sent == 0:
        print("ℹ️ No elite matches found. Sending status update to Discord...")
        notifier.send_status_update("Daily sync completed. No elite matches (>90%) were found in this cycle. Keeping the radar active!")

if __name__ == "__main__":
    # First run
    run_aggregator()
    
    # Schedule: Every morning at 09:00 and every 6 hours
    schedule.every().day.at("09:00").do(run_aggregator)
    schedule.every(6).hours.do(run_aggregator)
    
    print("\n⏰ Scheduler ACTIVE. Running at 09:00 every day and every 6 hours.")
    while True:
        schedule.run_pending()
        time.sleep(60)
