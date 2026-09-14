process PROKKA {
 label 'process_medium'; tag meta.genome_id
 container params.prokka_container
 publishDir "${params.outdir}/06_prokka", mode:'copy', overwrite:true, saveAs:{ n -> "${meta.genome_id}/${n}" }
 input: tuple val(meta), path(fasta)
 output: tuple val(meta), path("${meta.genome_id}.gff"), path("${meta.genome_id}.faa"), path("${meta.genome_id}.ffn"), path("${meta.genome_id}.gbk"), emit: annotations
 script:
 """
 /prokka-1.15.6/bin/prokka --cpus ${task.cpus} --outdir annotation \
  --prefix '${meta.genome_id}' --locustag '${meta.genome_id.replaceAll('[^A-Za-z0-9]','').take(16)}' \
  --genus Lawsonella --usegenus --compliant '${fasta}'
 for ext in gff faa ffn gbk; do test -s "annotation/${meta.genome_id}.\$ext"; cp "annotation/${meta.genome_id}.\$ext" .; done
 """
}
