# Lawsonella MAG Functional Analysis — Nextflow implementation plan

## 1. Immediate outcome

Build a reusable Nextflow DSL2 workflow for uniform QC, taxonomy, dereplication, pangenome construction, functional annotation, metabolic reconstruction, and clade-aware reporting of Lawsonella MAGs and reference genomes.

The workflow code will live at:

`/data/software/nextflow/lawsonella_mag_functional_nf/`

Project-specific inputs, run configuration, logs, and results remain under:

`/data/home2/ksy/260914_Lawsonella_pangenome/`

This document is a design record only. Writing it does not launch a production analysis.

## 2. Corrected pinned container mapping

The CheckM2 and GTDB-Tk paths in the operator's initial list were reversed. Use the following mapping:

| Tool | Container | Validation required before production |
|---|---|---|
| CheckM2 1.0.2 | `/data/software/singularity/checkm2_1.0.2.sif` | `checkm2 --version`, DB bind, one-genome result schema |
| GTDB-Tk 2.6.1 | `/data/software/singularity/gtdbtk_2.6.1--pyh1f0d9b5_2.sif` | version, r226 read-only bind, `gtdbtk check_install`, one-genome classify smoke test |
| Prokka 1.15.6 | `/data/software/singularity/prokka.sif` | actual executable `/prokka-1.15.6/bin/prokka`, one-genome output set |
| Panaroo 1.6.0 | `/data/software/singularity/panaroo.sif` | actual executable `/opt/conda/bin/panaroo`, small multi-genome smoke test |
| eggNOG-mapper 2.1.15 | `/data/software/singularity/eggnog-mapper/eggnog-mapper_2.1.15--pyhdfd78af_0.sif` | DB 5.0.2 bind and representative-protein smoke test |
| KofamScan 1.3.0 | `/data/software/singularity/kofamscan/kofamscan_1.3.0--hdfd78af_2.sif` | profile/KO-list bind, threshold-aware output smoke test |
| gapseq 2.1.0 | `/data/software/singularity/gapseq/gapseq_2.1.0--hdfd78af_0.sif` | Bacteria sequence DB 1.5 bind, pathway/transport/model smoke test |

GTDB-Tk 2.5.2 is retained only as legacy provenance and must not be selected by the production profile. The pinned GTDB-Tk 2.6.1 image has SHA-256 `1bd21ad071fd93e3bce27ca476cac8af839a33271cd5ff92dac2ce04b2b83111`; it contains skani 0.3.1 and has passed `check_install` against GTDB r226.

## 3. Scientific and workflow boundaries

- Treat every output as a genome-derived hypothesis, not experimental proof.
- Apply one CheckM2 version/database and one GTDB-Tk version/release to all candidates.
- Filter at completeness >=90, contamination <5, then genus `g__Lawsonella`; allow unclassified species.
- Run uniform QC on UHGC, then exclude UHGC before dRep because of known dataset overlap with SMGC.
- Dereplicate MAGs and isolate/reference genomes jointly with primary ANI 0.90, secondary ANI 0.999, minimum alignment coverage 0.10, fastANI, and validated CheckM2 genome information.
- Annotate dRep representatives with Prokka and build the pangenome with Panaroo.
- Run eggNOG-mapper and KofamScan on validated Panaroo representative proteins while retaining cluster-to-gene-to-genome mappings.
- Use KOfam threshold-aware KO calls and explicit KEGG logical definitions for formal module reconstruction. Do not derive module completeness from eggNOG pathway columns.
- Run gapseq per dRep representative genome/proteome. Never run it on Panaroo cluster sequences.
- Keep directly detected reactions separate from gap-filled or clade-pan reactions.
- Aggregate by clade only after per-genome outputs validate; account for MAG quality and unequal sampling.

## 4. Proposed repository layout

```text
lawsonella_mag_functional_nf/
├── README.md
├── IMPLEMENTATION_PLAN.md
├── main.nf
├── nextflow.config
├── conf/
│   ├── base.config
│   ├── singularity.config
│   ├── local.config
│   └── slurm.config
├── modules/local/
│   ├── provenance.nf
│   ├── validate_manifest.nf
│   ├── checkm2.nf
│   ├── gtdbtk.nf
│   ├── inclusion_filter.nf
│   ├── drep.nf
│   ├── prokka.nf
│   ├── panaroo.nf
│   ├── eggnog_mapper.nf
│   ├── kofamscan.nf
│   ├── kegg_reconstruct.nf
│   ├── gapseq_find.nf
│   ├── gapseq_transport.nf
│   ├── gapseq_model.nf
│   ├── gapseq_fill.nf
│   └── summarize.nf
├── subworkflows/local/
│   ├── qc_taxonomy.nf
│   ├── derep_annotation.nf
│   ├── pangenome_function.nf
│   └── genome_metabolism.nf
├── bin/
│   ├── validate_manifest.py
│   ├── normalize_checkm2.py
│   ├── normalize_gtdbtk.py
│   ├── apply_inclusion_policy.py
│   ├── validate_panaroo_mapping.py
│   ├── reconstruct_kegg_modules.py
│   └── build_checkpoint.py
├── assets/
│   ├── schemas/
│   └── report_templates/
└── tests/
    ├── fixtures/
    └── nextflow.config
```

Do not place genomes, databases, SIF images, work directories, or production results in this reusable workflow repository.

## 5. Inputs and configuration contract

Required runtime inputs:

- candidate manifest with stable `genome_id`, absolute staged FASTA path, dataset, genome type, accession, and provenance fields;
- canonical analysis YAML defining thresholds, releases, tool/database/container paths, and run ID;
- optional accepted clade map; otherwise use `unassigned` and disable inferential clade comparisons;
- optional medium definitions for gapseq gap filling.

All filesystem paths will be supplied as absolute paths through parameters. Container and database paths must not be hardcoded inside process scripts. The resolved configuration and input checksums will be copied into `results/<run_id>/00_provenance/`.

Initial parameters should include:

```text
--manifest
--analysis_config
--run_id
--outdir
--checkm2_db
--gtdbtk_db
--eggnog_db
--kofam_profiles
--kofam_ko_list
--gapseq_db
--clade_map
--media_dir
```

## 6. Authoritative stage plan

### C00 — Environment and container audit

1. Validate Git/project state, writable output/work/log paths, disk and inode availability, locale, Java, Nextflow, Singularity, and scheduler.
2. Record SHA-256 and metadata for every SIF.
3. Bind each DB read-only and run tool-specific help/version checks.
4. Run small functional self-tests, including GTDB-Tk r226 and gapseq.
5. Write `C00.json` only when every required acceptance criterion passes.

### C01 — Manifest and staged-input validation

1. Accept the checksum-frozen staged manifest from the project.
2. Validate unique IDs, regular files, nonzero size, gzip integrity, FASTA syntax/alphabet, source/staged checksum equality, and controlled categories.
3. Confirm expected dataset counts and retain discrepancy explanations.
4. Emit a normalized staged manifest and validation report.

### C02 — Uniform CheckM2 and GTDB-Tk

1. Run CheckM2 per genome with the pinned image/database.
2. Validate output existence, one-to-one genome IDs, numeric fields, and failure accounting.
3. Run GTDB-Tk 2.6.1 against release 226 using a read-only bind.
4. Normalize bacterial summary output and explicitly record unclassified/tool-failed cases.
5. Join QC, taxonomy, and checksums without using legacy values for filtering.

Implementation note: GTDB-Tk may run as a validated batch rather than one process per genome if reference-data I/O and classifier behavior make batching materially more efficient. Preserve per-genome accounting and make batch size configurable.

### C03 — Inclusion filter and freeze

Apply filters in the accepted order: completeness, contamination, genus, then UHGC dataset exclusion. Emit a frozen pre-dRep manifest, derived exclusion ledger, count waterfall, QC distributions, and checksum list. Fail unless every candidate is accounted for exactly once.

### C04 — Joint dRep

Run MAGs and references together with `--genomeInfo`; never use `--ignoreGenomeQuality`. Validate cluster membership, representative uniqueness, ANI/alignment parameters, and complete mapping back to the frozen C03 manifest.

Implementation status (2026-09-15): pinned dRep 3.5.0 in `/data/software/singularity/drep_3.5.0--pyhdfd78af_0.sif` (SHA-256 `6ccf7812e2bb78cde2532b7a5df689a2ff1c2c7a178aa010dd1a2e94ccab0b4d`) and validated fastANI 1.33. Do not silently use an unversioned host executable.

### C05 — Prokka annotation

Run one task per dRep representative with genus Lawsonella, `--usegenus`, and `--compliant`. Require complete GFF/FAA/FFN/GBK outputs and reject partial legacy annotation directories.

### C06 — Panaroo pangenome

Validate all Prokka GFFs before a strict Panaroo run with invalid-gene removal. Validate gene-presence/absence tables, representative sequences, graph outputs, and one-to-one cluster/gene/genome projection.

### C07 — eggNOG and KOfam annotation

After C06 validation, run eggNOG-mapper and KofamScan independently in parallel on Panaroo representative proteins. Preserve raw evidence, thresholds, scores, e-values, and cluster mappings. EggNOG supplies broad labels only; KOfam supplies formal KO evidence.

### C08 — KO, EC, reaction, and KEGG module reconstruction

Build a versioned evidence model preserving `genome -> gene -> cluster -> evidence -> KO/EC -> reaction -> module`. Implement AND/OR/complex/alternative/optional logic explicitly and report complete, incomplete, and uncertain states with missing required steps.

A licensed/versioned KEGG module-definition source is not present in the supplied list. During implementation, use only an authorized local source or a redistributable compatible representation; stop before downloading or redistributing restricted KEGG content without operator authority.

### C09 — Per-genome gapseq

For each dRep representative, run pathway finding, `find-transport`, draft model creation, and configured medium-specific gap filling. Store found sequence evidence separately from added reactions. Run clade-level `gapseq pan` only as a secondary analysis after per-genome completion.

### C10 — Integrated summaries and sensitivity analysis

Join pangenome functions, KEGG reconstruction, transporter evidence, gapseq predictions, genome quality, dRep status, clade, and reference status. Produce descriptive and clade-aware analyses with sensitivity to completeness, contamination, fragmentation, genome size, singleton references, and uneven clade sizes.

## 7. Channel and checkpoint design

Use typed tuple channels carrying at minimum:

```text
meta(genome_id, dataset, genome_type, reference_status), fasta, sha256
```

Never recover biological metadata by parsing task filenames. Each stage must emit both scientific outputs and a compact validation record. A checkpoint JSON is created only after its validator passes and must contain input hashes, image/database versions, command/process name, metrics, timestamp, and status.

The main workflow gates downstream branches on validated checkpoint artifacts:

```text
C01 -> CheckM2 + GTDB-Tk -> C02 -> C03 -> dRep -> C04
C04 -> Prokka -> C05 -> Panaroo -> C06
C06 -> eggNOG + KOfam -> C07 -> KEGG reconstruction -> C08
C04/C05 -> per-genome gapseq -> C09
C08 + C09 + clade metadata -> C10
```

## 8. Execution profiles and resource policy

- `base`: common parameters, error strategy, process labels, publishing rules, trace/report defaults.
- `singularity`: enable Singularity, auto-mounts as appropriate, explicit read-only DB binds, external cache path.
- `local`: bounded CPUs/memory for this non-scheduler host.
- `slurm`: define but do not enable unless Slurm is detected and tested.
- Labels: `process_small`, `process_medium`, `process_large`, `process_memory_heavy`.
- Retry only transient exit conditions; schema, biological-data, and validation failures terminate without retry.
- Publish irreplaceable outputs with copy semantics. Work cache is never the sole result copy.
- Launch with `LC_ALL=C` because this CentOS 7 host does not provide `C.UTF-8`.

## 9. Testing strategy

1. Static checks: `nextflow config`, script syntax/unit tests, controlled-value schemas.
2. Container checks: exact versions, executables, read-only database binds, image hashes.
3. Four-genome smoke test spanning Bosanjin, SMGC, ELSG, and External datasets; this tests file/data diversity, not clade diversity.
4. Failure fixtures: duplicate ID, zero-byte FASTA, corrupt gzip, invalid alphabet, missing QC row, duplicate content under conflicting IDs, malformed KOfam result, and broken Panaroo mapping.
5. Resume test: intentionally stop after a checkpoint and prove `-resume` does not rerun valid upstream tasks.
6. Small end-to-end test through reporting before any 400-genome production launch.

## 10. Implementation sequence

1. Scaffold repository, `.gitignore`, README, configs, schemas, and test harness.
2. Implement provenance plus C01 manifest validation first.
3. Implement C02 CheckM2 and GTDB-Tk modules with normalizers and smoke tests.
4. Implement C03 policy engine and frozen-manifest validator.
5. Locate/pin dRep, then implement and test C04.
6. Implement Prokka/Panaroo and validate full gene-cluster mappings.
7. Implement eggNOG/KOfam branches and evidence projection.
8. Implement the licensed/versioned KEGG logic layer only after its definition source is resolved.
9. Implement per-genome gapseq and medium-specific gap filling.
10. Implement integrated summaries, sensitivity analyses, and final report.
11. Run the small end-to-end fixture, then launch production with a new immutable run ID and durable logs.

## 11. Decisions and unresolved prerequisites

Accepted decisions:

- Use GTDB-Tk 2.6.1 with GTDB r226, not the legacy 2.5.2 image.
- Keep the reusable workflow separate from project inputs/results.
- Preserve the existing scientific filter and dRep policies from the project AGENTS.md.

Resolve before the affected production stage:

- exact CheckM2 database release identifier and immutable manifest;
- authorized versioned KEGG module/reaction definition source;
- full gapseq self-test and medium definitions;
- accepted biological clade map and replicate eligibility;
- local resource estimates after smoke benchmarking.

No production checkpoint should be marked passed while its prerequisite remains unresolved.

Implementation status (2026-09-15): C00-C10 workflow code, validators, checkpoint gates, medium-specific gapseq filling, integrated summaries, synthetic logic fixtures, end-to-end smoke testing, and resume testing are implemented. Production C08 still requires an authorized versioned definition input, and inferential clade analysis remains disabled unless an accepted clade map is supplied.
