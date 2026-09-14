process GTDBTK_BATCH {
    tag params.run_id
    label 'process_large'
    container params.gtdbtk_container
    publishDir "${params.outdir}/03_gtdbtk/raw", mode: 'copy', overwrite: true

    input:
    path manifest
    path staged_fastas

    output:
    path 'gtdbtk.bac120.summary.tsv', emit: summary

    script:
    """
    python3 ${projectDir}/bin/stage_gtdb_batch.py --manifest '${manifest}' --output-dir genomes
    export GTDBTK_DATA_PATH='${params.gtdbtk_db}'
    gtdbtk classify_wf --genome_dir genomes --out_dir gtdbtk \
      --extension fna --cpus ${task.cpus} --skip_ani_screen
    test -s gtdbtk/gtdbtk.bac120.summary.tsv
    cp gtdbtk/gtdbtk.bac120.summary.tsv gtdbtk.bac120.summary.tsv
    """
}
