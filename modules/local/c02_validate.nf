process VALIDATE_C02 {
    tag params.run_id
    label 'process_small'
    publishDir "${params.outdir}", mode: 'copy', overwrite: true, saveAs: { name -> name == 'C02.json' ? "checkpoints/${name}" : "02_qc_taxonomy/${name}" }

    input:
    path manifest
    path checkm_reports
    path gtdb_summaries

    output:
    path 'qc_taxonomy.tsv', emit: table
    path 'c02_validation.json', emit: report
    path 'C02.json', emit: checkpoint

    script:
    """
    python3 ${projectDir}/bin/normalize_c02.py --manifest '${manifest}' \
      --checkm2 ${checkm_reports.join(' ')} --gtdbtk ${gtdb_summaries.join(' ')} \
      --output qc_taxonomy.tsv --report c02_validation.json \
      --checkpoint C02.json --run-id '${params.run_id}'
    """
}
