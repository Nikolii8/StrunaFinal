from flask import Flask, jsonify, request, render_template
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Зареждаме .env файл
load_dotenv()

# Supabase ключове
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)

# Counter row
def ensure_counter_row():
    resp = supabase.table("counter").select("id").eq("id", 1).execute()
    rows = resp.data or []
    if not rows:
        supabase.table("counter").insert({"id": 1, "clicks": 0}).execute()

ensure_counter_row()

# --- API за брояч ---
@app.route("/count", methods=["GET"])
def get_count():
    try:
        resp = supabase.table("counter").select("clicks").eq("id", 1).execute()
        rows = resp.data or []
        clicks = rows[0]["clicks"] if rows else 0
        return jsonify({"clicks": clicks})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/click", methods=["POST"])
def add_click():
    try:
        resp = supabase.table("counter").select("clicks").eq("id", 1).execute()
        rows = resp.data or []
        clicks = rows[0]["clicks"] if rows else 0
        new = clicks + 1
        supabase.table("counter").update({"clicks": new}).eq("id", 1).execute()
        return jsonify({"clicks": new})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/waitlist", methods=["POST"])
def add_email():
    try:
        data = request.get_json() or {}
        email = data.get("email")
        if not email:
            return jsonify({"error": "Email is required"}), 400
        supabase.table("waitlist").insert({"email": email}).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- HTML страници ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# --- Стартиране ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
