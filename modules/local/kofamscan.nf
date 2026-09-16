process KOFAMSCAN {
 label 'process_large'; tag params.run_id
 container params.kofam_container
 publishDir "${params.outdir}/09_kofam", mode:'copy', overwrite:true
 input: path proteins
 output: path 'kofam.detail.tsv', emit: detail
 script:
 """
 exec_annotation --profile '${params.kofam_profiles}' --ko-list '${params.kofam_ko_list}' \
  --cpu ${task.cpus} --format detail-tsv -o kofam.detail.tsv '${proteins}'
 test -s kofam.detail.tsv
 """
}
