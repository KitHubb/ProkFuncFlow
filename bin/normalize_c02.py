#!/usr/bin/env python3
import argparse,csv,hashlib,json,os
from datetime import datetime,timezone
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument("--manifest",required=True);p.add_argument("--checkm2",nargs="+",required=True);p.add_argument("--gtdbtk",nargs="+",required=True)
 for k in ("output","report","checkpoint","run-id"):p.add_argument("--"+k,required=True)
 a=p.parse_args()
 with open(a.manifest,newline="") as f:manifest={r["genome_id"]:r for r in csv.DictReader(f,delimiter="\t")}
 cm={};gt={}
 for path in a.checkm2:
  with open(path,newline="") as f:rows=list(csv.DictReader(f,delimiter="\t"))
  if len(rows)!=1:raise ValueError(f"one CheckM2 row required: {path}")
  gid=os.path.basename(path)[:-len(".checkm2.tsv")];r=rows[0]
  for k in ("Completeness","Contamination"):float(r[k])
  if gid in cm:raise ValueError(f"duplicate CheckM2: {gid}")
  cm[gid]=r
 for path in a.gtdbtk:
  with open(path,newline="") as f:rows=list(csv.DictReader(f,delimiter="\t"))
  if not rows:raise ValueError(f"empty GTDB result: {path}")
  for row in rows:
   gid=row.get("user_genome") or os.path.basename(path)[:-len(".gtdbtk.tsv")]
   if gid in gt:raise ValueError(f"duplicate GTDB: {gid}")
   gt[gid]=row
 if set(manifest)!=set(cm) or set(manifest)!=set(gt):raise ValueError(f"ID coverage mismatch: manifest={len(manifest)} checkm2={len(cm)} gtdbtk={len(gt)}")
 fields="genome_id dataset genome_type accession staged_fasta sha256 completeness contamination checkm2_model gtdb_classification gtdb_genus gtdb_species gtdb_outcome".split();out=[]
 for gid,m in manifest.items():
  c=cm[gid];tax=gt[gid].get("classification") or "Unclassified";ranks=(tax.split(";")+[""]*7)[:7]
  out.append(dict(genome_id=gid,dataset=m["dataset"],genome_type=m["genome_type"],accession=m["accession"],staged_fasta=m["staged_fasta"],sha256=m["sha256"],completeness=c["Completeness"],contamination=c["Contamination"],checkm2_model=c.get("Completeness_Model_Used","NA"),gtdb_classification=tax,gtdb_genus=ranks[5] or "g__",gtdb_species=ranks[6] or "s__",gtdb_outcome="unclassified" if tax=="Unclassified" else "classified"))
 with open(a.output,"w",newline="") as f:w=csv.DictWriter(f,fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(out)
 metrics={"status":"pass","manifest_genomes":len(manifest),"checkm2_results":len(cm),"gtdbtk_outcomes":len(gt),"unclassified":sum(x["gtdb_outcome"]=="unclassified" for x in out)}
 with open(a.report,"w") as f:json.dump(metrics,f,indent=2,sort_keys=True)
 cp={"checkpoint":"C02","status":"pass","run_id":a.run_id,"timestamp":datetime.now(timezone.utc).isoformat(),"command":"VALIDATE_C02","input_checksums":{"manifest":sha(a.manifest)},"metrics":metrics,"tool_versions":{"checkm2":"1.0.2","gtdbtk":"2.6.1","gtdb_release":"226"}}
 with open(a.checkpoint,"w") as f:json.dump(cp,f,indent=2,sort_keys=True)
if __name__=="__main__":main()
