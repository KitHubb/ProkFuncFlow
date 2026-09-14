process PANAROO {
 label 'process_large'; tag params.run_id
 container params.panaroo_container
 publishDir "${params.outdir}/07_panaroo", mode:'copy', overwrite:true
 input: path gffs; path faas
 output:
 path 'panaroo/gene_presence_absence.csv', emit: presence
 path 'representative_proteins.faa', emit: proteins
 path 'cluster_gene_genome.tsv', emit: mapping
 script:
 """
 export PATH=/opt/conda/bin:\$PATH
 /opt/conda/bin/panaroo -i ${gffs.join(' ')} -o panaroo --clean-mode strict \
  --remove-invalid-genes --threads ${task.cpus}
 test -s panaroo/gene_presence_absence.csv
 python3 ${projectDir}/bin/extract_panaroo_representatives.py \
  --presence panaroo/gene_presence_absence.csv --faa ${faas.join(' ')} \
  --proteins representative_proteins.faa --mapping cluster_gene_genome.tsv
 test -s representative_proteins.faa; test -s cluster_gene_genome.tsv
 """
}
