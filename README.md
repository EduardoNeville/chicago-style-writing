# chicago-style-writing

An agent skill for writing, editing, and auditing English prose to **The Chicago
Manual of Style, 18th edition (2024)**, and for keeping AI slop out of any text an
agent ships: essays, documentation, frontend strings, on-screen video copy. Ships a
deterministic linter, so conformance is checkable rather than asserted.

Works in pi, Claude Code, Codex, Cursor, Copilot, Gemini CLI, OpenCode, and any
other agent that reads the [Agent Skills](https://agentskills.io/specification)
format. One skill directory, plain Markdown, one stdlib-only Python script.
No package manager, no network, no API key.

## Install

`gh` builds the skill straight into whichever agents you name:

```bash
# pi
gh skill install EduardoNeville/chicago-style-writing chicago-style-writing --agent pi --scope user

# Claude Code, Codex, Cursor, Copilot, Gemini CLI. Pick one or repeat
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
pi install git:github.com/EduardoNeville/chicago-style-writing@v1.1.0
```

Or copy it yourself. The directory is self-contained:

```bash
git clone https://github.com/EduardoNeville/chicago-style-writing
cp -r chicago-style-writing/skills/chicago-style-writing ~/.agents/skills/
```

Pin a version with `@v1.1.0` (tag) or `--pin <sha>`.

## Use

Ask your agent to write, revise, copyedit, or audit something, or invoke the skill
directly (`/chicago-style-writing`). It loads on demand, so it costs nothing until
you need it.

The skill runs in three hats: **compose** (draft with the rules as prohibitions),
**verify** (check the whole piece at once), and **audit** (name the patterns, quote
the lines, no rewrite). Compose first, verify once, never interleave: paragraph by
paragraph editing hides the defects that only show across a document.

By hand:

```bash
python3 skills/chicago-style-writing/scripts/cmos_lint.py draft.md
python3 skills/chicago-style-writing/scripts/cmos_lint.py --errors-only -   # CI gate
python3 skills/chicago-style-writing/scripts/cmos_lint.py --json draft.md   # machine-readable
python3 skills/chicago-style-writing/scripts/cmos_lint.py --register spoken narration.md
```

Every finding names its source: a CMOS rule number, or `house` for a rule where the
skill deliberately overrides the manual. `error` is must-not-ship, either a
mechanical rule of the manual or a house rule; `hint` is a judgment call the manual
only describes, so it is never applied blindly:

```
draft.md:14:9   ERROR SLOP.EM_DASH [house]  em dashes are banned (house override of 6.91)
draft.md:14:42  HINT  PROSE.NOMINALIZATION [5.195]  turn the hidden verb back into a verb
    > utilization of
```

`--register` names who reads the text. `prose` is the default. `spoken` (narration
read aloud), `display` (title cards, kickers, footers), and `ui` (buttons, errors,
empty states) each switch off the mechanical rule families that do not apply to
them. A register never switches off a slop rule.

## What you get

- **`SKILL.md`**: the manual’s own doctrine on editing (a light hand, respect the
  writer’s voice, clarity outranks compliance), the two phases, six passes in a
  fixed order (brief, structure, sentence, word, mechanics, evidence), the house
  overrides, and the **do-not-flag list**: sentence-initial *And*, split
  infinitives, terminal prepositions, singular *they*, and the other things a style
  robot breaks.
- **`references/`**: 1 MB of rule-by-rule detail for every chapter of the manual,
  each claim carrying its rule number, plus two files this skill adds. The rhetoric
  file names the slop patterns and the words to cut; the artifacts file covers
  registers, text inventories, and gating text that lives inside a build.
- **`EVAL.md`**: the judgment half of verification. Seventeen pass-or-fail
  questions covering what a regex cannot check, including whether the text still
  sounds like its writer.
- **`scripts/cmos_lint.py`**: 63 checks across punctuation, hyphens and compounds,
  numbers, abbreviations, capitalization, titles, usage, concision, and slop. It
  skips code spans, fenced blocks, and URLs, and it never flags quoted matter.
- **`tests/`**: fixtures and a verifier you can run yourself, including one fixture
  per register and a slop paragraph that goes from eleven errors to zero.

## Verify it

```bash
python3 skills/chicago-style-writing/tests/verify.py
```

```
PASS  all 63 required rules fire on bad.md
PASS  no rule fires on bad.md outside the documented set
PASS  `Chicago-conformant, slop-free prose produces zero findings
PASS  code spans, fenced blocks, and URLs are skipped
PASS  spoken register is clean on spoken.md (6 errors as prose)
PASS  display register is clean on display.md (1 errors as prose)
PASS  ui register is clean on ui.md (1 errors as prose)
PASS  slop fires in every register on slop-before.md
PASS  all 15 slop rules are errors
PASS  --errors-only suppresses hints
PASS  --register rejects an unknown name
PASS  worked example: 11 slop errors -> 0 + 0
PASS  mechanics example: 13 errors + 6 hints -> 0 + 0
all checks passed
```

CI runs that on three Python versions, checks the packaging, validates the
manifests, installs the skill the way a user would, and lints this README and
`SKILL.md` with `--errors-only`, which means this repository’s own prose has to pass
the slop rules it documents.

## Layout

```
SKILL.md · skills/chicago-style-writing/
├── SKILL.md                          doctrine, two phases, six passes, house overrides, style sheet
├── EVAL.md                           the judgment half of verification
├── references/10-prose.md            ch 2 editing process + ch 5 grammar, syntax, usage A-Z
├── references/15-rhetoric.md        slop patterns, words to cut, portability test
├── references/25-artifacts.md       registers, text inventories, gates for other artifacts
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

- **Where the skill departs from the manual, it says so.** Three overrides are
  recorded in `SKILL.md` and cited as `house` by the linter: no em dashes ever
  (6.91 permits them), no stacks of dramatic fragments (2.57 licenses them), and no
  colon reveal (6.65 and 6.67 permit it). A slop rule outranks a CMOS permission; a
  CMOS rule outranks a style preference. If a `house` rule is wrong for your
  document, that is what the written justification in a report is for.
- **Prose-level slop is not all mechanically checkable.** The linter cannot see a
  fake-profound kicker, synonym cycling, robotic rhythm, or whether a sentence could
  travel unchanged to another company. Those live in `EVAL.md`, and they depend on
  the agent’s own answers.
- A wrong `error` forces an edit to correct prose, so every slop rule ships with a
  fixture that must stay quiet. `SLOP.EMPTY_ADVERB` is the narrowest: `just before`
  and `simply put` are not intensifiers, and the rule knows it.
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
Manual of Style*, 18th ed., © 2024 by The University of Chicago. The slop patterns
are adapted from the `no-ai-slop` skill by Peter Yang, MIT. This project is
independent and not affiliated with or endorsed by the University of Chicago
Press. See [LICENSE](LICENSE).
