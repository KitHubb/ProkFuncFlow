# ProkFuncFlow

Reusable Nextflow DSL2 workflow for uniform Lawsonella genome QC, taxonomy,
dereplication, pangenome construction, functional annotation, and metabolic
reconstruction. The main path currently connects C00-C07 and the implemented
portion of C09, with checkpoint-validated C01-C04 gates.

## Main workflow

```bash
LC_ALL=C nextflow run main.nf -profile singularity,local \
  --manifest /absolute/path/candidate_manifest.tsv \
  --analysis_config config/analysis.yml --run_id RUN_ID \
  --outdir /absolute/path/results/RUN_ID --run_downstream true
```

C04 jointly dereplicates the C03-filtered genomes using dRep 3.5.0 and fastANI,
then passes only validated representatives to Prokka, Panaroo, eggNOG-mapper,
KofamScan, and per-genome gapseq. Use `-resume` after correcting an interrupted
task.

## Focused C04 smoke test

```bash
LC_ALL=C nextflow run c04.nf -profile singularity,local \
  --filtered_manifest /absolute/path/pre_drep_manifest.tsv \
  --run_id smoke_drep --outdir results/smoke_drep
```

The four-genome smoke test is structural validation only; it does not mean the
full project dataset has been analyzed. Production results, work directories,
databases, and SIF images are not stored in this repository.
