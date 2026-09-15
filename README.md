# ProkFuncFlow

Nextflow DSL2 workflow implementing the checkpointed Lawsonella genome analysis from C00 through C10: uniform QC/taxonomy, filtering, dRep, Prokka, Panaroo, eggNOG/Kofam evidence, logical module reconstruction, per-genome gapseq gap filling, and integrated clade-aware summaries.

## Production entrypoint

```bash
LC_ALL=C nextflow run main.nf -profile singularity,local \
  --manifest /absolute/path/candidate_manifest.tsv \
  --analysis_config config/analysis.yml \
  --module_definitions /authorized/versioned/module_definitions.tsv \
  --module_definitions_version VERSION \
  --clade_map /absolute/path/clades.tsv \
  --run_id RUN_ID --outdir /absolute/path/results/RUN_ID \
  --run_downstream true
```

The module-definition TSV requires `module_id`, `name`, and `definition`. Supported operators are whitespace (AND), `+` (complex AND), `,` (alternative OR), `-` (optional), and parentheses. Formal module calls use threshold-passing Kofam evidence; eggNOG pathway fields are retained only as broad annotations.

The default C09 medium is the gapseq 2.1.0 image's `gut.csv`; override `--gapseq_medium` and `--gapseq_medium_name` for another validated medium. If `--clade_map` is omitted, all representatives are `unassigned` and inferential comparisons are disabled.

## Focused entrypoints

Run C04 from a frozen C03 manifest:

```bash
LC_ALL=C nextflow run c04.nf -profile singularity,local \
  --filtered_manifest /absolute/path/pre_drep_manifest.tsv \
  --run_id smoke_drep --outdir results/smoke_drep
```

Run C05-C10 from validated C04 outputs:

```bash
LC_ALL=C nextflow run downstream.nf -profile singularity,local -resume \
  --representatives_manifest /absolute/path/representative_genomes.tsv \
  --clusters_manifest /absolute/path/cluster_membership.tsv \
  --module_definitions /authorized/versioned/module_definitions.tsv \
  --module_definitions_version VERSION \
  --run_id RUN_ID --outdir /absolute/path/results/RUN_ID
```

Every validator writes `checkpoints/C00.json` through `C10.json` only after its acceptance checks pass. Results, work directories, databases, and SIF images are intentionally excluded from Git. The bundled synthetic module definitions are test fixtures only and are not biological results.
