#!/usr/bin/env python3
import argparse,csv,hashlib,json,re
from collections import defaultdict
from datetime import datetime,timezone
p=argparse.ArgumentParser()
for x in ('mapping','eggnog','kofam','evidence','ko-matrix','checkpoint','run-id'):p.add_argument('--'+x,required=True)
a=p.parse_args();maps=[]
with open(a.mapping,newline='') as f:maps=list(csv.DictReader(f,delimiter='\t'))
bycluster=defaultdict(list)
for r in maps:bycluster[r['cluster_id']].append(r)
egg={}
with open(a.eggnog,newline='') as f:
 lines=(x for x in f if not x.startswith('##'))
 for r in csv.DictReader(lines,delimiter='\t'):egg[r['#query']]=r
kof=[]
with open(a.kofam) as f:
 for line in f:
  if not line.startswith('*'):continue
  x=line.rstrip('\n').split('\t')
  if len(x)<7:raise ValueError('malformed accepted Kofam row')
  kof.append({'cluster':x[1],'ko':x[2],'threshold':x[3],'score':x[4],'evalue':x[5],'definition':x[6].strip('"')})
if not kof:raise ValueError('no threshold-passing Kofam calls')
fields=['genome_id','gene_id','cluster_id','evidence_source','ko','ec','reaction','score','threshold','evalue','description']
rows=[];kos=defaultdict(set)
for k in kof:
 if k['cluster'] not in bycluster:raise ValueError('Kofam query absent from mapping: '+k['cluster'])
 er=egg.get(k['cluster'],{});ecs=re.findall(r'\d+\.\d+\.\d+\.[\d-]+',k['definition']);rx=er.get('KEGG_Reaction','-')
 for m in bycluster[k['cluster']]:
  kos[m['genome_id']].add(k['ko'])
  rows.append([m['genome_id'],m['gene_id'],k['cluster'],'Kofam',k['ko'],';'.join(ecs) or '-',rx,k['score'],k['threshold'],k['evalue'],k['definition']])
for cluster,er in egg.items():
 if cluster not in bycluster:continue
 for m in bycluster[cluster]:
  rows.append([m['genome_id'],m['gene_id'],cluster,'eggNOG',er.get('KEGG_ko','-'),er.get('EC','-'),er.get('KEGG_Reaction','-'),er.get('score','-'),'-',er.get('evalue','-'),er.get('Description','-')])
with open(a.evidence,'w',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(fields);w.writerows(rows)
allko=sorted({x for v in kos.values() for x in v})
with open(a.ko_matrix,'w',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['genome_id']+allko)
 for g in sorted({r['genome_id'] for r in maps}):w.writerow([g]+[int(k in kos[g]) for k in allko])
cp={'checkpoint':'C07','status':'pass','run_id':a.run_id,'timestamp':datetime.now(timezone.utc).isoformat(),'command':'FUNCTION_EVIDENCE_VALIDATE','input_sha256':hashlib.sha256(open(a.mapping,'rb').read()).hexdigest(),'tool_versions':{'eggnog_mapper':'2.1.15','kofamscan':'1.3.0'},'parameters':{'formal_ko_source':'Kofam threshold-passing calls','eggnog_role':'broad annotation only'},'metrics':{'mapping_rows':len(maps),'accepted_kofam_calls':len(kof),'evidence_rows':len(rows),'genomes':len({r['genome_id'] for r in maps})}}
with open(a.checkpoint,'w') as f:json.dump(cp,f,indent=2,sort_keys=True)
