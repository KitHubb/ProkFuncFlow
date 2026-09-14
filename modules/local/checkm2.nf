process CHECKM2 {
    tag meta.genome_id
    label 'process_medium'
    container params.checkm2_container
    publishDir "${params.outdir}/02_checkm2/raw", mode: 'copy', overwrite: true, saveAs: { name -> "${meta.genome_id}/${name}" }

    input:
    tuple val(meta), path(fasta)

    output:
    tuple val(meta), path("${meta.genome_id}.checkm2.tsv"), emit: reports

    script:
    """
    mkdir input
    cp -L '${fasta}' 'input/${meta.genome_id}.fna'
    checkm2 predict --threads ${task.cpus} --input input \
      --output-directory checkm2 --database_path '${params.checkm2_db}'
    test -s checkm2/quality_report.tsv
    cp checkm2/quality_report.tsv '${meta.genome_id}.checkm2.tsv'
    """
}
