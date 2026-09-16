nextflow.enable.dsl = 2

process CHECKM2_VERSION {
  container params.checkm2_container
  output: path 'checkm2.ok'
  script: """checkm2 --version > checkm2.ok"""
}
process GTDBTK_VERSION {
  container params.gtdbtk_container
  output: path 'gtdbtk.ok'
  script: """gtdbtk --version > gtdbtk.ok"""
}
process DREP_VERSION {
  container params.drep_container
  output: path 'drep.ok'
  script: """python -c 'import importlib.metadata as m; print(m.version("drep"))' > drep.ok"""
}
process PROKKA_VERSION {
  container params.prokka_container
  output: path 'prokka.ok'
  script: """${params.prokka_executable} --version > prokka.ok"""
}
process PANAROO_VERSION {
  container params.panaroo_container
  output: path 'panaroo.ok'
  script: """${params.panaroo_executable} --version > panaroo.ok"""
}
process EGGNOG_VERSION {
  container params.eggnog_container
  output: path 'eggnog.ok'
  script: """emapper.py --version > eggnog.ok 2>&1"""
}
process KOFAM_VERSION {
  container params.kofam_container
  output: path 'kofam.ok'
  script: """exec_annotation --help > kofam.ok 2>&1"""
}
process GAPSEQ_VERSION {
  container params.gapseq_container
  output: path 'gapseq.ok'
  script: """gapseq -v > gapseq.ok"""
}
process ANVIO_VERSION {
  container params.anvio_container
  output: path 'anvio.ok'
  script: """export PATH='${params.anvio_bin_dir}':\$PATH; anvi-gen-contigs-database --version > anvio.ok"""
}

workflow {
  CHECKM2_VERSION(); GTDBTK_VERSION(); DREP_VERSION(); PROKKA_VERSION()
  PANAROO_VERSION(); EGGNOG_VERSION(); KOFAM_VERSION(); GAPSEQ_VERSION(); ANVIO_VERSION()
}
