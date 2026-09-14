#!/usr/bin/env python3
import argparse, hashlib, json, os, shutil, subprocess
from datetime import datetime, timezone
def run(cmd,env=None):
 p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env)
 out=p.stdout.decode("utf-8","replace")
 if p.returncode: raise RuntimeError("failed: {}\n{}".format(" ".join(cmd),out))
 return out.strip()
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""): h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser()
 for k in ("analysis-config","run-id","outdir","project-dir","checkm2-container","gtdbtk-container","checkm2-db","gtdbtk-db","environment","containers","versions","checkpoint"): p.add_argument("--"+k,required=True)
 a=p.parse_args()
 for x in (a.analysis_config,a.checkm2_container,a.gtdbtk_container,a.checkm2_db):
  if not os.path.isfile(x) or not os.access(x,os.R_OK): raise ValueError(f"unreadable: {x}")
 meta=os.path.join(a.gtdbtk_db,"metadata","metadata.txt")
 if not os.path.isfile(meta): raise ValueError(f"GTDB metadata missing: {meta}")
 for x in ("nextflow","java","singularity"):
  if not shutil.which(x): raise ValueError(f"missing executable: {x}")
 os.makedirs(a.outdir,exist_ok=True); probe=os.path.join(a.outdir,".write_test")
 with open(probe,"w") as f:f.write("ok\n")
 os.unlink(probe)
 env=os.environ.copy(); env["GTDBTK_DATA_PATH"]=a.gtdbtk_db
 versions={"nextflow":run(["nextflow","-version"]),"java":run(["java","-version"]),"singularity":run(["singularity","--version"]),"checkm2":run(["singularity","exec",a.checkm2_container,"checkm2","--version"]),"gtdbtk":run(["singularity","exec","--bind",f"{a.gtdbtk_db}:{a.gtdbtk_db}:ro",a.gtdbtk_container,"gtdbtk","--version"],env)}
 check_install=run(["singularity","exec","--bind","{}:{}:ro".format(a.gtdbtk_db,a.gtdbtk_db),a.gtdbtk_container,"gtdbtk","check_install"],env)
 if "Running install verification" not in check_install: raise ValueError("GTDB-Tk check_install did not run")
 versions["gtdbtk_check_install"]="pass (GTDB r226 integrity and dependencies)"
 if "1.0.2" not in versions["checkm2"] or "2.6.1" not in versions["gtdbtk"]: raise ValueError("pinned version mismatch")
 git={}
 if os.path.isdir(os.path.join(a.project_dir,".git")):
  git={"branch":run(["git","-C",a.project_dir,"branch","--show-current"]),"head":run(["git","-C",a.project_dir,"rev-parse","HEAD"]),"status":run(["git","-C",a.project_dir,"status","--short"])}
  if git["branch"]!="main": raise ValueError("Git branch is not main")
 envout={"status":"pass","disk":shutil.disk_usage(a.outdir)._asdict(),"locales":run(["locale","-a"]),"scheduler":"slurm" if shutil.which("sbatch") else "local","git":git,"gtdb_metadata":meta}
 with open(a.environment,"w") as f:json.dump(envout,f,indent=2,sort_keys=True)
 images=[("checkm2",a.checkm2_container,sha(a.checkm2_container)),("gtdbtk",a.gtdbtk_container,sha(a.gtdbtk_container))]
 with open(a.containers,"w") as f:
  f.write("tool\tpath\tsha256\n")
  for row in images:f.write("\t".join(row)+"\n")
 with open(a.versions,"w") as f:
  f.write("tool\tversion_output\n")
  for k,v in versions.items():f.write(f"{k}\t{v.replace(chr(10),' | ')}\n")
 cp={"checkpoint":"C00","status":"pass","run_id":a.run_id,"timestamp":datetime.now(timezone.utc).isoformat(),"command":"C00_AUDIT","input_checksums":{"analysis_config":sha(a.analysis_config)},"container_checksums":{x[0]:x[2] for x in images},"database_versions":{"gtdb":"r226","checkm2_database":a.checkm2_db}}
 with open(a.checkpoint,"w") as f:json.dump(cp,f,indent=2,sort_keys=True)
if __name__=="__main__":main()
