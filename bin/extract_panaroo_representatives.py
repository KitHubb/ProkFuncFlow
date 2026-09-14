#!/usr/bin/env python3
import argparse,csv
p=argparse.ArgumentParser();p.add_argument('--presence',required=True);p.add_argument('--faa',nargs='+',required=True);p.add_argument('--proteins',required=True);p.add_argument('--mapping',required=True);a=p.parse_args()
seq={}
for path in a.faa:
 with open(path) as f:
  key=None;buf=[]
  for line in f:
   if line.startswith('>'):
    if key:seq[key]=''.join(buf)
    key=line[1:].split()[0];buf=[]
   else:buf.append(line.strip())
  if key:seq[key]=''.join(buf)
with open(a.presence,newline='') as f:rows=list(csv.DictReader(f))
mapping=[]; reps=[]
metadata={'Gene','Non-unique Gene name','Annotation','No. isolates','No. sequences','Avg sequences per isolate','Genome Fragment','Order within Fragment','Accessory Fragment','Accessory Order with Fragment','QC','Min group size nuc','Max group size nuc','Avg group size nuc'}
for r in rows:
 cluster=r['Gene']; members=[]
 for k,v in r.items():
  if k not in metadata and v:
   for gene in v.split(';'):members.append((k,gene.strip()))
 found=[x for x in members if x[1] in seq]
 if not found:raise ValueError('no protein mapping for cluster '+cluster)
 rep=found[0][1];reps.append((cluster,seq[rep]))
 for genome,gene in members:mapping.append((cluster,rep,genome,gene))
with open(a.proteins,'w') as f:
 for k,s in reps:f.write('>{}\n{}\n'.format(k,s))
with open(a.mapping,'w') as f:
 f.write('cluster_id\trepresentative_gene\tgenome_id\tgene_id\n')
 for x in mapping:f.write('\t'.join(x)+'\n')
