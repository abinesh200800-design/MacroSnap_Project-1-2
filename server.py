from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
import tomllib
import time

app = Flask(__name__)

# Read Gemini API key from .streamlit/secrets.toml
with open(".streamlit/secrets.toml", "rb") as f:
    secrets = tomllib.load(f)

GEMINI_API_KEY = secrets["GEMINI_API_KEY"]

# Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-3.5-flash"

SYSTEM_PROMPT = """
You are MY CHAT, a friendly general-purpose AI assistant.

Answer questions about:
- Education
- Colleges and universities
- Places
- Computer and programming
- Technology
- C, C++, Python, Java
- HTML, CSS, JavaScript
- AI and Machine Learning
- Science and general knowledge
- Food and nutrition
- Casual conversation

If the user says hi, hello, saptiya, enna pandra, vanakkam,
or similar casual messages, reply naturally and briefly.

Always reply in the same language/style used by the user:
Tamil -> Tamil
Tanglish -> Tanglish
English -> English
Mixed -> naturally mixed Tamil and English.

Keep simple questions short.
Explain educational questions clearly.

If an image is provided:
- Describe what is visible.
- If it is food, identify it and give an approximate
  calorie, protein, carbohydrate and fat estimate.

Do not invent facts.
If you are unsure, say that you are unsure.
"""

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    message = request.form.get("message", "").strip()
    image = request.files.get("image")

    parts = []

    if image:
        image_bytes = image.read()

        parts.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=image.mimetype
            )
        )

    if message:
        parts.append(message)

    if image and not message:
        parts.append(
            "Analyze this image and describe what you see. "
            "If it is food, identify it and estimate calories, "
            "protein, carbohydrates and fat."
        )

    if not parts:
        return jsonify({
            "reply": "Please type a message or attach an image."
        })

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=parts,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                )
            )

            return jsonify({
                "reply": response.text
            })

        except Exception as error:

            error_text = str(error)

            if "503" in error_text or "UNAVAILABLE" in error_text:
                if attempt < 2:
                    time.sleep(5)
                    continue

                return jsonify({
                    "reply": "Gemini server busy-ah irukku. Konjam neram kalichu try pannunga."
                })

            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                return jsonify({
                    "reply": "Gemini quota limit reached 😕. Quota reset aana piragu try pannunga."
                })

            return jsonify({
                "reply": "Sorry, Gemini connection-la problem irukku."
            })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )