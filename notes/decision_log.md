# Decision log

## 2026-09-14 — C00-C02 implementation

- Use the pinned CheckM2 1.0.2 and GTDB-Tk 2.6.1 images from the implementation plan; GTDB-Tk image SHA-256 matches the recorded digest.
- Use GTDB release 226 and require `gtdbtk check_install` through a read-only bind before C00 can pass.
- Preserve CheckM2 as one task per genome. Run GTDB-Tk as one configurable manifest batch because each r226 pplacer invocation has very high reference-memory overhead.
- The four-genome smoke set spans Bosanjin, SMGC, ELSG, and External datasets; it does not establish clade coverage.
- The current reusable workflow directory is not itself a Git repository. C00 records Git state when present; no repository was initialized because no Git mutation was requested.

## 2026-09-14 — Smoke observations

- Initial per-genome GTDB-Tk smoke passed 4/4 but each task peaked near 173 GB RSS. The production path was changed to one batch.
- The first batch attempt lacked binds for absolute FASTA/DB paths because only the manifest was a declared path input. Declaring the FASTA collection as a process path input restored Nextflow automatic `/data` binding.
- Final batch smoke passed C00, C01, and C02. CheckM2 tasks were cache hits on the final `-resume` run.

## 2026-09-15 — dRep C04 implementation

- Pin Bioconda dRep 3.5.0 image `drep_3.5.0--pyhdfd78af_0.sif` with SHA-256 `6ccf7812e2bb78cde2532b7a5df689a2ff1c2c7a178aa010dd1a2e94ccab0b4d`.
- Use fastANI 1.33 with primary ANI 0.90, secondary ANI 0.999, and minimum alignment coverage 0.10.
- Supply the uniformly computed C02 CheckM2 completeness/contamination values through dRep `--genomeInfo`; do not invoke `--ignoreGenomeQuality`.
- Require all frozen C03 genomes in Cdb, unique Wdb representatives, and exact agreement between Wdb and `dereplicated_genomes`.
- The four-genome focused C04 smoke test produced three clusters and three representatives; it is a software validation, not a production analysis.

## 2026-09-15 — Complete C05-C10 implementation

- Gate every stage with validators and C05-C10 JSON checkpoints.
- Use only threshold-passing Kofam calls for formal module reconstruction; preserve eggNOG as broad annotation evidence.
- Support nested AND/OR/complex/optional module logic via a versioned input TSV. The bundled definitions are synthetic tests and are never production defaults.
- Run gapseq gap filling per representative using a named medium and compare draft/gap-filled RDS reaction slots to retain added reactions separately.
- Treat gapseq transporter table rows as candidates rather than confirmed transport.
- Disable inferential clade comparison when an accepted map is absent, while still producing descriptive output and inverse-clade-size weights.
- The three-representative C05-C10 end-to-end smoke and full resume-cache test passed.
