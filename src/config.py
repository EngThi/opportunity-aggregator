import os
import requests
from google import genai

# --- APP CONFIGURATION INTERFACE ---

# Flag to toggle between Standard Hierarchy and Dynamic Selection
LIST_ALL_AVAILABLE_MODELS = True 

def get_gemini_key():
    return os.environ.get("GEMINI_API_KEY")

def get_openrouter_key():
    return os.environ.get("OPENROUTER_API_KEY")

def fetch_available_google_models():
    """Fetches all accessible models from Google Gemini API."""
    api_key = get_gemini_key()
    if not api_key: return []
    try:
        # Using the new genai client to list models
        client = genai.Client(api_key=api_key)
        models = client.models.list()
        # In the new SDK, we use 'supported_actions'
        return [m.name.replace("models/", "") for m in models if m.supported_actions and "generateContent" in m.supported_actions]
    except Exception as e:
        print(f"Error fetching Google models: {e}")
        return []

def fetch_available_openrouter_models():
    """Fetches all available models from OpenRouter API."""
    api_key = get_openrouter_key()
    if not api_key: return []
    try:
        response = requests.get("https://openrouter.ai/api/v1/models", 
                               headers={"Authorization": f"Bearer {api_key}"})
        if response.status_code == 200:
            data = response.json()
            return [m["id"] for m in data.get("data", [])]
        return []
    except Exception as e:
        print(f"Error fetching OpenRouter models: {e}")
        return []

# Default models (used if dynamic selection isn't performed)
GOOGLE_DEFAULT_MODELS = [
    "gemini-3-flash-preview", 
    "gemini-3.1-flash-lite-preview", 
    "gemini-3.1-pro-preview"
]
OPENROUTER_DEFAULT_MODEL = "google/gemma-3-4b-it:free"
