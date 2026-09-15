# C03-C10 implementation and verification status

All planned workflow stages C00-C10 are implemented as Nextflow DSL2 processes or validators.

- C03 applies the ordered quality, genus, and UHGC-overlap policy.
- C04 runs joint dRep 3.5.0/fastANI and validates complete membership and representatives.
- C05 validates complete Prokka GFF/FAA/FFN/GBK sets for every representative.
- C06 validates Panaroo presence/absence, final graph, representative proteins, and cluster-gene-genome projection.
- C07 preserves eggNOG broad annotations and threshold-passing Kofam evidence separately.
- C08 evaluates versioned module definitions with AND, OR, complex, optional, and nested-parenthesis logic; formal KO evidence comes only from Kofam.
- C09 runs gapseq find, transporter search, draft, and medium-specific gap filling per representative. Sequence, transporter-candidate, and gap-filled reaction evidence remain distinct.
- C10 joins genome quality, pangenome mapping, functional evidence, modules, reaction evidence, clade metadata, and reference status. It reports genome/clade summaries and quality, fragmentation, genome-size, reference, and singleton-clade sensitivity scenarios.

The three-representative end-to-end smoke run `smoke_e2e_c05_c10` passed C05-C10 using the bundled synthetic module-definition fixture and the gapseq 2.1.0 `gut` medium. It produced 2,604 Panaroo clusters, 4,226 cluster/gene/genome mappings, 1,530 accepted Kofam calls, 6,404 functional evidence rows, 6,146 sequence-supported reaction rows, 57,907 transporter-candidate rows, and 370 gap-filled reactions. A repeated `-resume` launch returned every expensive upstream process from cache.

The synthetic module fixture tests software logic only and must not be represented as biological KEGG reconstruction. Production C08 requires an operator-supplied authorized, versioned definition TSV (`module_id`, `name`, `definition`). Without a clade map, genomes are assigned `unassigned` and inferential clade comparisons are disabled.
