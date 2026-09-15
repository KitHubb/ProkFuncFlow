process DREP {
 label 'process_large'; tag params.run_id
 container params.drep_container
 publishDir "${params.outdir}", mode:'copy', overwrite:true, saveAs:{ n -> n=='C04.json' ? "checkpoints/${n}" : (n in ['representative_genomes.tsv','cluster_membership.tsv','genomeInfo.csv'] ? "05_drep/${n}" : "05_drep/raw/${n}") }
 input:
 path manifest
 path staged_fastas
 output:
 path 'representative_genomes.tsv', emit: representatives
 path 'cluster_membership.tsv', emit: clusters
 path 'genomeInfo.csv', emit: genome_info
 path 'drep', emit: raw
 path 'C04.json', emit: checkpoint
 script:
 """
 python3 ${projectDir}/bin/prepare_drep_inputs.py --manifest '${manifest}' \
  --genome-dir genomes --genome-info genomeInfo.csv
 dRep dereplicate drep -g genomes/*.fna --genomeInfo genomeInfo.csv \
  -p ${task.cpus} -pa ${params.drep_primary_ani} -sa ${params.drep_secondary_ani} \
  -nc ${params.drep_min_coverage} --S_algorithm fastANI -comp 0 -con 100
 python3 ${projectDir}/bin/validate_drep.py --manifest '${manifest}' --drep-dir drep \
  --representatives representative_genomes.tsv --clusters cluster_membership.tsv \
  --checkpoint C04.json --run-id '${params.run_id}' \
  --primary-ani ${params.drep_primary_ani} --secondary-ani ${params.drep_secondary_ani} \
  --min-coverage ${params.drep_min_coverage}
 """
}
