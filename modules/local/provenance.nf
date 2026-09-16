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
      --drep-container '${params.drep_container}' \
      --prokka-container '${params.prokka_container}' --panaroo-container '${params.panaroo_container}' \
      --eggnog-container '${params.eggnog_container}' --kofam-container '${params.kofam_container}' \
      --gapseq-container '${params.gapseq_container}' --anvio-container '${params.anvio_container}' \
      --checkm2-db '${params.checkm2_db}' --gtdbtk-db '${params.gtdbtk_db}' \
      --eggnog-db '${params.eggnog_db}' --kofam-profiles '${params.kofam_profiles}' \
      --kofam-ko-list '${params.kofam_ko_list}' --gapseq-db '${params.gapseq_db}' \
      --anvio-kegg-data '${params.anvio_kegg_data}' \
      --environment environment.json --containers container_checksums.tsv \
      --versions software_versions.tsv --checkpoint C00.json
    """
}
