from google import genai
from openai import OpenAI
import os
import re
from src import config

def calculate_match_score(opportunity_desc, user_skills):
    """
    Calculates match score using a multi-tier fallback strategy:
    Tier 1-3: Google Direct (3 -> 2.5 -> 2)
    Tier 4: OpenRouter (Gemma Free)
    """
    gemini_key = config.get_gemini_key()
    
    # --- GOOGLE DIRECT TIERS ---
    if gemini_key:
        client = genai.Client(api_key=gemini_key)
        for model_id in config.GOOGLE_DEFAULT_MODELS:
            try:
                prompt = f"Return ONLY a number (0-100) representing the job match for: Skills [{user_skills}] and Opportunity [{opportunity_desc}]"
                
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt
                )
                
                match = re.search(r'\d+', response.text)
                if match:
                    print(f"✅ Success using Google Direct: {model_id}")
                    return int(match.group())
            except Exception as e:
                print(f"⚠️ Tier failed ({model_id}): {str(e)[:50]}...")
                continue # Try next model in sequence

    # --- OPENROUTER FALLBACK TIER ---
    or_key = config.get_openrouter_key()
    if or_key:
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=or_key,
            )
            
            model_name = config.OPENROUTER_DEFAULT_MODEL
            prompt = f"Score match 0-100 between Skills: {user_skills} and Job: {opportunity_desc}. Return digits only."
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                extra_headers={
                    "HTTP-Referer": "https://github.com/gemini-cli/opportunity-aggregator",
                    "X-Title": "Opportunity Aggregator Bot",
                }
            )
            
            score_text = response.choices[0].message.content
            match = re.search(r'\d+', score_text)
            if match:
                print(f"✅ Success using OpenRouter Fallback: {model_name}")
                return int(match.group())
        except Exception as e:
            print(f"❌ Critical: OpenRouter fallback also failed: {e}")

    # Final Default case
    return 50
