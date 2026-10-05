#!/usr/bin/env python3
"""Poll the GitHub Pages build, then verify the published URL serves exactly the local page."""
import hashlib, json, re, time, urllib.request, urllib.error

TOKEN = open('/root/.hermes/profiles/banksy/home/.git-credentials').read().strip().split(':')[2].split('@')[0]
OWNER, REPO = "darrenhopwood13-maker", "ib-landing"
URL = f"https://{OWNER}.github.io/{REPO}/"

def api(path):
    req = urllib.request.Request("https://api.github.com" + path,
        headers={"Authorization": "token " + TOKEN, "User-Agent": "ib-verify",
                 "Accept": "application/vnd.github+json"})
    try:
        r = urllib.request.urlopen(req, timeout=45)
        return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]

def get(url, tries=40, delay=10):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0",
                "Cache-Control": "no-cache"})
            r = urllib.request.urlopen(req, timeout=45)
            return r.status, r.read(), dict(r.headers)
        except urllib.error.HTTPError as e:
            if i == tries - 1:
                return e.code, b"", {}
            time.sleep(delay)
        except Exception:
            if i == tries - 1:
                return 0, b"", {}
            time.sleep(delay)

# 1. wait for the build to report built
for i in range(40):
    s, d = api(f"/repos/{OWNER}/{REPO}/pages/builds/latest")
    if s == 200:
        st = d.get("status")
        print(f"build {i}: status={st} error={d.get('error')} {d.get('created_at')}")
        if st == "built":
            break
    else:
        print("build poll ->", s, d)
    time.sleep(10)

# 2. fetch the published page
status, body, headers = get(URL)
print("\nGET", URL, "->", status, "| server:", headers.get("Server"), "| type:", headers.get("Content-Type"))
if status != 200:
    raise SystemExit("published URL did not return 200")

local = open("/root/ib-landing/index.html", "rb").read()

def norm(b):
    t = b.decode("utf-8", "replace")
    return re.sub(r"\s+", " ", t).strip()

same = norm(local) == norm(body)
print("published bytes:", len(body), "| local bytes:", len(local))
print("normalised content identical to local file:", same)
print("local  sha256:", hashlib.sha256(local).hexdigest()[:32])
print("remote sha256:", hashlib.sha256(body).hexdigest()[:32])

# 3. every asset the page references must resolve
assets = sorted(set(re.findall(r'(?:src|href)="(https://[^"]+)"', body.decode("utf-8", "replace"))))
bad = []
for a in assets:
    if "github.io" in a:
        continue
    try:
        req = urllib.request.Request(a, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        code = urllib.request.urlopen(req, timeout=30).status
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception as e:
        code = repr(e)[:40]
    if str(code) != "200":
        bad.append((a, code))
    print(f"  asset {code}  {a}")
print("\nBROKEN ASSETS:", bad if bad else "none")
print("\nTITLE:", re.search(r"<title>(.*?)</title>", body.decode('utf-8','replace')).group(1))
