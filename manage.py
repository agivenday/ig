#!/usr/bin/env python3
"""
manage.py — list and delete Instagram media

Usage:
    python manage.py list-stories
    python manage.py list-posts
    python manage.py delete <media_id>
"""

import sys
import os
import requests

ACCESS_TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
ACCOUNT_ID   = os.environ["INSTAGRAM_ACCOUNT_ID"]
BASE_API     = f"https://graph.facebook.com/v21.0"

def list_stories():
    r = requests.get(
        f"{BASE_API}/{ACCOUNT_ID}/stories",
        params={
            "fields":       "id,timestamp,media_type",
            "access_token": ACCESS_TOKEN,
        }
    )
    r.raise_for_status()
    stories = r.json().get("data", [])
    if not stories:
        print("No active stories found.")
        return
    for s in stories:
        print(f"  ID: {s['id']}  |  Type: {s.get('media_type')}  |  Posted: {s.get('timestamp')}")

def list_posts():
    r = requests.get(
        f"{BASE_API}/{ACCOUNT_ID}/media",
        params={
            "fields":       "id,timestamp,media_type,caption",
            "access_token": ACCESS_TOKEN,
        }
    )
    r.raise_for_status()
    posts = r.json().get("data", [])
    if not posts:
        print("No posts found.")
        return
    for p in posts:
        caption = (p.get("caption") or "")[:40]
        print(f"  ID: {p['id']}  |  Type: {p.get('media_type')}  |  Posted: {p.get('timestamp')}  |  Caption: {caption}")

def delete_media(media_id: str):
    r = requests.delete(
        f"{BASE_API}/{media_id}",
        params={"access_token": ACCESS_TOKEN}
    )
    r.raise_for_status()
    result = r.json()
    if result.get("success"):
        print(f"✓ Deleted {media_id}")
    else:
        print(f"✗ Could not delete {media_id}: {result}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list-stories":
        list_stories()
    elif cmd == "list-posts":
        list_posts()
    elif cmd == "delete" and len(sys.argv) == 3:
        delete_media(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)
