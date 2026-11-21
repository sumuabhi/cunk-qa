import json
import os
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# Render will inject GEMINI_API_KEY automatically from your environment settings
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

GALI_WORDS = {
    "fuck", "fucking", "shit", "bitch", "asshole", "bastard", "dick",
    "bhosdike", "bhosrike", "madarchod", "behenchod", "bhenchod",
    "chutiya", "gandu", "harami", "kamina", "kamine", "saala", "sala", "bc", "mc"
}

def contains_gali(text: str) -> bool:
    words = set(re.findall(r"[a-zA-Z]+", text.lower()))
    return bool(words & GALI_WORDS)

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()
    has_gali = contains_gali(question)

    prompt = f"""
    You are a witty, deadpan assistant. Analyze the user's input and return ONLY valid JSON with two keys:
    1. "reaction": string — MUST be one of:
       - "gali" (if the input contains profanity, Hindi/English gali, insults, or abusive language)
       - "stupid" (if the question is absurd, obvious, nonsensical, lazy, or silly)
       - "normal" (if it is a genuine question)
    2. "answer": string (a clear, helpful, slightly deadpan answer to the user's question).

    User input: "{question}"
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        ai_data = json.loads(response.text)

        reaction = ai_data.get("reaction", "normal")
        if has_gali:
            reaction = "gali"

        return jsonify({
            "reaction": reaction,
            "answer": ai_data.get("answer", "I have no words for this.")
        })
    except Exception as e:
        return jsonify({
            "reaction": "gali" if has_gali else "stupid",
            "answer": f"API error: {e}"
        })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
