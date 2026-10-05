#!/usr/bin/env python3
"""Create the ib-landing repo on GitHub and enable Pages. Read-only with respect to every other repo."""
import json, urllib.request, urllib.error

TOKEN = open('/root/.hermes/profiles/banksy/home/.git-credentials').read().strip().split(':')[2].split('@')[0]
OWNER = "darrenhopwood13-maker"
REPO = "ib-landing"

def api(path, method="GET", data=None):
    req = urllib.request.Request(
        "https://api.github.com" + path, method=method,
        headers={"Authorization": "token " + TOKEN, "User-Agent": "ib-landing-publisher",
                 "Accept": "application/vnd.github+json"},
        data=json.dumps(data).encode() if data is not None else None)
    try:
        r = urllib.request.urlopen(req, timeout=45)
        body = r.read().decode()
        return r.status, (json.loads(body) if body.strip() else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]

# 1. does it already exist?
s, d = api(f"/repos/{OWNER}/{REPO}")
print("GET repo ->", s, d if s != 200 else d.get("full_name"))
if s == 404:
    s2, d2 = api("/user/repos", "POST", {
        "name": REPO,
        "description": "instructBrain landing page design mockup (standalone, not the product repo)",
        "private": False,
        "has_issues": False, "has_wiki": False, "has_projects": False,
        "auto_init": False,
    })
    print("CREATE repo ->", s2, d2 if s2 not in (200, 201) else d2.get("full_name"))

# 2. enable GitHub Pages from main / root
s3, d3 = api(f"/repos/{OWNER}/{REPO}/pages")
if s3 == 200:
    print("Pages already enabled:", d3.get("html_url"), d3.get("status"))
else:
    for payload in ({"source": {"branch": "main", "path": "/"}, "build_type": "legacy"},
                    {"source": {"branch": "main", "path": "/"}}):
        s4, d4 = api(f"/repos/{OWNER}/{REPO}/pages", "POST", payload)
        print("ENABLE Pages", payload.get("build_type"), "->", s4, str(d4)[:200])
        if s4 in (201, 200):
            break
