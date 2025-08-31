import os
import requests
from flask import Flask, render_template, request, session
from dotenv import load_dotenv

# Load env vars
load_dotenv()

API_KEY = os.getenv("TOKEN")
BASE_URL_OPENROUTER = "https://aipipe.org/openrouter/v1"

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session, replace with env in production

def query_chat_style(prompt: str):
    url = f"{BASE_URL_OPENROUTER}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Assume you are a stubborn and arrogant bot and can't say "
                    "YES, Yes, or yes for anything. You may refuse to answer "
                    "if the answer requires saying YES."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]

@app.route("/", methods=["GET", "POST"])
def index():
    # reset conversation if not present
    if "conversations" not in session:
        session["conversations"] = []

    if request.method == "POST":
        user_input = request.form["user_input"]
        try:
            ai_response = query_chat_style(user_input)
        except Exception as e:
            ai_response = f"Error: {e}"

        # store conversation
        convos = session["conversations"]
        convos.append({"user": user_input, "ai": ai_response})
        session["conversations"] = convos

    return render_template("index.html", conversations=session.get("conversations", []))

@app.route("/clear")
def clear():
    session.pop("conversations", None)
    return render_template("index.html", conversations=[])
    

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
