include { GAPSEQ_FIND; GAPSEQ_TRANSPORT; GAPSEQ_DRAFT } from '../../modules/local/gapseq'
workflow GENOME_METABOLISM {
 take: proteomes
 main:
 GAPSEQ_FIND(proteomes)
 GAPSEQ_TRANSPORT(proteomes)
 found_by_id=GAPSEQ_FIND.out.found.map { m,r,p -> tuple(m.genome_id,m,r,p) }
transport_by_id=GAPSEQ_TRANSPORT.out.transporters.map { m,t -> tuple(m.genome_id,t) }
draft_inputs=found_by_id.join(transport_by_id).map { id,m,r,p,t -> tuple(m,r,p,t) }
GAPSEQ_DRAFT(draft_inputs)
 emit: models=GAPSEQ_DRAFT.out.models
}
