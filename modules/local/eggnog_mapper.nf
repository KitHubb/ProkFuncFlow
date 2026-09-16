process EGGNOG_MAPPER {
 label 'process_large'; tag params.run_id
 container params.eggnog_container
 publishDir "${params.outdir}/08_eggnog", mode:'copy', overwrite:true
 input: path proteins
 output: path 'eggnog.emapper.annotations', emit: annotations
 script:
 """
 emapper.py -i '${proteins}' --output eggnog --data_dir '${params.eggnog_db}' \
  --cpu ${task.cpus} --override
 test -s eggnog.emapper.annotations
 """
}
