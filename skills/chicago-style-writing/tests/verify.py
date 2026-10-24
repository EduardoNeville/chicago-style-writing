#!/usr/bin/env python3
"""Verify that cmos_lint catches what the skill claims it catches.

Four assertions:
  1. every rule listed in REQUIRED fires on tests/bad.md;
  2. tests/bad.md fires no rule outside KNOWN;
  3. tests/good.md (Chicago-conformant prose) produces zero findings;
  4. text inside code spans, fenced blocks, and URLs is never linted.

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
DASH.DOUBLE_HYPHEN DASH.SPACED_HYPHEN DASH.EM_SPACED DASH.EM_OVERUSE
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
PROSE.DANGLER PROSE.LONG_SENTENCE PROSE.OF_CHAIN PROSE.UTILIZE PROSE.AN
TITLE.SHORT_WORD_CAPPED TITLE.LONG_PREP_LOWER
""".split()


def run(*args):
    p = subprocess.run([sys.executable, str(LINT), *args],
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def findings(*args):
    code, out, err = run("--json", *args)
    if code == 2:
        sys.exit(f"lint failed: {err}")
    return code, json.loads(out)


def known_rules():
    src = (ROOT / "scripts" / "cmos_lint.py").read_text(encoding="utf-8")
    table = set(re.findall(r'R\("([A-Z][A-Z0-9_.]+)"', src))
    # Rules contributed by the structural checkers rather than the regex table.
    structural = {"DASH.EM_OVERUSE", "PROSE.LONG_SENTENCE", "PROSE.OF_CHAIN",
                  "PROSE.AN", "TITLE.SHORT_WORD_CAPPED", "TITLE.LONG_PREP_LOWER"}
    return table | structural


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

    # 3. The good fixture: zero findings of any severity.
    code, good = findings(str(TESTS / "good.md"))
    detail = "" if good["errors"] + good["hints"] == 0 else \
        " -> " + "; ".join(f"{f['rule']}@{f['line']}" for f in good["findings"])
    check(good["errors"] == 0 and good["hints"] == 0,
          "Chicago-conformant prose produces zero findings" + detail)
    check(code == 0, "exit status 0 on clean prose")

    # 4. Masking: nothing inside code or URLs is linted.
    code, masked = findings(str(TESTS / "masked.md"))
    check(not masked["findings"],
          "code spans, fenced blocks, and URLs are skipped"
          + ("" if not masked["findings"] else
             " -> " + str(sorted({f["rule"] for f in masked["findings"]}))))

    # 5. End-to-end: the worked example in tests/. Following the skill's passes
    #    takes a sloppy paragraph from many findings to none.
    _, before = findings(str(TESTS / "demo-before.md"))
    _, after = findings(str(TESTS / "demo-after.md"))
    check(before["errors"] >= 10 and after["errors"] == 0 and after["hints"] == 0,
          f"worked example: {before['errors']} errors + {before['hints']} hints "
          f"-> {after['errors']} + {after['hints']}")

    # 6. The CLI contracts the skill documents.
    code, out, _ = run("--errors-only", str(TESTS / "bad.md"))
    check("HINT" not in out, "--errors-only suppresses hints")
    p = subprocess.run([sys.executable, str(LINT), "-"],
                       input="The report was late.  It arrived.\n",
                       capture_output=True, text=True)
    check(p.returncode == 1 and "SPACE.SENTENCE" in p.stdout, "reads stdin via -")

    print()
    if failures:
        print(f"{len(failures)} check(s) failed")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
