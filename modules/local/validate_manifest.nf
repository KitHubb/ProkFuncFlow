process VALIDATE_MANIFEST {
    tag params.run_id
    label 'process_small'
    publishDir "${params.outdir}", mode: 'copy', overwrite: true, saveAs: { name -> name == 'C01.json' ? "checkpoints/${name}" : "01_manifest/${name}" }

    input:
    path manifest
    path analysis_config

    output:
    path 'staged_genomes.tsv', emit: manifest
    path 'manifest_validation.json', emit: report
    path 'C01.json', emit: checkpoint

    script:
    """
    python3 ${projectDir}/bin/validate_manifest.py \
      --manifest '${manifest}' --analysis-config '${analysis_config}' \
      --normalized staged_genomes.tsv --report manifest_validation.json \
      --checkpoint C01.json --run-id '${params.run_id}'
    """
}
