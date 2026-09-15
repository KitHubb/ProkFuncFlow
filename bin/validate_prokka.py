#!/usr/bin/env python3
import argparse,csv,hashlib,json,os
from datetime import datetime,timezone
p=argparse.ArgumentParser()
for x in ('representatives','manifest','checkpoint','run-id'):p.add_argument('--'+x,required=True)
p.add_argument('--gff',nargs='+',required=True);p.add_argument('--faa',nargs='+',required=True);p.add_argument('--ffn',nargs='+',required=True);p.add_argument('--gbk',nargs='+',required=True)
a=p.parse_args()
with open(a.representatives,newline='') as f: reps=list(csv.DictReader(f,delimiter='\t'))
ids={r['genome_id'] for r in reps}
if len(ids)!=len(reps) or not ids: raise ValueError('invalid representative manifest')
sets={k:{os.path.basename(x).rsplit('.',1)[0] for x in v} for k,v in {'gff':a.gff,'faa':a.faa,'ffn':a.ffn,'gbk':a.gbk}.items()}
for k,v in sets.items():
 if v!=ids:raise ValueError('%s does not match representatives: %s' %(k,sorted(ids^v)))
for path in a.gff+a.faa+a.ffn+a.gbk:
 if not os.path.isfile(path) or os.path.getsize(path)==0:raise ValueError('empty Prokka output: '+path)
with open(a.manifest,'w',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['genome_id','gff','faa','ffn','gbk'])
 byext={ext:{os.path.basename(x).rsplit('.',1)[0]:os.path.abspath(x) for x in paths} for ext,paths in {'gff':a.gff,'faa':a.faa,'ffn':a.ffn,'gbk':a.gbk}.items()}
 for gid in sorted(ids):w.writerow([gid]+[byext[x][gid] for x in ('gff','faa','ffn','gbk')])
h=hashlib.sha256(open(a.representatives,'rb').read()).hexdigest()
cp={'checkpoint':'C05','status':'pass','run_id':a.run_id,'timestamp':datetime.now(timezone.utc).isoformat(),'command':'PROKKA_VALIDATE','input_sha256':h,'tool_versions':{'prokka':'1.15.6'},'parameters':{'genus':'Lawsonella','usegenus':True,'compliant':True},'metrics':{'representatives':len(ids),'complete_output_sets':len(ids)}}
with open(a.checkpoint,'w') as f:json.dump(cp,f,indent=2,sort_keys=True)
