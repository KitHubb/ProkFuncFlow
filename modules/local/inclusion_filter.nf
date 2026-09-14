process INCLUSION_FILTER {
 label 'process_small'; tag params.run_id
 publishDir "${params.outdir}", mode:'copy', overwrite:true, saveAs:{ n -> n=='C03.json' ? "checkpoints/${n}" : "04_filter/${n}" }
 input: path qc_taxonomy
 output:
 path 'pre_drep_manifest.tsv', emit: manifest
 path 'exclusion_ledger.tsv', emit: exclusions
 path 'count_waterfall.tsv', emit: waterfall
 path 'C03.json', emit: checkpoint
 script:
 """
 python3 ${projectDir}/bin/apply_inclusion_policy.py --input '${qc_taxonomy}' \
  --included pre_drep_manifest.tsv --excluded exclusion_ledger.tsv \
  --waterfall count_waterfall.tsv --checkpoint C03.json --run-id '${params.run_id}'
 """
}
