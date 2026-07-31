import os
import tempfile

import pytest

os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="donations-test-"))

from app import app  # noqa: E402


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_homepage_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Donation Gallery" in resp.data


def test_upload_page_loads(client):
    resp = client.get("/upload")
    assert resp.status_code == 200
    assert b"Upload Item" in resp.data


def test_admin_requires_access(client):
    resp = client.get("/__admin/items")
    assert resp.status_code == 200
    assert b"Access denied" in resp.data
