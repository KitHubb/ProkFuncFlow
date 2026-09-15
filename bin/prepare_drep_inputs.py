#!/usr/bin/env python3
import argparse,csv,os
p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--genome-dir',required=True);p.add_argument('--genome-info',required=True);a=p.parse_args()
os.makedirs(a.genome_dir,exist_ok=True)
with open(a.manifest,newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
if not rows:raise ValueError('empty C03 manifest')
with open(a.genome_info,'w',newline='') as f:
 w=csv.DictWriter(f,['genome','completeness','contamination'],lineterminator='\n');w.writeheader()
 for r in rows:
  name=r['genome_id']+'.fna'; target=os.path.join(a.genome_dir,name)
  os.symlink(r['staged_fasta'],target)
  float(r['completeness']);float(r['contamination'])
  w.writerow({'genome':name,'completeness':r['completeness'],'contamination':r['contamination']})
