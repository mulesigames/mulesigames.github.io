#!/usr/bin/env python3
"""Build the GitHub Pages copy (mulesigames.github.io) that forwards visitors to mulesigames.com.

    python3 _deploy/github_pages.py <outdir>

Run by .github/workflows/pages.yml on every push. Each page keeps its full content (store review
crawlers read it without JavaScript), gets a canonical link, and a script sends browsers to the same
path on mulesigames.com. app-ads.txt and images are copied unchanged. Old URLs that shipped builds
and store listings use are recreated from their new pages.
"""
import os
import shutil
import subprocess
import sys

SITE = "https://mulesigames.com"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = ("_deploy/", ".github/", "CNAME", "README")
# old path -> page it now lives at
LEGACY = {"privacy.html": "dontdrop/privacy/index.html"}

FORWARD = ('<link rel="canonical" href="{url}">\n'
           '<script>location.replace("' + SITE + '"+location.pathname+location.search+location.hash)</script>\n')


def page_url(rel):
    path = rel[: -len("index.html")] if rel.endswith("index.html") else rel
    return f"{SITE}/{path}"


def write(out, rel, src):
    dst = os.path.join(out, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if rel.endswith(".html"):
        html = open(os.path.join(REPO, src), encoding="utf-8").read()
        html = html.replace("<head>\n", "<head>\n" + FORWARD.format(url=page_url(src)), 1)
        open(dst, "w", encoding="utf-8").write(html)
    else:
        shutil.copyfile(os.path.join(REPO, src), dst)


def main():
    out = sys.argv[1]
    files = subprocess.check_output(["git", "-C", REPO, "ls-files"], text=True).splitlines()
    for rel in files:
        if not rel.startswith(SKIP):
            write(out, rel, rel)
    for old, new in LEGACY.items():
        write(out, old, new)
    print(f"built {out}")


if __name__ == "__main__":
    main()
