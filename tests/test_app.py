import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="donations-test-"))

from app import app, get_db, item_expiry_label  # noqa: E402


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


@pytest.fixture()
def db_path(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    uploads = data_dir / "uploads"
    uploads.mkdir(parents=True)
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.setenv("ADMIN_TOKEN", "")
    monkeypatch.setenv("ALLOWED_ADMIN_CIDRS", "")
    return data_dir


def test_homepage_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Donation Gallery" in resp.data


def test_upload_page_loads(client):
    resp = client.get("/upload")
    assert resp.status_code == 200
    assert b"Upload Item" in resp.data


def test_hidden_admin_page_renders_locally(client):
    resp = client.get("/__admin/items")
    assert resp.status_code == 200
    assert b"Hidden admin" in resp.data
    assert b"Items" in resp.data


def test_item_expiry_label_formats_countdown():
    item = {"date_added": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")}
    label = item_expiry_label(item, now=datetime.now())
    assert "Expires in" in label


def test_expired_item_is_hidden_from_homepage(client, db_path):
    with app.app_context():
        with get_db() as conn:
            conn.execute(
                "INSERT INTO items (image_filename, description, date_added, is_claimed) VALUES (?, ?, ?, ?)",
                ("expired.jpg", "Expired item", (datetime.now() - timedelta(days=31)).strftime("%Y-%m-%d %H:%M:%S"), 0),
            )
            conn.commit()

    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Expired item" not in resp.data
