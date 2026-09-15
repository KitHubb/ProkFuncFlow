process GAPSEQ_FILL {
 label 'process_large'; tag meta.genome_id
 container params.gapseq_container
 publishDir "${params.outdir}/12_gapseq_genomes", mode:'copy', overwrite:true, saveAs:{ n -> "${meta.genome_id}/gapfill/${params.gapseq_medium_name}/${n}" }
 input: tuple val(meta), path(draft)
 output: tuple val(meta), path("${meta.genome_id}.gapfilled.RDS"), path("${meta.genome_id}.gapfilled.xml"), path("${meta.genome_id}.added_reactions.tsv"), path("${meta.genome_id}.fill.log"), emit: filled
 script:
 """
 mkdir fill
 gapseq fill -m '${draft}' -n '${params.gapseq_medium}' -f fill -q TRUE > '${meta.genome_id}.fill.log' 2>&1
 test -s "fill/${meta.genome_id}.RDS"; test -s "fill/${meta.genome_id}.xml"
 mv "fill/${meta.genome_id}.RDS" '${meta.genome_id}.gapfilled.RDS'
 mv "fill/${meta.genome_id}.xml" '${meta.genome_id}.gapfilled.xml'
 Rscript - '${draft}' '${meta.genome_id}.gapfilled.RDS' '${meta.genome_id}.added_reactions.tsv' <<'RS'
args <- commandArgs(trailingOnly=TRUE); before <- readRDS(args[1]); after <- readRDS(args[2])
added <- setdiff(slot(after, 'react_id'), slot(before, 'react_id'))
write.table(data.frame(reaction_id=added, evidence_class='gap_filled'), args[3], sep='\t', row.names=FALSE, quote=FALSE)
RS
 test -s '${meta.genome_id}.added_reactions.tsv'
 """
}
