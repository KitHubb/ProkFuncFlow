nextflow.enable.dsl = 2

include { C00_AUDIT } from './modules/local/provenance'
include { VALIDATE_MANIFEST } from './modules/local/validate_manifest'
include { CHECKM2 } from './modules/local/checkm2'
include { GTDBTK_BATCH } from './modules/local/gtdbtk_batch'
include { VALIDATE_C02 } from './modules/local/c02_validate'
include { INCLUSION_FILTER } from './modules/local/inclusion_filter'
include { DREP } from './modules/local/drep'
include { PROKKA } from './modules/local/prokka'
include { VALIDATE_C05 } from './modules/local/checkpoints_downstream'
include { VALIDATE_C09; SUMMARIZE_C10 } from './modules/local/finalize'
include { PANGENOME_FUNCTION } from './subworkflows/local/pangenome_function'
include { GENOME_METABOLISM } from './subworkflows/local/genome_metabolism'

workflow {
    if (!params.manifest) error "--manifest is required"
    if (!params.run_id) error "--run_id is required"
    if (!params.outdir) params.outdir = "${projectDir}/results/${params.run_id}"

    manifest_file = file(params.manifest, checkIfExists: true)
    config_file = file(params.analysis_config, checkIfExists: true)

    if (!params.skip_c00) C00_AUDIT(config_file)
    VALIDATE_MANIFEST(manifest_file, config_file)

    genomes = VALIDATE_MANIFEST.out.manifest
        .splitCsv(header: true, sep: '\t')
        .map { row ->
            def meta = [genome_id: row.genome_id, dataset: row.dataset,
                        genome_type: row.genome_type, accession: row.accession,
                        sha256: row.sha256]
            tuple(meta, file(row.staged_fasta, checkIfExists: true))
        }

    CHECKM2(genomes)
    gtdb_fastas = genomes.map { meta, fasta -> fasta }.collect()
    GTDBTK_BATCH(VALIDATE_MANIFEST.out.manifest, gtdb_fastas)

    checkm_files = CHECKM2.out.reports.map { meta, report -> report }.collect()
    gtdb_files = GTDBTK_BATCH.out.summary.collect()
    VALIDATE_C02(VALIDATE_MANIFEST.out.manifest, checkm_files, gtdb_files)
    INCLUSION_FILTER(VALIDATE_C02.out.table)

    drep_fastas = INCLUSION_FILTER.out.manifest.splitCsv(header:true, sep:'\t')
        .map { row -> file(row.staged_fasta, checkIfExists:true) }.collect()
    DREP(INCLUSION_FILTER.out.manifest, drep_fastas)

    if (params.run_downstream) {
        if (!params.module_definitions || !params.module_definitions_version) error "--module_definitions and --module_definitions_version are required for C08"
        definitions = file(params.module_definitions, checkIfExists:true)
        clade_map = file(params.clade_map ?: "${projectDir}/assets/NO_CLADE_MAP.tsv", checkIfExists:true)
        representatives = DREP.out.representatives.splitCsv(header:true, sep:'\t').map { row ->
            def meta=[genome_id:row.genome_id,dataset:row.dataset,genome_type:row.genome_type,accession:row.accession,sha256:row.sha256]
            tuple(meta,file(row.staged_fasta,checkIfExists:true))
        }
        PROKKA(representatives)
        gffs=PROKKA.out.annotations.map{m,g,f,n,b->g}.collect(); faas=PROKKA.out.annotations.map{m,g,f,n,b->f}.collect()
        ffns=PROKKA.out.annotations.map{m,g,f,n,b->n}.collect(); gbks=PROKKA.out.annotations.map{m,g,f,n,b->b}.collect()
        VALIDATE_C05(DREP.out.representatives,gffs,faas,ffns,gbks)
        PANGENOME_FUNCTION(PROKKA.out.annotations,definitions)
        proteomes = PROKKA.out.annotations.map { m,g,f,n,b -> tuple(m,f) }
        GENOME_METABOLISM(proteomes)
        fills=GENOME_METABOLISM.out.filled
        VALIDATE_C09(DREP.out.representatives,GENOME_METABOLISM.out.reactions.collect(),GENOME_METABOLISM.out.pathways.collect(),
          GENOME_METABOLISM.out.transporters.collect(),GENOME_METABOLISM.out.drafts.collect(),fills.map{m,r,x,a,l->r}.collect(),fills.map{m,r,x,a,l->x}.collect(),
          fills.map{m,r,x,a,l->a}.collect(),fills.map{m,r,x,a,l->l}.collect())
        SUMMARIZE_C10(DREP.out.representatives,DREP.out.clusters,PANGENOME_FUNCTION.out.modules,VALIDATE_C09.out.evidence,PANGENOME_FUNCTION.out.evidence,PANGENOME_FUNCTION.out.mapping,clade_map)
    }
}
