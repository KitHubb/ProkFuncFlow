process PANAROO {
 label 'process_large'; tag params.run_id
 container params.panaroo_container
 publishDir "${params.outdir}", mode:'copy', overwrite:true, saveAs:{ n -> n=='C06.json' ? "checkpoints/${n}" : "07_panaroo/${n}" }
 input: path gffs; path faas
 output:
 path 'panaroo/gene_presence_absence.csv', emit: presence
 path 'representative_proteins.faa', emit: proteins
 path 'cluster_gene_genome.tsv', emit: mapping
 path 'panaroo/final_graph.gml', emit: graph
 path 'C06.json', emit: checkpoint
 script:
 """
 ${params.panaroo_executable} -i ${gffs.join(' ')} -o panaroo --clean-mode strict \
  --remove-invalid-genes --threads ${task.cpus}
 test -s panaroo/gene_presence_absence.csv
 python3 ${projectDir}/bin/extract_panaroo_representatives.py \
  --presence panaroo/gene_presence_absence.csv --faa ${faas.join(' ')} \
  --proteins representative_proteins.faa --mapping cluster_gene_genome.tsv
 test -s representative_proteins.faa; test -s cluster_gene_genome.tsv; test -s panaroo/final_graph.gml
 python3 ${projectDir}/bin/validate_panaroo.py --presence panaroo/gene_presence_absence.csv \
  --proteins representative_proteins.faa --mapping cluster_gene_genome.tsv \
  --graph panaroo/final_graph.gml --checkpoint C06.json --run-id '${params.run_id}'
 """
}
