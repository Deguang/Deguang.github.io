#!/usr/bin/env python3
"""本地维护页面：勾选要展示的项目、填写展示信息，保存到 featured.json。

用法：
    python3 admin.py              # 默认 http://127.0.0.1:7788
    python3 admin.py --port 9000

页面里可以：
- 勾选/取消 GitHub 项目（候选 = 开了 Pages 或填了 homepage 的仓库，自动发现）
- 为每个项目填写展示名/标题/描述（留空则部署时用 GitHub 上的信息）
- 添加不在 GitHub 上的站外项目（如 einktools.com）
- 点"生成预览"本地跑一次 generate_dashboard.py
"""
import argparse
import json
import subprocess
import sys
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
USERNAME = "Deguang"
FEATURED_FILE = ROOT / "featured.json"
ADMIN_HTML = ROOT / "admin.html"
GENERATOR = ROOT / "generate_dashboard.py"

REST_HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Deguang-App-Dashboard",
}


def fetch_repos():
    """拉取公开仓库，供候选列表展示。"""
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner&sort=updated"
    req = urllib.request.Request(url, headers=REST_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Error fetching repos: {e}")
        return []


def load_featured():
    try:
        with open(FEATURED_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("projects", [])
    except FileNotFoundError:
        return []


def validate_projects(projects):
    """校验保存内容，返回 (合法条目列表, 错误信息列表)。"""
    cleaned, errors = [], []
    seen = set()
    if not isinstance(projects, list):
        return None, ["projects 必须是数组"]
    for i, entry in enumerate(projects):
        if isinstance(entry, str):
            name = entry.strip()
            if not name:
                errors.append(f"第 {i + 1} 项：仓库名为空")
                continue
            key = f"repo:{name}"
            if key in seen:
                errors.append(f"第 {i + 1} 项：仓库 {name} 重复")
                continue
            seen.add(key)
            cleaned.append(name)
        elif isinstance(entry, dict):
            repo = (entry.get("repo") or "").strip()
            url = (entry.get("url") or "").strip()
            if not repo and not url:
                errors.append(f"第 {i + 1} 项：缺少 repo 或 url")
                continue
            if repo and url:
                errors.append(f"第 {i + 1} 项：repo 与 url 只能填一个")
                continue
            key = f"repo:{repo}" if repo else f"url:{url}"
            if key in seen:
                errors.append(f"第 {i + 1} 项：{repo or url} 重复")
                continue
            seen.add(key)
            item = {"repo": repo} if repo else {"url": url}
            for field in ("name", "title", "description"):
                value = (entry.get(field) or "").strip()
                if value:
                    item[field] = value
            if url:
                updated = (entry.get("updated") or "").strip()
                if updated:
                    item["updated"] = updated
            cleaned.append(item)
        else:
            errors.append(f"第 {i + 1} 项：类型无效")
    return cleaned, errors


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, code, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        try:
            self._route_get()
        except Exception as e:  # 任何异常都返回 JSON，避免浏览器拿到空响应
            try:
                self._send_json(500, {"error": f"{type(e).__name__}: {e}"})
            except Exception:
                pass

    def do_POST(self):
        try:
            self._route_post()
        except Exception as e:
            try:
                self._send_json(500, {"ok": False, "errors": [f"{type(e).__name__}: {e}"]})
            except Exception:
                pass

    def _route_get(self):
        if self.path in ("/", "/index.html"):
            try:
                html = ADMIN_HTML.read_bytes()
            except FileNotFoundError:
                self._send_json(500, {"error": "admin.html 不存在"})
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
        elif self.path == "/api/state":
            repos, github_error = [], None
            try:
                repos = fetch_repos()
            except Exception as e:
                github_error = f"{type(e).__name__}: {e}"
            repos_by_name = {r["name"]: r for r in repos}
            featured = load_featured()
            featured_repo_names = [
                e if isinstance(e, str) else e.get("repo")
                for e in featured
            ]
            featured_repo_names = [n for n in featured_repo_names if n]

            shown, seen = [], set()
            for r in repos:
                name = r["name"]
                if r.get("fork") or r.get("archived"):
                    continue
                if name.lower() == f"{USERNAME.lower()}.github.io":
                    continue
                # 候选 = 有 Pages 或 homepage；当前已收录的仓库即使不满足也显示出来
                if r.get("has_pages") or r.get("homepage") or name in featured_repo_names:
                    seen.add(name)
                    shown.append({
                        "repo": name,
                        "has_pages": bool(r.get("has_pages")),
                        "homepage": r.get("homepage"),
                        "description": r.get("description"),
                        "pushed_at": r.get("pushed_at"),
                        "html_url": r.get("html_url"),
                    })
            # 已收录但 API 里没有的仓库（拉取失败等），补一个占位条目
            for n in featured_repo_names:
                if n not in seen:
                    shown.append({
                        "repo": n,
                        "has_pages": False,
                        "homepage": None,
                        "description": None,
                        "pushed_at": None,
                        "html_url": f"https://github.com/{USERNAME}/{n}",
                    })
            shown.sort(key=lambda r: r["pushed_at"] or "", reverse=True)
            self._send_json(200, {"repos": shown, "featured": featured, "github_error": github_error})
        else:
            self._send_json(404, {"error": "not found"})

    def _route_post(self):
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
        except json.JSONDecodeError:
            self._send_json(400, {"ok": False, "errors": ["请求体不是合法 JSON"]})
            return

        if self.path == "/api/save":
            projects, errors = validate_projects(body.get("projects"))
            if errors:
                self._send_json(400, {"ok": False, "errors": errors})
                return
            with open(FEATURED_FILE, "w", encoding="utf-8") as f:
                json.dump({"projects": projects}, f, ensure_ascii=False, indent=2)
                f.write("\n")
            self._send_json(200, {"ok": True, "count": len(projects)})
        elif self.path == "/api/generate":
            try:
                result = subprocess.run(
                    [sys.executable, str(GENERATOR)],
                    cwd=str(ROOT), capture_output=True, text=True, timeout=120,
                )
                self._send_json(200, {
                    "ok": result.returncode == 0,
                    "code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                })
            except subprocess.TimeoutExpired:
                self._send_json(500, {"ok": False, "stderr": "生成超时（120s）"})
            except Exception as e:
                self._send_json(500, {"ok": False, "stderr": str(e)})
        else:
            self._send_json(404, {"error": "not found"})


def main():
    parser = argparse.ArgumentParser(description="App dashboard 本地维护页面")
    parser.add_argument("--port", type=int, default=7788)  # 避开 8787（wrangler dev 默认端口）
    args = parser.parse_args()

    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError as e:
        print(f"启动失败：{e}")
        print(f"端口 {args.port} 可能被占用（也许已有一个 admin.py 在跑），或换个端口：python3 admin.py --port {args.port + 1}")
        sys.exit(1)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"维护页面已启动：{url}（Ctrl+C 退出）")
    print("注意：保持这个终端窗口开着，关闭或 Ctrl+C 会停止服务")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已退出")


if __name__ == "__main__":
    main()
