#!/usr/bin/env python3
"""cmos_lint - deterministic checks for prose written in Chicago style.

Every finding names its source: a CMOS rule number, or `house` for a rule of
this skill that overrides the manual (House overrides, in SKILL.md). Two
severities:

  error  must not ship: a mechanical rule of The Chicago Manual of Style, 18th
         ed. (2024), or a house rule. Every slop rule is a house rule, and every
         slop rule is an error.
  hint   a judgment heuristic drawn from a CMOS rule. Never auto-apply.
         Read the sentence before changing it (CMOS 2.57).
  warn   the manual requires it, but a house style may override it, so it does not
         fail --errors-only.

--register names the register of the text (prose, spoken, display, ui). A register
switches off the mechanical rule families that do not apply to it: no curly
apostrophes in narration that is read aloud, no sentence-length checks on a title
card. Slop rules are never switched off, in any register.

Stdlib only; no dependencies; harness-agnostic -- run it from any agent,
editor, or CI step.

    python3 cmos_lint.py draft.md               # human report
    python3 cmos_lint.py --json draft.md        # machine report
    python3 cmos_lint.py --errors-only draft.md # errors, no hints
    python3 cmos_lint.py --register spoken narration.md
    cat draft.md | python3 cmos_lint.py -       # stdin

Exit status: 0 clean, 1 findings of the selected severities, 2 usage error.
"""

import argparse
import json
import re
import sys

# --------------------------------------------------------------------------
# Word lists
# --------------------------------------------------------------------------

# Take "a" despite a vowel letter: consonant sound first.
A_WORDS = set("""
eulogy euphemism euphoria euphoric euphonium europe european europeans ewe ewes
one ones once oneself
ubiquitous ubiquity ukulele unanimous unicorn unicycle uniform uniformed
uniformity unify unilateral union unions unionist unique uniquely uniqueness
unison unit units unitary unite united unity universal universality universe
universities university unary uranium urinal urinary use used useful usefulness
useless user users usual usually usury utensil utensils uterus utilitarian
utilities utility utilize utilization utopia utopian uvula uxorious
ewer
""".split())

# Take "an" despite a consonant letter: silent h, or a vowel sound.
AN_WORDS = set("""
heir heiress heirloom heirlooms heirship
herb herbs herbaceous herbal
honest honestly honesty honorary honor honorable honorably honored honorarium
honorific honour honours
hour hourly hours houri
""".split())

# Initialisms whose spoken first letter is a vowel sound (an MBA, an FBI agent).
VOWEL_SOUND_INITIALS = set("aefhilmnorsx")

# "-ly" words that are adjectives, so a hyphen after them is legitimate.
LY_ADJECTIVES = set("""
early only friendly lovely lonely likely unlikely daily weekly monthly yearly
hourly costly scholarly elderly silly ugly holy jolly deadly lively orderly
timely untimely stately bodily heavenly leisurely cowardly kindly curly burly
ghastly surly grisly measly seemly comely homely lowly melancholy
""".split())

# 8.160 rules 1-2: lowercase these inside a title (unless first or last).
SHORT_FUNCTION_WORDS = set(
    "a an the and but or nor for so yet to as of in on at by with per via".split())

# 8.160 rule 3: capitalize prepositions of five letters or more.
LONG_PREPOSITIONS = set("""
about above across after against along amid among around before behind below
beneath beside besides between beyond despite during except inside outside over
past since through throughout toward towards under underneath until unto upon
within without
""".split())

MONTHS = ("January February March April May June July August September October "
          "November December")

SUPERSCRIPTS = set("\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078"
                   "\u2079\u207f\u02b0\u02b2\u02b3\u02b7\u02e1\u02e3")

CONTINUATION_YEARS = "|".join(str(y) for y in range(2000, 2100))


class Finding:
    __slots__ = ("rule", "cmos", "severity", "path", "line", "col", "message", "text")

    def __init__(self, rule, cmos, severity, path, line, col, message, text=""):
        self.rule, self.cmos, self.severity = rule, cmos, severity
        self.path, self.line, self.col = path, line, col
        self.message, self.text = message, text

    def as_dict(self):
        return {k: getattr(self, k) for k in self.__slots__}


class Rule:
    """One regex check. `reject` suppresses a match; `flags` are re flags."""

    __slots__ = ("rule", "cmos", "severity", "message", "pattern", "reject", "rx", "rj")

    def __init__(self, rule, cmos, severity, message, pattern, reject="", flags=0):
        self.rule, self.cmos, self.severity = rule, cmos, severity
        self.message, self.pattern = message, pattern
        self.rx = re.compile(pattern, flags)
        self.rj = re.compile(reject) if reject else None


def R(rule, cmos, severity, message, pattern, reject="", flags=0):
    return Rule(rule, cmos, severity, message, pattern, reject, flags)


# --------------------------------------------------------------------------
# Rules. Grouped by chapter, in the manual's order.
# --------------------------------------------------------------------------
RULES = [
    # -- Manuscript hygiene (ch 2) ---------------------------------------
    R("SPACE.SENTENCE", "2.11, 6.7", "error",
      "one space between sentences, not two",
      r"[.!?][\"'\u201d\u2019)]? {2,}(?=\S)"),
    R("SPACE.COLON", "6.66", "error",
      "one space after a colon, never two",
      r": {2,}(?=\S)"),
    R("SPACE.BEFORE_PUNCT", "6.7", "error",
      "no space before a mark of punctuation",
      r"(?<![.\s]) +[,;:.!?](?=\s|$)"),
    R("DASH.DOUBLE_HYPHEN", "2.17, 6.91", "error",
      "two hyphens do not make a dash; use a colon, a comma, or parentheses",
      r"(?<![-\w])--(?![-\w])"),
    R("DASH.SPACED_HYPHEN", "6.91", "error",
      "a spaced hyphen is not a dash; use a colon, a comma, or parentheses",
      r"(?<=[A-Za-z,)])\t* +-[ \t]+(?=[A-Za-z])"),
    R("ELLIPSIS.DOTS", "12.59, 12.62", "error",
      "use spaced ellipsis points (. . .) or the ellipsis character, "
      "not three unspaced periods",
      r"(?<!\.)\.\.\.(?!\.)"),
    R("ELLIPSIS.DOUBLE_PERIOD", "6.132", "error",
      "do not double a period at the end of a sentence",
      r"(?<=[a-z])\.\.(?=\s|$)"),

    # -- Quotation marks and apostrophes (6.123-6.126) -------------------
    R("QUOTE.STRAIGHT_DOUBLE", "6.123", "error",
      'use directional quotation marks (\u201c \u201d), not the default straight mark',
      r'"'),
    R("QUOTE.STRAIGHT_APOSTROPHE", "6.125", "error",
      "use the directional apostrophe (\u2019), never a straight mark "
      "or a left single quotation mark",
      r"(?<![0-9A-Za-z])'|'(?![0-9A-Za-z])|(?<=[A-Za-z])'(?=[A-Za-z])"),

    # -- Punctuation (ch 6) ---------------------------------------------
    R("COLON.AFTER_VERB", "6.71", "error",
      "no colon between a verb and its object or complement: the introduction "
      "must itself be a complete sentence",
      r"\b(is|are|was|were|be|been|being|includes?|consists?|comprises?|involves?|"
      r"contains?|feature[sd]?)\s*:\s"),
    R("COMMA.SERIAL", "6.19", "warn",
      "Chicago requires the serial comma before 'and' in a series of three or more",
      r",\s+[^,;:.\n]{1,40}?\s+and\s+[^,;:.\n]{1,40}(?=[.;)]|\n|$)"),
    R("COMMA.JR_SR", "6.46", "error",
      "no commas around Jr. or Sr.",
      r",\s*(?:Jr|Sr)\.|(?:Jr|Sr)\.\s*,"),
    R("COMMA.CORPORATE", "6.47", "error",
      "no commas around Inc., Ltd., or Corp.",
      r",\s*(?:Inc|Ltd|Corp|LLC)\.|(?:Inc|Ltd|Corp)\.\s*,"),
    R("COMMA.TOO_EITHER", "6.56", "hint",
      "no comma before 'too' or 'either' meaning 'also'",
      r",\s+(?:too|either)\b(?=[.;,]|$)"),

    # -- Numbers (ch 9) --------------------------------------------------
    R("RANGE.HYPHEN", "6.83, 9.62", "error",
      "use an en dash for a range of numbers, not a hyphen",
      r"\b\d{1,4}\s?-\s?\d{1,4}\b"),
    R("RANGE.FROM", "6.83, 9.62", "error",
      "write 'from X to Y', never 'from X\u2013Y' or 'from X-Y'",
      r"\bfrom\s+\d[\d,.]*\s*[\u2013-]\s*\d"),
    R("RANGE.BETWEEN", "6.83, 9.62", "error",
      "write 'between X and Y', never 'between X\u2013Y' or 'between X-Y'",
      r"\bbetween\s+\d[\d,.]*\s*[\u2013-]\s*\d"),
    R("NUMBER.SENTENCE_START", "9.5", "error",
      "spell out a number that begins a sentence, or recast the sentence",
      r"(?:^|(?<=[.!?]\s)|(?<=\n\n))\d[\d,.]*"),
    R("NUMBER.DATE_ORDINAL", "9.33, 9.6", "error",
      "no ordinal suffix on a month-day-year date",
      r"\b(?:%s)\s+\d{1,2}(?:st|nd|rd|th)\b" % MONTHS.replace(" ", "|")),
    R("NUMBER.NUMERIC_DATE", "6.115, 9.37", "error",
      "avoid all-numeral dates in formal prose; spell out the month",
      r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"),
    R("NUMBER.DECADE_APOSTROPHE", "9.35", "error",
      "decades take no apostrophe: 1990s, not 1990's",
      r"\b(?:1[6-9]|20)\d0['\u2019]s\b"),
    R("NUMBER.UNIT_SPACE", "9.18, 10.55", "error",
      "put a space between a numeral and its unit (50 km, not 50km)",
      r"\b\d+(?:kg|km|cm|mm|mL|kW|kHz|MHz|GHz|Hz|kPa|MPa|mg|ms|nm|ft|lb|oz|mi|"
      r"kWh|mAh)\b"),
    R("NUMBER.ORDINAL_SUPERSCRIPT", "9.6", "error",
      "write 122nd, 123rd, 125th - never a superscript ordinal", r"\d[\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079\u207f\u02b0\u02b2\u02b3\u02b7\u02e1\u02e3]"),
    R("NUMBER.PERCENT_SPACE", "9.20", "error",
      "no space between a numeral and the percent sign",
      r"\d\s+%"),
    R("NUMBER.NOON_MIDNIGHT", "9.40", "error",
      "12:00 a.m. and 12:00 p.m. are ambiguous; write noon or midnight",
      r"\b12:00\s*[ap]\.?m\.?"),
    R("NUMBER.AM_REDUNDANT", "9.39, 10.46", "error",
      "do not use a.m./p.m. with morning, afternoon, evening, night, or o'clock",
      r"\b[ap]\.?m\.?\s+(?:in\s+the\s+)?(?:morning|afternoon|evening|night)\b|"
      r"o['\u2019]clock\s+[ap]\.?m\b"),

    # -- Abbreviations (ch 10) ------------------------------------------
    R("ABBR.PERIODS", "10.4", "error",
      "no periods in abbreviations of two or more capitals",
      r"\bU\.S\.A?\.?|\bU\.K\.|\bPh\.D\.|\bB\.A\.|\bM\.A\.|\bP\.M\.s?|\bA\.M\.|"
      r"\bB\.C\.E?\.?|\bA\.D\.|\bC\.E\.|\bN\.Y\.|\bD\.C\."),
    R("ABBR.EG_COMMA", "5.254, 10.48", "error",
      "follow e.g. and i.e. with a comma",
      r"\b(?:e\.g\.|i\.e\.)(?!\s*,)"),
    R("ABBR.AND_ETC", "5.254", "error",
      "'etc.' already means 'and so forth'; delete 'and'",
      r"\band\s+etc\."),
    R("ABBR.ETC_AFTER_EG", "5.254", "error",
      "no 'etc.' after e.g., such as, or for example: they already signal a partial list",
      r"\b(?:e\.g\.|such as|for example)[^.;]{0,80}\betc\."),

    # -- Word usage (ch 5, ch 7) ----------------------------------------
    R("WORD.PREVENTATIVE", "5.254", "error",
      "use preventive, not preventative",
      r"\bpreventative\b"),
    R("WORD.NONSTANDARD", "5.254, 7.1", "error",
      "nonstandard form; see the usage entry",
      r"\b(?:irregardless|alright|supercede[sd]?|miniscule|orientate[sd]?|"
      r"cohabitate[sd]?|impactful|undoubtably|supposably|expresso|expecially|"
      r"nucular|sherbert|would of|could of|should of)\b"),
    R("WORD.COMPRISED_OF", "5.254", "error",
      "the whole comprises the parts; write 'composed of' or 'consisting of'",
      r"\bcomprised?\s+of\b"),
    R("WORD.DIFFERENT_THAN", "5.254", "error",
      "write 'different from'; 'different than' is defensible only before a dependent clause",
      r"\bdifferent(?:ly)?\s+than\b(?!\s+(?:if|when|it|they|he|she|we|I|the|a|what)\b)"),
    R("WORD.UNGRADABLE", "5.93", "error",
      "an absolute adjective takes no comparative or intensifier",
      r"\b(?:very|more|most|less|least|somewhat|quite|rather|extremely|totally|"
      r"completely)\s+(?:unique|impossible|perfect|complete|entire|pregnant|"
      r"infinite|fatal|universal|dead|empty|total)\b"),
    R("WORD.LEGALESE", "5.254", "hint",
      "avoid legalese in ordinary prose",
      r"\b(?:as per|in the affirmative|in the negative|and/or|therefor)\b"),

    # -- Hyphenation (ch 7) ---------------------------------------------
    R("HYPHEN.LY_ADVERB", "7.93", "error",
      "never hyphenate an -ly adverb to the word it modifies",
      r"\b([A-Za-z]{3,}ly)-([A-Za-z]{3,})\b"),
    R("HYPHEN.PREDICATE_COMPOUND", "7.91", "hint",
      "a compound modifier goes open after a linking verb (the student is well read)",
      r"\b(?:is|are|was|were|seems?|became|becomes|looks?|feels?)\s+"
      r"(?:[a-z]+-[a-z]+)\b(?!\s+(?:and|or)\b)"),

    # -- Concision and clarity (ch 2, ch 5) -----------------------------
    R("PROSE.WORDY_PHRASE", "5.180, 5.254", "hint",
      "replace the phrase with one word (because, before, to, about, if)",
      r"\b(?:in order to|in order for|due to the fact that|in spite of the fact that|"
      r"the fact that|at this point in time|at the present time|in the event that|"
      r"for the purpose of|with regard to|in regard to|with respect to|"
      r"in connection with|by means of|by reason of|prior to|in the process of|"
      r"in terms of|as to whether|on a (?:daily|weekly|monthly|yearly|regular) basis)\b"),
    R("PROSE.NOMINALIZATION", "5.195", "hint",
      "nominalization + of: turn the hidden verb back into a verb "
      "(maximization of profits -> maximizing profits)",
      r"\b[A-Za-z]{4,}(?:tion|sion|ment|ance|ence|ity|ism)\s+of\b"),
    R("PROSE.EXPLETIVE", "5.246", "hint",
      "expletive opening: if the real subject is short, lead with it",
      r"(?:^|(?<=[.!?]\s))\s*There\s(?:is|are|were|was)\s+"
      r"(?:many|several|a number of|numerous|countless)\b",
      flags=re.M),
    R("PROSE.PASSIVE_AGENT", "5.122", "hint",
      "explicit passive agent: passive voice is often inferior to active",
      r"\b(?:is|are|was|were|be|been|being)\s+[a-z]+(?:ed|en)\s+by\s"),
    R("PROSE.DANGLER", "5.119, 5.120", "hint",
      "sentence-initial participle with an it/there main clause: likely dangling",
      r"^[A-Z][a-z]+ing\b[^.;]{0,60},\s+(?:it|there)\s+(?:is|are|was|were|seems)\b",
      flags=re.M),

    # -- Slop: house rules, not CMOS rules (see House overrides) ---------
    # Every one is an error. The manual permits some of these shapes; the House
    # overrides entry records which rule each one displaces, so a reader can tell
    # a deliberate departure from a mistake. A register never switches these off.
    R("SLOP.EM_DASH", "house", "error",
      "em dashes are banned (house override of 6.91): use a colon, a comma, or "
      "parentheses",
      "—"),
    R("SLOP.BINARY_CONTRAST", "house", "error",
      "binary contrast: state the affirmative directly",
      r"\b(?:is|are|was|were|does|do|did)\s+not(?:\s+just|\s+merely|\s+simply)?\s+"
      r"[^.!?\n]{1,60}[.!]\s+(?:It|That|This)(?:'s|\s+is|\s+was)\b"
      r"|\bnot just\b[^.!?\n]{2,60}\bbut\b"
      r"|\b(?:isn't|aren't|wasn't|weren't)\s+[^.!?\n]{1,50}[.,]\s*"
      r"(?:it's|it is|they're|they are)\b"),
    R("SLOP.NEGATIVE_LIST", "house", "error",
      "negative listing: just say what it is",
      r"\bNot (?:a|an|the) [^.!?\n]{1,40}[.!]\s+(?:Not|Just)\s+(?:a|an|the)\b"),
    R("SLOP.THROAT_CLEARING", "house", "error",
      "throat-clearing: cut the run-up and state the point",
      r"(?:^|(?<=[.!?]\s))\s*(?:Here'?s (?:the thing|what I mean)"
      r"|Let me be (?:clear|honest)|It(?:'s| is) (?:worth|important) (?:noting|to note)"
      r"|It(?:'s| is) (?:important|interesting|worth|necessary) (?:to|that)\b"
      r"|At the end of the day|In today'?s (?:world|landscape|market)"
      r"|When it comes to|At its core|The (?:reality|truth) is"
      r"|Let'?s dive in|In this article)\b",
      flags=re.M),
    R("SLOP.FAUX_INSIGHT", "house", "error",
      "faux-insight setup: make the claim stand on its own",
      r"\b(?:[Ww]hat nobody (?:tells you|mentions|talks about)"
      r"|[Ww]hat most people (?:miss|get wrong|don'?t)"
      r"|[Tt]he part (?:everyone|most people|nobody) (?:misses|skips|gets wrong)"
      r"|[Tt]he thing nobody (?:tells you|says))\b"),
    R("SLOP.COLON_REVEAL", "house", "error",
      "colon reveal: write it as a plain sentence (house override of 6.65, 6.67)",
      r"\bthe (?:best|real|actual|interesting|key|main|whole|only) "
      r"(?:part|thing|reason|point)\s*:\s+[a-z]"
      r"|\bthe (?:catch|kicker|twist|punchline|takeaway|lesson|trick"
      r"|detail that makes it work)\s*:\s+[a-z]"
      r"|\bhere'?s (?:the|where) (?:thing|part|catch|kicker|twist)\s*:\s+[a-z]",
      flags=re.I),
    R("SLOP.ING_ANALYSIS", "house", "error",
      "trailing -ing clause that claims to explain meaning: say what it does",
      r",\s+(?:highlight|underscor|reflect|showcas|emphasiz|signal|demonstrat)\w*ing\b"
      r"[^.!?\n]{0,80}[.!?]"),
    R("SLOP.PUFFERY", "house", "error",
      "importance puffery: state the fact and let the reader judge it",
      r"\b(?:marks? a (?:pivotal|turning) (?:moment|point)|stands? as a testament"
      r"|a testament to|plays? a (?:vital|crucial|key) role"
      r"|solidif\w+ (?:its|the company'?s|the team'?s) position"
      r"|underscor\w+ (?:its|the) significance)\b"),
    R("SLOP.WEASEL", "house", "error",
      "weasel attribution: name the source or cut the claim",
      r"\b(?:experts|studies|research|reports|analysts|industry)\s+"
      r"(?:agree|shows?|suggests?|says?|indicates?|argue)\b"
      r"|\bwidely (?:regarded|considered|seen|believed) as\b"
      r"|\bit is (?:widely )?(?:said|believed|thought)\b",
      flags=re.I),
    R("SLOP.RHETORICAL_SETUP", "house", "error",
      "rhetorical setup: drop it and make the point",
      r"\bWhat if I told you\b|\bThink about it\s*:|\bPlot twist\s*:"),
    R("SLOP.RECAP_ENDING", "house", "error",
      "summary recap: end on the last concrete point, not a restatement",
      r"(?m)^[>\s]*(?:In conclusion|To sum up|All in all|Ultimately|Overall)\b[,:]?\s"),
    R("SLOP.BANNED_WORD", "house", "error",
      "banned word: see the words-to-cut list in references/15-rhetoric.md",
      r"\b(?:delve[sd]?|delving|foster\w*|leverag\w*|utiliz\w*|facilitat\w*|empower\w*"
      r"|streamlin\w*|robust\w*|cutting-edge|paradigm shift|game changer"
      r"|this is huge|this changes everything|tapestry|realm|beacon|multifaceted"
      r"|meticulous|intricate|paramount|transformative|elevate[sd]?|elevating"
      r"|embark(?:s|ed|ing)?|supercharg\w*|harness(?:es|ed|ing)?|ever-evolving)\b",
      flags=re.I),
    R("SLOP.EMPTY_ADVERB", "house", "error",
      "empty adverb: cut it unless it carries emphasis or the writer's rhythm",
      r"\b(?:just|literally|honestly|simply|actually|truly|fundamentally|importantly"
      r"|crucially|inherently|inevitably)\b",
      flags=re.I),
    R("SLOP.WEAK_VERB", "house", "error",
      "make the verb do the work (decide, analyze, help, can)",
      r"\b(?:has|have|had) the ability to\b|\b(?:is|are|was|were) able to\b"
      r"|\b(?:makes?|made) (?:a|an|the) (?:decision|choice|analysis|assessment"
      r"|recommendation)\b"
      r"|\b(?:performs?|performed) (?:a|an|the) (?:analysis|review|assessment"
      r"|evaluation)\b"
      r"|\bprovides? (?:assistance|support|guidance)\b",
      flags=re.I),
]

FORCE_SUFFIX = "st|nd|rd|th"

# Registers. A register switches off the mechanical rule families that do not
# apply to it. Slop rules are never switched off (see skipped).
REGISTER_SKIP = {
    "prose": (),
    "spoken": ("QUOTE.", "PROSE.LONG_SENTENCE", "PROSE.OF_CHAIN",
               "PROSE.NOMINALIZATION", "PROSE.WORDY_PHRASE",
               "PROSE.PASSIVE_AGENT", "PROSE.DANGLER"),
    "display": ("PROSE.LONG_SENTENCE", "PROSE.OF_CHAIN",
                "PROSE.NOMINALIZATION", "PROSE.WORDY_PHRASE",
                "PROSE.PASSIVE_AGENT", "PROSE.DANGLER", "PROSE.EXPLETIVE",
                "COLON.AFTER_VERB", "NUMBER.SENTENCE_START"),
    "ui": ("ABBR.", "NUMBER.", "RANGE.", "ELLIPSIS.", "QUOTE."),
}

def skipped(rule_id, register):
    """True when this register does not apply the rule. Never true for slop."""
    if rule_id.startswith("SLOP."):
        return False
    return any(rule_id.startswith(p) for p in REGISTER_SKIP[register])

def in_blockquote(text, pos):
    """True when pos sits on a line that opens a blockquote (quoted matter)."""
    start = text.rfind("\n", 0, pos) + 1
    return text[start:start + 200].lstrip().startswith(">")

def is_list_line(text, pos):
    """True for a list item, table row, or heading: structure, not a fragment."""
    start = text.rfind("\n", 0, pos) + 1
    return bool(re.match(r"\s*(?:[-*+]\s|\d+[.)]\s|\||#{1,6}\s)",
                         text[start:start + 80]))


# --------------------------------------------------------------------------
# Masking: keep every offset and line number, blank out what must not be linted.
# --------------------------------------------------------------------------
def mask(text):
    """Blank out regions that must not be linted, preserving offsets.

    Returns (masked_text, spans) so the driver can discard any match that
    overlaps a masked region (which otherwise leaves a run of spaces that
    looks exactly like a doubled word space).
    """
    out = list(text)
    spans = []

    def blank(a, b):
        spans.append((a, b))
        for i in range(a, b):
            if out[i] != "\n":
                out[i] = " "

    if text.startswith("---\n"):
        end = text.find("\n---\n", 3)
        if end != -1:
            blank(0, end + 5)
    for m in re.finditer(r"^\s*(?:```|~~~).*?(?:^\s*(?:```|~~~)|\Z)", text, re.S | re.M):
        blank(*m.span())
    for m in re.finditer(r"`[^`\n]*`", text):
        blank(*m.span())
    for m in re.finditer(r"<[^>\n]{1,120}>", text):
        blank(*m.span())
    for m in re.finditer(r"https?://\S+|www\.\S+|\S+@\S+\.\w+", text):
        blank(*m.span())
    for m in re.finditer(r"^\s*\d+\.\s", text, re.M):
        blank(*m.span())
    return "".join(out), spans


def line_col(text, pos):
    return text.count("\n", 0, pos) + 1, pos - (text.rfind("\n", 0, pos) + 1) + 1


# --------------------------------------------------------------------------
# Checks that need more than one regex match
# --------------------------------------------------------------------------
def check_sentences(masked, path, add, register="prose", text=None):
    """Sentence-level checks. `text` is the unmasked source, for list detection."""
    source = masked if text is None else text
    flat = masked.replace("\n", " ")  # same length, so offsets stay valid
    for m in re.finditer(r"[^.!?]+[.!?]?", flat):
        s = m.group(0)
        words = s.split()
        ln, col = line_col(masked, m.start())
        if len(words) > 40 and not skipped("PROSE.LONG_SENTENCE", register):
            add(Finding("PROSE.LONG_SENTENCE", "5.229", "hint", path, ln, col,
                        f"sentence is {len(words)} words long; check that the main "
                        "clause is not buried"))
        n_of = len(re.findall(r"\bof\b", s, re.I))
        if n_of >= 3 and not skipped("PROSE.OF_CHAIN", register):
            add(Finding("PROSE.OF_CHAIN", "5.254", "hint", path, ln, col,
                        f"{n_of} of-phrases in one sentence; remove every of-phrase "
                        "you reasonably can"))

    # Slop: a stack of three or more four-word-or-shorter sentences inside one
    # paragraph is rhythm for its own sake. Slop outranks 2.57's licence for a
    # deliberate fragment (House overrides). A list item is not a fragment.
    if skipped("SLOP.FRAGMENT_STACK", register):
        return
    for para in re.finditer(r"[^\n]+(?:\n(?!\s*\n)[^\n]+)*", masked):
        # A list item (with its wrapped lines) is structure, not a fragment run.
        if is_list_line(source, para.start()) or in_blockquote(masked, para.start()):
            continue
        run = []
        for s in re.finditer(r"[^.!?]+[.!?]", para.group(0)):
            txt = s.group(0).strip()
            pos = para.start() + s.start()
            if (txt[:1] in "-*|>" or in_blockquote(masked, pos)
                    or is_list_line(source, pos)
                    or len(txt.split()) > 4):
                run = []
                continue
            run.append(pos)
            if len(run) == 3:
                ln, col = line_col(masked, run[0])
                add(Finding("SLOP.FRAGMENT_STACK", "house", "error", path,
                            ln, col, "three short fragments in a row: write "
                            "sentences, not rhythm"))
                run = []


def check_articles(masked, path, add, register="prose"):
    """a/an by spoken sound: 7.32, 7.33, 5.78, 10.10."""
    if skipped("PROSE.AN", register):
        return

    def report(m, why):
        ln, col = line_col(masked, m.start())
        add(Finding("PROSE.AN", "7.32, 7.33, 5.78", "error", path, ln, col, why,
                    m.group(0)))

    for m in re.finditer(r"\b(a|an)\s+([\w'\u2019-]+)", masked):
        art, nxt = m.group(1).lower(), m.group(2)
        low = nxt.lower().strip("'\u2019")
        if not low:
            continue
        initialism = nxt.isupper() and len(nxt) > 1

        # An initialism is decided by the name of its first letter alone:
        # a URL, a UFO, a HUD program; an MBA, an HMO, an FBI agent (7.33).
        if initialism:
            vowel_sound = low[0] in VOWEL_SOUND_INITIALS
            if art == "a" and vowel_sound:
                report(m, f"initialism starts with a vowel sound: use 'an {nxt}'")
            elif art == "an" and not vowel_sound:
                report(m, f"initialism starts with a consonant sound: use 'a {nxt}'")
            continue

        if art == "a":
            if low in AN_WORDS:
                report(m, f"silent h or vowel sound: use 'an {nxt}'")
            elif low[0] in "aeiou" and low not in A_WORDS and not low.startswith(
                    ("eu", "ew", "one", "once", "uni", "use", "usu", "uti",
                     "ura", "ure", "uro", "ubiq")):
                report(m, f"vowel sound: use 'an {nxt}'")
        else:
            if low in A_WORDS:
                report(m, f"consonant sound: use 'a {nxt}'")
            elif low[0].isdigit():
                if not (low[0] == "8" or low.startswith(("11", "18"))):
                    report(m, f"number starts with a consonant sound: use 'a {nxt}'")
            elif low[0] in "bcdfgjklmnpqrstvwxyz" and low not in AN_WORDS:
                report(m, f"consonant sound: use 'a {nxt}'")


def check_titles(text, masked, path, add, register="prose"):
    """Headline-style title case: 8.160 rules 1-3, 8.162."""
    if skipped("TITLE.SHORT_WORD_CAPPED", register):
        return

    def examine(segment, seg_start, require_title_case=True):
        words = list(re.finditer(r"[A-Za-z][A-Za-z'\u2019-]*", segment))
        if len(words) < 3:
            return
        if require_title_case and sum(
                1 for w in words if w.group(0)[0].isupper()) / len(words) < 0.6:
            return
        for i, w in enumerate(words):
            if i in (0, len(words) - 1):
                continue
            word = w.group(0)
            low = word.lower()
            ln, col = line_col(masked, seg_start + w.start())
            if low in SHORT_FUNCTION_WORDS and word[0].isupper():
                add(Finding("TITLE.SHORT_WORD_CAPPED", "8.160", "error", path, ln, col,
                            f"lowercase '{low}' inside a title (rules 1-2)", word))
            elif low in LONG_PREPOSITIONS and word[0].islower():
                add(Finding("TITLE.LONG_PREP_LOWER", "8.160", "error", path, ln, col,
                            f"capitalize '{low}': prepositions of five or more letters "
                            "are capitalized in a title (rule 3)", word))

    for m in re.finditer(r"^#{1,6}\s+(.+)$", text, re.M):
        segment = re.sub(r"^[\d.)\s]+", lambda mm: " " * len(mm.group(0)), m.group(1))
        # A markdown heading is a title by definition, so no title-case test.
        examine(segment, m.start(1), require_title_case=False)


# --------------------------------------------------------------------------
# Context guards for rules whose regex alone is too coarse
# --------------------------------------------------------------------------
def suppressed(rule_id, masked, m):
    s, e = m.span()
    local = masked[max(0, s - 12):min(len(masked), e + 12)]

    # Quoted matter is reproduced, not authored (2.67): a line that opens a
    # blockquote is exempt from the slop rules.
    if rule_id.startswith("SLOP.") and in_blockquote(masked, s):
        return True

    if rule_id == "SLOP.EMPTY_ADVERB":
        word, after = m.group(0).lower(), masked[e:e + 12]
        if word == "just" and re.match(
                r"\s+(?:as|before|after|when|once|enough|now|in case|so|over|"
                r"under|like|yet|beyond|there)\b", after):
            return True
        return word == "simply" and bool(re.match(r"\s+put\b", after))

    if rule_id == "RANGE.HYPHEN":
        # ISO dates (9.38) legitimately use hyphens, including the second part.
        if re.match(r"\d{4}-\d{2}-\d{2}", masked[s:s + 10]):
            return True
        if re.match(r"\d{4}-\d{2}$", masked[max(0, s - 5):s + 7]):
            return True
        # Phone numbers and ISBNs (6.81) legitimately use hyphens.
        if re.match(r"\d-\d{3}-\d{4}", masked[s:s + 20]):
            return True
        # A letter immediately after the second number means a compound (3-D),
        # not a range.
        return bool(re.match(r"\d[.,]?\d*\s?-\s?[A-Za-z]", masked[s:s + 8]))

    if rule_id == "NUMBER.SENTENCE_START":
        # A year is allowed to open a sentence (9.5), and so are 3D / 401(k).
        after = masked[e:e + 2]
        return bool(re.match(r"[a-zA-Z(]", after))

    if rule_id == "HYPHEN.LY_ADVERB":
        if m.group(1).lower() in LY_ADJECTIVES:
            return True
        # A three-word phrase may take hyphens for clarity (7.93).
        return bool(re.match(r"[A-Za-z]+-", masked[max(0, s - 14):s]))

    if rule_id == "COMMA.SERIAL":
        parts = [p.strip() for p in re.split(r",|\band\b", m.group(0)) if p.strip()]
        if len(parts) < 2:
            return True
        # Reject when any element reads as a clause rather than a list item.
        return any(re.search(r"\b(?:is|are|was|were|be|been|has|have|had|will|"
                             r"would|can|could|should|must)\b", p) for p in parts)

    if rule_id == "SPACE.BEFORE_PUNCT":
        # Spaced ellipsis points are correct (12.59).
        window = masked[max(0, s - 1):e + 5]
        return bool(re.search(r"\.\s+\.", window))

    if rule_id == "ELLIPSIS.DOUBLE_PERIOD":
        return bool(re.search(r"\betc\.{2}$|\.\.\.$", local))

    return False


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
def lint(text, path="<text>", register="prose"):
    masked, spans = mask(text)
    findings = []

    def add(f):
        findings.append(f)

    def overlaps_mask(s, e):
        return any(s < b and e > a for a, b in spans)

    for rule in RULES:
        if skipped(rule.rule, register):
            continue
        for m in rule.rx.finditer(masked):
            if rule.rj and rule.rj.search(m.group(0)):
                continue
            if overlaps_mask(*m.span()) and rule.rule not in (
                    "PROSE.LONG_SENTENCE", "PROSE.OF_CHAIN"):
                continue
            if suppressed(rule.rule, masked, m):
                continue
            ln, col = line_col(masked, m.start())
            add(Finding(rule.rule, rule.cmos, rule.severity, path, ln, col,
                        rule.message, m.group(0).strip()[:60]))

    check_sentences(masked, path, add, register, text)
    check_articles(masked, path, add, register)
    check_titles(text, masked, path, add, register)

    out, seen = [], set()
    for f in sorted(findings, key=lambda f: (f.line, f.col, f.rule)):
        key = (f.rule, f.line, f.col)
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="cmos_lint",
        description="Check prose against the mechanical rules of The Chicago "
                    "Manual of Style, 18th edition (2024).")
    ap.add_argument("files", nargs="+", help="files to check, or - for stdin")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    ap.add_argument("--errors-only", action="store_true", help="suppress hints")
    ap.add_argument("--register", default="prose", choices=sorted(REGISTER_SKIP),
                    help="register of the text (default: prose)")
    ap.add_argument("--summary", action="store_true", help="counts only")
    args = ap.parse_args(argv)

    all_findings, failed = [], False
    for path in args.files:
        try:
            text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
        except OSError as exc:
            print(f"cmos_lint: {exc}", file=sys.stderr)
            return 2
        found = lint(text, path, args.register)
        if args.errors_only:
            found = [f for f in found if f.severity == "error"]
        all_findings += found
        failed = failed or bool(found)

    errors = sum(1 for f in all_findings if f.severity == "error")
    hints = len(all_findings) - errors

    if args.json:
        print(json.dumps({"errors": errors, "hints": hints,
                          "findings": [f.as_dict() for f in all_findings]},
                         indent=2, ensure_ascii=False))
    elif args.summary:
        print(f"{errors} error(s), {hints} hint(s)")
    else:
        for f in all_findings:
            label = "ERROR" if f.severity == "error" else "HINT "
            print(f"{f.path}:{f.line}:{f.col}  {label} {f.rule} [{f.cmos}]  {f.message}")
            if f.text:
                print(f"    > {f.text}")
        print(f"\n{errors} error(s), {hints} hint(s)" if all_findings else "no findings")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
