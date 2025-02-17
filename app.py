from flask import Flask, request, jsonify, send_from_directory
import requests
import pymongo
import os
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)

# MongoDB connection URL and Groq API key
MONGO_URL = "mongodb+srv://batman:1%40mBATMAN@cluster0.edbvm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
GROQ_API_KEY = "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"

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client["chatbotDB"]

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

@app.route("/api/upload_context", methods=["POST"])
def upload_context():
    user_id = request.form.get("user_id")
    context_file = request.files.get("context_file")
    if not user_id or not context_file:
        return jsonify({"error": "Missing user_id or context file"}), 400

    context_data = context_file.read().decode('utf-8')

    # Update or create the user's context in the database
    db.users.update_one(
        {"user_id": user_id},
        {"$set": {"context": context_data}},
        upsert=True
    )
    return jsonify({"message": "Context data uploaded successfully"}), 200

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id")
    query = data.get("query")
    if not user_id or not query:
        return jsonify({"error": "Missing user_id or query"}), 400

    # Retrieve user-specific context from DB
    user_data = db.users.find_one({"user_id": user_id})
    if not user_data or 'context' not in user_data:
        return jsonify({"error": "User context not found"}), 404

    context_data = user_data.get("context", "Default chatbot context")
    system_prompt = f"""
    You are a chatbot assisting the user.
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

    embed_code = f'''
    <iframe 
        src="https://enbewddable-chatbot.onrender.com/index.html?user_id={user_id}"
        style="width: 400px; height: 600px; border: none; position: fixed; bottom: 0; right: 0;"
    ></iframe>
    '''
    return jsonify({"embed_code": embed_code})

# Serve embed.js from the static folder
@app.route("/embed.js")
def serve_embed_js():
    return send_from_directory(app.static_folder, "embed.js")

# Serve index.html from the static folder
@app.route("/index.html")
def serve_index_html():
    return send_from_directory(app.static_folder, "index.html")

# Serve style.css from the static folder
@app.route("/style.css")
def serve_style_css():
    return send_from_directory(app.static_folder, "style.css")

# Serve script.js from the static folder
@app.route("/script.js")
def serve_script_js():
    return send_from_directory(app.static_folder, "script.js")

# Serve files from the data folder (for dynamic context data)
@app.route('/data/<path:filename>')
def serve_data(filename):
    data_path = os.path.join(app.root_path, 'data')
    return send_from_directory(data_path, filename)

# Home route
@app.route("/")
def home():
    return "Welcome to the Embeddable Chatbot API! Use /api/chat and /api/generate_embed."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
