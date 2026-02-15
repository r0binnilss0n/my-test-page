import os
import json
import html
import requests
from datetime import datetime

GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v24.0")
IG_USER_ID = os.environ["IG_USER_ID"]
ACCESS_TOKEN = os.environ["IG_ACCESS_TOKEN"]
LIMIT = int(os.getenv("IG_LIMIT", "5"))

OUT_JSON = "ig/posts.json"
OUT_HTML = "index.html"  # optional: we will rewrite it

FIELDS = "id,caption,media_type,media_url,permalink,timestamp,thumbnail_url"

def fetch_media():
    url = f"https://graph.instagram.com/{GRAPH_API_VERSION}/{IG_USER_ID}/media"
    params = {
        "fields": FIELDS,
        "limit": LIMIT,
        "access_token": ACCESS_TOKEN,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json().get("data", [])
    # Prefer thumbnail_url for videos if present
    for p in data:
        if p.get("media_type") in ("VIDEO", "REELS") and p.get("thumbnail_url"):
            p["display_url"] = p["thumbnail_url"]
        else:
            p["display_url"] = p.get("media_url")
    return data

def write_json(posts):
    os.makedirs("ig", exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

def shorten(s, n=220):
    s = (s or "").strip()
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"

def render_index(posts):
    # This generates a full static page (same vibe as your earlier one)
    # Update these paths if you want.
    header_image = "assets/header.jpg"  # or your generated header file
    title = "Aurora Digital"

    def esc(x): return html.escape(x or "")

    cards = []
    for p in posts:
        cards.append(f"""
        <a class="card" href="{esc(p.get("permalink"))}" target="_blank" rel="noopener">
          <img src="{esc(p.get("display_url"))}" alt="" loading="lazy">
          <div class="meta">
            <div class="caption">{esc(shorten(p.get("caption")) )}</div>
            <div class="link">Open on Instagram ↗</div>
          </div>
        </a>
        """)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<style>
:root {{ --max-width: 1200px; }}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: #fafafa;
  color: #111;
}}
.hero {{
  height: 320px;
  background: url("{esc(header_image)}") center/cover no-repeat;
}}
.navbar {{ background: white; border-bottom: 1px solid #eee; }}
.nav-inner {{
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 16px 20px;
  display: flex;
  align-items: center;
}}
.logo {{ font-weight: 800; font-size: 18px; }}
nav {{ margin-left: auto; }}
nav a {{
  text-decoration: none;
  margin-left: 20px;
  color: #111;
  font-weight: 500;
  transition: opacity 0.2s ease;
}}
nav a:hover {{ opacity: 0.6; }}
main {{
  max-width: var(--max-width);
  margin: 42px auto;
  padding: 0 20px 70px 20px;
}}
h2 {{ margin: 0 0 16px; }}
.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
}}
.card {{
  display: block;
  background: white;
  border-radius: 18px;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  box-shadow: 0 12px 30px rgba(0,0,0,0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.card:hover {{
  transform: translateY(-4px);
  box-shadow: 0 18px 40px rgba(0,0,0,0.08);
}}
.card img {{
  width: 100%;
  height: 300px;
  object-fit: cover;
  display: block;
}}
.meta {{ padding: 14px 16px; }}
.caption {{
  font-size: 14px;
  line-height: 1.4;
  max-height: 3.6em;
  overflow: hidden;
}}
.link {{ margin-top: 8px; font-size: 13px; opacity: 0.6; }}
.footer {{
  margin-top: 24px;
  font-size: 12px;
  opacity: 0.55;
}}
</style>
</head>
<body>
<header class="hero"></header>
<div class="navbar">
  <div class="nav-inner">
    <div class="logo">{esc(title)}</div>
    <nav>
      <a href="/">Home</a>
      <a href="https://www.instagram.com/" target="_blank" rel="noopener">Instagram</a>
    </nav>
  </div>
</div>
<main>
  <h2>Latest Instagram Posts</h2>
  <div class="grid">
    {''.join(cards)}
  </div>
  <div class="footer">Updated {esc(datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))}</div>
</main>
</body>
</html>
"""
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(page)

def main():
    posts = fetch_media()
    write_json(posts)
    render_index(posts)

if __name__ == "__main__":
    main()