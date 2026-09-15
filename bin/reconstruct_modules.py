#!/usr/bin/env python3
import argparse,csv,hashlib,json,re
from collections import defaultdict
from datetime import datetime,timezone
p=argparse.ArgumentParser()
for x in ('evidence','definitions','output','checkpoint','run-id','definition-version'):p.add_argument('--'+x,required=True)
a=p.parse_args();kos=defaultdict(set)
with open(a.evidence,newline='') as f:
 for r in csv.DictReader(f,delimiter='\t'):
  if r['evidence_source']=='Kofam' and r['ko'] not in ('','-'):kos[r['genome_id']].add(r['ko'])
with open(a.definitions,newline='') as f:defs=list(csv.DictReader(f,delimiter='\t'))
if not defs or not {'module_id','name','definition'}.issubset(defs[0]):raise ValueError('versioned module definitions are required')
def evaluate(expr,present):
 tokens=re.findall(r'K\d{5}|[(),+\-]',expr);i=[0]
 def combine_and(vals):
  return (sum(x[0] for x in vals),sum(x[1] for x in vals),sum((x[2] for x in vals),[]))
 def factor():
  optional=False
  if i[0]<len(tokens) and tokens[i[0]]=='-':optional=True;i[0]+=1
  if i[0]>=len(tokens):raise ValueError('truncated definition: '+expr)
  if tokens[i[0]]=='(':
   i[0]+=1;v=alternative()
   if i[0]>=len(tokens) or tokens[i[0]]!=')':raise ValueError('unbalanced definition: '+expr)
   i[0]+=1
  else:
   ko=tokens[i[0]];i[0]+=1
   if not ko.startswith('K'):raise ValueError('unexpected token in definition: '+ko)
   v=(int(ko in present),1,[] if ko in present else [ko])
  return (0,0,[]) if optional else v
 def conjunction():
  vals=[]
  while i[0]<len(tokens) and tokens[i[0]] not in (',',')'):
   if tokens[i[0]]=='+':i[0]+=1;continue
   vals.append(factor())
  return combine_and(vals)
 def alternative():
  vals=[conjunction()]
  while i[0]<len(tokens) and tokens[i[0]]==',':i[0]+=1;vals.append(conjunction())
  return max(vals,key=lambda x:(x[0]/x[1] if x[1] else 1.0,-x[1]))
 got,need,missing=alternative()
 if i[0]!=len(tokens):raise ValueError('unparsed definition: '+expr)
 return (got/need if need else 1.0,sorted(set(missing)),got,need)
rows=[]
for genome in sorted(kos):
 for d in defs:
  score,missing,got,need=evaluate(d['definition'],kos[genome]);state='complete' if score==1 else ('uncertain' if need==0 else 'incomplete')
  rows.append([genome,d['module_id'],d['name'],d['definition'],state,'%.6f'%score,got,need,';'.join(missing) or '-'])
with open(a.output,'w',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['genome_id','module_id','module_name','definition','state','completeness','steps_present','steps_required','missing_required']);w.writerows(rows)
cp={'checkpoint':'C08','status':'pass','run_id':a.run_id,'timestamp':datetime.now(timezone.utc).isoformat(),'command':'KEGG_LOGIC_RECONSTRUCT','input_sha256':hashlib.sha256(open(a.definitions,'rb').read()).hexdigest(),'database_versions':{'module_definitions':a.definition_version},'parameters':{'formal_evidence':'Kofam','operators':{'space':'AND','+':'complex AND',',':'alternative OR','-':'optional'}},'metrics':{'genomes':len(kos),'modules':len(defs),'complete_calls':sum(r[4]=='complete' for r in rows),'calls':len(rows)}}
with open(a.checkpoint,'w') as f:json.dump(cp,f,indent=2,sort_keys=True)
