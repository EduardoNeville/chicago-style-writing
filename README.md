# chicago-style-writing

An agent skill for writing and editing English prose to **The Chicago Manual of
Style, 18th edition (2024)** — with a deterministic linter, so conformance is
checkable rather than asserted.

Works in pi, Claude Code, Codex, Cursor, Copilot, Gemini CLI, OpenCode, and any
other agent that reads the [Agent Skills](https://agentskills.io/specification)
format. One skill directory, plain Markdown, one stdlib-only Python script.
No package manager, no network, no API key.

## Install

`gh` builds the skill straight into whichever agents you name:

```bash
# pi
gh skill install EduardoNeville/chicago-style-writing chicago-style-writing --agent pi --scope user

# Claude Code, Codex, Cursor, Copilot, Gemini CLI — pick one or repeat
gh skill install EduardoNeville/chicago-style-writing chicago-style-writing --agent claude-code --scope user
gh skill install EduardoNeville/chicago-style-writing chicago-style-writing --agent codex --scope user

# whatever is already on your PATH, into every detected agent
npx skills add EduardoNeville/chicago-style-writing
```

As a Claude Code plugin, from the marketplace in this repo:

```
/plugin install chicago-style-writing --marketplace EduardoNeville/chicago-style-writing
```

As a pi package:

```bash
pi install git:github.com/EduardoNeville/chicago-style-writing@v1.0.0
```

Or copy it yourself — the directory is self-contained:

```bash
git clone https://github.com/EduardoNeville/chicago-style-writing
cp -r chicago-style-writing/skills/chicago-style-writing ~/.agents/skills/
```

Pin a version with `@v1.0.0` (tag) or `--pin <sha>`.

## Use

Ask your agent to write, revise, copyedit, or style-check something, or invoke
the skill directly (`/chicago-style-writing`). It loads on demand, so it costs
nothing until you need it.

By hand:

```bash
python3 skills/chicago-style-writing/scripts/cmos_lint.py draft.md
python3 skills/chicago-style-writing/scripts/cmos_lint.py --errors-only -   # CI gate
python3 skills/chicago-style-writing/scripts/cmos_lint.py --json draft.md   # machine-readable
```

Every finding names its CMOS rule. `error` is a mechanical rule of the manual;
`hint` is a judgment call the manual only describes, so it is never applied
blindly:

```
draft.md:14:9   ERROR RANGE.HYPHEN [6.83, 9.62]  use an en dash for a range of numbers
draft.md:14:42  HINT  PROSE.NOMINALIZATION [5.195]  turn the hidden verb back into a verb
    > utilization of
```

## What you get

- **`SKILL.md`** — the manual’s own doctrine on editing (a light hand, respect
  the writer’s voice, clarity outranks compliance), then six passes in a fixed
  order: brief → structure → sentence → word → mechanics → evidence. Plus the
  **do-not-flag list**: sentence-initial *And*, split infinitives, terminal
  prepositions, singular *they*, and the other things a style robot breaks.
- **`references/`** — 1 MB of rule-by-rule detail for every chapter of the
  manual, each claim carrying its rule number. Every file opens with the ranked
  short list, followed by the evidence.
- **`scripts/cmos_lint.py`** — 51 checks across punctuation, hyphens and
  compounds, numbers, abbreviations, capitalization, titles, usage, and
  concision. Skips code spans, fenced blocks, and URLs.
- **`tests/`** — fixtures and a verifier you can run yourself.

## Verify it

```bash
python3 skills/chicago-style-writing/tests/verify.py
```

```
PASS  all 51 required rules fire on bad.md
PASS  no rule fires on bad.md outside the documented set
PASS  Chicago-conformant prose produces zero findings
PASS  code spans, fenced blocks, and URLs are skipped
PASS  worked example: 11 errors + 7 hints -> 0 + 0
PASS  --errors-only suppresses hints
PASS  reads stdin via -
all checks passed
```

CI runs that on three Python versions, checks the packaging, validates the
manifests, and installs the skill the way a user would.

## Layout

```
SKILL.md · skills/chicago-style-writing/
├── SKILL.md                          doctrine, six passes, do-not-flag list, style sheet
├── references/10-prose.md            ch 2 editing process + ch 5 grammar, syntax, usage A-Z
├── references/20-punctuation.md      ch 6
├── references/30-spelling-hyphenation.md   ch 7
├── references/40-names-titles.md     ch 8
├── references/50-numbers.md          ch 9
├── references/60-abbreviations.md    ch 10
├── references/70-quotations-language.md    ch 12, ch 11
├── references/80-citations.md        ch 13, ch 14
├── references/90-structure.md        ch 1, ch 3
├── references/95-rights-and-index.md ch 4, ch 15, glossary
├── scripts/cmos_lint.py              the checkable half
└── tests/                            fixtures + verify.py

.claude-plugin/                       Claude Code plugin and marketplace manifests
package.json                          pi package and npm metadata
.github/                              CI, plus the packaging checks it runs
```

## Limits you should know

- The reference files were derived from the text layer of a PDF of the 18th
  edition. **The linter’s rules were checked directly against the PDF text**;
  the prose summaries were assembled and summarised by machine, not verified
  line by line. For legal, contractual, or high-stakes publishing work, confirm
  the rule in the manual.
- CMOS rules are not law, and the manual says so: they “are meant for the
  average case, and must be applied with a certain degree of elasticity”
  (Preface, quoting the 1906 first edition). The skill encodes that.
- The manual itself is **not** included. Bring your own copy:
  <https://www.chicagomanualofstyle.org/>

## License

MIT for the skill text and the code. The rules described are from *The Chicago
Manual of Style*, 18th ed., © 2024 by The University of Chicago. This project is
independent and not affiliated with or endorsed by the University of Chicago
Press. See [LICENSE](LICENSE).
