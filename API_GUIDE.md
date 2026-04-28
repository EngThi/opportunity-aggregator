# 🔑 AI Configuration & API Guide

This guide explains how to obtain your API keys and configure the Opportunity Aggregator for the best (and cheapest) performance.

## 1. Google Gemini (Preferred)
The bot is optimized for the **Gemini 3.1** family.

### How to get a FREE Key:
1.  Go to [Google AI Studio](https://aistudio.google.com/).
2.  Log in with your Google Account.
3.  Click on **"Get API Key"** on the left sidebar.
4.  Create a key in a new project.
5.  **Copy the key** and use `/config_gemini` in Discord.

### Important Notes:
*   **Gemini 1.5 Flash:** Extremely fast and has a generous free tier.
*   **Gemini 1.5 Pro:** More powerful but has stricter rate limits on the free tier.
*   **GCP Linking:** If you want to use "Pay-as-you-go" or avoid some regional restrictions, you may need to link your AI Studio project to a **Google Cloud Platform (GCP)** project with a billing account attached. However, for most users, the standard AI Studio free tier is enough.

---

## 2. OpenRouter (Fallback & Variety)
OpenRouter allows you to use models from Meta (Llama), Mistral, and even Google via a single API.

### How to get a Key:
1.  Go to [OpenRouter.ai](https://openrouter.ai/).
2.  Create an account.
3.  Go to **Keys** and click **"Create Key"**.
4.  **Copy the key** and use `/config_openrouter` in Discord.

### Free Model Recommendations:
When using `/config_model`, try these free IDs:
*   `google/gemma-3-4b-it:free` (Fast and smart)
*   `meta-llama/llama-3-8b-instruct:free`
*   `mistralai/mistral-7b-instruct:free`

---

## 3. Best Setup for the Bot
For the best experience without spending a cent:
1.  Set your **Gemini Key** (AI Studio).
2.  Use the default **Gemini 1.5 Flash** (it's the bot's default).
3.  Upload a **Markdown Profile** using `/config_profile` so the AI knows what you like.

---
*Generated for Opportunity Aggregator v1.0*
