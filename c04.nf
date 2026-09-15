nextflow.enable.dsl = 2

include { DREP } from './modules/local/drep'

workflow {
    if (!params.filtered_manifest) error "--filtered_manifest is required"
    if (!params.run_id) error "--run_id is required"
    if (!params.outdir) params.outdir = "${projectDir}/results/${params.run_id}"

    filtered_manifest = Channel.fromPath(params.filtered_manifest, checkIfExists: true)
    staged_fastas = filtered_manifest
        .splitCsv(header: true, sep: '\t')
        .map { row -> file(row.staged_fasta, checkIfExists: true) }
        .collect()

    DREP(filtered_manifest, staged_fastas)
}
