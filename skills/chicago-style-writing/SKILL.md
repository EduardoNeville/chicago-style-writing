---
name: chicago-style-writing
description: Draft, revise, copyedit, and audit English prose to The Chicago Manual of Style, 18th edition (2024), and strip AI slop from any text you ship an essay, a README, a frontend string, or on-screen video copy. Covers sentence clarity and concision, the slop patterns that make generated prose sound generic, punctuation, hyphenation and compounds, numbers, abbreviations, capitalization and titles of works, quotations and dialogue, and CMOS notes-bibliography or author-date citations. Use when writing or editing any prose, when proofreading or style-checking a draft, when asked “is this Chicago style?”, when asked whether writing reads as AI, or when a document or a product’s text must conform to CMOS.
license: MIT. Rules are described from The Chicago Manual of Style, 18th ed. (2024); the manual itself is copyrighted and is not redistributed here.
compatibility: Requires Python 3.8+ for scripts/cmos_lint.py and tests/verify.py. No network, no dependencies, no API key. Runs anywhere; installable with gh skill install, npx skills add, or as a Claude Code plugin.
metadata:
  author: Eduardo Neville
  version: "1.1.0"
  repository: https://github.com/EduardoNeville/chicago-style-writing
  source: The Chicago Manual of Style, 18th edition (2024)
  rules: "63 checks, each tied to a CMOS rule number or marked house"
---

# Chicago style writing

You are writing or editing prose to Chicago. Every claim in this skill carries a
CMOS 18th-edition rule number, or the label `house` when this skill deliberately
departs from the manual, so you can defend a change, check it, or knowingly
override it. `references/` holds the detail; `scripts/cmos_lint.py` checks the
mechanical half mechanically.

Rule numbers are the manual’s own (6.19 = serial comma, 9.2 = spell out one
through one hundred). Cite them when you explain an edit and when you disagree
with one.

## The doctrine

These are the manual’s own commitments, not decoration. Read them before editing.

1. **Rules serve the average case and bend to the case in hand.**
   > “They are meant for the average case, and must be applied with a certain degree of elasticity.”
   Epigraph to the Preface, quoting the first edition (1906).

2. **A light hand beats a heavy one.**
   > “A light editorial hand is nearly always more effective than a heavy one, and a flexible approach is usually better than a prescriptive one for anything beyond the correction of outright errors and inconsistencies.” (2.57)

3. **Respect the writer’s voice, and never enforce a rule mindlessly.**
   > “an editor should never mindlessly enforce ‘the rules’ without accounting for an author’s style, the viewpoint of the narrator and any other voices in the manuscript . . . and the conventions of the discipline or genre” . . . “an author’s style should be respected, whether it is baroque or minimalist.” (2.57)

4. **Consistency is a means, not an end.** Pick one form and hold it (2.8, 2.61);
   let the choice be governed by the reader, not by a preference (1.126, 6.16).

5. **Clarity outranks compliance.**
   > “The role of punctuation . . . is to promote ease of reading by clarifying relationships within and between sentences.” (6.1)
   When a rule and a clear sentence collide, reword the sentence (6.19, 6.27, 6.86).

6. **Write for the reader who arrives without context.** A heading must survive
   being lifted out of the page (1.61, 1.13); a table or chart must “make sense on
   its own terms” (3.42, 3.48); an abstract must stand alone (1.102).

7. **Good style is invisible.** “the substantive contribution of each article stands
   out more sharply when typographical distractions are at a minimum” (1.126).

8. **Usage is evidence, and a dictionary records rather than licenses.**
   > “The mere presence of a word in the dictionary’s pages does not mean that the word is in all respects fit for print as Standard Written English.” (5.254)

9. **Correct the error, not the register.** Formal prose, conversation, fiction, and
   legal drafting are held to different rules (6.1, 12.51, 2.57).

## Two phases: compose, then verify

**Compose.** The rules act as prohibitions while you write. Do not produce a banned
word, an em dash, a binary contrast, a colon reveal, or a fragment stack. Compose
the whole piece before checking any of it: nothing exists to lint yet, and every
rule obeyed here costs nothing.

**Verify.** The text exists, so the whole piece is checked at once: run the linter,
then work `EVAL.md`. Never interleave the phases. Editing paragraph by paragraph
hides the defects that appear only across a document: repeated sentence shapes, a
recap ending, numeral drift between sections.

**Audit.** A read-only third job. Name each pattern, quote the line, give the fix in
a few words. Do not rewrite, do not score, and do not guess whether AI wrote the
text. Detectors guess; a named pattern is evidence the reader can check.

## Text that lives in another artifact

Much of the text this skill touches does not live in a document. It lives in a JSON
script, a scene file, a component, or a translation table, and something expensive
consumes it: speech synthesis, a render, a deploy. Three laws keep it verifiable.

1. **Lint the source of truth, never generated output.** Built HTML, bundled JS, and
   rendered frames are artifacts. The file a human edits is the source.
2. **Words live in one declared file per register, before layout.** If they are
   scattered through markup, extract them once; the extraction becomes the source
   and the code reads from it. Text that lives only in a template cannot be linted,
   and it drifts.
3. **Freeze the words before the artifact consumes them,** and prove it with a hash.

Name the register and lint with it: `--register prose` (the default), `spoken`,
`display`, or `ui`. A register switches off the mechanical rules that do not apply
to it. It never switches off a slop rule. `references/25-artifacts.md` holds the
register table, the inventory contract, and a worked video example.

## Procedure

Work the passes **in this order**. Skipping ahead is the standard failure: you
polish commas in sentences whose modifiers dangle.

### Pass 0: Fix the brief

Ask, or infer from the document, and write the answers down:

- **Register and genre**: prose, spoken, display, or ui; then academic, trade,
  fiction, journalism, legal, or internal memo.
- **Which file owns the words.** If they are scattered through markup, extract
  first (see *Text that lives in another artifact*).
- **Voice traits to preserve**: vocabulary, cadence, bluntness, humor, uncertainty,
  digressions, level of polish. Name them before touching a sentence (2.57).
- **Citation system**: notes-bibliography (humanities) or author-date (sciences), or
  none. Never mix them (13.2, 13.4).
- **Which rules are genuinely two-way.** Several CMOS rules are a choice, not a duty:
  numerals threshold (`one hundred` style 9.2 vs `nine` style 9.3), title case vs
  sentence case for headings (8.159–8.160), serial comma (6.19; Chicago requires
  it, a house style may not), em dash spacing (6.91, overridden here). Record the
  choice.
- **Any house overrides** that beat this skill.

Output of this pass: a **style sheet** (see *Style sheet* below). Keep it current;
it is the one artifact that stops the same inconsistency reappearing five times.

### Pass 1: Structure

Level of edit: developmental (2.53). Do not touch sentences yet.

- Headings: short, descriptive, **parallel in structure and tone** across a level (1.61).
- Never let the first sentence under a heading point back at it with a pronoun:
  write `SECONDARY SPONGIOSA / The secondary spongiosa, a vaulted structure. . .`,
  not `. . . / This vaulted structure. . .` (1.61). *This is the single most common
  structural defect in drafted prose.*
- Use the fewest levels that work; almost nothing needs more than three (1.62).
  Never leave a single subhead with no sibling (1.62).
- Do not number headings unless something cross-references them (1.63).
- A paragraph does one job; a section earns its heading.
- Abstract or summary, if any: self-contained, one paragraph, no citations, no
  “see below” (2.29, 1.102).
- Front matter, back matter, appendix, notes, bibliography in the canonical order (1.4, 1.65–1.73).
- **Formatting slop**: emoji in headings, bold sprinkled mid-sentence for emphasis,
  bullets where two sentences of prose would read better, a header over a
  two-sentence section. Format follows the content.

Detail: `references/90-structure.md`.

### Pass 2: Sentence

Level of edit: line (2.53). Run the grammar diagnostics **in this fixed order**;
each later check is invalid while an earlier one fails.

1. **Agreement**: the subject governs the verb and the pronoun, not the nearest
   noun (5.143, 5.147, 5.192). Watch `as well as`, `along with`, `a number of`,
   and `one of those who work` (5.66, 5.145, 5.147).
2. **Modifier attachment**: every sentence-initial participle or infinitive must be
   performed by the main clause’s subject (5.113, 5.119, 5.120). Recast; do not
   patch. `Reviewing the suggestions, it is clear that. . .` has no reviewer.
3. **Parallelism**: every element of a series is the same grammatical function
   (5.249); repeat a preposition when the series mixes prepositions (5.250); put
   correlatives immediately before what they join (5.251); one auxiliary may not
   govern verb phrases that need another (5.252).
4. **Pronouns and antecedents**: one unambiguous antecedent, adjacent to the
   relative pronoun (5.31, 5.63, 5.64); case in compounds (`for you and me`, 5.40).
5. **Comparisons**: complete both terms; `than I` and `than me` say different
   things, so don’t leave it elliptical (5.49). A superlative needs three (5.90).
6. **Clause attachment and `that`**: restore a dropped `that` wherever the clause
   boundary could be misread (5.212, 5.233).
7. **Voice and concision**: active unless the actor is unknown or irrelevant (5.122);
   delete nominalizations and their `of`-phrases (5.195); one preposition per 10–15
   words is a good ratio (5.193).

Then the **slop shapes**. Each is a named pattern, each is an error, and each
outranks any permission the manual gives for the same move (see *House overrides*).

- **Binary contrast**: `It is not a process problem. It is a tooling problem.` State
  the affirmative.
- **Negative listing**: `Not a feature. Not a workflow.` Say what it is.
- **Colon reveal**: `The best part: it learns.` Write it as a sentence.
- **Throat-clearing**: `It is worth noting that`, `Here’s the thing`, `When it
  comes to`. Cut the run-up and state the point.
- **Faux-insight setup**: `What nobody tells you is`. Make the claim stand alone.
- **Rhetorical setup**: `Think about it:`, `What if I told you`. Drop it.
- **Trailing `-ing` analysis**: `adds search, highlighting the team’s commitment`.
  Say what it does for the reader.
- **Fragment stack**: three short fragments in a row, as in `That’s it. That is it.
  Done.` Write sentences. A label is not a fragment (see *Do not flag these*).
- **Robotic rhythm**: repeated sentence shapes, identical paragraph structures,
  stacked punchy fragments with no sentence between them.

Detail: `references/15-rhetoric.md`, `references/10-prose.md`.

### Pass 3: Word

Level of edit: line/copyedit.

- Check each contested word against the usage entry (`references/10-prose.md`, the
  A-Z under 5.254). Do not defend a misuse with a dictionary listing (5.254).
- Strip inflation: `use` not `utilize`, `affect` not `impact`, `because` not
  `due to the fact that`, `about` not `with regard to` (5.180, 5.254).
- **Banned words**, all errors: the full list is in `references/15-rhetoric.md`.
  The usual suspects are `leverage`, `robust`, `delve`, `foster`, and
  `streamline`. The manual does not license any of them.
- **Empty adverbs**, all errors: eleven of them, listed in
  `references/15-rhetoric.md`. `just before` and `simply put` are not intensifiers
  and are allowed.
- **Make verbs do the work**: `decided` for `made a decision`; `can` for
  `has the ability to`; `helps` for `provides assistance`.
- **The portability test**: if a sentence could move unchanged to another person,
  company, or country, it is filler. Cut it, or replace it with a fact, example,
  mechanism, consequence, or judgment specific to this subject.
- **Protect the specific fact**: `significantly improves productivity` becomes `cut
  review time from 30 minutes to 8`.
- **Synonym cycling**: repeat the clear word. Do not rotate agent, assistant, and
  tool for variety.
- Register: contractions are good (5.109); legalese, compound adverbs, and
  nominalizations are not (5.166, 5.195, 5.254).
- Inclusive language: reason case by case (5.255–66). Chip does not maintain
  a banned-word list (5.257); that is the point.
- Singular *they* is Chicago style. Do not edit it out, do not rewrite to
  `he or she`, and keep the plural verb (5.51, 5.52, 5.266).

### Pass 4: Mechanics

Level of edit: copyedit. Run in the manual’s own cleanup order (2.85), because each
step makes the next one cheaper.

1. Spaces: one between sentences, one after a colon, none before punctuation (2.11, 6.7, 6.66).
2. Straight quotes and apostrophes to directional (6.123, 6.125). `’90s`, `’em`, `rock ’n’ roll`.
3. Punctuation relative to closing quotation marks and parentheses (6.9, 6.10, Table 6.1).
4. Dashes and ellipses regularized: no em dash ever (house override of 6.91); no
   spaced hyphen; ellipsis points spaced (12.59).
5. Numeric ranges use an en dash; never `from 2019–22` or `between 3–5` (6.83, 9.62).
6. Abbreviations: no periods in two-plus-capital forms, `e.g.,` and `i.e.,` with a comma (10.4, 5.254).
7. Numerals: threshold and subsequent consistency (9.2–9.7); no sentence-initial numeral (9.5).
8. Compounds and hyphenation: open by default, hyphenate a modifier before its noun (7.91, 7.96).
9. Capitalization and titles (8.160–8.164).

Detail: `references/20-punctuation.md`, `30-spelling-hyphenation.md`,
`40-names-titles.md`, `50-numbers.md`, `60-abbreviations.md`.

### Pass 5: Evidence

- **Quotation fidelity.** Change only the wrapper: quotation marks, dash length,
  initial capitalization, terminal punctuation, note references, typography (12.7).
  Anything a reader could mistake for the source’s words must be disclosed.
- **Weasel attribution.** `Experts agree`, `studies show`, `widely regarded as`, and
  `many argue` name nobody. Name the source or cut the claim. If the writer has no
  source, query it instead of inventing one.
- Ellipses must not create a statement alien to the original (12.60). Brackets, not
  parentheses, for clarification (12.71). `sic` only for errors a reader would blame
  on the transcriber (12.72). Added emphasis must be labelled (12.73).
- **Citations.** One system throughout; notes use commas, bibliographies use periods
  (13.18, 13.102); no `ibid.`, use a short form (13.37); invert only the first
  author, and only in the list (13.22, 13.77).
- **Cross-check** against the brief’s own inventory: quotations vs. sources,
  in-text citations vs. reference list, headings vs. contents, figures vs. captions (2.37–2.39).

Detail: `references/70-quotations-language.md`, `references/80-citations.md`.

### Pass 6: Verify and report

Run the linter and resolve every finding:

```bash
python3 scripts/cmos_lint.py draft.md            # human report
python3 scripts/cmos_lint.py --errors-only -     # CI gate
python3 scripts/cmos_lint.py --register spoken narration.md
```

For each `error`: fix it, or state why the rule does not apply here (a rule number
or `house`, plus a reason: quoted matter, code, a house override, a deliberate
nonstandard form in dialogue). For each `hint`: read the sentence, then keep or
change. Hints are never auto-applied (2.57).

Then check the judgment half against `EVAL.md`: recap endings, the fake-profound
kicker, robotic rhythm, synonym cycling, metadiscourse, the portability test. If a
check fails, fix the draft and run both halves again.

Report in proportion: a document gets the four-part shape below, a paragraph or a
button label gets three lines. Always return the full edited text.

1. **What I changed**, grouped by pass, each item citing its rule number or `house`.
2. **Style sheet**: the decisions made, so the next editor does not re-litigate them.
3. **Queries**: things only the author can settle, phrased as `OK?` or
   `Do you mean X or Y?` (2.75).
4. **Verification**: linter counts before and after, and the command to reproduce.

## Do not flag these

Most damage done by an over-eager style agent is here. Each of these is *correct*
Chicago and must survive a cleanup pass:

| Do not “fix” | Because |
| Sentence-initial *And*, *But*, *So* | “no historical or grammatical foundation” for the prohibition; common in first-rate prose (5.209) |
| A split infinitive (`to boldly go`) | permitted, and sometimes necessary to keep the emphasis (5.112, 5.176) |
| A preposition at the end of a sentence | “an unnecessary and pedantic restriction. And it is wrong.” (5.186) |
| Singular *they*, including for a known person | Chicago “now endorses it” (5.51, 5.52, 5.266) |
| An adverb between auxiliary and verb (`has consistently repudiated`) | “There has never been a rule against such placement” (5.176) |
| *However* opening a sentence | grammatical; it is ponderous, not wrong (5.210) |
| *data* / *media* with a singular verb outside the sciences | accepted mass-noun use (5.16) |
| *hopefully* as a sentence adverb, *none is*/*none are*, *over* for *more than* | all established (5.254) |
| Contractions, *I*, second person, one-sentence paragraphs | register choices, not errors (5.109) |
| A semicolon in fiction-free prose | correct and useful (6.60) |
| A label, title card, or button string that reads as a fragment | a label was never a sentence, so no fragment is present; check the register |
| `which` in a restrictive clause after a preposition | required there (`the situation in which we find ourselves`, 6.29) |
| A passive sentence whose actor is unknown or irrelevant | passive is “often inferior”, not always (5.122) |
| A numeral in a title, a table, a date, or a grade | numerals are required there (9.8) |

Also do not:
- Rewrite quoted matter. Query it instead (2.67).
- Impose a citation style on an existing one that is already consistent and clear (2.70).
- “Correct” a spelling you cannot verify. Look it up at Merriam-Webster.com (7.1).
- Fix a typo you suspect is in the source. That is what `sic` is for (12.72).
- Change anything at proof stage beyond “the correction of fact or of gross
  syntactical error” (2.123).

## House overrides

This skill departs from the manual in three places. The linter cites them as
`house`, so `grep house` on its rule table lists every departure, and a reader can
tell a deliberate choice from a mistake.

| Overridden | What the manual says | What this skill does |
| **6.91** | the em dash is permitted, and called the most versatile mark in the repertoire | never used; a colon, a comma, or parentheses instead |
| **2.57** | a deliberate fragment for effect is licensed | a stack of three or more short fragments is an error; a label is not a fragment |
| **6.65, 6.67** | a colon may introduce an emphatic clause, lowercased when what follows is not a complete sentence | that reveal is an error; write the sentence |

Precedence, in order: a slop rule outranks a CMOS permission; a CMOS rule outranks
a style preference; the writer’s voice governs the edit, never the finding. Voice
cannot excuse a slop pattern, and it can forbid flattening prose where no pattern
is present.

`references/` reproduces the manual’s own examples, so those files keep the em
dashes the manual uses. The ban applies to text this skill writes (2.67, quoted
matter).

## Style sheet

Produce this and keep it with the document (2.61). It is what makes a long project
consistent, and it is the artifact that proves the work was done deliberately.

```markdown
# Style sheet — <document>
Chicago 18th ed., with these decisions:
- Register: prose | spoken | display | ui
- Numerals: spell out one through one hundred (9.2)
- Headings: sentence case (8.159), max three levels
- Serial comma: always (6.19)
- Dash: none (house); ellipsis: spaced points (12.59)
- Citations: notes-bibliography (13.2)
- Words: co-citizen, ghetto-like, Métis, Third World, macOS, web page
- "emphasis mine" in quotations that carry added italics (12.73)
- Anything else: Chicago 18th edition governs.
```

## Rule map

| Need | File |
| Procedure, style sheet, proofreading, levels of edit | `references/10-prose.md` (ch 2 sections) |
| Grammar, syntax, word usage A-Z, inclusive language | `references/10-prose.md` |
| Slop patterns, words to cut, portability test | `references/15-rhetoric.md` |
| Registers, text inventories, gates for other artifacts | `references/25-artifacts.md` |
| Commas, dashes, quotation marks, colons, lists | `references/20-punctuation.md` |
| Plurals, possessives, italics, compounds, hyphenation | `references/30-spelling-hyphenation.md` |
| Capitalization, names, titles of works, title case | `references/40-names-titles.md` |
| Numerals, dates, ranges, percent, money, roman numerals | `references/50-numbers.md` |
| Abbreviations, initials, `e.g.`, `p.m.`, `PhD` | `references/60-abbreviations.md` |
| Quotations, dialogue, ellipses, foreign languages | `references/70-quotations-language.md` |
| Notes, bibliographies, author-date, DOIs | `references/80-citations.md` |
| Book structure, headings, captions, tables, alt text | `references/90-structure.md` |
| Permissions, fair use, indexes, glossary of terms | `references/95-rights-and-index.md` |
| The judgment half of verification | `EVAL.md` |
| Mechanical check | `scripts/cmos_lint.py` |

Start with the `## Apply these first` block at the top of any reference file: it is
the ranked short list; the rest is the evidence.

## Verifying the skill itself

```bash
python3 tests/verify.py     # asserts the linter catches what it claims
```

It checks that all 63 documented rules fire on a deliberately bad fixture, that a
Chicago-conformant and slop-free fixture produces zero findings, that code spans,
fenced blocks, and URLs are never flagged, that each register is clean on its own
fixture while the prose register still flags it, that slop fires in every register,
that no slop rule is a hint, that the worked examples (mechanics and slop) go from
many findings to zero, and that the documented CLI contracts (exit codes,
`--errors-only`, `--register`, stdin) hold.
