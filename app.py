from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
import os
from datetime import datetime
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration - prefer an explicit env var, then mounted K8s storage, then local dev.
DATA_DIR = (
    os.environ.get('DATA_DIR')
    or ('/data' if os.path.exists('/data') else None)
    or ('/app/data' if os.path.exists('/app/data') else None)
    or os.getcwd()
)
UPLOAD_FOLDER = os.path.join(DATA_DIR, 'uploads')
DB_PATH = os.path.join(DATA_DIR, 'donations.db')

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_filename TEXT NOT NULL,
            description TEXT,
            date_added TIMESTAMP NOT NULL,
            claimed_by TEXT,
            is_claimed BOOLEAN DEFAULT 0
        )
    ''')

    existing_columns = {
        row['name'] for row in conn.execute("PRAGMA table_info(items)").fetchall()
    }
    if 'description' not in existing_columns:
        conn.execute("ALTER TABLE items ADD COLUMN description TEXT")
    if 'claimed_by' not in existing_columns:
        conn.execute("ALTER TABLE items ADD COLUMN claimed_by TEXT")
    if 'is_claimed' not in existing_columns:
        conn.execute("ALTER TABLE items ADD COLUMN is_claimed BOOLEAN DEFAULT 0")

    conn.commit()
    conn.close()

def get_days_left(days_remaining):
    return f"{days_remaining} days left" if days_remaining > 0 else "Expired!"

def parse_item_timestamp(raw_value):
    if isinstance(raw_value, datetime):
        return raw_value

    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f'):
        try:
            return datetime.strptime(raw_value, fmt)
        except ValueError:
            continue

    return datetime.fromisoformat(raw_value)

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Donation Gallery - RFX</title>
    <style>
        body { font-family: sans-serif; background-color: #f0f2f5; margin: 0; padding: 10px; color: #333; }
        .container { max-width: 1000px; margin: auto; }
        header { text-align: center; margin-bottom: 20px; padding: 20px 0; }
        h1 { color: #1a73e5; font-size: 1.8rem; margin: 0; }
        .upload-section { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; text-align: center; }
        .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
        .item-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: transform 0.3s; position: relative; border: 1px solid #eee; }
        .item-card:hover { transform: translateY(-5px); }
        .item-end { width: 100%; height: 200px; object-fit: cover; }
        .item-info { padding: 15px; text-align: center; }
        .badge { font-size: 0.75rem; padding: 4px 10px; border-radius: 20px; font-weight: bold; display: inline-block; margin-bottom: 10px; }
        .badge-active { background: #e6f4ea; color: #1e8e3e; }
        .badge-claimed { background: #e8f0fe; color: #1a73e5; }
        .countdown { font-size: 0.85rem; color: #d93025; font-weight: bold; margin-top: 10px; }
        .claim-form { margin-top: 15px; border-top: 1px solid #eee; padding-top: 15px; }
        .claim-input { width: 85%; padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; text-align: center; }
        button { background: #1a73e5; color: white; border: none; padding: 12px 25px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.3s; width: 100%; }
        button:hover { background: #1557b0; }
        .claimed-section { margin-top: 50px; border-top: 2px solid #ccc; padding-top: 30px; opacity: 0.8; }
        .claimed-item { filter: grayscale(0.6); }
        @media (max-width: 600px) {
            h1 { font-size: 1.5rem; }
            body { padding: 5px; }
            .gallery { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header><h1 style="margin:0;">📦 RFX Donation Gallery</h1><p>Treasures waiting for a new home!</p></header>
        <section class="upload-section">
            <h3 style="margin:0 0 20px 0;">Add an Item</h3>
            <a href="/upload" style="display: inline-block; background: #1a73e5; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: bold;">Go to Upload Page</a>
        </section>
        <h2 style="text-align:center;">Available Treasures</h2>
        <div class="gallery">
            {% for item in active_items %}
            <div class="item-card">
                <img src="{{ url_for('serve_image', filename=item.image_filename) }}" class="item-end">
                <div class="item-info">
                    <span class="badge badge-active">Available</span>
                    <p style="margin: 5px 0; font-size: 0.85rem;">Added: {{ item.date_added }}</p>
                    <div class="countdown">{{ get_days_left(item.days_remaining) }}</div>
                    <form action="/claim/{{ item.id }}" method="post" class="claim-form">
                        <input type="text" name="username" class="claim-input" placeholder="Your Name" required>
                        <button type="submit">Claim!</button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>
        {% if claimed_items %}
        <section class="claimed-section">
            <h2 style="text-align:center;">Recently Claimed</h2>
            <div class="gallery">
                {% for item in claimed_items %}
                <div class="item-card claimed-item">
                    <img src="{{ url_for('serve_image', filename=item.image_filename) }}" class="item-end">
                    <div class="item-info">
                        <span class="badge badge-claimed">Claimed</span>
                        <p style="margin: 5px 0; font-size: 0.85rem;"><strong style="color:#1a73e5;">{{ item.claimed_by }}</strong> grabbed this!</p>
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>
        {% endif %}
    </div>
</body>
</html>
"""

UPLOAD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Item - RFX</title>
    <style>
        body { font-family: sans:sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; width: 100%; max-width: 400px; }
        h1 { color: #1a73e5; margin-bottom: 20px; font-size: 1.5rem; }
        p { color: #666; margin-bottom: 25px; line-height: 1.4; }
        input[type="file"] { margin-bottom: 20px; width: 100%; font-size: 0.9rem; }
        button { background: #1a73e5; color: white; border: none; padding: 14px 25px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; transition: background 0.3s; font-size: 1rem; }
        button:hover { background: #1557b0; }
        .back { margin-top: 25px; display: block; text-decoration: none; color: #666; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="card">
        <h1 style="margin:0;">📦 Upload New Item</h1>
        <p>Select an image from your device to add it to the gallery.</p>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="text" name="description" placeholder="Enter a description" style="width: 100%; padding: 10px; margin-bottom: 20px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box;"><br>
            <input type="file" name="file" accept="image/*" required><br>
            <button type="submit">Upload Item</button>
        </form>
        <a href="/" class="back">← Back to Gallery</a>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor_data = cursor.execute("SELECT * FROM items ORDER BY date_added DESC").fetchall()
    except Exception:
        cursor_data = []
    conn.close()

    active_items = []
    claimed_items = []
    now = datetime.now()

    for row in cursor_data:
        item = dict(row)
        date_added = parse_item_timestamp(item['date_added'])
        days_old = (now - date_added).days
        if days_old >= 30: continue
        item['days_remaining'] = 30 - days_old
        if item['is_claimed']:
            claimed_items.append(item)
        else:
            active_items.append(item)

    return render_template_string(
        HTML_TEMPLATE,
        active_items=active_items,
        claimed_items=claimed_items,
        get_days_left=get_days_left
    )

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        if 'file' not in request.files: return redirect(url_for('index'))
        file = request.files['file']
        if file.filename == '': return redirect(url_for('index'))
        if file:
            filename = secure_filename(file.filename)
            description = request.form.get('description', '')
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)
            conn = get_db_connection()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn.execute("INSERT INTO items (image_filename, description, date_added) VALUES (?, ?, ?)", (filename, description, timestamp))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template_string(UPLOAD_TEMPLATE)

@app.route('/claim/<int:item_id>', methods=['POST'])
def claim_item(item_id):
    username = request.form.get('username')
    if not username: return "Name is required", 400
    conn = get_db_connection()
    cursor = conn.execute(
        "UPDATE items SET claimed_by = ?, is_claimed = 1 WHERE id = ? AND COALESCE(is_claimed, 0) = 0",
        (username, item_id),
    )
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return "Item not found or already claimed", 409

    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
