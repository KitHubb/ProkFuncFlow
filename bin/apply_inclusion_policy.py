#!/usr/bin/env python3
import argparse,csv,hashlib,json
from datetime import datetime,timezone
p=argparse.ArgumentParser()
for k in ('input','included','excluded','waterfall','checkpoint','run-id'):p.add_argument('--'+k,required=True)
a=p.parse_args()
with open(a.input,newline='') as f: rows=list(csv.DictReader(f,delimiter='\t'))
seen=set(); included=[]; excluded=[]; counts={'input':len(rows),'completeness':0,'contamination':0,'genus':0,'dataset':0}
for r in rows:
 gid=r['genome_id']
 if gid in seen:raise ValueError('duplicate genome_id: '+gid)
 seen.add(gid); reason=''
 if float(r['completeness'])<90:reason='completeness_below_90'
 else:
  counts['completeness']+=1
  if float(r['contamination'])>=5:reason='contamination_at_or_above_5'
  else:
   counts['contamination']+=1
   if r['gtdb_genus']!='g__Lawsonella':reason='genus_not_Lawsonella'
   else:
    counts['genus']+=1
    if r['dataset']=='UHGC':reason='dataset_overlap_with_SMGC'
    else:counts['dataset']+=1
 if reason:excluded.append(dict(genome_id=gid,dataset=r['dataset'],exclusion_stage='C03',exclusion_code=reason,evidence_file='qc_taxonomy.tsv'))
 else:included.append(r)
if len(included)+len(excluded)!=len(rows):raise ValueError('accounting failure')
with open(a.included,'w',newline='') as f:w=csv.DictWriter(f,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(included)
with open(a.excluded,'w',newline='') as f:w=csv.DictWriter(f,['genome_id','dataset','exclusion_stage','exclusion_code','evidence_file'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(excluded)
with open(a.waterfall,'w') as f:
 f.write('step\tremaining\n')
 for k in ('input','completeness','contamination','genus','dataset'):f.write('{}\t{}\n'.format(k,counts[k]))
h=hashlib.sha256(open(a.input,'rb').read()).hexdigest();cp={'checkpoint':'C03','status':'pass','run_id':a.run_id,'timestamp':datetime.now(timezone.utc).isoformat(),'command':'INCLUSION_FILTER','input_sha256':h,'metrics':{'input':len(rows),'included':len(included),'excluded':len(excluded),'waterfall':counts}}
with open(a.checkpoint,'w') as f:json.dump(cp,f,indent=2,sort_keys=True)
