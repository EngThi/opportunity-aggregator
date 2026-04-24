import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

load_dotenv()

class AIScorer:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None
            print("⚠️ GEMINI_API_KEY not found. Scoring will use fallback logic.")

    def _load_profile(self):
        """Lê o perfil do usuário (Hot-reload)"""
        try:
            with open("user_profile.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "General developer interested in hackathons and coding."

    def score_opportunity(self, opportunity):
        if not self.model:
            return self._fallback_score(opportunity)

        user_profile = self._load_profile()
        prompt = f"""
        Act as a career mentor. Match this opportunity to the user profile below.
        
        USER PROFILE:
        {user_profile}
        
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
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(text)
            return result.get("score", 0), result.get("rationale", "Sem justificativa.")
        except Exception as e:
            print(f"❌ Error in AI scoring: {str(e)[:100]}")
            return self._fallback_score(opportunity)

    def _fallback_score(self, opportunity):
        keywords = ["python", "hackathon", "fellowship", "ai", "automation", "api"]
        score = 0
        content = (opportunity.get('title', '') + ' ' + opportunity.get('description', '')).lower()
        for kw in keywords:
            if kw in content:
                score += 15
        return min(score, 100), "Match básico via palavras-chave (Fallback)."
