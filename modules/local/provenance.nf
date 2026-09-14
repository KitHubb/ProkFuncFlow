process C00_AUDIT {
    tag params.run_id
    label 'process_small'
    publishDir "${params.outdir}", mode: 'copy', overwrite: true, saveAs: { name -> name == 'C00.json' ? "checkpoints/${name}" : "00_provenance/${name}" }

    input:
    path analysis_config

    output:
    path 'environment.json'
    path 'container_checksums.tsv'
    path 'software_versions.tsv'
    path 'C00.json', emit: checkpoint

    script:
    """
    python3 ${projectDir}/bin/audit_environment.py \
      --analysis-config '${analysis_config}' --project-dir '${projectDir}' --run-id '${params.run_id}' \
      --outdir '${params.outdir}' --checkm2-container '${params.checkm2_container}' \
      --gtdbtk-container '${params.gtdbtk_container}' \
      --checkm2-db '${params.checkm2_db}' --gtdbtk-db '${params.gtdbtk_db}' \
      --environment environment.json --containers container_checksums.tsv \
      --versions software_versions.tsv --checkpoint C00.json
    """
}
