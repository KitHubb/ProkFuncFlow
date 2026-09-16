process ANVIO_GENOME_KEGG {
    label 'process_large'
    tag meta.genome_id
    container params.anvio_container
    publishDir "${params.outdir}/11_kegg_modules/genomes", mode: 'copy', overwrite: true,
        saveAs: { name -> "${meta.genome_id}/${name}" }

    input:
    tuple val(meta), path(fasta)

    output:
    tuple val(meta), path("${meta.genome_id}_modules.txt"),
        path("${meta.genome_id}_module_paths.txt"),
        path("${meta.genome_id}_module_steps.txt"),
        path("${meta.genome_id}_hits.txt"),
        path("${meta.genome_id}-CONTIGS.db"), emit: results

    script:
    """
    export PATH='${params.anvio_bin_dir}':\$PATH
    case '${fasta}' in
      *.gz) gzip -cd '${fasta}' > '${meta.genome_id}.fna' ;;
      *) cp -L '${fasta}' '${meta.genome_id}.fna' ;;
    esac

    anvi-gen-contigs-database \
      -f '${meta.genome_id}.fna' \
      -o '${meta.genome_id}-CONTIGS.db' \
      -n '${meta.genome_id}' \
      --num-threads ${task.cpus}

    anvi-run-kegg-kofams \
      -c '${meta.genome_id}-CONTIGS.db' \
      --kegg-data-dir '${params.anvio_kegg_data}' \
      --num-threads ${task.cpus}

    anvi-estimate-metabolism \
      -c '${meta.genome_id}-CONTIGS.db' \
      --kegg-data-dir '${params.anvio_kegg_data}' \
      --module-completion-threshold ${params.anvio_module_completion_threshold} \
      --output-modes modules,module_paths,module_steps,hits \
      -O '${meta.genome_id}'

    for output in '${meta.genome_id}_modules.txt' \
                  '${meta.genome_id}_module_paths.txt' \
                  '${meta.genome_id}_module_steps.txt' \
                  '${meta.genome_id}_hits.txt' \
                  '${meta.genome_id}-CONTIGS.db'; do
      test -s "\$output"
    done
    """
}

process VALIDATE_ANVIO_C08 {
    label 'process_small'
    tag params.run_id
    container params.anvio_container
    publishDir "${params.outdir}", mode: 'copy', overwrite: true,
        saveAs: { name -> name == 'C08.json' ? "checkpoints/${name}" : "11_kegg_modules/${name}" }

    input:
    path representatives
    path modules
    path module_paths
    path module_steps
    path hits
    path contigs_dbs

    output:
    path 'module_reconstruction.tsv', emit: modules
    path 'module_missing_steps.tsv', emit: missing_steps
    path 'anvio_module_paths.tsv', emit: paths
    path 'anvio_module_steps.tsv', emit: steps
    path 'anvio_kofam_hits.tsv', emit: hits
    path 'anvio_database_manifest.tsv', emit: database_manifest
    path 'C08.json', emit: checkpoint

    script:
    """
    python3 ${projectDir}/bin/validate_anvio_metabolism.py \
      --representatives '${representatives}' \
      --modules ${modules.join(' ')} \
      --module-paths ${module_paths.join(' ')} \
      --module-steps ${module_steps.join(' ')} \
      --hits ${hits.join(' ')} \
      --contigs-dbs ${contigs_dbs.join(' ')} \
      --kegg-data-dir '${params.anvio_kegg_data}' \
      --strict-threshold ${params.anvio_module_completion_threshold} \
      --sensitivity-threshold ${params.anvio_module_sensitivity_threshold} \
      --modules-output module_reconstruction.tsv \
      --missing-output module_missing_steps.tsv \
      --paths-output anvio_module_paths.tsv \
      --steps-output anvio_module_steps.tsv \
      --hits-output anvio_kofam_hits.tsv \
      --database-manifest anvio_database_manifest.tsv \
      --checkpoint C08.json --run-id '${params.run_id}'
    """
}
