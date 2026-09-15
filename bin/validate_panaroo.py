#!/usr/bin/env python3
import argparse,csv,hashlib,json,os
from datetime import datetime,timezone
p=argparse.ArgumentParser()
for x in ('presence','proteins','mapping','graph','checkpoint','run-id'):p.add_argument('--'+x,required=True)
a=p.parse_args()
for x in (a.presence,a.proteins,a.mapping,a.graph):
 if not os.path.isfile(x) or os.path.getsize(x)==0:raise ValueError('missing Panaroo output: '+x)
with open(a.presence,newline='') as f:pres=list(csv.DictReader(f))
with open(a.mapping,newline='') as f:maps=list(csv.DictReader(f,delimiter='\t'))
clusters={r['Gene'] for r in pres};mapped={r['cluster_id'] for r in maps}
if not clusters or clusters!=mapped:raise ValueError('presence/mapping cluster mismatch')
keys=[(r['cluster_id'],r['genome_id'],r['gene_id']) for r in maps]
if len(keys)!=len(set(keys)):raise ValueError('duplicate cluster-gene-genome mapping')
fasta=[]
with open(a.proteins) as f:
 for line in f:
  if line.startswith('>'):fasta.append(line[1:].split()[0])
if len(fasta)!=len(set(fasta)) or set(fasta)!=clusters:raise ValueError('representative protein IDs do not match clusters')
cp={'checkpoint':'C06','status':'pass','run_id':a.run_id,'timestamp':datetime.now(timezone.utc).isoformat(),'command':'PANAROO_VALIDATE','input_sha256':hashlib.sha256(open(a.presence,'rb').read()).hexdigest(),'tool_versions':{'panaroo':'1.6.0'},'parameters':{'clean_mode':'strict','remove_invalid_genes':True},'metrics':{'clusters':len(clusters),'mapping_rows':len(maps),'representative_proteins':len(fasta)}}
with open(a.checkpoint,'w') as f:json.dump(cp,f,indent=2,sort_keys=True)
