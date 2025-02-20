from flask import Flask, request, jsonify, send_from_directory
import requests
import pymongo
import os
import json
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow CORS from all origins

# MongoDB connection URL and Groq API key
MONGO_URL = "mongodb+srv://batman:1%40mBATMAN@cluster0.edbvm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
GROQ_API_KEY = "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"

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client["chatbotDB"]

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

### ✅ Allow Users to Upload Their Own Chatbot Context ###
@app.route("/api/upload_context", methods=["POST"])
def upload_context():
    try:
        data = request.json
        user_id = data.get("user_id")
        context_data = data.get("context_data")

        if not user_id or not context_data:
            return jsonify({"error": "Missing user_id or context_data"}), 400

        # Ensure context_data is stored as JSON
        if isinstance(context_data, str):
            try:
                context_data = json.loads(context_data)
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid JSON format"}), 400

        # Update or create user-specific chatbot data
        db.users.update_one(
            {"user_id": user_id},
            {"$set": {"context": context_data}},
            upsert=True
        )
        return jsonify({"message": "Context data uploaded successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

### ✅ Get User-Specific Chatbot Responses ###
@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_id = data.get("user_id")
        query = data.get("query")

        if not user_id or not query:
            return jsonify({"error": "Missing user_id or query"}), 400

        # Retrieve user's chatbot context from MongoDB
        user_data = db.users.find_one({"user_id": user_id})
        if not user_data or "context" not in user_data:
            return jsonify({"error": "User context not found"}), 404

        context_data = user_data["context"]
        system_prompt = f"""
        You are a chatbot personalized for user {user_id}.
        Context: {json.dumps(context_data, indent=2)}
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

    except Exception as e:
        return jsonify({"error": str(e)}), 500

### ✅ Generate a Personalized Embed Code for Each User ###
@app.route("/api/generate_embed", methods=["POST"])
def generate_embed():
    data = request.json
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    embed_code = f"""
    <iframe 
        src='https://enbewddable-chatbot.onrender.com/index.html?user_id={user_id}'
        style='width: 400px; height: 600px; border: none; position: fixed; bottom: 0; right: 0;'>
    </iframe>
    """
    return jsonify({"embed_code": embed_code.strip()})

### ✅ New Endpoint: Get Dynamic Context for a User ###
@app.route("/api/get_context", methods=["GET"])
def get_context():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    user_data = db.users.find_one({"user_id": user_id})
    if not user_data or "context" not in user_data:
        return jsonify({"error": "User context not found"}), 404
    return jsonify({"context": user_data["context"]})

### ✅ NEW: Update User Details (Name and Email) ###
@app.route("/api/update_user_details", methods=["POST"])
def update_user_details():
    try:
        data = request.json
        user_id = data.get("user_id")
        name = data.get("name")
        email = data.get("email")
        
        if not user_id or not name or not email:
            return jsonify({"error": "Missing user_id, name, or email"}), 400
        
        # Update the MongoDB record with the provided name and email
        db.users.update_one(
            {"user_id": user_id},
            {"$set": {"name": name, "email": email}},
            upsert=True
        )
        return jsonify({"message": "User details updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

### ✅ Serve Static Files with Enhanced CORS ###
@app.route("/embed.js")
def serve_embed_js():
    response = send_from_directory(app.static_folder, "embed.js")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route("/index.html")
def serve_index_html():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/style.css")
def serve_style_css():
    return send_from_directory(app.static_folder, "style.css")

@app.route("/script.js")
def serve_script_js():
    return send_from_directory(app.static_folder, "script.js")

### ✅ Serve User-Specific Data Files ###
@app.route('/data/<path:filename>')
def serve_data(filename):
    data_path = os.path.join(app.root_path, 'data')
    return send_from_directory(data_path, filename)

### ✅ Home Route ###
@app.route("/")
def home():
    return "Welcome to the Multi-Instance Chatbot API! Use /api/chat and /api/upload_context."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
