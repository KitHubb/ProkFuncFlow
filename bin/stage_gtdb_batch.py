#!/usr/bin/env python3
import argparse, csv, os
p=argparse.ArgumentParser();p.add_argument("--manifest",required=True);p.add_argument("--output-dir",required=True);a=p.parse_args()
os.makedirs(a.output_dir,exist_ok=True)
with open(a.manifest,newline="") as f:
 for row in csv.DictReader(f,delimiter="\t"):
  target=os.path.join(a.output_dir,row["genome_id"]+".fna")
  os.symlink(row["staged_fasta"],target)
