from flask import Flask, render_template, request, redirect, url_for
import os
import psycopg2
from cryptography.fernet import Fernet
from time import time

app = Flask(__name__)

# 🔑 ENV VARIABLES
DATABASE_URL = os.environ.get("DATABASE_URL")
SECRET_KEY = os.environ.get("SECRET_KEY")

cipher = Fernet(SECRET_KEY.encode())

# 🔒 Rate limit config
RATE_LIMIT = 10
WINDOW = 1800

# Store timestamps per IP (bounded)
request_log = {}

def is_rate_limited(ip):
    now = time()

    logs = request_log.get(ip, [])

    # keep only recent timestamps (in-place to reduce memory churn)
    new_logs = []
    for t in logs:
        if now - t < WINDOW:
            new_logs.append(t)

    if len(new_logs) >= RATE_LIMIT:
        request_log[ip] = new_logs
        return True

    new_logs.append(now)
    request_log[ip] = new_logs

    return False


def save_user(username, password, text):
    encrypted_text = cipher.encrypt(text.encode()).decode()

    # use context manager → auto close (safer, less leak risk)
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password, content) VALUES (%s, %s, %s)",
                (username, password, encrypted_text)
            )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    ip = request.remote_addr or "unknown"

    if is_rate_limited(ip):
        return redirect(url_for("home"))

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    text = request.form.get("textarea", "")

    save_user(username, password, text)

    return redirect(url_for("home"))


if __name__ == "__main__":
    # turn off debug → reduces memory + CPU
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=False)
