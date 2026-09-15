process VALIDATE_C05 {
 label 'process_small'; tag params.run_id
 publishDir "${params.outdir}", mode:'copy', overwrite:true, saveAs:{ n -> n=='C05.json' ? "checkpoints/${n}" : "06_prokka/${n}" }
 input:
 path representatives
 path gffs
 path faas
 path ffns
 path gbks
 output:
 path 'prokka_manifest.tsv', emit: manifest
 path 'C05.json', emit: checkpoint
 script:
 """
 python3 ${projectDir}/bin/validate_prokka.py --representatives '${representatives}' \
  --gff ${gffs.join(' ')} --faa ${faas.join(' ')} --ffn ${ffns.join(' ')} --gbk ${gbks.join(' ')} \
  --manifest prokka_manifest.tsv --checkpoint C05.json --run-id '${params.run_id}'
 """
}

process BUILD_FUNCTION_EVIDENCE {
 label 'process_small'; tag params.run_id
 publishDir "${params.outdir}", mode:'copy', overwrite:true, saveAs:{ n -> n=='C07.json' ? "checkpoints/${n}" : "10_function_evidence/${n}" }
 input: path mapping; path eggnog; path kofam
 output:
 path 'functional_evidence.tsv', emit: evidence
 path 'genome_ko_matrix.tsv', emit: ko_matrix
 path 'C07.json', emit: checkpoint
 script:
 """
 python3 ${projectDir}/bin/build_function_evidence.py --mapping '${mapping}' --eggnog '${eggnog}' \
  --kofam '${kofam}' --evidence functional_evidence.tsv --ko-matrix genome_ko_matrix.tsv \
  --checkpoint C07.json --run-id '${params.run_id}'
 """
}

process RECONSTRUCT_MODULES {
 label 'process_small'; tag params.run_id
 publishDir "${params.outdir}", mode:'copy', overwrite:true, saveAs:{ n -> n=='C08.json' ? "checkpoints/${n}" : "11_kegg_modules/${n}" }
 input: path evidence; path definitions
 output:
 path 'module_reconstruction.tsv', emit: modules
 path 'C08.json', emit: checkpoint
 script:
 """
 python3 ${projectDir}/bin/reconstruct_modules.py --evidence '${evidence}' --definitions '${definitions}' \
  --definition-version '${params.module_definitions_version}' --output module_reconstruction.tsv \
  --checkpoint C08.json --run-id '${params.run_id}'
 """
}
