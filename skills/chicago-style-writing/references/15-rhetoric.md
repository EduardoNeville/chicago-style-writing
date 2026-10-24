# Rhetoric: the slop patterns and the words to cut

Source: the named patterns are adapted from the `no-ai-slop` skill by Peter Yang
(MIT), rewritten for this skill's rule identifiers and its precedence rules. This
file is **not** The Chicago Manual of Style. These rules are `house`: the linter
cites them as `[house]`, and where they disagree with the manual they win (see
*House overrides* in SKILL.md).

Why they are errors and not preferences: a slop pattern is a shape that says
nothing while sounding like it said something. It survives proofreading because it
is grammatical, and it survives editing because it is the shape the writer reached
for in the first place. Naming it is the only way to remove it.

## Composing rule

Do not produce these shapes while drafting. The cheapest slop to remove is the slop
never written: no second pass, and no risk of the removal pass flattening the voice.
`EVAL.md` holds the questions that catch what the linter cannot.

## Patterns the linter catches

Each heading is the rule identifier a finding carries.

### `SLOP.EM_DASH`

The em dash is banned outright (house override of 6.91). Use a colon, a comma, or
parentheses. Two hyphens and spaced hyphens are not substitutes either. En dashes
stay: they mark ranges (6.83, 9.62).

### `SLOP.BINARY_CONTRAST`

`It is not a tooling problem. It is a process problem.` Also `not just X, but Y` and
`isn't about X, it's about Y`.

State the affirmative: `The problem is the process.` The negated setup buys rhythm
and spends meaning.

### `SLOP.NEGATIVE_LIST`

`Not a feature. Not a workflow.` Say what it is, once. Three negations in a row are
a drumbeat with no information.

### `SLOP.COLON_REVEAL`

`The best part: it learns.` Also `The catch:`, `The kicker:`, `The detail that makes
it work:`, `Here's the thing:`.

Write the sentence: `A separate agent grades the draft, which is what makes it
work.` CMOS 6.65 and 6.67 permit the emphatic colon and its lowercase reveal; the
ban is a house override. Colons that introduce a list or a definition are fine:
`Three checks run:` is not a reveal.

### `SLOP.THROAT_CLEARING`

`It is worth noting that`, `It is important to note`, `Here's the thing`, `Let me be
clear`, `When it comes to`, `At the end of the day`, `In today's world`, `At its
core`, `The reality is`, `Let's dive in`, `In this article`.

Cut the run-up and start with the point. This is also an expletive opening (5.246).

### `SLOP.FAUX_INSIGHT`

`What nobody tells you`, `What most people miss`, `The part everyone skips`, `The
thing nobody says`. The setup flatters the writer as the lone expert and adds no
claim. Make the claim stand alone.

### `SLOP.RHETORICAL_SETUP`

`Think about it:`, `What if I told you`, `Plot twist:`. Drop it and make the point.

### `SLOP.ING_ANALYSIS`

`The launch adds file search, highlighting the team's commitment to better
workflows.` The trailing participle pretends to explain meaning.

Say what it does for the reader: `The launch adds file search, so users can find old
drafts without leaving the editor.`

### `SLOP.FRAGMENT_STACK`

`That's it. That is it. Done.` Three or more short fragments in a row are rhythm for
its own sake. Write sentences.

Two boundaries, both grammatical rather than discretionary:

- **A label is not a fragment.** `Table 9 · open-weight models` and `01 · The Idea`
  were never sentences, so nothing is broken. This applies on screen (register
  `display`).
- **A complete short sentence is not a fragment.** `You ask for a decision. You get
  nine hundred words of reasoning.` is two full clauses: antithesis, which stays.
  A list item is structure, not a stack.

### `SLOP.PUFFERY`

`marks a pivotal moment`, `stands as a testament to`, `plays a vital role`,
`solidifies its position`, `underscores its significance`.

State the fact and let the reader judge whether it matters: `The launch is the
company's first paid product.`

### `SLOP.WEASEL`

`Experts agree`, `studies show`, `widely regarded as`, `many argue`, `it is believed`.

Name the source or cut the claim. If the writer has no source, query it instead of
inventing one (Pass 5).

### `SLOP.RECAP_ENDING`

`In conclusion`, `To sum up`, `Ultimately`, `Overall`, and the final paragraph that
restates the piece. The reader was just there. End on the last concrete point, the
takeaway, or the next action.

### `SLOP.BANNED_WORD`

Twenty-four words. Every one of them is vague in a way that sounds important:

```
delve  foster  leverage  utilize  facilitate  empower  streamline  robust
cutting-edge  paradigm shift  game changer  this is huge  this changes everything
tapestry  realm  beacon  multifaceted  meticulous  intricate  paramount
transformative  elevate  embark  supercharge  harness  ever-evolving
```

The manual does not license any of them: none appears in the 5.254 usage glossary,
and where it does speak it agrees (`impact` as a verb, `utilize`, `preventative`).
Technical terms lose too: `robust` in a statistics paper is an error. Use the plain
word, quote the source's term, or justify it in the report.

### `SLOP.EMPTY_ADVERB`

Eleven words that usually add nothing:

```
just  literally  honestly  simply  actually  truly
fundamentally  importantly  crucially  inherently  inevitably
```

Not intensifiers, and therefore allowed: `just as`, `just before`, `just after`,
`just when`, `just enough`, `just now`, `just in case`, `simply put`. The manual
keeps an adverb that carries real uncertainty or the writer's spoken rhythm (2.57);
within this list, the linter cannot tell, so the list is narrow instead.

### `SLOP.WEAK_VERB`

`made a decision` becomes `decided`. `has the ability to` becomes `can`. `provides
assistance` becomes `helps`. `performed an analysis` becomes `analyzed`.

## Patterns the linter cannot check

Cross-sentence judgment, and a regex would be wrong about them. `EVAL.md` asks the
questions.

- **Fake-profound kicker.** The final line that turns the point into a cute
  metaphor or a mic-drop. Delete it; do not rewrite it into a better metaphor. End
  on the clearest concrete sentence already in the draft.
- **Synonym cycling.** `The agent reviews the draft. The assistant scores the piece.
  The tool suggests fixes.` One thing, three names. Repeat the clear word.
- **Robotic rhythm.** Identical sentence shapes, identical paragraph structures,
  every paragraph equally tidy.
- **Interpretive metadiscourse.** `That last part matters more than it sounds.` `The
  key point is.` `As you can see.` `In other words.` Cut the aside, or replace it
  with the support it was standing in for.
- **Formatting slop.** Emoji in headings, bold sprinkled mid-sentence, bullets where
  two sentences of prose would read better, a header over a two-sentence section.

## The portability test

If a sentence could move unchanged to another person, company, product, country, or
year, it is filler. Cut it, or replace it with a fact, an example, a mechanism, a
consequence, or a judgment that only fits this subject.

`The integration improved efficiency.` fails. `The integration cut deploy time from
40 minutes to 4.` passes.

## Protect the specific fact

Do not smooth a number into a claim. `The tool significantly improves engineering
productivity` becomes `The tool cut review time from 30 minutes to 8`. A specific
detail is the hardest thing to invent, so it is the last thing to delete.

## Do not flatten the writer

Slop rules remove shapes, not personality. Keep vocabulary, cadence, bluntness,
humor, profanity, self-interruption, honest uncertainty, and digressions. The
minimum effective edit is the standard: fix the pattern, leave the strong sentence
alone, and do not make every paragraph equally tidy (2.57).
