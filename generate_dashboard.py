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

    <!-- 引入 PaperCSS 实现手写风格 -->
    <link rel="stylesheet" href="https://unpkg.com/papercss@1.9.2/dist/paper.min.css">
    <style>
        body {{ padding: 2rem 1rem; }}
        .dashboard-header {{ margin-bottom: 3rem; text-align: center; }}
        .card {{ height: 100%; display: flex; flex-direction: column; }}
        .card-body {{ flex: 1; }}
        .card-footer {{ margin-top: auto; padding-top: 1rem; }}
        .site-footer {{ margin-top: 3rem; text-align: center; }}
    </style>
</head>
<body>
    <div class="row flex-center">
        <div class="col-12 sm-10 md-10 lg-8">
            <header class="dashboard-header">
                <h1>Hi, I'm Deguang 👋</h1>
                <p>Welcome to my application dashboard. 欢迎来到我的应用导航页。</p>
                <p class="text-muted">Last updated: {update_time}</p>
            </header>
            <main>
                <div class="row">
                    {cards}
                </div>
            </main>
            <footer class="site-footer text-muted">
                <p>&copy; {year} Li Deguang &middot; <a href="https://github.com/{username}">GitHub</a></p>
            </footer>
        </div>
    </div>
</body>
</html>
"""

card_template = """
<div class="col-12 sm-6 md-6 lg-4 margin-bottom">
    <div class="card">
        <div class="card-body">
            <h4 class="card-title">{name}</h4>
            <p class="card-text">{description}</p>
            <div class="card-footer">
                <a href="/{name}/" class="paper-btn btn-primary btn-block">Visit App</a>
            </div>
        </div>
    </div>
</div>
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
