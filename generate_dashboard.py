import os
import json
import urllib.request
from datetime import datetime

USERNAME = "Deguang"
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

# 筛选出带有 Github Pages 的仓库
pages_repos = [repo for repo in repos if repo.get("has_pages")]

html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Li Deguang - App Dashboard</title>
    <meta name="description" content="Li Deguang 的应用导航台与开源项目集">
    <!-- 引入 PaperCSS 实现手写风格 -->
    <link rel="stylesheet" href="https://unpkg.com/papercss@1.9.2/dist/paper.min.css">
    <style>
        body { padding: 2rem 1rem; }
        .dashboard-header { margin-bottom: 3rem; text-align: center; }
        .card { height: 100%; display: flex; flex-direction: column; }
        .card-body { flex: 1; }
        .card-footer { margin-top: auto; padding-top: 1rem; }
    </style>
</head>
<body>
    <div class="row flex-center">
        <div class="col-12 sm-10 md-10 lg-8">
            <div class="dashboard-header">
                <h1>Hi, I'm Deguang 👋</h1>
                <p>Welcome to my application dashboard. 欢迎来到我的应用导航页。</p>
                <p class="text-muted">Last updated: {update_time}</p>
            </div>
            <div class="row">
                {cards}
            </div>
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
    # 排除根域名自身项目，防止套娃
    if repo["name"].lower() == f"{USERNAME.lower()}.github.io":
        continue
        
    desc = repo.get("description") or "暂无描述 (No description provided)."
    cards_html += card_template.format(
        name=repo["name"],
        description=desc,
        html_url=repo["html_url"]
    )

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
final_html = html_template.replace("{cards}", cards_html).replace("{update_time}", current_time)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("Dashboard generated successfully.")