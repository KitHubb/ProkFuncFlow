nextflow.enable.dsl = 2
include { PROKKA } from './modules/local/prokka'
include { VALIDATE_C05 } from './modules/local/checkpoints_downstream'
include { PANGENOME_FUNCTION } from './subworkflows/local/pangenome_function'
include { GENOME_METABOLISM } from './subworkflows/local/genome_metabolism'
include { GENOME_KEGG } from './subworkflows/local/genome_kegg'
include { VALIDATE_C09; SUMMARIZE_C10 } from './modules/local/finalize'
workflow {
 if (!params.representatives_manifest) error '--representatives_manifest from validated C04 is required'
 if (!params.clusters_manifest) error '--clusters_manifest from validated C04 is required'
 if (!params.run_id) error '--run_id is required'
 if (!params.eggnog_db || !params.kofam_profiles || !params.kofam_ko_list || !params.anvio_kegg_data) error 'eggNOG, Kofam, and anvi-o KEGG database paths are required; use -profile server or provide an external config'
 if (!params.outdir) params.outdir="${projectDir}/results/${params.run_id}"
 reps_manifest=Channel.fromPath(params.representatives_manifest,checkIfExists:true)
 clusters=Channel.fromPath(params.clusters_manifest,checkIfExists:true)
 clade_map=Channel.fromPath(params.clade_map ?: "${projectDir}/assets/NO_CLADE_MAP.tsv",checkIfExists:true)
 reps=reps_manifest.splitCsv(header:true,sep:'\t').map{r->
  def m=[genome_id:r.genome_id,dataset:r.dataset,genome_type:r.genome_type,accession:r.accession,sha256:r.sha256]
  tuple(m,file(r.staged_fasta,checkIfExists:true))
 }
 PROKKA(reps)
 gffs=PROKKA.out.annotations.map{m,g,f,n,b->g}.collect();faas=PROKKA.out.annotations.map{m,g,f,n,b->f}.collect()
 ffns=PROKKA.out.annotations.map{m,g,f,n,b->n}.collect();gbks=PROKKA.out.annotations.map{m,g,f,n,b->b}.collect()
 VALIDATE_C05(reps_manifest,gffs,faas,ffns,gbks)
 PANGENOME_FUNCTION(PROKKA.out.annotations)
 GENOME_KEGG(reps,reps_manifest)
 GENOME_METABOLISM(PROKKA.out.annotations.map{m,g,f,n,b->tuple(m,f)})
 fills=GENOME_METABOLISM.out.filled
 VALIDATE_C09(reps_manifest,GENOME_METABOLISM.out.reactions.collect(),GENOME_METABOLISM.out.pathways.collect(),GENOME_METABOLISM.out.transporters.collect(),GENOME_METABOLISM.out.drafts.collect(),fills.map{m,r,x,a,l->r}.collect(),fills.map{m,r,x,a,l->x}.collect(),fills.map{m,r,x,a,l->a}.collect(),fills.map{m,r,x,a,l->l}.collect())
 SUMMARIZE_C10(reps_manifest,clusters,GENOME_KEGG.out.modules,VALIDATE_C09.out.evidence,PANGENOME_FUNCTION.out.evidence,PANGENOME_FUNCTION.out.mapping,clade_map)
}
