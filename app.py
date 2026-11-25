from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, json
from io import BytesIO

app = Flask(__name__)
app.secret_key = "pixelcraft-studio-change-this-secret"
DB = os.path.join(os.path.dirname(__file__), "pixelcraft.db")

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS designs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            design_data TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

@app.route("/")
def home():
    return redirect(url_for("editor") if session.get("user_id") else url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 4:
            error = "Username must be 3+ characters and password 4+ characters."
        else:
            try:
                with db() as con:
                    cur = con.execute("INSERT INTO users(username,password) VALUES(?,?)",
                                      (username, generate_password_hash(password)))
                    session["user_id"] = cur.lastrowid
                    session["username"] = username
                return redirect(url_for("editor"))
            except sqlite3.IntegrityError:
                error = "Username already exists. Please choose another."
    return render_template("auth.html", mode="Create account", error=error)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with db() as con:
            user = con.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("editor"))
        error = "Incorrect username or password."
    return render_template("auth.html", mode="Login", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/editor")
def editor():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    with db() as con:
        designs = con.execute("SELECT id,title,updated_at FROM designs WHERE user_id=? ORDER BY updated_at DESC",
                              (session["user_id"],)).fetchall()
    return render_template("editor.html", designs=designs, username=session.get("username"))

@app.route("/save", methods=["POST"])
def save():
    if not session.get("user_id"):
        return jsonify(ok=False, error="Please login first."), 401
    payload = request.get_json(force=True)
    title = (payload.get("title") or "Untitled Design")[:80]
    data = json.dumps(payload.get("design", {}))
    design_id = payload.get("id")
    with db() as con:
        if design_id:
            cur = con.execute("UPDATE designs SET title=?, design_data=?, updated_at=CURRENT_TIMESTAMP WHERE id=? AND user_id=?",
                              (title, data, design_id, session["user_id"]))
            if cur.rowcount == 0:
                design_id = None
        if not design_id:
            cur = con.execute("INSERT INTO designs(user_id,title,design_data) VALUES(?,?,?)",
                              (session["user_id"], title, data))
            design_id = cur.lastrowid
    return jsonify(ok=True, id=design_id)

@app.route("/design/<int:design_id>")
def load_design(design_id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    with db() as con:
        item = con.execute("SELECT * FROM designs WHERE id=? AND user_id=?",
                           (design_id, session["user_id"])).fetchone()
    if not item:
        return redirect(url_for("editor"))
    return render_template("editor.html", designs=[], username=session.get("username"),
                           initial_design=json.loads(item["design_data"]), design_id=item["id"], title=item["title"])

@app.route("/delete/<int:design_id>", methods=["POST"])
def delete_design(design_id):
    if not session.get("user_id"):
        return jsonify(ok=False), 401
    with db() as con:
        con.execute("DELETE FROM designs WHERE id=? AND user_id=?", (design_id, session["user_id"]))
    return jsonify(ok=True)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
