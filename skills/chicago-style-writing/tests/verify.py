#!/usr/bin/env python3
"""Verify that cmos_lint catches what the skill claims it catches.

Six assertions:
  1. every rule listed in REQUIRED fires on tests/bad.md;
  2. tests/bad.md fires no rule outside the documented set;
  3. tests/good.md (Chicago-conformant, slop-free prose) produces zero findings;
  4. text inside code spans, fenced blocks, and URLs is never linted;
  5. each register silences its own false positives but never a slop rule;
  6. no slop rule is a hint, and the CLI contracts in the docs still hold.

Run: python3 tests/verify.py
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINT = ROOT / "scripts" / "cmos_lint.py"
TESTS = ROOT / "tests"

# Rules that must fire on the bad fixture.
REQUIRED = """
SPACE.SENTENCE SPACE.BEFORE_PUNCT SPACE.COLON
QUOTE.STRAIGHT_DOUBLE QUOTE.STRAIGHT_APOSTROPHE
DASH.DOUBLE_HYPHEN DASH.SPACED_HYPHEN
ELLIPSIS.DOTS ELLIPSIS.DOUBLE_PERIOD
COLON.AFTER_VERB COMMA.SERIAL COMMA.JR_SR COMMA.CORPORATE COMMA.TOO_EITHER
RANGE.HYPHEN RANGE.FROM RANGE.BETWEEN
NUMBER.SENTENCE_START NUMBER.DATE_ORDINAL NUMBER.NUMERIC_DATE
NUMBER.DECADE_APOSTROPHE NUMBER.UNIT_SPACE NUMBER.ORDINAL_SUPERSCRIPT
NUMBER.PERCENT_SPACE NUMBER.NOON_MIDNIGHT NUMBER.AM_REDUNDANT
ABBR.PERIODS ABBR.EG_COMMA ABBR.AND_ETC ABBR.ETC_AFTER_EG
WORD.PREVENTATIVE WORD.NONSTANDARD WORD.COMPRISED_OF WORD.DIFFERENT_THAN
WORD.UNGRADABLE WORD.LEGALESE
HYPHEN.LY_ADVERB HYPHEN.PREDICATE_COMPOUND
PROSE.WORDY_PHRASE PROSE.NOMINALIZATION PROSE.EXPLETIVE PROSE.PASSIVE_AGENT
PROSE.DANGLER PROSE.LONG_SENTENCE PROSE.OF_CHAIN PROSE.AN
TITLE.SHORT_WORD_CAPPED TITLE.LONG_PREP_LOWER
SLOP.EM_DASH SLOP.BINARY_CONTRAST SLOP.NEGATIVE_LIST SLOP.THROAT_CLEARING
SLOP.FAUX_INSIGHT SLOP.COLON_REVEAL SLOP.ING_ANALYSIS SLOP.PUFFERY SLOP.WEASEL
SLOP.RHETORICAL_SETUP SLOP.RECAP_ENDING SLOP.FRAGMENT_STACK SLOP.BANNED_WORD
SLOP.EMPTY_ADVERB SLOP.WEAK_VERB
""".split()

# Registers whose own fixture must lint clean, and must not lint clean as prose:
# the flag has to do something.
REGISTERS = {
    "spoken": "spoken.md",
    "display": "display.md",
    "ui": "ui.md",
}


def run(*args):
    p = subprocess.run([sys.executable, str(LINT), *args],
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def findings(*args):
    code, out, err = run("--json", *args)
    if code == 2:
        sys.exit(f"lint failed: {err}")
    return code, json.loads(out)


def source():
    return (ROOT / "scripts" / "cmos_lint.py").read_text(encoding="utf-8")


def known_rules():
    table = set(re.findall(r'R\("([A-Z][A-Z0-9_.]+)"', source()))
    # Rules contributed by the structural checkers rather than the regex table.
    structural = {"PROSE.LONG_SENTENCE", "PROSE.OF_CHAIN",
                  "PROSE.AN", "TITLE.SHORT_WORD_CAPPED", "TITLE.LONG_PREP_LOWER",
                  "SLOP.FRAGMENT_STACK"}
    return table | structural


def slop_rules():
    """(rule, severity) for every SLOP rule, table or structural."""
    src = source()
    return re.findall(r'R\("(SLOP\.[A-Z_]+)",\s*"[^"]*",\s*"(\w+)"', src) + \
        re.findall(r'Finding\("(SLOP\.[A-Z_]+)",\s*"[^"]*",\s*"(\w+)"', src)


def total(n):
    return sum(1 for f in findings(str(TESTS / n))[1]["findings"])


def main():
    failures = []

    def check(ok, label):
        print(("PASS  " if ok else "FAIL  ") + label)
        if not ok:
            failures.append(label)

    # 1 + 2. The bad fixture.
    code, bad = findings(str(TESTS / "bad.md"))
    fired = {f["rule"] for f in bad["findings"]}
    missing = sorted(set(REQUIRED) - fired)
    unknown = sorted(fired - known_rules())
    check(not missing, f"all {len(REQUIRED)} required rules fire on bad.md"
                       + (f" (missing: {missing})" if missing else ""))
    check(not unknown, "no rule fires on bad.md outside the documented set"
                       + (f" (unexpected: {unknown})" if unknown else ""))
    check(code == 1, "exit status 1 when errors are present")
    check(bad["errors"] > 40, f"bad.md raises {bad['errors']} errors, {bad['hints']} hints")

    # 3. The good fixture: zero findings of any severity, in every register.
    code, good = findings(str(TESTS / "good.md"))
    detail = "" if good["errors"] + good["hints"] == 0 else \
        " -> " + "; ".join(f"{f['rule']}@{f['line']}" for f in good["findings"])
    check(good["errors"] == 0 and good["hints"] == 0,
          "Chicago-conformant, slop-free prose produces zero findings" + detail)
    check(code == 0, "exit status 0 on clean prose")

    # 4. Masking: nothing inside code or URLs is linted.
    code, masked = findings(str(TESTS / "masked.md"))
    check(not masked["findings"],
          "code spans, fenced blocks, and URLs are skipped"
          + ("" if not masked["findings"] else
             " -> " + str(sorted({f["rule"] for f in masked["findings"]}))))

    # 5. Registers. Each silences its own false positives; slop is never silenced.
    for register, fixture in REGISTERS.items():
        path = str(TESTS / fixture)
        _, own = findings("--register", register, path)
        prose_errors = findings(path)[1]["errors"]
        check(not own["findings"] and prose_errors > 0,
              f"{register} register is clean on {fixture} "
              f"({prose_errors} errors as prose)")
    for fixture in ("slop-before.md", "slop-display.md"):
        path = str(TESTS / fixture)
        errors = {r: findings("--register", r, path)[1]["errors"]
                  for r in ("prose",) + tuple(REGISTERS)}
        check(all(n > 0 for n in errors.values()),
              f"slop fires in every register on {fixture} {errors}")

    # 6. Slop is never a hint, and the documented CLI contracts hold.
    hints = [r for r, sev in slop_rules() if sev != "error"]
    check(bool(slop_rules()) and not hints,
          f"all {len(slop_rules())} slop rules are errors"
          + (f" (not: {hints})" if hints else ""))
    code, out, _ = run("--errors-only", str(TESTS / "bad.md"))
    check("HINT" not in out, "--errors-only suppresses hints")
    p = subprocess.run([sys.executable, str(LINT), "-"],
                       input="The report was late.  It arrived.\n",
                       capture_output=True, text=True)
    check(p.returncode == 1 and "SPACE.SENTENCE" in p.stdout, "reads stdin via -")
    _, _, err = run("--register", "hologram", str(TESTS / "good.md"))
    check(run("--register", "hologram", "-")[0] == 2, "--register rejects an unknown name")

    # 7. End to end: the documented passes take slop to zero.
    _, before = findings(str(TESTS / "slop-before.md"))
    _, after = findings(str(TESTS / "slop-after.md"))
    check(before["errors"] >= 10 and after["errors"] == 0 and after["hints"] == 0,
          f"worked example: {before['errors']} slop errors -> "
          f"{after['errors']} + {after['hints']}")

    # 8. The other worked example still holds: mechanics, not rhetoric.
    _, mech_before = findings(str(TESTS / "demo-before.md"))
    _, mech_after = findings(str(TESTS / "demo-after.md"))
    check(mech_before["errors"] >= 10 and mech_after["errors"] == 0
          and mech_after["hints"] == 0,
          f"mechanics example: {mech_before['errors']} errors + "
          f"{mech_before['hints']} hints -> {mech_after['errors']} + "
          f"{mech_after['hints']}")

    print()
    if failures:
        print(f"{len(failures)} check(s) failed")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
