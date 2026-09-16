include { ANVIO_GENOME_KEGG; VALIDATE_ANVIO_C08 } from '../../modules/local/anvio_metabolism'

workflow GENOME_KEGG {
    take:
    representatives
    representatives_manifest

    main:
    ANVIO_GENOME_KEGG(representatives)
    modules = ANVIO_GENOME_KEGG.out.results.map { meta, m, p, s, h, db -> m }.collect()
    paths = ANVIO_GENOME_KEGG.out.results.map { meta, m, p, s, h, db -> p }.collect()
    steps = ANVIO_GENOME_KEGG.out.results.map { meta, m, p, s, h, db -> s }.collect()
    hits = ANVIO_GENOME_KEGG.out.results.map { meta, m, p, s, h, db -> h }.collect()
    dbs = ANVIO_GENOME_KEGG.out.results.map { meta, m, p, s, h, db -> db }.collect()
    VALIDATE_ANVIO_C08(representatives_manifest, modules, paths, steps, hits, dbs)

    emit:
    modules = VALIDATE_ANVIO_C08.out.modules
    missing_steps = VALIDATE_ANVIO_C08.out.missing_steps
    paths = VALIDATE_ANVIO_C08.out.paths
    steps = VALIDATE_ANVIO_C08.out.steps
    hits = VALIDATE_ANVIO_C08.out.hits
}
