#!/usr/bin/env python3
import argparse,csv,hashlib,json,os
from datetime import datetime,timezone
p=argparse.ArgumentParser()
for x in ('representatives','evidence','manifest','checkpoint','run-id','medium'):p.add_argument('--'+x,required=True)
for x in ('reactions','pathways','transporters','drafts','filled','xmls','added','logs'):p.add_argument('--'+x,nargs='+',required=True)
a=p.parse_args()
with open(a.representatives,newline='') as f:reps=list(csv.DictReader(f,delimiter='\t'))
ids={r['genome_id'] for r in reps}
suffix={'reactions':'-all-Reactions.tbl','pathways':'-all-Pathways.tbl','transporters':'-Transporter.tbl','drafts':'-draft.RDS','filled':'.gapfilled.RDS','xmls':'.gapfilled.xml','added':'.added_reactions.tsv','logs':'.fill.log'}
paths={}
for key,suf in suffix.items():
 vals=getattr(a,key);d={os.path.basename(x)[:-len(suf)]:os.path.abspath(x) for x in vals}
 if set(d)!=ids:raise ValueError('%s genome accounting mismatch: %s'%(key,sorted(ids^set(d))))
 if any(os.path.getsize(x)==0 for x in vals):raise ValueError('empty '+key+' output')
 paths[key]=d
for gid in ids:
 with open(paths['logs'][gid],encoding='utf-8',errors='replace') as f:
  if 'Final growth rate:' not in f.read():raise ValueError('gap filling did not report final growth: '+gid)
evidence=[]
for gid in sorted(ids):
 with open(paths['reactions'][gid],newline='',encoding='utf-8',errors='replace') as f:
  lines=(x for x in f if not x.startswith('#'))
  for r in csv.DictReader(lines,delimiter='\t'):
   if r.get('status')=='good_blast':evidence.append([gid,r.get('rxn','-'),r.get('qseqid','-'),'sequence_detected'])
 with open(paths['transporters'][gid],newline='',encoding='utf-8',errors='replace') as f:
  lines=(x for x in f if not x.startswith('#'))
  for r in csv.DictReader(lines,delimiter='\t'):
   for reaction in (x.strip() for x in r.get('rea','').split(',') if x.strip()):evidence.append([gid,reaction,r.get('qseqid','-'),'transporter_candidate'])
 with open(paths['added'][gid],newline='') as f:
  for r in csv.DictReader(f,delimiter='\t'):evidence.append([gid,r['reaction_id'],'-',r['evidence_class']])
with open(a.evidence,'w',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['genome_id','reaction_id','gene_id','evidence_class']);w.writerows(evidence)
with open(a.manifest,'w',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['genome_id','draft_model','gapfilled_model','fill_log','medium'])
 for gid in sorted(ids):w.writerow([gid,paths['drafts'][gid],paths['filled'][gid],paths['logs'][gid],a.medium])
cp={'checkpoint':'C09','status':'pass','run_id':a.run_id,'timestamp':datetime.now(timezone.utc).isoformat(),'command':'GAPSEQ_VALIDATE','input_sha256':hashlib.sha256(open(a.representatives,'rb').read()).hexdigest(),'tool_versions':{'gapseq':'2.1.0','sequence_db':'1.5'},'parameters':{'medium':a.medium,'direct_and_gapfilled_separated':True},'metrics':{'genomes':len(ids),'sequence_evidence_rows':sum(r[3]=='sequence_detected' for r in evidence),'transporter_candidates':sum(r[3]=='transporter_candidate' for r in evidence),'gap_filled_reactions':sum(r[3]=='gap_filled' for r in evidence)}}
with open(a.checkpoint,'w') as f:json.dump(cp,f,indent=2,sort_keys=True)
