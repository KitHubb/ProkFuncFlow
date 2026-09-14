process GTDBTK {
    tag meta.genome_id
    label 'process_large'
    container params.gtdbtk_container
    publishDir "${params.outdir}/03_gtdbtk/raw", mode: 'copy', overwrite: true, saveAs: { name -> "${meta.genome_id}/${name}" }

    input:
    tuple val(meta), path(fasta)

    output:
    tuple val(meta), path("${meta.genome_id}.gtdbtk.tsv"), emit: summaries


    script:
    """
    mkdir genomes
    export GTDBTK_DATA_PATH='${params.gtdbtk_db}'
    cp -L '${fasta}' 'genomes/${meta.genome_id}.fna'
    gtdbtk classify_wf --genome_dir genomes --out_dir gtdbtk \
      --extension fna --cpus ${task.cpus} --skip_ani_screen
    test -s gtdbtk/gtdbtk.bac120.summary.tsv
    cp gtdbtk/gtdbtk.bac120.summary.tsv '${meta.genome_id}.gtdbtk.tsv'
    """
}
