include { PANAROO } from '../../modules/local/panaroo'
include { EGGNOG_MAPPER } from '../../modules/local/eggnog_mapper'
include { KOFAMSCAN } from '../../modules/local/kofamscan'
include { BUILD_FUNCTION_EVIDENCE } from '../../modules/local/checkpoints_downstream'
workflow PANGENOME_FUNCTION {
 take: annotations
 main:
 gffs=annotations.map{m,g,f,n,b->g}.collect(); faas=annotations.map{m,g,f,n,b->f}.collect()
 PANAROO(gffs,faas)
 EGGNOG_MAPPER(PANAROO.out.proteins)
 KOFAMSCAN(PANAROO.out.proteins)
 BUILD_FUNCTION_EVIDENCE(PANAROO.out.mapping,EGGNOG_MAPPER.out.annotations,KOFAMSCAN.out.detail)
 emit:
 proteins=PANAROO.out.proteins
 mapping=PANAROO.out.mapping
 eggnog=EGGNOG_MAPPER.out.annotations
 kofam=KOFAMSCAN.out.detail
 evidence=BUILD_FUNCTION_EVIDENCE.out.evidence
}
