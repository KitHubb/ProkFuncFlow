#!/usr/bin/env python3
import argparse, csv, gzip, os, shutil

p=argparse.ArgumentParser();p.add_argument("--manifest",required=True);p.add_argument("--output-dir",required=True);a=p.parse_args()
os.makedirs(a.output_dir,exist_ok=True)
with open(a.manifest,newline="") as f:
 for row in csv.DictReader(f,delimiter="\t"):
  source=row["staged_fasta"]
  target=os.path.join(a.output_dir,row["genome_id"]+".fna")
  with open(source,"rb") as raw:
   compressed=raw.read(2)==b"\x1f\x8b"
  if compressed:
   with gzip.open(source,"rb") as src, open(target,"wb") as dst:
    shutil.copyfileobj(src,dst)
  else:
   os.symlink(source,target)
