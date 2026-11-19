import os
import json
import urllib.request
from datetime import datetime, timezone

USERNAME = "Deguang"
DOMAIN = "https://app.lideguang.com"
TOKEN = os.getenv("GITHUB_TOKEN")

# 展示清单（死列表）：收录与否 + 展示信息都维护在 featured.json（可用 admin.py 可视化编辑）。
# GitHub 项目写 {"repo": "<仓库名>"}，name/title/description 可选（留空则在部署时用 GitHub 上的信息）；
# 站外项目写 {"url": "...", ...}，信息全靠条目自带。
# 列表顺序不影响展示，卡片按更新时间自动排序。
FEATURED_FILE = "featured.json"

with open(FEATURED_FILE, encoding="utf-8") as f:
    featured_items = json.load(f).get("projects", [])

# Chrome 应用商店链接，GitHub API 无法拿到，手动维护
CHROME_STORE_LINKS = {}

REST_HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Deguang-App-Dashboard",
}
if TOKEN:
    REST_HEADERS["Authorization"] = f"token {TOKEN}"

# 获取用户的公开仓库 (最多取前 100 个)
repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner&sort=updated"
req = urllib.request.Request(repos_url, headers=REST_HEADERS)
try:
    with urllib.request.urlopen(req) as response:
        repos = json.loads(response.read().decode())
except Exception as e:
    print(f"Error fetching repos: {e}")
    repos = []

repos_by_name = {repo["name"]: repo for repo in repos}


def build_item(entry):
    """把 featured.json 条目解析成统一的展示结构。动态信息以部署时拉取的 API 结果为准。"""
    if isinstance(entry, dict) and entry.get("url"):
        # 站外项目：GitHub 上没有，信息全部来自条目本身
        display_name = entry.get("name") or entry["url"].split("//", 1)[-1].rstrip("/")
        title_attr = entry.get("title") or f"{display_name} - Developer Tool"
        description = entry.get("description") or f"A developer tool and open-source project for {display_name}."
        app_url = entry["url"]
        target_attr = ' target="_blank" rel="noopener"'
        repo_url = None
        pushed_at = entry.get("updated")  # 可选 ISO 时间，如 "2026-11-01T00:00:00Z"
        has_pages = False
        raw_name = display_name
    else:
        if isinstance(entry, str):
            name, override = entry, {}
        elif isinstance(entry, dict) and entry.get("repo"):
            name, override = entry["repo"], entry
        else:
            print(f"Warning: featured entry missing 'repo' or 'url', skipped: {entry!r}")
            return None
        repo = repos_by_name.get(name)
        if repo is None:
            # 仓库不存在或 API 拉取失败：仍然出卡片，但没有更新时间等动态信息
            print(f"Warning: featured repo not found on GitHub: {name}")
            repo = {
                "name": name,
                "html_url": f"https://github.com/{USERNAME}/{name}",
                "homepage": None,
                "description": None,
                "has_pages": False,
                "pushed_at": None,
            }
        display_name = override.get("name") or format_title(name)
        title_attr = override.get("title") or f"{display_name} - Developer Tool"
        description = override.get("description") or repo.get("description") or f"A developer tool and open-source project for {display_name}."
        has_pages = bool(repo.get("has_pages"))
        app_url = f"/{name}/" if has_pages else (repo.get("homepage") or repo["html_url"])
        target_attr = "" if has_pages else ' target="_blank" rel="noopener"'
        repo_url = repo["html_url"]
        pushed_at = repo.get("pushed_at")
        raw_name = name

    return {
        "name": display_name,
        "raw_name": raw_name,
        "title_attr": title_attr,
        "description": description,
        "app_url": app_url,
        "target_attr": target_attr,
        "has_pages": has_pages,
        "repo_url": repo_url,
        "pushed_at": pushed_at,
    }


def relative_time(iso_str):
    dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    days = (datetime.now(timezone.utc) - dt).days
    if days < 1:
        return "今天更新"
    if days < 30:
        return f"{days} 天前更新"
    months = days // 30
    if months < 12:
        return f"{months} 个月前更新"
    return f"{days // 365} 年前更新"


def format_title(name):
    return " ".join(word.capitalize() for word in name.replace("_", "-").split("-"))


display_items = [item for item in (build_item(entry) for entry in featured_items) if item]

# 最新更新的排在最前面（拿不到更新时间的站外项目沉底）
display_items.sort(key=lambda item: item["pushed_at"] or "", reverse=True)


html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Li Deguang - App Dashboard</title>
    <meta name="description" content="Personal dashboard and open-source project collection by Li Deguang (GitHub: {username}).">
    <meta name="author" content="Li Deguang">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{domain}/">
    <link rel="icon" type="image/png" href="https://github.com/{username}.png">
    <link rel="apple-touch-icon" href="https://github.com/{username}.png">
    <meta name="theme-color" content="#f7f7f8" media="(prefers-color-scheme: light)">
    <meta name="theme-color" content="#0f1115" media="(prefers-color-scheme: dark)">

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{domain}/">
    <meta property="og:title" content="Li Deguang - App Dashboard">
    <meta property="og:description" content="Personal dashboard and open-source project collection by Li Deguang">
    <meta property="og:image" content="https://github.com/{username}.png">
    <meta property="og:locale" content="en_US">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary">
    <meta name="twitter:creator" content="@deguang_li">
    <meta name="twitter:title" content="Li Deguang - App Dashboard">
    <meta name="twitter:description" content="Personal dashboard and open-source project collection by Li Deguang">
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
        .tagline-sub {{ color: var(--muted); font-size: 0.8rem; opacity: 0.75; margin: 0 0 0.75rem; }}
        .meta {{ color: var(--muted); font-size: 0.85rem; margin: 0; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 1.25rem;
        }}
        .card {{
            position: relative;
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
        .card-head {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }}
        .card-title {{
            font-size: 1.05rem;
            font-weight: 600;
            margin: 0;
            line-height: 1.4;
        }}
        /* Primary anchor text with stretched link covering the entire card */
        .card-title-link {{
            color: var(--text);
            text-decoration: none;
            transition: color 0.15s ease;
        }}
        .card-title-link:hover,
        .card:hover .card-title-link {{
            color: var(--accent);
        }}
        .card-title-link::after {{
            content: "";
            position: absolute;
            inset: 0;
            z-index: 1;
            border-radius: 14px;
        }}
        .card-updated {{
            font-size: 0.75rem;
            color: var(--muted);
            white-space: nowrap;
            position: relative;
            z-index: 2;
        }}
        .card-desc {{
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.6;
            flex: 1;
            margin: 0 0 1.25rem;
        }}
        .card-links {{
            display: flex;
            align-items: center;
            gap: 1.1rem;
            flex-wrap: wrap;
            position: relative;
            z-index: 2;
            pointer-events: none;
        }}
        /* Visual button indicator without <a> to avoid SEO anchor dilution */
        .card-btn-action {{
            color: var(--accent);
            font-weight: 600;
            font-size: 0.9rem;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            pointer-events: none;
            transition: gap 0.15s ease;
        }}
        .card:hover .card-btn-action {{
            gap: 0.55rem;
        }}
        .card-link {{
            color: var(--accent);
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            pointer-events: auto;
            transition: gap 0.15s ease, color 0.15s ease;
            position: relative;
            z-index: 2;
            cursor: pointer;
        }}
        .card-link:hover {{
            gap: 0.55rem;
        }}
        .card-link-ghost {{
            color: var(--muted);
            font-weight: 500;
        }}
        .card-link-ghost:hover {{
            color: var(--accent);
        }}
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
            <p class="tagline">Welcome to my application dashboard.</p>
            <p class="tagline-sub">欢迎来到我的应用导航页</p>
            <p class="meta">Last updated: {update_time}</p>
        </header>
        <main class="grid">
            {cards}
        </main>
        <footer class="footer">
            <p>&copy; {year} Li Deguang &middot; <a href="https://github.com/{username}">GitHub</a> &middot; <a href="https://x.com/deguang_li">X (Twitter)</a> &middot; <a href="https://blog.lideguang.com">Blog</a></p>
        </footer>
    </div>
</body>
</html>
"""

card_template = """
<article class="card">
    <div class="card-head">
        <h2 class="card-title"><a href="{app_url}" class="card-title-link" title="{title_attr}"{target_attr}>{name}</a></h2>
        <span class="card-updated">{updated}</span>
    </div>
    <p class="card-desc">{description}</p>
    <div class="card-links">
        {action_indicator}{repo_link}{store_link}
    </div>
</article>
"""

cards_html = ""
for item in display_items:
    action_indicator = '<span class="card-btn-action" aria-hidden="true">Visit App &rarr;</span>' if item["has_pages"] else ""
    store_url = CHROME_STORE_LINKS.get(item["raw_name"])
    store_link = f'<a href="{store_url}" class="card-link card-link-ghost" target="_blank" rel="noopener">Chrome Store &rarr;</a>' if store_url else ""
    repo_link = f'<a href="{item["repo_url"]}" class="card-link card-link-ghost" target="_blank" rel="noopener">GitHub &rarr;</a>' if item["repo_url"] else ""
    updated = relative_time(item["pushed_at"]) if item["pushed_at"] else ""
    cards_html += card_template.format(
        name=item["name"],
        title_attr=item["title_attr"],
        app_url=item["app_url"],
        target_attr=item["target_attr"],
        description=item["description"],
        updated=updated,
        action_indicator=action_indicator,
        repo_link=repo_link,
        store_link=store_link,
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
            "sameAs": [f"https://github.com/{USERNAME}", "https://x.com/deguang_li", "https://blog.lideguang.com"],
        },
        {
            "@type": "CollectionPage",
            "name": "Li Deguang - App Dashboard",
            "url": f"{DOMAIN}/",
            "description": "Personal dashboard and open-source project collection by Li Deguang",
            "author": {"@type": "Person", "name": "Li Deguang"},
            "hasPart": [
                {
                    "@type": "SoftwareApplication",
                    "name": item["name"],
                    "url": f"{DOMAIN}{item['app_url']}" if item["app_url"].startswith("/") else item["app_url"],
                    "description": item["description"],
                    "applicationCategory": "WebApplication",
                }
                for item in display_items
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

# Compute Matrix links from display_items (mirroring the dashboard cards)
matrix_links_list = []
for item in display_items:
    url = item["app_url"]
    if url.startswith("/"):
        url = f"{DOMAIN}{url}"
    matrix_links_list.append(f'<a href="{url}" target="_blank" rel="noopener">{item["name"]}</a>')

matrix_html = ""
if matrix_links_list:
    matrix_links = "".join(matrix_links_list)
    matrix_html = f'''
                    <div class="matrix-section">
                        <h3 class="matrix-heading">App Matrix</h3>
                        <div class="matrix-grid">
                            {matrix_links}
                        </div>
                    </div>
                    <hr class="footer-divider" />'''

shared_css = """
        :host, .deguang-footer-fallback { display: block; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
        .footer { margin-top: 4rem; padding: 4rem 1.5rem 2rem; background-color: var(--dg-bg-subtle, transparent); border-top: 1px solid var(--dg-border, #eaeaea); display: flex; flex-direction: column; align-items: center; }
        .footer-content { width: 100%; max-width: 900px; display: flex; flex-direction: column; gap: 2.5rem; }
        .matrix-section { display: flex; flex-direction: column; gap: 1.5rem; width: 100%; }
        .matrix-heading { margin: 0; font-size: 0.875rem; font-weight: 600; color: var(--dg-heading, #111827); letter-spacing: 0.05em; text-transform: uppercase; }
        .matrix-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.25rem 2rem; }
        @media (min-width: 640px) { .matrix-grid { grid-template-columns: repeat(3, 1fr); } }
        @media (min-width: 768px) { .matrix-grid { grid-template-columns: repeat(4, 1fr); } }
        .matrix-grid a { color: var(--dg-muted, #6b7280); font-size: 0.875rem; text-decoration: none; transition: color 0.2s ease, transform 0.2s ease; display: inline-block; }
        .matrix-grid a:hover { color: var(--dg-main, #111827); transform: translateX(3px); }
        .footer-divider { border: 0; height: 1px; background: var(--dg-border, #eaeaea); width: 100%; margin: 0; }
        .footer-bottom { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1.5rem; font-size: 0.875rem; color: var(--dg-muted, #9ca3af); }
        .footer-links { display: flex; gap: 1.5rem; flex-wrap: wrap; }
        .footer-links a { color: var(--dg-muted, #9ca3af); text-decoration: none; transition: color 0.2s ease; }
        .footer-links a:hover { color: var(--dg-main, #111827); }
        @media (prefers-color-scheme: dark) {
            .footer { --dg-border: #2a2e37; --dg-heading: #f3f4f6; --dg-muted: #9ca3af; --dg-main: #ffffff; }
        }
"""

def get_footer_inner_html(year_str):
    return f'''
            <footer class="footer">
                <div class="footer-content">{matrix_html}
                    <div class="footer-bottom">
                        <div class="footer-copyright">&copy; {year_str} Li Deguang</div>
                        <div class="footer-links">
                            <a href="https://app.lideguang.com" target="_blank" rel="noopener">Dashboard</a>
                            <a href="https://github.com/{USERNAME}" target="_blank" rel="noopener">GitHub</a>
                            <a href="https://x.com/deguang_li" target="_blank" rel="noopener">X</a>
                        </div>
                    </div>
                </div>
            </footer>
'''

# Generate a dynamic Web Component for other projects to use as a unified footer
footer_js_content = f"""class DeguangFooter extends HTMLElement {{
    constructor() {{
        super();
        this.attachShadow({{ mode: 'open' }});
    }}
    connectedCallback() {{
        const year = new Date().getFullYear();
        this.shadowRoot.innerHTML = `
            <style>{shared_css}</style>
{get_footer_inner_html('${year}')}
        `;
    }}
}}
customElements.define('deguang-footer', DeguangFooter);
"""
with open("deguang-footer.js", "w", encoding="utf-8") as f:
    f.write(footer_js_content)

# Optional: Generate a pure HTML snippet for build-time pulling (CI/CD)
footer_hybrid_snippet = f"""
<!-- SEO & 兜底静态结构 (会被动态 JS 覆盖) -->
<deguang-footer>
    <style>{shared_css}</style>
    <div class="deguang-footer-fallback">
{get_footer_inner_html(current_date[:4])}
    </div>
</deguang-footer>
<!-- 运行时动态拉取最新组件 -->
<script src="./deguang-footer.js" type="module" async></script>
"""
with open("footer-snippet.html", "w", encoding="utf-8") as f:
    f.write(footer_hybrid_snippet)

# 生成 sitemap.xml：收录主页及所有开启了 Pages 的项目页面
sitemap_urls = [f"{DOMAIN}/"] + [
    f"{DOMAIN}/{repo['name']}/"
    for repo in repos
    if repo.get("has_pages") and repo["name"].lower() != f"{USERNAME.lower()}.github.io"
]
# If repos was empty, fall back to display_items
if len(sitemap_urls) == 1 and display_items:
    sitemap_urls += [
        f"{DOMAIN}/{item['raw_name']}/" for item in display_items if item.get("has_pages")
    ]
seen = set()
unique_sitemap_urls = []
for u in sitemap_urls:
    if u not in seen:
        seen.add(u)
        unique_sitemap_urls.append(u)

sitemap_entries = "\n".join(
    f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{current_date}</lastmod>\n  </url>"
    for u in unique_sitemap_urls
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
