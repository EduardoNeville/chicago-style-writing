#!/usr/bin/env python3
"""Packaging checks for the repository, run by CI.

These are not prose checks (that is the skill's own verify.py). They assert that
the repository stays installable: the Agent Skills frontmatter is legal, every
JSON manifest parses, the declared names agree everywhere, and the paths the
docs promise actually exist.

    python3 .github/checks.py
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "chicago-style-writing"
SKILL = SKILL_DIR / "SKILL.md"

failures = []


def check(ok, label):
    print(("PASS  " if ok else "FAIL  ") + label)
    if not ok:
        failures.append(label)


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    fields = {}
    key = None
    for line in m.group(1).split("\n"):
        if re.match(r"^[a-z-]+:", line):
            key, _, value = line.partition(":")
            fields[key] = value.strip()
        elif key and line.startswith(("  ", "\t")) and ":" in line:
            sub, _, value = line.strip().partition(":")
            fields.setdefault(f"{key}.{sub}", value.strip())
    return fields


def main():
    # --- Agent Skills frontmatter -------------------------------------------
    text = SKILL.read_text(encoding="utf-8")
    fm = frontmatter(text)
    name = fm.get("name", "")
    desc = fm.get("description", "")

    check(SKILL.exists(), "skills/chicago-style-writing/SKILL.md exists")
    check(bool(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name)) and len(name) <= 64,
          f"name is lowercase-hyphenated and <= 64 chars ({name!r})")
    check(name == SKILL_DIR.name,
          f"name matches its directory ({name!r} == {SKILL_DIR.name!r})")
    check(0 < len(desc) <= 1024, f"description is 1-1024 chars ({len(desc)})")
    check(len(fm.get("compatibility", "")) <= 500, "compatibility is <= 500 chars")
    check(fm.get("compatibility", "x") != "", "compatibility is present for the record")
    check(len(text) < 60_000, f"SKILL.md stays loadable ({len(text)} bytes)")

    # --- Every path SKILL.md promises must exist ----------------------------
    referenced = {m.group(0).rstrip(".,)") for m in re.finditer(
        r"(?<![`\w])(?:references|scripts|tests)/[A-Za-z0-9_.*-]+", text)}
    missing = sorted(p for p in referenced
                     if "*" not in p and not (SKILL_DIR / p).exists())
    check(bool(referenced) and not missing,
          f"every path SKILL.md references exists ({len(referenced)} checked)"
          + (f" (missing: {missing})" if missing else ""))

    # --- JSON manifests -----------------------------------------------------
    for rel in (".claude-plugin/marketplace.json", ".claude-plugin/plugin.json",
                "package.json"):
        path = ROOT / rel
        try:
            json.loads(path.read_text(encoding="utf-8"))
            ok = True
        except Exception as exc:  # noqa: BLE001 - report any parse failure
            ok = False
            print(f"      {rel}: {exc}")
        check(ok, f"{rel} parses as JSON")

    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))

    # A marketplace entry name must equal the plugin's manifest name, and the
    # skill name should agree too, or installs pick up the wrong identifier.
    entries = market.get("plugins", [])
    check(len(entries) == 1, "marketplace lists exactly one plugin")
    entry = entries[0] if entries else {}
    check(entry.get("name") == plugin.get("name") == name,
          "plugin entry name == plugin.json name == skill name")
    check(entry.get("source") in (".", "./"),
          f"plugin source is the repo root ({entry.get('source')!r})")
    check(market.get("owner", {}).get("name") is not None, "marketplace declares an owner")

    # --- pi package ---------------------------------------------------------
    check("pi-package" in pkg.get("keywords", []), "package.json carries the pi-package keyword")
    check(pkg.get("pi", {}).get("skills") == ["./skills"],
          "package.json declares pi.skills = ['./skills']")
    check(pkg.get("version") == plugin.get("version"),
          "package.json and plugin.json versions agree")

    # --- Repository hygiene -------------------------------------------------
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
    check("assets/" in ignored, ".gitignore excludes the source PDF directory")
    for rel in ("LICENSE", "README.md"):
        check((ROOT / rel).exists(), f"{rel} exists")

    # The manual itself must never be committed.
    try:
        tracked = subprocess.run(
            ["git", "ls-files", "--", "*.pdf"], cwd=ROOT,
            capture_output=True, text=True, timeout=30).stdout.split()
    except (OSError, subprocess.SubprocessError):
        tracked = []  # not a git checkout (e.g. a tarball); nothing to enforce
    check(not tracked, f"no PDFs are tracked by git ({tracked})")

    print()
    if failures:
        print(f"{len(failures)} packaging check(s) failed")
        return 1
    print("all packaging checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
