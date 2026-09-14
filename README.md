# Lawsonella MAG functional workflow

Reusable Nextflow DSL2 workflow implementing the checkpointed Lawsonella MAG
analysis described in `IMPLEMENTATION_PLAN.md`. C00-C02 are currently
implemented.

## Smoke test

```bash
LC_ALL=C nextflow run main.nf -profile singularity,local \
  --manifest /data/home2/ksy/260914_Lawsonella_pangenome/config/smoke_genomes.tsv \
  --analysis_config config/analysis.yml --run_id smoke_c00_c02 \
  --outdir results/smoke_c00_c02
```

Use `-resume` after correcting an interrupted task. A successful run writes
`checkpoints/C00.json`, `C01.json`, and `C02.json`; checkpoint files are emitted
only by validators that have passed all acceptance checks.
# ProkFuncFlow
