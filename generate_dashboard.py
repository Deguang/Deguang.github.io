import os
import json
import urllib.request
from datetime import datetime

USERNAME = "Deguang"
DOMAIN = "https://app.lideguang.com"
TOKEN = os.getenv("GITHUB_TOKEN")

# 获取用户的公开仓库 (最多取前 100 个)
url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner&sort=updated"
headers = {"Accept": "application/vnd.github.v3+json"}
if TOKEN:
    headers["Authorization"] = f"token {TOKEN}"

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        repos = json.loads(response.read().decode())
except Exception as e:
    print(f"Error fetching repos: {e}")
    repos = []

# 筛选出带有 Github Pages 的仓库，并排除根域名自身项目，防止套娃
pages_repos = [
    repo for repo in repos
    if repo.get("has_pages") and repo["name"].lower() != f"{USERNAME.lower()}.github.io"
]

html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Li Deguang - App Dashboard | 应用导航台</title>
    <meta name="description" content="Li Deguang 的应用导航台，汇集开源项目与在线工具。Personal dashboard and open-source project collection by Li Deguang (GitHub: {username}).">
    <meta name="author" content="Li Deguang">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{domain}/">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>%F0%9F%91%8B</text></svg>">
    <meta name="theme-color" content="#f7f7f8" media="(prefers-color-scheme: light)">
    <meta name="theme-color" content="#0f1115" media="(prefers-color-scheme: dark)">

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{domain}/">
    <meta property="og:title" content="Li Deguang - App Dashboard">
    <meta property="og:description" content="Li Deguang 的应用导航台与开源项目集">
    <meta property="og:image" content="https://github.com/{username}.png">
    <meta property="og:locale" content="zh_CN">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="Li Deguang - App Dashboard">
    <meta name="twitter:description" content="Li Deguang 的应用导航台与开源项目集">
    <meta name="twitter:image" content="https://github.com/{username}.png">

    <!-- Structured data for search engines & AI/LLM answer engines (GEO) -->
    <script type="application/ld+json">
{json_ld}
    </script>

    <style>
        :root {{
            --bg: #f7f7f8;
            --surface: #ffffff;
            --border: #e5e7eb;
            --text: #18181b;
            --muted: #6b7280;
            --accent: #4f46e5;
            --shadow: 0 1px 2px rgba(0,0,0,0.04), 0 1px 3px rgba(0,0,0,0.06);
            --shadow-hover: 0 10px 24px rgba(0,0,0,0.09);
        }}
        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg: #0f1115;
                --surface: #1a1d23;
                --border: #2a2e37;
                --text: #f3f4f6;
                --muted: #9aa0a8;
                --accent: #818cf8;
                --shadow: 0 1px 2px rgba(0,0,0,0.3);
                --shadow-hover: 0 10px 24px rgba(0,0,0,0.5);
            }}
        }}
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }}
        .page {{ max-width: 1080px; margin: 0 auto; padding: 4rem 1.5rem 3rem; }}
        .hero {{ text-align: center; margin-bottom: 3rem; }}
        .avatar {{ border-radius: 50%; margin-bottom: 1rem; box-shadow: var(--shadow); }}
        .hero h1 {{ font-size: 2rem; margin: 0 0 0.5rem; font-weight: 700; }}
        .wave {{ display: inline-block; animation: wave 2.2s infinite; transform-origin: 70% 70%; }}
        @keyframes wave {{
            0%, 60%, 100% {{ transform: rotate(0deg); }}
            10% {{ transform: rotate(14deg); }}
            20% {{ transform: rotate(-8deg); }}
            30% {{ transform: rotate(14deg); }}
            40% {{ transform: rotate(-4deg); }}
            50% {{ transform: rotate(10deg); }}
        }}
        .tagline {{ color: var(--muted); margin: 0 0 0.25rem; }}
        .meta {{ color: var(--muted); font-size: 0.85rem; margin: 0; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 1.25rem;
        }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            box-shadow: var(--shadow);
            transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
        }}
        .card:hover {{
            transform: translateY(-3px);
            box-shadow: var(--shadow-hover);
            border-color: var(--accent);
        }}
        .card-title {{ font-size: 1.05rem; font-weight: 600; margin: 0 0 0.5rem; }}
        .card-desc {{ color: var(--muted); font-size: 0.9rem; flex: 1; margin: 0 0 1.25rem; }}
        .card-link {{
            align-self: flex-start;
            color: var(--accent);
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            transition: gap 0.15s ease;
        }}
        .card-link:hover {{ gap: 0.55rem; }}
        .footer {{ text-align: center; margin-top: 3.5rem; color: var(--muted); font-size: 0.85rem; }}
        .footer a {{ color: var(--accent); text-decoration: none; }}
        .footer a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="page">
        <header class="hero">
            <img class="avatar" src="https://github.com/{username}.png" alt="Li Deguang avatar" width="72" height="72" loading="lazy">
            <h1>Hi, I'm Deguang <span class="wave">👋</span></h1>
            <p class="tagline">Welcome to my application dashboard. 欢迎来到我的应用导航页。</p>
            <p class="meta">Last updated: {update_time}</p>
        </header>
        <main class="grid">
            {cards}
        </main>
        <footer class="footer">
            <p>&copy; {year} Li Deguang &middot; <a href="https://github.com/{username}">GitHub</a></p>
        </footer>
    </div>
</body>
</html>
"""

card_template = """
<article class="card">
    <h2 class="card-title">{name}</h2>
    <p class="card-desc">{description}</p>
    <a href="/{name}/" class="card-link">Visit App <span aria-hidden="true">&rarr;</span></a>
</article>
"""

cards_html = ""
for repo in pages_repos:
    desc = repo.get("description") or "暂无描述 (No description provided)."
    cards_html += card_template.format(
        name=repo["name"],
        description=desc,
    )

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
current_date = datetime.now().strftime("%Y-%m-%d")
current_year = datetime.now().strftime("%Y")

# JSON-LD structured data: identifies the author entity and lists the apps
# as a machine-readable collection, so search/AI engines can cite them accurately.
json_ld_data = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "Person",
            "name": "Li Deguang",
            "url": f"{DOMAIN}/",
            "sameAs": [f"https://github.com/{USERNAME}"],
        },
        {
            "@type": "CollectionPage",
            "name": "Li Deguang - App Dashboard",
            "url": f"{DOMAIN}/",
            "description": "Li Deguang 的应用导航台与开源项目集",
            "author": {"@type": "Person", "name": "Li Deguang"},
            "hasPart": [
                {
                    "@type": "SoftwareApplication",
                    "name": repo["name"],
                    "url": f"{DOMAIN}/{repo['name']}/",
                    "description": repo.get("description") or "暂无描述 (No description provided).",
                    "applicationCategory": "WebApplication",
                }
                for repo in pages_repos
            ],
        },
    ],
}
json_ld = json.dumps(json_ld_data, ensure_ascii=False, indent=2)

final_html = html_template.format(
    username=USERNAME,
    domain=DOMAIN,
    json_ld=json_ld,
    cards=cards_html,
    update_time=current_time,
    year=current_year,
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

# 生成 sitemap.xml，帮助搜索引擎与生成式引擎发现所有子项目页面
sitemap_urls = [f"{DOMAIN}/"] + [f"{DOMAIN}/{repo['name']}/" for repo in pages_repos]
sitemap_entries = "\n".join(
    f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{current_date}</lastmod>\n  </url>"
    for u in sitemap_urls
)
sitemap_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f"{sitemap_entries}\n"
    "</urlset>\n"
)
with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(sitemap_xml)

print("Dashboard, and sitemap generated successfully.")
