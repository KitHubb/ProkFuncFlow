nextflow.enable.dsl = 2

include { C00_AUDIT } from './modules/local/provenance'
include { VALIDATE_MANIFEST } from './modules/local/validate_manifest'
include { CHECKM2 } from './modules/local/checkm2'
include { GTDBTK_BATCH } from './modules/local/gtdbtk_batch'
include { VALIDATE_C02 } from './modules/local/c02_validate'
include { INCLUSION_FILTER } from './modules/local/inclusion_filter'
include { PROKKA } from './modules/local/prokka'
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

    if (params.run_downstream) {
        if (!params.representatives_manifest && !params.smoke_skip_drep) error "Downstream production requires --representatives_manifest from validated C04 dRep"
        reps_source = params.representatives_manifest ? file(params.representatives_manifest, checkIfExists:true) : INCLUSION_FILTER.out.manifest
        representatives = reps_source.splitCsv(header:true, sep:'\t').map { row ->
            def meta=[genome_id:row.genome_id,dataset:row.dataset,genome_type:row.genome_type,accession:row.accession,sha256:row.sha256]
            tuple(meta,file(row.staged_fasta,checkIfExists:true))
        }
        PROKKA(representatives)
        PANGENOME_FUNCTION(PROKKA.out.annotations)
        proteomes = PROKKA.out.annotations.map { m,g,f,n,b -> tuple(m,f) }
        GENOME_METABOLISM(proteomes)
    }
}
