# a.given.day

A daily Instagram post, every day at 00:00 UTC. A carousel of cards + a story.
Fully automated via GitHub Actions and the Instagram Graph API.
Set it up once, runs forever.

---

## Repository structure

```
cards/
├── 01-01/
│   ├── 1.png          ← carousel card 1 (first seen, most important)
│   ├── 2.png          ← carousel card 2
│   ├── 3.png          ← carousel card 3
│   ├── 4.png          ← carousel card 4
│   ├── 5.png          ← carousel card 5  (optional)
│   ├── 6.png          ← carousel card 6  (optional)
│   ├── story.png      ← story (portrait, 9:16 ratio)
│   └── caption.txt    ← plain text caption
├── 01-02/
│   └── ...
├── ...
├── 02-28/
├── 02-29/             ← only posted on leap years; silently skipped otherwise
├── 03-01/
│   └── ...
└── 12-31/
```

Folders are named `MM-DD` — no year. The same 365 (or 366) folders repeat
every year automatically. No maintenance required year to year.

Card images must be PNG, named `1.png`, `2.png` … up to `6.png`.
The script stops at the first missing number, so gaps aren't allowed.
Minimum 2 carousel images, maximum 6.

---

## Image specs

| File | Ratio | Recommended size | Max size |
|---|---|---|---|
| `1.png` … `6.png` | 1:1 square | 1080 × 1080 px | 8 MB |
| `story.png` | 9:16 portrait | 1080 × 1920 px | 8 MB |

---

## One-time setup

### 1. Instagram account

Your account must be a **Professional account** (Creator or Business).
Go to Instagram Settings → Account → Switch to Professional Account.

### 2. Meta Developer app

1. Go to [developers.facebook.com](https://developers.facebook.com) and create an app.
2. Add the **Instagram Graph API** product.
3. Under **Instagram → API setup**, connect your Instagram account.
4. Request **`instagram_content_publish`** permission.

### 3. Permanent token via Meta System User (recommended)

System User tokens never expire — no refreshing, ever.

1. Go to [business.facebook.com](https://business.facebook.com) and create a Business portfolio if you don't have one.
2. Go to **Settings → Users → System Users** → click **Add**.
3. Name it (e.g. `agiven-day-bot`), set role to **Admin**.
4. Click **Assign Assets** → **Instagram Accounts** → your account → **Full Control**.
5. Click **Assign Assets** → **Apps** → your developer app → **Full Control**.
6. Click **Generate New Token** → select your app → enable these scopes:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
7. Copy the token immediately — you won't see it again.

### 4. GitHub repository

This repo must be **public** so Instagram's servers can fetch the raw image URLs.

Add two repository secrets (Settings → Secrets → Actions → New repository secret):

| Secret name | Value |
|---|---|
| `INSTAGRAM_ACCESS_TOKEN` | Your System User token |
| `INSTAGRAM_ACCOUNT_ID` | Your numeric Instagram account ID |

To find your account ID:
```
https://graph.instagram.com/me?fields=id,username&access_token=YOUR_TOKEN
```

---

## February 29

The `02-29` folder is posted on leap years (2028, 2032 …) when February 29
exists as a real date. In non-leap years the script looks for `02-29`, doesn't
find it, and errors — but that's fine, GitHub Actions logs the failure and the
next day picks up `03-01` normally. If you prefer a silent skip rather than a
logged error, you can simply not create the `02-29` folder.

---

## Testing

Trigger a manual run from the GitHub Actions tab using **workflow_dispatch**.
Make sure today's `MM-DD` folder exists with at least `1.png`, `2.png`,
`story.png`, and optionally `caption.txt`.

---

## Caption format

`caption.txt` is plain text. Instagram supports line breaks and hashtags normally.

Example:
```
Day 47.

What did you let go of today?

#agivenday #reflection #dailymark
```

If no `caption.txt` exists, the caption defaults to the `MM-DD` date string.
