# C03-C09 implementation status

Implemented and smoke-tested on four genomes:

- C03 ordered inclusion policy: completeness >=90, contamination <5,
  `g__Lawsonella`, then UHGC overlap exclusion; complete accounting and waterfall.
- C05 Prokka 1.15.6 with `--genus Lawsonella --usegenus --compliant`.
- C06 Panaroo 1.6.0 strict cleaning and validated representative-protein plus
  cluster/gene/genome mapping generation.
- C07 eggNOG-mapper 2.1.15 and KofamScan 1.3.0 in parallel on Panaroo
  representative proteins. KOfam uses `detail-tsv` to retain scores and thresholds.
- C09 gapseq 2.1.0 per representative proteome: pathway/reaction search,
  transporter search, and draft model construction. Direct evidence and models
  are published separately.

C04 is an explicit production gate. The downstream entrypoint requires a
validated dRep representative manifest. `main.nf --smoke_skip_drep true` exists
only for test fixtures; it must not be used for scientific production. A pinned
dRep image is still unresolved in `IMPLEMENTATION_PLAN.md`.

Medium-specific gapseq gap filling is not enabled because no accepted medium
definitions were supplied. No KEGG module completeness logic or restricted KEGG
content is included.

Smoke evidence (`results/` and `logs/` are intentionally ignored): 16 complete
Prokka files, 2,610 Panaroo representative proteins, 5,611 mapping rows, 2,337
eggNOG annotation rows, 77,331 KOfam detail rows, and four nonempty gapseq draft
models.
