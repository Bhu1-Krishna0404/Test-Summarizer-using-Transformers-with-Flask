from flask import Flask, render_template, request, redirect, url_for, session, flash
import os, json
from functools import wraps
from transformers import pipeline

app = Flask(__name__)


app.secret_key = "my_super_secret_key_123"

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

# ---------------- USERS UTILS ----------------
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
        json.dump(users, f, indent=4)

# ---------------- LOGIN DECORATOR ----------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("tool"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Enter both username and password.", "danger")
            return redirect(url_for("register"))

        users = load_users()
        if username in users:
            flash("Username already exists.", "danger")
            return redirect(url_for("register"))

        users[username] = {"password": password}
        save_users(users)

        flash("Registered successfully. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        users = load_users()
        if username in users and users[username]["password"] == password:
            session["username"] = username
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("tool"))

        flash("Invalid credentials.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))

# ---------------- TOOL PAGE ----------------
@app.route("/tool", methods=["GET", "POST"])
@login_required
def tool():
    original = ""
    result = ""
    action = ""

    if request.method == "POST":
        original = request.form.get("user_text", "").strip()
        action = request.form.get("action", "")

        if not original:
            flash("Please enter text.", "warning")
            return redirect(url_for("tool"))

        try:
            #  Load model ONCE per request
            t5 = pipeline(
                "text2text-generation",
                model="t5-small",
                framework="tf"
            )

            if action == "summarize":
                prompt = "summarize: " + original
                output = t5(prompt, max_length=150, min_length=30, do_sample=False)
                result = output[0]["generated_text"]

            elif action == "paraphrase":
                prompt = "paraphrase: " + original
                output = t5(prompt, max_length=150, do_sample=False)
                result = output[0]["generated_text"]

            else:
                result = "Invalid action selected."

        except Exception as e:
            result = f"Model error. First time run lo internet undali.\n\n{e}"

    return render_template(
        "tool.html",
        original=original,
        result=result,
        action=action
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
