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
