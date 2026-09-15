#!/usr/bin/env python3
import argparse,csv,hashlib,json,os
from datetime import datetime,timezone
p=argparse.ArgumentParser()
for k in ('manifest','drep-dir','representatives','clusters','checkpoint','run-id'):p.add_argument('--'+k,required=True)
p.add_argument('--primary-ani',required=True,type=float);p.add_argument('--secondary-ani',required=True,type=float);p.add_argument('--min-coverage',required=True,type=float)
a=p.parse_args()
with open(a.manifest,newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
by_id={r['genome_id']:r for r in rows}
if len(by_id)!=len(rows):raise ValueError('duplicate IDs in C03 manifest')
cdb=os.path.join(a.drep_dir,'data_tables','Cdb.csv');wdb=os.path.join(a.drep_dir,'data_tables','Wdb.csv')
for path in (cdb,wdb):
 if not os.path.isfile(path) or os.path.getsize(path)==0:raise ValueError('missing dRep table: '+path)
with open(cdb,newline='') as f:clusters=list(csv.DictReader(f))
with open(wdb,newline='') as f:winners=list(csv.DictReader(f))
def gid(name):return os.path.basename(name).rsplit('.',1)[0]
cluster_by_id={gid(r['genome']):r.get('secondary_cluster','NA') for r in clusters}
if set(cluster_by_id)!=set(by_id):raise ValueError('Cdb does not account for every C03 genome')
winner_ids=[gid(r['genome']) for r in winners]
if len(winner_ids)!=len(set(winner_ids)) or not set(winner_ids).issubset(by_id):raise ValueError('invalid Wdb representatives')
rep_files={gid(x):os.path.join(a.drep_dir,'dereplicated_genomes',x) for x in os.listdir(os.path.join(a.drep_dir,'dereplicated_genomes'))}
if set(winner_ids)!=set(rep_files):raise ValueError('Wdb and dereplicated_genomes disagree')
fields=list(rows[0].keys())+['drep_cluster','drep_representative']
with open(a.representatives,'w',newline='') as f:
 w=csv.DictWriter(f,fields,delimiter='\t',lineterminator='\n');w.writeheader()
 for x in winner_ids:
  r=dict(by_id[x]);r['drep_cluster']=cluster_by_id[x];r['drep_representative']='true';w.writerow(r)
with open(a.clusters,'w',newline='') as f:
 w=csv.DictWriter(f,['genome_id','drep_cluster','drep_representative'],delimiter='\t',lineterminator='\n');w.writeheader()
 for x in sorted(by_id):w.writerow({'genome_id':x,'drep_cluster':cluster_by_id[x],'drep_representative':str(x in winner_ids).lower()})
h=hashlib.sha256(open(a.manifest,'rb').read()).hexdigest();cp={'checkpoint':'C04','status':'pass','run_id':a.run_id,'timestamp':datetime.now(timezone.utc).isoformat(),'command':'DREP','input_sha256':h,'tool_versions':{'drep':'3.5.0','fastANI':'1.33'},'parameters':{'primary_ani':a.primary_ani,'secondary_ani':a.secondary_ani,'min_alignment_coverage':a.min_coverage,'algorithm':'fastANI','genome_info':True},'metrics':{'input_genomes':len(rows),'clusters':len(set(cluster_by_id.values())),'representatives':len(winner_ids)}}
with open(a.checkpoint,'w') as f:json.dump(cp,f,indent=2,sort_keys=True)
