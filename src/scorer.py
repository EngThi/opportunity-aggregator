import os
from google import genai
from openai import OpenAI
from dotenv import load_dotenv
import json
import re
from src import config, database

load_dotenv()

class AIScorer:
    def __init__(self, user_id=None):
        self.user_id = user_id
        user_keys = database.get_user_keys(user_id) if user_id else {}
        self.gemini_key = user_keys.get("gemini_key") or config.get_gemini_key()
        self.or_key = user_keys.get("openrouter_key") or config.get_openrouter_key()
        self.custom_profile = user_keys.get("profile_md")
        self.preferred_model = user_keys.get("preferred_model")

    def _get_system_prompt(self):
        return """
        You are an elite career mentor and technical strategist. 
        Match opportunities against the user's Markdown profile.
        
        RULES:
        1. Accuracy: Be critical. 
        2. Format: Return valid JSON object.
        3. Language: Respond in the SAME LANGUAGE as the provided User Profile.
        4. Structure: {"score": <int>, "rationale": "<brief explanation>"}
        """

    def _load_profile(self):
        if self.custom_profile: return self.custom_profile
        try:
            with open("user_profile.md", "r", encoding="utf-8") as f: return f.read()
        except: return "Developer interested in AI, Hackathons and Automation."

    def score_opportunity(self, opportunity):
        user_profile = self._load_profile()
        system_prompt = self._get_system_prompt()
        user_content = f"USER PROFILE:\n{user_profile}\n\nOPPORTUNITY:\n{opportunity.get('title')} - {opportunity.get('description')}"
        
        # --- USER PREFERRED MODEL & PROVIDER ---
        if self.preferred_model and ":" in self.preferred_model:
            provider, model_id = self.preferred_model.split(":", 1)
            
            # Case OpenRouter
            if provider == "openrouter" and self.or_key:
                try:
                    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=self.or_key)
                    response = client.chat.completions.create(
                        model=model_id,
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}]
                    )
                    text = response.choices[0].message.content.strip()
                    if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
                    result = json.loads(text)
                    return result.get("score", 0), f"(Model: {model_id}) {result.get('rationale', 'N/A')}"
                except: pass
            
            # Case Gemini
            elif provider == "gemini" and self.gemini_key:
                try:
                    client = genai.Client(api_key=self.gemini_key)
                    response = client.models.generate_content(model=model_id, config={'system_instruction': system_prompt}, contents=user_content)
                    text = response.text.strip()
                    if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
                    result = json.loads(text)
                    return result.get("score", 0), f"(Model: {model_id}) {result.get('rationale', 'N/A')}"
                except: pass

        # --- DEFAULT HIERARCHY (Fallback) ---
        if self.gemini_key:
            try:
                client = genai.Client(api_key=self.gemini_key)
                for model_id in config.GOOGLE_DEFAULT_MODELS:
                    try:
                        response = client.models.generate_content(model=model_id, config={'system_instruction': system_prompt}, contents=user_content)
                        text = response.text.strip()
                        if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
                        result = json.loads(text)
                        return result.get("score", 0), result.get("rationale", "N/A")
                    except: continue
            except: pass

        return 50, "Fallback scoring used."

    def generate_daily_strategy(self, scored_opportunities):
        user_profile = self._load_profile()
        top_opps = sorted(scored_opportunities, key=lambda x: x['score'], reverse=True)[:5]
        opps_summary = "\n".join([f"- {o['title']} (Score: {o['score']}%): {o['description'][:100]}" for o in top_opps])
        
        system_prompt = "You are a strategic career advisor. Suggest a path in the same language as the user profile."
        user_content = f"PROFILE:\n{user_profile}\n\nOPPS:\n{opps_summary}\n\nWrite a 3-sentence strategy."

        # Use preferred or first default
        model_id = self.preferred_model if self.preferred_model and "gemini" in self.preferred_model else config.GOOGLE_DEFAULT_MODELS[0]

        if self.gemini_key:
            try:
                client = genai.Client(api_key=self.gemini_key)
                response = client.models.generate_content(model=model_id, config={'system_instruction': system_prompt}, contents=user_content)
                return response.text.strip()
            except: pass
        return "Focus on the highest score opportunities today."
