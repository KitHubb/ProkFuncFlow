process VALIDATE_C09 {
 label 'process_small'; tag params.run_id
 publishDir "${params.outdir}", mode:'copy', overwrite:true, saveAs:{ n -> n=='C09.json' ? "checkpoints/${n}" : "12_gapseq_summary/${n}" }
 input:
 path representatives
 path reactions
 path pathways
 path transporters
 path drafts
 path filled
 path xmls
 path added
 path logs
 output:
 path 'reaction_evidence.tsv', emit: evidence
 path 'gapseq_models.tsv', emit: manifest
 path 'C09.json', emit: checkpoint
 script:
 """
 export PROKFUNCFLOW_C09_SCHEMA=4
 python3 ${projectDir}/bin/validate_gapseq.py --representatives '${representatives}' \
  --reactions ${reactions.join(' ')} --pathways ${pathways.join(' ')} \
  --transporters ${transporters.join(' ')} --drafts ${drafts.join(' ')} \
  --filled ${filled.join(' ')} --xmls ${xmls.join(' ')} --added ${added.join(' ')} --logs ${logs.join(' ')} \
  --medium '${params.gapseq_medium_name}' --evidence reaction_evidence.tsv \
  --manifest gapseq_models.tsv --checkpoint C09.json --run-id '${params.run_id}'
 """
}

process SUMMARIZE_C10 {
 label 'process_small'; tag params.run_id
 publishDir "${params.outdir}", mode:'copy', overwrite:true, saveAs:{ n -> n=='C10.json' ? "checkpoints/${n}" : "13_summary/${n}" }
 input:
 path representatives
 path clusters
 path modules
 path reactions
 path functional_evidence
 path mapping
 path clade_map
 output:
 path 'genome_summary.tsv', emit: genomes
 path 'clade_summary.tsv', emit: clades
 path 'sensitivity_analysis.tsv', emit: sensitivity
 path 'report.md', emit: report
 path 'C10.json', emit: checkpoint
 script:
 def cladeArg = clade_map.name == 'NO_CLADE_MAP.tsv' ? '' : "--clade-map '${clade_map}'"
 """
 python3 ${projectDir}/bin/summarize_results.py --representatives '${representatives}' \
  --clusters '${clusters}' --modules '${modules}' --reactions '${reactions}' \
  --functional-evidence '${functional_evidence}' --mapping '${mapping}' ${cladeArg} \
  --genome-summary genome_summary.tsv --clade-summary clade_summary.tsv \
  --sensitivity sensitivity_analysis.tsv --report report.md --checkpoint C10.json \
  --run-id '${params.run_id}'
 """
}
