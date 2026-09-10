import os
import requests


def load_dotenv():
    """Load variables from .env file securely into environment."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file = os.path.join(base_dir, ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip()
        except Exception as e:
            print(f"[TrafficVision AI] Error reading .env: {e}")


load_dotenv()


def ask_groq_chatbot(user_query, dataset_summary="", api_key=None):
    """
    Connects to Groq API (groq/compound model) using GROQ_API_KEY stored safely in .env
    to generate real-time AI responses enriched with dataset telemetry context.
    """
    load_dotenv()
    key = api_key or os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")

    if not key:
        return None

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    system_instruction = (
        "You are TrafficVision AI, an enterprise AI assistant specialized in road traffic safety analytics, "
        "accident telemetry, and transportation risk management. Answer user queries clearly, professionally, "
        "and concisely using emojis, bold text, and bullet points."
    )

    if dataset_summary:
        system_instruction += f"\n\nActive Dataset Telemetry Context:\n{dataset_summary}"

    payload = {
        "model": "groq/compound",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_query}
        ],
        "temperature": 0.7,
        "max_tokens": 600
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=12)
        if res.status_code == 200:
            data = res.json()
            choices = data.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content")
                if content:
                    return content
        elif res.status_code in [400, 404]:
            # Try fallback model groq/compound-mini
            payload["model"] = "groq/compound-mini"
            res_fallback = requests.post(url, json=payload, headers=headers, timeout=12)
            if res_fallback.status_code == 200:
                data = res_fallback.json()
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content")
                    if content:
                        return content
        else:
            print(f"[TrafficVision AI] Groq API HTTP {res.status_code}: {res.text}")
    except Exception as e:
        print(f"[TrafficVision AI] Groq API call error: {e}")

    return None
