import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AIScorer:
    def __init__(self, model_name="gemini-3.1-flash-lite-preview"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None
            print("⚠️ GEMINI_API_KEY not found. Scoring will use fallback logic.")

        self.user_profile = self._load_profile()

    def _load_profile(self):
        try:
            with open("user_profile.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "General developer interested in hackathons and coding."

    def score_opportunity(self, opportunity):
        """
        Takes an opportunity dict and returns (score, rationale).
        """
        if not self.model:
            return self._fallback_score(opportunity)

        prompt = f"""
        Act as a career mentor. Match this opportunity to the user profile below.
        
        USER PROFILE:
        {self.user_profile}
        
        OPPORTUNITY:
        Title: {opportunity.get('title')}
        Description: {opportunity.get('description')}
        Source: {opportunity.get('source')}
        
        Return exactly a JSON in this format:
        {{
            "score": <int 0-100>,
            "rationale": "<short explanation in Portuguese why it matches or not>"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Basic JSON extraction from AI response
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            import json
            result = json.loads(text)
            return result.get("score", 0), result.get("rationale", "N/A")
        except Exception as e:
            print(f"❌ Error in AI scoring: {e}")
            return self._fallback_score(opportunity)

    def _fallback_score(self, opportunity):
        # Basic keyword matching as fallback
        keywords = ["python", "hackathon", "fellowship", "ai", "automation"]
        score = 0
        content = (opportunity.get('title', '') + ' ' + opportunity.get('description', '')).lower()
        for kw in keywords:
            if kw in content:
                score += 20
        return min(score, 100), "Match básico de palavras-chave (Fallback)."

    def generate_daily_strategy(self, scored_opportunities):
        """
        Summarizes the best opportunities and suggests a strategic path.
        """
        if not self.model or not scored_opportunities:
            return "Foco do dia: Explore as oportunidades listadas acima e priorize aquelas com maior score de match básico."

        top_opps = sorted(scored_opportunities, key=lambda x: x['score'], reverse=True)[:10]
        opps_summary = "\n".join([f"- {o['title']} (Score: {o['score']}%): {o['description']}" for o in top_opps])

        prompt = f"""
        As a career strategist for a developer with this profile:
        {self.user_profile}
        
        Review these top opportunities found today:
        {opps_summary}
        
        Write a 3-4 sentence "Strategic Recommendation" in Portuguese for the developer's day. 
        Be encouraging, specific, and tell them exactly which one to prioritize and why.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Estratégia do dia: Você tem {len(top_opps)} ótimos matches. Comece pelo que possui o maior score!"

def calculate_match_score(text, skills):
    """
    Legacy function to support bot_legacy.py.
    Calculates a simple match score based on skills presence in text.
    """
    if not skills:
        return 0
        
    text_lower = text.lower()
    # Handle comma separated skills
    skills_list = [s.strip().lower() for s in skills.split(',') if s.strip()]
    
    if not skills_list:
        return 0
        
    matches = 0
    for skill in skills_list:
        if skill in text_lower:
            matches += 1
            
    # Simple scoring: percentage of skills found
    if len(skills_list) > 0:
        score = (matches / len(skills_list)) * 100
        return int(min(score, 100))
    
    return 0

if __name__ == "__main__":
    # Test Scorer
    scorer = AIScorer()
    mock_opp = {
        "title": "MLH Global Hack Week: Python",
        "description": "A week-long hackathon focused on backend development and automation using Python.",
        "source": "MLH"
    }
    score, rationale = scorer.score_opportunity(mock_opp)
    print(f"Score: {score} | Rationale: {rationale}")

