# Primary sources

Every claim about rules, formats or device protocols in this repository cites a primary source.
This directory holds the sources themselves, or — when the licence forbids a copy — a pointer.

## Layout

```
docs/sources/
  README.md
  index.md                 # one row per source (see below)
  iof/                     # IOF rules, Data Standard 3.0 + XSD, organiser guides
  irf/                     # rogaining
  iaru/                    # ARDF
  minsport-ru/             # Russian national rules, EVSK (national package only)
  equipment/               # SPORTident, SFR, SRPID, Impinj protocol documents
  services/                # Eventor, WinSplits, Livelox requirements
  python/                  # Python release/EOL data used in ADRs
```

## Rules

1. `index.md` has one row per source: id, title, publisher, edition/version, date, URL, licence,
   local file (or "pointer only"), SHA-256 of the file or of the fetched page, date fetched.
2. Cite as `[правила: <id>, <edition>, <clause>]` or `[спецификация: <id>, <section>]`.
3. If the licence does not allow a copy, store only the row in `index.md` (URL, edition, date, hash).
4. Never paraphrase a rule from memory. No text in this directory — no citation; raise a question
   to the maintainer instead.
5. Personal data never goes here; race corpora have their own rules (see `docs/data-request.md`).
