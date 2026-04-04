import os
import sys
import time
import requests
from datetime import datetime, timezone
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────

ACCESS_TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
ACCOUNT_ID   = os.environ["INSTAGRAM_ACCOUNT_ID"]
REPO         = os.environ["GITHUB_REPOSITORY"]
BRANCH       = os.environ.get("GITHUB_BRANCH", "main")

BASE_API = f"https://graph.facebook.com/v21.0/{ACCOUNT_ID}"
BASE_RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"

# ─── Helpers ──────────────────────────────────────────────────────────────────

def image_url(folder: str, filename: str) -> str:
    return f"{BASE_RAW}/cards/{folder}/{filename}"

def file_exists_at_url(url: str) -> bool:
    """Check whether a raw GitHub file URL resolves."""
    r = requests.head(url, timeout=10)
    return r.status_code == 200

def upload_media(url: str, is_carousel_item=False, is_story=False) -> str:
    """Upload an image to Instagram and return its container ID."""
    params = {
        "image_url":    url,
        "access_token": ACCESS_TOKEN,
    }
    if is_carousel_item:
        params["is_carousel_item"] = "true"
    if is_story:
        params["media_type"] = "STORIES"
    r = requests.post(f"{BASE_API}/media", data=params)
    r.raise_for_status()
    return r.json()["id"]

def create_carousel(children_ids: list[str], caption: str) -> str:
    """Combine uploaded images into a carousel container."""
    params = {
        "media_type":   "CAROUSEL",
        "children":     ",".join(children_ids),
        "caption":      caption,
        "access_token": ACCESS_TOKEN,
    }
    r = requests.post(f"{BASE_API}/media", data=params)
    r.raise_for_status()
    return r.json()["id"]

def publish(container_id: str) -> str:
    """Publish a container. Returns the published post ID."""
    params = {
        "creation_id":  container_id,
        "access_token": ACCESS_TOKEN,
    }
    r = requests.post(f"{BASE_API}/media_publish", data=params)
    r.raise_for_status()
    return r.json()["id"]

def wait_until_ready(container_id: str, retries: int = 10, delay: int = 6) -> None:
    """Poll container status until FINISHED or raise on timeout/error."""
    params = {
        "fields":       "status_code",
        "access_token": ACCESS_TOKEN,
    }
    for attempt in range(retries):
        r = requests.get(f"https://graph.facebook.com/v21.0/{container_id}", params=params)
        r.raise_for_status()
        status = r.json().get("status_code")
        print(f"  Container status: {status} (attempt {attempt + 1})")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"Container {container_id} failed with ERROR status")
        time.sleep(delay)
    raise RuntimeError(f"Container {container_id} not ready after {retries} attempts")

# ─── Posting logic ────────────────────────────────────────────────────────────

def post_carousel(folder: str, caption: str) -> str:
    print("── Carousel ────────────────────────────")
    children = []

    for i in range(1, 7):
        url = image_url(folder, f"{i}.png")
        if not file_exists_at_url(url):
            print(f"  {i}.png not found — stopping at {i - 1} images")
            break
        cid = upload_media(url, is_carousel_item=True)
        children.append(cid)
        print(f"  Uploaded {i}.png → {cid}")
        wait_until_ready(cid)

    if len(children) < 2:
        raise ValueError(f"Need at least 2 images for a carousel, found {len(children)}")

    print(f"  Creating carousel ({len(children)} images)…")
    carousel_id = create_carousel(children, caption)

    print("  Waiting for Meta to process carousel…")
    wait_until_ready(carousel_id)

    print("  Publishing…")
    post_id = publish(carousel_id)
    print(f"  ✓ Carousel live: {post_id}")
    return post_id

def post_story(folder: str) -> str:
    print("── Story ───────────────────────────────")
    url = image_url(folder, "story.png")

    if not file_exists_at_url(url):
        raise FileNotFoundError(f"story.png not found for {folder}")

    cid = upload_media(url, is_story=True)
    print(f"  Uploaded story.png → {cid}")

    print("  Waiting for Meta to process story…")
    wait_until_ready(cid)

    print("  Publishing…")
    story_id = publish(cid)
    print(f"  ✓ Story live: {story_id}")
    return story_id

def run_with_retries(fn, label: str, retries: int = 3, delay: int = 30, *args, **kwargs):
    """Run a posting function with retries. Stops immediately on success."""
    for attempt in range(1, retries + 1):
        try:
            fn(*args, **kwargs)
            return True
        except Exception as e:
            print(f"\n⚠ {label} attempt {attempt} failed: {e}", file=sys.stderr)
            if attempt < retries:
                print(f"  Retrying in {delay} s…", file=sys.stderr)
                time.sleep(delay)
            else:
                print(f"  {label} failed after {retries} attempts.", file=sys.stderr)
    return False

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    folder = os.environ.get("POST_DATE") or datetime.now(timezone.utc).strftime("%m-%d")
    print(f"\n{'═' * 40}")
    print(f"  a.given.day — {folder}")
    print(f"{'═' * 40}\n")

    caption_file = Path(f"cards/{folder}/caption.txt")
    caption = caption_file.read_text(encoding="utf-8").strip() if caption_file.exists() else folder
    print(f"Caption: {caption!r}\n")

    run_with_retries(post_carousel, "Carousel", 3, 30, folder, caption)

    print("\nWaiting 10 s before story…")
    time.sleep(10)

    run_with_retries(post_story, "Story", 3, 30, folder)

    print("\n✓ All done.\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
