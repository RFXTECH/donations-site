from flask import Flask, render_template_string, request, redirect, url_for, flash
import datetime

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Required for flashing messages

# List of donation items or featured opportunities
ITEMS = [
    {
        "name": "RFX Tech Support",
        "description": "Support our infrastructure and development efforts.",
        "image_url": "https://via.placeholder.com/300x200?text=RFX+Tech",
        "date": "2026-01-01"
    },
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Donations - RFX</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding: 50px; background-color: #f4f4f4; }
        .container { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 30px; }
        .card { background: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 300px; overflow: hidden; transition: transform 0.2s; }
        .card:hover { transform: translateY(-5px); }
        .card img { width: 100%; height: 200px; object-fit: cover; }
        .card-content { padding: 15px; text-align: left; }
        h1 { color: #333; }
        h3 { margin: 0 0 10px 0; color: #444; }
        p { color: #666; margin: 0; line-height: 1.4; }
        .flash { padding: 10px; border-radius: 5px; margin-bottom: 20px; display: inline-block; }
        .error { background-color: #f8d7da; color: #721c24; }
        .success { background-color: #d4edda; color: #155724; }
        form { text-align: left; max-width: 400px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="date"], textarea { width: 100%; padding: 8px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        button { background-color: #333; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; }
        button:hover { background-color: #555; }
    </style>
</head>
<body>
    <h1>Support RFX Tech</h1>
    <p>Thank you for visiting the donations page.</p>

    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="flash {{ category }}">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <div class="container">
        {% for item in items %}
        <div class="card">
            <img src="{{ item.image_url }}" alt="{{ item.name }}">
            <div class="card-content">
                <h3 style="margin-bottom: 5px;">{{ item.name }}</h3>
                <p style="font-size: 0.85em; color: #888; margin-bottom: 10px;">Posted: {{ item.date }}</p>
                <p>{{ item.description }}</p>
            </div>
        </div>
        {% endfor %}
    </div>

    <hr style="margin-top: 50px; border: 0; border-top: 1px solid #ddd;">

    <div style="margin-top: 30px;">
        <a href="/upload" style="color: #999; text-decoration: none; font-size: 0.8em;">Admin Upload</a>
    </div>

    <p style="font-size: 0.8em; color: #999; margin-top: 20px;">This site is powered by Kubernetes and Longhorn.</p>
</body>
</html>"""

UPLOAD_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<body style="font-family: sans-serif; text-align: center; padding: 50px; background-color: #f4f4f4;">
    <h1>Upload New Item</h1>
    <form method="POST" style="text-align: left; max-width: 400px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <label>Password</label>
        <input type="text" name="password" required placeholder="Enter password" style="width: 100%; padding: 8px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 4px;">

        <label>Name</label>
        <input type="text" name="name" required style="width: 100%; padding: 8px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 4px;">

        <label>Date Posted</label>
        <input type="date" name="date" required style="width: 100%; padding: 8px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 4px;">

        <label>Image URL</label>
        <input type="text" name="image_url" required placeholder="https://..." style="width: 100%; padding: 8px; margin-bottom: 15px; border: 1px solid #ccc; border: 1px solid #ccc; border-radius: 4px;">

        <label>Description</label>
        <textarea name="description" rows="4" required style="width: 100%; padding: 8px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 4px;"></textarea>

        <button type="submit" style="background-color: #333; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%;">Upload Item</button>
    </form>
    <br>
    <a href="/" style="color: #666; text-decoration: none;">&larr; Back to main page</a>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, items=ITEMS)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        password = request.form.get('password')
        if password != 'thefoxes':
            flash('Incorrect password!', 'error')
            return redirect(url_for('upload'))
        
        name = request.form.get('name')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        date_str = request.form.get('date')
        
        try:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
            new_item = {
                "name": name,
                "description": description,
                "image_url": image_url,
                "date": date_str
            }
            ITEMS.insert(0, new_item)
            flash('Item uploaded successfully!', 'success')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
        return redirect(url_for('index'))

    return render_template_string(UPLOAD_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
