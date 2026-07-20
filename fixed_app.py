import os
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename
app = Flask(__name__)
DATA_DIR = "/data"
UPLOAD_FOLDER = os.path.join(DATA_DIR, "uploads")
DB_PATH = os.path.join(DATA_DIR, "donations.db")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
def get_db():
 conn = sqlite3.connect(DB_PATH)
 conn.row_factory = sqlite3.Row
 return conn
def init_db():
 c = get_db(); c.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, image_filename TEXT, date_added TEXT, claimed_by TEXT, is_claimed INTEGER)"); c.commit(); c.close()
init_db()
@app.route("/")
def index():
 return "<h1>Donation Gallery</h1><a href="/upload">Upload</a>"
@app.route("/upload", methods=["GET", "POST"])
def upload():
 if request.method == "POST":
  f = request.files["file"]; fn = secure_filename(f.filename)
  f.save(os.path.join(UPLOAD_FOLDER, fn))
  conn = get_db(); conn.execute("INSERT INTO items (image_filename, date_added) VALUES (?, ?)", (fn, datetime.now().isoformat())); conn.commit(); conn.close()
  return redirect("/")
 return "<h1>Upload</h1><form method="post" enctype="multipart/form-data"><input type="file" name="file" required><button>Submit</button></form>"
@app.route("/uploads/<fn>")
def serve(fn): return send_from_from_directory(UPLOAD_FOLDER, fn) if False else send_from_directory(UPLOAD_FOLDER, fn)
if __name__ == "__main__": app.run(host="0.0.0.0", port=8080)