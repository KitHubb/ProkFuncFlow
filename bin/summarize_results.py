#!/usr/bin/env python3
import argparse,csv,hashlib,json,statistics
from collections import defaultdict
from datetime import datetime,timezone
p=argparse.ArgumentParser()
for x in ('representatives','clusters','modules','reactions','functional-evidence','mapping','genome-summary','clade-summary','sensitivity','report','checkpoint','run-id'):p.add_argument('--'+x,required=True)
p.add_argument('--clade-map');a=p.parse_args()
def read(path):
 with open(path,newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
reps=read(a.representatives);clusters=read(a.clusters);mods=read(a.modules);rxns=read(a.reactions);func=read(a.functional_evidence);maps=read(a.mapping);clades={}
if a.clade_map:
 for r in read(a.clade_map):clades[r['genome_id']]=r['clade']
module=defaultdict(list);rx=defaultdict(list);cluster={};pangenes=defaultdict(set);annotated=defaultdict(set)
for r in maps:pangenes[r['genome_id']].add(r['cluster_id'])
for r in func:annotated[r['genome_id']].add(r['cluster_id'])
for r in mods:module[r['genome_id']].append(r)
for r in rxns:rx[r['genome_id']].append(r)
for r in clusters:
 if r['drep_representative']=='true':cluster[r['genome_id']]=r['drep_cluster']
fields=['genome_id','dataset','genome_type','clade','clade_weight','drep_cluster','completeness','contamination','genome_size_bp','contig_count','pangenome_clusters','annotated_clusters','complete_modules','incomplete_modules','sequence_reactions','transporter_candidates','gap_filled_reactions']
summary=[]
for r in reps:
 gid=r['genome_id'];m=module[gid];g=rx[gid]
 path=r['staged_fasta'];size=contigs=0
 with open(path,encoding='ascii') as fasta:
  for line in fasta:
   if line.startswith('>'):contigs+=1
   else:size+=len(line.strip())
 summary.append({'genome_id':gid,'dataset':r['dataset'],'genome_type':r['genome_type'],'clade':clades.get(gid,'unassigned'),'clade_weight':0,'drep_cluster':cluster.get(gid,r.get('drep_cluster','NA')),'completeness':r['completeness'],'contamination':r['contamination'],'genome_size_bp':size,'contig_count':contigs,'pangenome_clusters':len(pangenes[gid]),'annotated_clusters':len(annotated[gid]),'complete_modules':sum(x['state']=='complete' for x in m),'incomplete_modules':sum(x['state']=='incomplete' for x in m),'sequence_reactions':sum(x['evidence_class']=='sequence_detected' for x in g),'transporter_candidates':sum(x['evidence_class']=='transporter_candidate' for x in g),'gap_filled_reactions':sum(x['evidence_class']=='gap_filled' for x in g)})
by=defaultdict(list)
for r in summary:by[r['clade']].append(r)
for r in summary:r['clade_weight']=1.0/len(by[r['clade']])
with open(a.genome_summary,'w',newline='') as f:
 w=csv.DictWriter(f,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(summary)
with open(a.clade_summary,'w',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['clade','genomes','mean_completeness','mean_contamination','mean_complete_modules','mean_sequence_reactions','inferential_comparison_enabled'])
 for c,rs in sorted(by.items()):w.writerow([c,len(rs),'%.3f'%statistics.mean(float(x['completeness']) for x in rs),'%.3f'%statistics.mean(float(x['contamination']) for x in rs),'%.3f'%statistics.mean(x['complete_modules'] for x in rs),'%.3f'%statistics.mean(x['sequence_reactions'] for x in rs),str(c!='unassigned' and len(by)>1).lower()])
median_contigs=statistics.median([r['contig_count'] for r in summary])
sizes=sorted(r['genome_size_bp'] for r in summary);lo=sizes[len(sizes)//4];hi=sizes[(3*len(sizes))//4]
scenarios={'all':summary,'completeness_ge_95':[r for r in summary if float(r['completeness'])>=95],'contamination_lt_1':[r for r in summary if float(r['contamination'])<1],'MAG_only':[r for r in summary if r['genome_type']=='MAG'],'references_only':[r for r in summary if r['genome_type']!='MAG'],'contigs_le_median':[r for r in summary if r['contig_count']<=median_contigs],'genome_size_iqr':[r for r in summary if lo<=r['genome_size_bp']<=hi],'exclude_singleton_clades':[r for r in summary if len(by[r['clade']])>1]}
with open(a.sensitivity,'w',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['scenario','genomes','mean_complete_modules','mean_sequence_reactions'])
 for name,rs in scenarios.items():w.writerow([name,len(rs),'%.3f'%statistics.mean([r['complete_modules'] for r in rs]) if rs else 'NA','%.3f'%statistics.mean([r['sequence_reactions'] for r in rs]) if rs else 'NA'])
with open(a.report,'w') as f:
 f.write('# ProkFuncFlow integrated report\n\nGenome-derived hypotheses only; experimental validation is required.\n\n')
 f.write('- Representatives: %d\n- Clades: %d\n- Formal module calls: %d\n- Reaction evidence rows: %d\n- Inferential clade comparison: %s\n'%(len(summary),len(by),len(mods),len(rxns),'enabled' if len(by)>1 and 'unassigned' not in by else 'disabled'))
cp={'checkpoint':'C10','status':'pass','run_id':a.run_id,'timestamp':datetime.now(timezone.utc).isoformat(),'command':'INTEGRATED_SUMMARIZE','input_sha256':hashlib.sha256(open(a.representatives,'rb').read()).hexdigest(),'metrics':{'representatives':len(summary),'clades':len(by),'module_calls':len(mods),'reaction_evidence_rows':len(rxns),'functional_evidence_rows':len(func),'pangenome_mapping_rows':len(maps)},'parameters':{'unassigned_clade_disables_inference':True,'sensitivity_scenarios':list(scenarios)}}
with open(a.checkpoint,'w') as f:json.dump(cp,f,indent=2,sort_keys=True)
