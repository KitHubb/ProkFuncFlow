process GAPSEQ_FIND {
 label 'process_large'; tag meta.genome_id
 container params.gapseq_container
 containerOptions "--bind ${params.gapseq_db}:/usr/local/share/gapseq/dat/seq/Bacteria:ro"
 publishDir "${params.outdir}/12_gapseq_genomes", mode:'copy', overwrite:true, saveAs:{ n -> "${meta.genome_id}/evidence/${n}" }
 input: tuple val(meta), path(proteins)
 output: tuple val(meta), path("${meta.genome_id}-all-Reactions.tbl"), path("${meta.genome_id}-all-Pathways.tbl"), emit: found
 script:
 """
 gapseq find -p all '${meta.genome_id}.faa'
 test -s '${meta.genome_id}-all-Reactions.tbl'; test -s '${meta.genome_id}-all-Pathways.tbl'
 """
}

process GAPSEQ_TRANSPORT {
 label 'process_large'; tag meta.genome_id
 container params.gapseq_container
 containerOptions "--bind ${params.gapseq_db}:/usr/local/share/gapseq/dat/seq/Bacteria:ro"
 publishDir "${params.outdir}/12_gapseq_genomes", mode:'copy', overwrite:true, saveAs:{ n -> "${meta.genome_id}/evidence/${n}" }
 input: tuple val(meta), path(proteins)
 output: tuple val(meta), path("${meta.genome_id}-Transporter.tbl"), emit: transporters
 script:
 """
 gapseq find-transport '${meta.genome_id}.faa'
 test -s '${meta.genome_id}-Transporter.tbl'
 """
}

process GAPSEQ_DRAFT {
 label 'process_medium'; tag meta.genome_id
 container params.gapseq_container
 containerOptions "--bind ${params.gapseq_db}:/usr/local/share/gapseq/dat/seq/Bacteria:ro"
 publishDir "${params.outdir}/12_gapseq_genomes", mode:'copy', overwrite:true, saveAs:{ n -> "${meta.genome_id}/models/${n}" }
 input:
 tuple val(meta), path(reactions), path(pathways), path(transporters)
 output: tuple val(meta), path("${meta.genome_id}-draft.RDS"), emit: models
 script:
 """
 gapseq draft -r '${reactions}' -t '${transporters}' -p '${pathways}'
 test -s '${meta.genome_id}-draft.RDS'
 """
}
