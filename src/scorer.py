import os
from google import genai
from openai import OpenAI
from dotenv import load_dotenv
import json
import re
from src import config

load_dotenv()

class AIScorer:
    def __init__(self):
        self.gemini_key = config.get_gemini_key()
        self.or_key = config.get_openrouter_key()
        
    def _load_profile(self):
        """Lê o perfil do usuário (Hot-reload)"""
        try:
            with open("user_profile.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "General developer interested in hackathons and coding."

    def score_opportunity(self, opportunity):
        """
        Calculates match score using a multi-tier fallback strategy:
        Tier 1-3: Google Direct (Gemini 3 family)
        Tier 4: OpenRouter Fallback
        """
        user_profile = self._load_profile()
        
        # --- GOOGLE DIRECT TIERS ---
        if self.gemini_key:
            client = genai.Client(api_key=self.gemini_key)
            for model_id in config.GOOGLE_DEFAULT_MODELS:
                try:
                    prompt = f"""
                    Match this opportunity to the user profile.
                    USER PROFILE: {user_profile}
                    OPPORTUNITY: {opportunity.get('title')} - {opportunity.get('description')}
                    
                    Return exactly a JSON:
                    {{
                        "score": <int 0-100>,
                        "rationale": "<short explanation in Portuguese>"
                    }}
                    """
                    
                    response = client.models.generate_content(
                        model=model_id,
                        contents=prompt
                    )
                    
                    text = response.text.strip()
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0].strip()
                    
                    result = json.loads(text)
                    # print(f"✅ Success using Google Direct: {model_id}")
                    return result.get("score", 0), result.get("rationale", "N/A")
                except Exception as e:
                    # print(f"⚠️ Tier failed ({model_id}): {str(e)[:50]}...")
                    continue

        # --- OPENROUTER FALLBACK TIER ---
        if self.or_key:
            try:
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.or_key,
                )
                
                model_name = config.OPENROUTER_DEFAULT_MODEL
                prompt = f"Score match 0-100 between Profile: {user_profile} and Job: {opportunity.get('title')}. Return JSON with 'score' and 'rationale' (in Portuguese)."
                
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                text = response.choices[0].message.content.strip()
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                
                result = json.loads(text)
                return result.get("score", 0), result.get("rationale", "N/A")
            except Exception as e:
                print(f"❌ Fallback OpenRouter failed: {e}")

        return self._fallback_score(opportunity)

    def _fallback_score(self, opportunity):
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
        if not self.gemini_key or not scored_opportunities:
            return "Foco do dia: Explore as oportunidades listadas acima e priorize aquelas com maior score."

        user_profile = self._load_profile()
        top_opps = sorted(scored_opportunities, key=lambda x: x['score'], reverse=True)[:5]
        opps_summary = "\n".join([f"- {o['title']} (Score: {o['score']}%): {o['description'][:100]}" for o in top_opps])

        prompt = f"""
        Act as a career strategist for this user:
        {user_profile}
        
        Review these top opportunities:
        {opps_summary}
        
        Write a 3-4 sentence "Strategic Recommendation" in Portuguese. 
        Be specific on which one to prioritize and why.
        """
        
        try:
            client = genai.Client(api_key=self.gemini_key)
            response = client.models.generate_content(
                model=config.GOOGLE_DEFAULT_MODELS[0],
                contents=prompt
            )
            return response.text.strip()
        except:
            return "Estratégia do dia: Você tem ótimos matches hoje. Foque no que possui o maior score!"
