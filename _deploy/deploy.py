#!/usr/bin/env python3
"""Mirror this repo to the Natro cPanel hosting (mulesigames.com) over FTPS.

    python3 _deploy/deploy.py            # upload + delete files that no longer exist locally
    python3 _deploy/deploy.py --dry-run  # show what would change

Uploads the git-tracked files (so commit first), plus _deploy/htaccess as .htaccess.
The FTP password is read from the macOS keychain:
    security add-internet-password -s ftp.mulesigames.com -a 'deploy@mulesigames.com' -w '<password>'
"""
import ftplib
import io
import os
import ssl
import subprocess
import sys

HOST = "ftp.mulesigames.com"  # keychain item name
SERVER = "94.73.144.194"  # Natro cPanel server; by IP so Cloudflare DNS can't get in the way
USER = "deploy@mulesigames.com"
WEBROOT = "public_html"
SITE = "mulesigames.com"

# Not part of the site (GitHub Pages only, or deploy tooling).
LOCAL_SKIP = ("_deploy/", ".github/", ".nojekyll", "CNAME", "README")
# Hosting files that belong to cPanel, never deleted.
REMOTE_KEEP = (".user.ini", "php.ini", ".well-known", "cgi-bin", ".ftpquota")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def password():
    return subprocess.check_output(
        ["security", "find-internet-password", "-s", HOST, "-a", USER, "-w"], text=True).strip()


def local_files():
    out = subprocess.check_output(["git", "-C", REPO, "ls-files"], text=True).splitlines()
    return [p for p in out if not p.startswith(LOCAL_SKIP)]


def https_ready():
    # Public DNS (not the Mac's cache) so we test what visitors get; a failed handshake = no valid cert yet.
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-m", "15",
                        "--doh-url", "https://1.1.1.1/dns-query", f"https://{SITE}/"])
    return r.returncode == 0


def htaccess(https):
    text = open(os.path.join(REPO, "_deploy", "htaccess")).read()
    text = text.replace("{SCHEME}", "https" if https else "http")
    if not https:
        start = text.index("# BEGIN force-https")
        end = text.index("# END force-https") + len("# END force-https")
        text = text[:start] + "# force-https disabled: certificate not issued yet" + text[end:]
    return text.encode()


def connect():
    ctx = ssl.create_default_context()
    # Shared host presents *.srvpanel.com, not ftp.mulesigames.com.
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ftp = ftplib.FTP_TLS(SERVER, context=ctx, timeout=60)
    ftp.login(USER, password())
    ftp.prot_p()
    return ftp


def remote_tree(ftp, path=""):
    """Yield (relative path, is_dir) for everything under WEBROOT, children before parents."""
    for name, facts in ftp.mlsd(f"{WEBROOT}/{path}".rstrip("/")):
        if name in (".", ".."):
            continue
        rel = f"{path}/{name}" if path else name
        if facts["type"] == "dir":
            yield from remote_tree(ftp, rel)
            yield rel, True
        elif facts["type"] == "file":
            yield rel, False


def ensure_dirs(ftp, rel, made):
    parts = rel.split("/")[:-1]
    for i in range(1, len(parts) + 1):
        d = "/".join(parts[:i])
        if d not in made:
            try:
                ftp.mkd(f"{WEBROOT}/{d}")
            except ftplib.error_perm:
                pass
            made.add(d)


def main():
    dry = "--dry-run" in sys.argv
    files = local_files()
    https = https_ready()
    print(f"HTTPS certificate: {'valid, forcing https' if https else 'not issued yet, staying on http'}")

    ftp = connect()
    remote = list(remote_tree(ftp))
    wanted = set(files) | {".htaccess"}
    wanted_dirs = {"/".join(p.split("/")[:i]) for p in wanted for i in range(1, p.count("/") + 1)}

    made = {d for d, is_dir in remote if is_dir}
    for rel in files:
        print(f"  up   {rel}")
        if not dry:
            ensure_dirs(ftp, rel, made)
            with open(os.path.join(REPO, rel), "rb") as fh:
                ftp.storbinary(f"STOR {WEBROOT}/{rel}", fh)
    print("  up   .htaccess")
    if not dry:
        ftp.storbinary(f"STOR {WEBROOT}/.htaccess", io.BytesIO(htaccess(https)))

    for rel, is_dir in remote:
        if rel.split("/")[0] in REMOTE_KEEP or rel in wanted or rel in wanted_dirs:
            continue
        print(f"  del  {rel}{'/' if is_dir else ''}")
        if not dry:
            (ftp.rmd if is_dir else ftp.delete)(f"{WEBROOT}/{rel}")

    ftp.quit()
    print("dry run, nothing changed" if dry else f"done: http{'s' if https else ''}://{SITE}/")


if __name__ == "__main__":
    main()
