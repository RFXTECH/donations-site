from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
import os
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration - robust path handling for local and container environments
DATA_DIR = (
    os.environ.get('DATA_DIR')
    or ('/data' if os.path.exists('/data') else None)
    or ('/app/data' if os.path.exists('/app/data') else None)
    or os.getcwd()
)

# Ensure DATA_DIR is valid and exists
if not os.path.exists(DATA_DIR):
    DATA_DIR = os.getcwd()

UPLOAD_FOLDER = os.path.join(DATA_DIR, 'uploads')
DB_PATH = os.path.join(DATA_DIR, 'donations.db')

# Ensure directories exist on startup
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and handles migrations."""
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_filename TEXT NOT NULL,
            description TEXT,
            date_added TIMESTAMP NOT NULL,
            claimed_by TEXT,
            is_claimed BOOLEAN DEFAULT 0
        )''')
        # Migrations: Ensure all columns exist
        existing = {r['name'] for r in conn.execute("PRAGMA table_info(items)").fetchall()}
        if 'description' not in existing:
            conn.execute("ALTER TABLE items ADD COLUMN description TEXT")
        if 'claimed_by' not in existing:
            conn.execute("ALTER TABLE items ADD COLUMN claimed_by TEXT")
        if 'is_claimed' not in existing:
            conn.execute("ALTER TABLE items ADD COLUMN is_claimed BOOLEAN DEFAULT 0")
        conn.commit()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Donation Gallery - RFX</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 1000px; margin: auto; }
        header { text-align: center; margin-bottom: 30px; }
        h1 { color: #1a73e5; }
        .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
        .item-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; padding: 15px; transition: transform 0.2s; }
        .item-card:hover { transform: translateY(-5px); }
        .item-img { width: 100%; height: 200px; object-fit: cover; cursor: zoom-in; border-radius: 8px; }
        #lightbox { display: none; position: fixed; z-index: 1000; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); justify-content: center; align-items: center; cursor: zoom-out; }
        #lightbox img { max-width: 90%; max-height: 90%; border-radius: 4px; box-shadow: 0 0 20px rgba(255,255,255,0.2); }
        .badge { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font_weight: bold; margin-bottom: 10px; }
        .badge-active { background: #e6f4ea; color: #1e8e3e; }
        .badge-claimed { background: #e8f0fe; color: #1a73e5; }
        .claim-form { margin-top: 15px; border-top: 1px solid #eee; padding-top: 15px; }
        .claim-input { width: 80%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px; text-align: center; }
        button { background: #1a73e5; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; }
        button:hover { background: #155:7b0; }
        .claimed-section { margin-top: 50px; opacity: 0.8; border-top: 2px solid #ccc; padding-top: 30px; }
        .claimed-item { filter: grayscale(0.5); }
    </style>
</head>
<body>
    <div class="container">
        <header><h1 style="margin:0;">📦 RFX Donation Gallery</h1><p>Treasures waiting for a new home!</p></header>
        <section>
            <h2 style="text-align:center;">Available Treasures</h2>
            <div class="gallery">
                {% for item in active_items %}
                <div class="item-card">
                    <a href="{{ url_for('serve_image', filename=item.image_filename) }}" class="lightbox-trigger">
                        <img src="{{ url_for('serve_image', filename=item.image_filename) }}" class="item-img">
                    </a>
                    <div style="margin-top:10px;">
                        <span class="badge badge-active">Available</span>
                        <p><strong>{{ item.description or 'No description' }}</strong></p>
                        <p style="font-size: 0.8rem; color: #666;">Added: {{ item:date_added }}</p>
                    </div>
                    <form action="{{ url_for('claim_item', item_id=item.id) }}" method="post" class="claim-form">
                        <input type="text" name="username" class="claim-input" placeholder="Your Name" required>
                        <button type="submit">Claim!</button>
                    </form>
                </div>
                {% endfor %}
            </div>
        </section>
        {% if claimed_items %}
        <section class="claimed-section">
            <h2 style="text-align:center;">Recently Claimed</h2>
            <div class="gallery">
                {% for item in claimed_items %}
                <div class="item-card claimed-item">
                    <a href="{{ url_for('serve_image', filename=item.image_filename) }}" class="lightbox-trigger">
                        <img src="{{ url_for('serve_image', filename=item.image_filename) }}" class="item-img">
                    </a>
                    <p style="margin-top:10px;">Claimed by: <strong>{{ item.claimed_by }}</strong></p>
                </div>
                {% endfor %}
            </div>
        </section>
        {% endif %}
        <div style="text-align:center; margin-top:40px;"><a href="/upload" style="color:#1a73e5; font-weight:bold;">Add an Item</a></div>
    </div>
    <div id="lightbox" onclick="this.style.display='none'">
        <img id="lightbox-img" src="">
    </div>
    <script>
        document.querySelectorAll('.lightbox-trigger').forEach(el => {
            el.onclick = (e) => {
                e.preventDefault();
                const lightbox = document.getElementById('lightbox');
                const img = document.getElementById('lightbox-img');
                img.src = el.href;
                lightbox.style.display = 'flex';
            };
        });
    </script>
</body>
</html>
"""

UPLOAD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><title>Upload Item - RFX</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; color: #333; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 400px; margin: auto; text-align: center; }
        input { width: 100%; margin-bottom: 15px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { background: #1a73e5; color: white; border: none; padding: 12px; width: 100%; border-radius: 6px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2 style="margin:0;">📦 Upload Item</h2>
        <form method="post" enctype="multipart/form-data">
            <input type="text" name="description" placeholder="Description" required>
            <input type="file" name="file" accept="image/*" required>
            <button type="submit">Upload</button>
        </form>
        <p><a href="/" style="color:#666;">&larr; Back</a></p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    with get_db() as conn:
        items = conn.execute("SELECT * FROM items ORDER BY date_added DESC").fetchall()
    active = [dict(i) for i in items if not i['is_claimed']]
    claimed = [dict(i) for i in items if i['is_claimed']]
    return render_template_string(HTML_TEMPLATE, active_items=active, claimed_items=claimed)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        desc = request.form.get('description', '')
        if file and file.filename:
            fn = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, fn))
            with get_db() as conn:
                conn.execute("INSERT INTO items (image_filename, description, date_added) VALUES (?, ?, ?)",
                             (fn, desc, datetime.now().strftime('%Y-%m_d %H:%M:%S')))
                conn.commit()
            return redirect(url_for('index'))
    return render_template_string(UPLOAD_TEMPLATE)

@app.route('/claim/<int:item_id>', methods=['POST'])
def claim_item(item_id):
    user = request.form.get('username', 'Anonymous')
    with get_db() as conn:
        conn.execute("UPDATE items SET claimed_by = ?, is_claimed = 1 WHERE id = ?", (user, item_id))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
