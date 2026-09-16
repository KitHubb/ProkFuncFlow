# C03-C10 implementation and verification status

All planned workflow stages C00-C10 are implemented as Nextflow DSL2 processes or validators.

- C03 applies the ordered quality, genus, and UHGC-overlap policy.
- C04 runs joint dRep 3.5.0/fastANI and validates complete membership and representatives.
- C05 validates complete Prokka GFF/FAA/FFN/GBK sets for every representative.
- C06 validates Panaroo presence/absence, final graph, representative proteins, and cluster-gene-genome projection.
- C07 preserves pangenome eggNOG/Kofam annotation separately from independent per-genome anvi'o KOfam evidence.
- C08 uses `anvi-estimate-metabolism` pathwise and stepwise completeness with the same pinned anvi'o KEGG snapshot; no project-written parser contributes production calls.
- C09 runs gapseq find, transporter search, draft, and medium-specific gap filling per representative. Sequence, transporter-candidate, and gap-filled reaction evidence remain distinct.
- C10 joins genome quality, pangenome mapping, functional evidence, modules, reaction evidence, clade metadata, and reference status. It reports genome/clade summaries and quality, fragmentation, genome-size, reference, and singleton-clade sensitivity scenarios.

The historical three-representative smoke run used the retired synthetic module-definition fixture and does not validate the current C08 implementation. Its Panaroo and gapseq checks remain historical diagnostics only. A new end-to-end anvi'o metabolism smoke test is required after the pinned anvi'o KEGG snapshot is installed.

The synthetic parser and fixture may remain as isolated software-history tests, but neither is connected to `main.nf` or `downstream.nf`, and neither may generate biological results. Without a clade map, genomes are assigned `unassigned` and inferential clade comparisons are disabled.
