nextflow.enable.dsl = 2
include { PROKKA } from './modules/local/prokka'
include { PANGENOME_FUNCTION } from './subworkflows/local/pangenome_function'
include { GENOME_METABOLISM } from './subworkflows/local/genome_metabolism'
workflow {
 if (!params.representatives_manifest) error '--representatives_manifest from validated C04 is required'
 if (!params.run_id) error '--run_id is required'
 if (!params.outdir) params.outdir="${projectDir}/results/${params.run_id}"
 reps=Channel.fromPath(params.representatives_manifest,checkIfExists:true).splitCsv(header:true,sep:'\t').map{r->
  def m=[genome_id:r.genome_id,dataset:r.dataset,genome_type:r.genome_type,accession:r.accession,sha256:r.sha256]
  tuple(m,file(r.staged_fasta,checkIfExists:true))
 }
 PROKKA(reps)
 PANGENOME_FUNCTION(PROKKA.out.annotations)
 GENOME_METABOLISM(PROKKA.out.annotations.map{m,g,f,n,b->tuple(m,f)})
}
