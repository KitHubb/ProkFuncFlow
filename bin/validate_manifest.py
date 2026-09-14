#!/usr/bin/env python3
import argparse, csv, gzip, hashlib, json, os
from datetime import datetime, timezone
DNA=set("ACGTURYSWKMBDHVN.-"); DATASETS={"Bosanjin","SMGC","ELSG","External","UHGC"}; TYPES={"MAG","isolate_reference","type_strain","other_reference"}
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""): h.update(b)
 return h.hexdigest()
def fasta(p):
 op=gzip.open if p.endswith(".gz") else open; n=b=0; seq=False
 with op(p,"rt",encoding="ascii") as f:
  for ln,s in enumerate(f,1):
   s=s.rstrip("\r\n")
   if s.startswith(">"):
    if s==">" or (n and not seq): raise ValueError(f"bad record line {ln}")
    n+=1; seq=False
   elif s:
    if not n: raise ValueError(f"sequence before header line {ln}")
    bad=set(s.upper())-DNA
    if bad: raise ValueError(f"invalid alphabet line {ln}: {sorted(bad)}")
    b+=len(s); seq=True
 if not n or not b or not seq: raise ValueError("empty/incomplete FASTA")
 return n,b
def main():
 p=argparse.ArgumentParser()
 for k in ("manifest","analysis-config","normalized","report","checkpoint","run-id"): p.add_argument("--"+k,required=True)
 a=p.parse_args()
 with open(a.manifest,newline="") as f: rows=list(csv.DictReader(f,delimiter="\t"))
 req={"genome_id","dataset","staged_fasta","sha256"}
 if not rows or not req.issubset(rows[0]): raise ValueError(f"required columns: {sorted(req)}")
 ids=set(); hashes={}; out=[]
 for r in rows:
  gid=r["genome_id"]; ds=r["dataset"]; path=r["staged_fasta"]
  if not gid or gid in ids: raise ValueError(f"duplicate/empty ID: {gid!r}")
  ids.add(gid)
  if ds not in DATASETS: raise ValueError(f"bad dataset: {ds}")
  if not os.path.isabs(path) or os.path.islink(path) or not os.path.isfile(path) or os.path.getsize(path)==0: raise ValueError(f"bad staged file: {path}")
  obs=sha(path)
  if obs!=r["sha256"]: raise ValueError(f"checksum mismatch: {gid}")
  if obs in hashes: raise ValueError(f"duplicate content: {hashes[obs]}, {gid}")
  hashes[obs]=gid; ns,nb=fasta(path)
  typ=r.get("genome_type") or ("other_reference" if ds=="External" else "MAG")
  if typ not in TYPES: raise ValueError(f"bad genome_type: {typ}")
  out.append(dict(genome_id=gid,dataset=ds,genome_type=typ,accession=r.get("accession") or "NA",staged_fasta=path,sha256=obs,sequence_count=ns,base_count=nb))
 fields=list(out[0])
 with open(a.normalized,"w",newline="") as f: w=csv.DictWriter(f,fields,delimiter="\t",lineterminator="\n"); w.writeheader(); w.writerows(out)
 metrics={"status":"pass","genomes":len(out),"unique_ids":len(ids),"unique_content":len(hashes),"datasets":{d:sum(x["dataset"]==d for x in out) for d in sorted(DATASETS)}}
 with open(a.report,"w") as f: json.dump(metrics,f,indent=2,sort_keys=True)
 cp={"checkpoint":"C01","status":"pass","run_id":a.run_id,"timestamp":datetime.now(timezone.utc).isoformat(),"command":"VALIDATE_MANIFEST","manifest_sha256":sha(a.manifest),"metrics":metrics}
 with open(a.checkpoint,"w") as f: json.dump(cp,f,indent=2,sort_keys=True)
if __name__=="__main__": main()
