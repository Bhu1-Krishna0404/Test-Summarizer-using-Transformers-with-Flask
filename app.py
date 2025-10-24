from flask import Flask, render_template, request, redirect, url_for, session, flash
import os, json
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("tool"))
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        if not username or not password:
            flash("Enter both username and password.", "danger")
            return redirect(url_for("register"))
        users = load_users()
        if username in users:
            flash("Username exists.", "danger")
            return redirect(url_for("register"))
        users[username] = {"password": password}
        save_users(users)
        flash("Registered. Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        users = load_users()
        if username in users and users[username].get("password") == password:
            session["username"] = username
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("tool"))
        flash("Invalid credentials.", "danger")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out.", "info")
    return redirect(url_for("index"))

@app.route("/tool", methods=["GET","POST"])
@login_required
def tool():
    original = ""
    result = None
    action = ""
    if request.method == "POST":
        original = request.form.get("user_text","").strip()
        action = request.form.get("action","")
        if not original:
            flash("Please enter text.", "warning")
            return redirect(url_for("tool"))
        try:
            # Use T5 (TensorFlow) for both summarization and paraphrasing.
            from transformers import pipeline
            if action == "summarize":
                summarizer = pipeline("text2text-generation", model="t5-small", framework="tf")
                prompt = "summarize: " + original
                out = summarizer(prompt, max_length=150, min_length=30, do_sample=False)
                result = out[0]["generated_text"]
            elif action == "paraphrase":
                paraphraser = pipeline("text2text-generation", model="t5-small", framework="tf")
                prompt = "paraphrase: " + original
                out = paraphraser(prompt, max_length=150, num_return_sequences=1)
                result = out[0]["generated_text"]
            else:
                result = "Unknown action."
        except Exception as e:
            result = ("Model error or models not downloaded. Make sure you installed requirements and have internet for first-time download.\n\nError: " + str(e))
    return render_template("tool.html", original=original, result=result, action=action)

if __name__ == '__main__':
    app.run(debug=True)
