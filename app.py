\from flask import Flask, request, jsonify, send_from_directory
import requests
import pymongo
import os
from flask_cors import CORS

# Set the static folder to "static" so all static files (HTML, CSS, JS, images) are served from there.
app = Flask(__name__, static_folder="static")
CORS(app)  # Allow cross-origin requests

# Use environment variables for security (with fallback defaults)
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://batman:1%40mBATMAN@cluster0.edbvm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client["chatbotDB"]

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

@app.route("/api/chat", methods=["GET"])
def chat():
    user_id = request.args.get("user_id")
    query = request.args.get("query")
    if not user_id or not query:
        return jsonify({"error": "Missing parameters"}), 400

    # Retrieve user-specific context from DB
    user_data = db.users.find_one({"user_id": user_id})
    if not user_data:
        return jsonify({"error": "User not found"}), 404

    context_data = user_data.get("context", "Default chatbot context")
    system_prompt = f"""
    You are a chatbot assisting {user_data['company_name']}.
    Product: {user_data['product']}
    Context: {context_data}
    """

    request_body = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        "temperature": 0.85,
        "max_tokens": 300
    }

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    response = requests.post(GROQ_API_URL, json=request_body, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Groq API Error"}), 500

    response_data = response.json()
    return jsonify({"response": response_data["choices"][0]["message"]["content"]})

# API to generate the embed code for users
@app.route("/api/generate_embed", methods=["POST"])
def generate_embed():
    data = request.json
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    embed_code = f'<script src="https://enbewddable-chatbot.onrender.com/embed.js" data-user-id="{user_id}" data-theme="light" data-color="#000"></script>'
    return jsonify({"embed_code": embed_code})

# Serve embed.js from the static folder
@app.route("/embed.js")
def serve_embed_js():
    return send_from_directory(app.static_folder, "embed.js")

# Serve index.html from the static folder so you can load the full UI
@app.route("/index.html")
def serve_index_html():
    return send_from_directory(app.static_folder, "index.html")

# NEW: Serve files from the data folder (for dynamic context data)
@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory('data', filename)

# Home route
@app.route("/")
def home():
    return "Welcome to the Embeddable Chatbot API! Use /api/chat and /api/generate_embed."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
