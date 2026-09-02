import os
import json
import urllib.request
from datetime import datetime, timezone

USERNAME = "Deguang"
DOMAIN = "https://app.lideguang.com"
TOKEN = os.getenv("GITHUB_TOKEN")

# Custom metadata to enrich SEO anchor text, title attributes, and context descriptions
APP_METADATA = {
    "query-params-viewer": {
        "name": "Query Params Viewer",
        "title": "URL Query String Parser & Parameter Visualizer",
        "description": "A free online developer tool to parse, decode, and visualize complex URL query string parameters with real-time editing and nested tree view.",
    },
    "gemini-graph-viewer": {
        "name": "Gemini Graph Viewer",
        "title": "Gemini Graph Split-Viewer & Diagram Visualizer Tool",
        "description": "A split-view diagram and graph visualizer tool designed for side-by-side comparison, rendering, and real-time visualization.",
    },
    "link-and-title-copy-pro": {
        "name": "Link & Title Copy Pro",
        "title": "Copy Browser Tab Title and URL Link Extension",
        "description": "A lightweight browser extension to copy tab titles and URL links simultaneously in Markdown, HTML, and text formats. 一键复制浏览器标签页标题与链接。",
    },
    "keep-scroll-sync": {
        "name": "Keep Scroll Sync",
        "title": "Cross-Platform Scroll Position Keeper & Synchronizer",
        "description": "A cross-platform productivity extension to preserve, record, and synchronize webpage scroll positions across browsers.",
    },
    "edgeform": {
        "name": "EdgeForm",
        "title": "Edge-Native Micro-Site Engine & Dynamic Form Generator",
        "description": "An edge-native micro-site engine and dynamic form builder powered by Cloudflare Pages, D1, and KV with zero hosting cost.",
    },
    "vue-pdf-reader": {
        "name": "Vue PDF Reader",
        "title": "Vue.js PDF Reader Component & Document Viewer",
        "description": "An open-source Vue.js component for responsive PDF reading, rendering, and document viewing based on PDF.js.",
    },
    "token-speed-visual": {
        "name": "Token Speed Visual",
        "title": "LLM Token Generation Speed & Latency Benchmark Visualizer",
        "description": "An interactive benchmark visualizer to measure, compare, and display real-time LLM token generation speed and throughput.",
    },
    "doc-parser": {
        "name": "Doc Parser",
        "title": "Smart Document Parser & Content Extractor",
        "description": "An automated document parsing and text extraction tool for structured data analysis and batch processing.",
    },
    "agent-course": {
        "name": "Agent Course",
        "title": "TypeScript AI Agent Development Course",
        "description": "A practical provider-neutral TypeScript course and hands-on guide for building autonomous AI agents.",
    },
    "snap-kit": {
        "name": "Snap Kit",
        "title": "Web Screenshot & Code Snippet Snapping Tool",
        "description": "A fast web snapshot and image capture utility for creating beautiful code snippets and UI screenshots.",
    },
}

# Default featured list used as fallback when no GitHub token / pinned items available
DEFAULT_FEATURED = [
    "query-params-viewer",
    "link-and-title-copy-pro",
    "keep-scroll-sync",
    "gemini-graph-viewer",
    "edgeform",
    "vue-pdf-reader",
]

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

# 通过 GraphQL 获取个人主页 pin 住的仓库 (最多 6 个，按 pin 顺序)
PINNED_QUERY = """
query($login: String!) {
  user(login: $login) {
    pinnedItems(first: 6, types: [REPOSITORY]) {
      nodes {
        ... on Repository {
          name
        }
      }
    }
  }
}
"""

pinned_names = []
if TOKEN:
    try:
        payload = json.dumps({"query": PINNED_QUERY, "variables": {"login": USERNAME}}).encode("utf-8")
        gql_req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=payload,
            headers={
                "Authorization": f"bearer {TOKEN}",
                "Content-Type": "application/json",
                "User-Agent": "Deguang-App-Dashboard",
            },
            method="POST",
        )
        with urllib.request.urlopen(gql_req) as response:
            result = json.loads(response.read().decode())
        nodes = result.get("data", {}).get("user", {}).get("pinnedItems", {}).get("nodes", [])
        pinned_names = [n["name"] for n in nodes]
    except Exception as e:
        print(f"Error fetching pinned repos: {e}")

# Priority order: pinned repos first, then additional featured repos
ordered_names = []
for name in pinned_names:
    if name not in ordered_names and name in repos_by_name:
        ordered_names.append(name)
for name in DEFAULT_FEATURED:
    if name not in ordered_names and name in repos_by_name:
        ordered_names.append(name)

if ordered_names:
    display_repos = [repos_by_name[name] for name in ordered_names]
else:
    # 兜底：退回展示所有开启了 Pages 的仓库
    display_repos = [
        repo for repo in repos
        if repo.get("has_pages") and repo["name"].lower() != f"{USERNAME.lower()}.github.io"
    ]

# 最新更新的排在最前面
display_repos.sort(key=lambda repo: repo["pushed_at"], reverse=True)


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


def get_repo_meta(repo):
    name = repo["name"]
    custom = APP_METADATA.get(name, {})

    display_name = custom.get("name") or format_title(name)
    title_attr = custom.get("title") or f"{display_name} - Developer Tool"
    description = custom.get("description") or repo.get("description") or f"A developer tool and open-source project for {display_name}."

    has_pages = bool(repo.get("has_pages"))
    if has_pages:
        app_url = f"/{name}/"
        target_attr = ""
    else:
        app_url = repo.get("homepage") or repo["html_url"]
        target_attr = ' target="_blank" rel="noopener"'

    return {
        "name": display_name,
        "raw_name": name,
        "title_attr": title_attr,
        "description": description,
        "app_url": app_url,
        "target_attr": target_attr,
        "has_pages": has_pages,
    }


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
        {action_indicator}<a href="{repo_url}" class="card-link card-link-ghost" target="_blank" rel="noopener">GitHub &rarr;</a>{store_link}
    </div>
</article>
"""

cards_html = ""
for repo in display_repos:
    meta = get_repo_meta(repo)
    action_indicator = '<span class="card-btn-action" aria-hidden="true">Visit App &rarr;</span>' if meta["has_pages"] else ""
    store_url = CHROME_STORE_LINKS.get(repo["name"])
    store_link = f'<a href="{store_url}" class="card-link card-link-ghost" target="_blank" rel="noopener">Chrome Store &rarr;</a>' if store_url else ""
    cards_html += card_template.format(
        name=meta["name"],
        title_attr=meta["title_attr"],
        app_url=meta["app_url"],
        target_attr=meta["target_attr"],
        description=meta["description"],
        updated=relative_time(repo["pushed_at"]),
        repo_url=repo["html_url"],
        action_indicator=action_indicator,
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
                    "name": get_repo_meta(repo)["name"],
                    "url": f"{DOMAIN}/{repo['name']}/" if repo.get("has_pages") else repo["html_url"],
                    "description": get_repo_meta(repo)["description"],
                    "applicationCategory": "WebApplication",
                }
                for repo in display_repos
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

# 生成 sitemap.xml：收录主页及所有开启了 Pages 的项目页面
sitemap_urls = [f"{DOMAIN}/"] + [
    f"{DOMAIN}/{repo['name']}/"
    for repo in repos
    if repo.get("has_pages") and repo["name"].lower() != f"{USERNAME.lower()}.github.io"
]
# If repos was empty, fall back to display_repos
if len(sitemap_urls) == 1 and display_repos:
    sitemap_urls += [
        f"{DOMAIN}/{repo['name']}/" for repo in display_repos if repo.get("has_pages")
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
