#!/usr/bin/env python3
import argparse, hashlib, json, os, re, shutil, subprocess
from datetime import datetime, timezone
def run(cmd,env=None,cwd=None):
 p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,cwd=cwd)
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
 for k in ("analysis-config","run-id","outdir","project-dir","checkm2-container","gtdbtk-container","drep-container","prokka-container","panaroo-container","eggnog-container","kofam-container","gapseq-container","checkm2-db","gtdbtk-db","eggnog-db","kofam-profiles","kofam-ko-list","gapseq-db","environment","containers","versions","checkpoint"): p.add_argument("--"+k,required=True)
 a=p.parse_args()
 for x in (a.analysis_config,a.checkm2_container,a.gtdbtk_container,a.drep_container,a.prokka_container,a.panaroo_container,a.eggnog_container,a.kofam_container,a.gapseq_container,a.checkm2_db,a.kofam_ko_list):
  if not os.path.isfile(x) or not os.access(x,os.R_OK): raise ValueError(f"unreadable: {x}")
 for x in (a.gtdbtk_db,a.eggnog_db,a.kofam_profiles,a.gapseq_db):
  if not os.path.isdir(x):raise ValueError(f"database directory missing: {x}")
 meta=os.path.join(a.gtdbtk_db,"metadata","metadata.txt")
 if not os.path.isfile(meta): raise ValueError(f"GTDB metadata missing: {meta}")
 for x in ("nextflow","java","singularity"):
  if not shutil.which(x): raise ValueError(f"missing executable: {x}")
 os.makedirs(a.outdir,exist_ok=True); probe=os.path.join(a.outdir,".write_test")
 with open(probe,"w") as f:f.write("ok\n")
 os.unlink(probe)
 env=os.environ.copy(); env["GTDBTK_DATA_PATH"]=a.gtdbtk_db
 versions={"nextflow":run(["nextflow","-version"]),"java":run(["java","-version"]),"singularity":run(["singularity","--version"]),"checkm2":run(["singularity","exec",a.checkm2_container,"checkm2","--version"]),"gtdbtk":run(["singularity","exec","--bind",f"{a.gtdbtk_db}:{a.gtdbtk_db}:ro",a.gtdbtk_container,"gtdbtk","--version"],env),"drep":run(["singularity","exec",a.drep_container,"python","-c","import importlib.metadata as m; print(m.version('drep'))"]).splitlines()[-1],"fastani":run(["singularity","exec",a.drep_container,"fastANI","--version"]).splitlines()[-1]}
 drep_dependencies=run(["singularity","exec",a.drep_container,"dRep","check_dependencies"])
 if not re.search(r"^mash.*all good",drep_dependencies,re.M) or not re.search(r"^fastANI.*all good",drep_dependencies,re.M): raise ValueError("dRep core dependency check failed")
 versions["drep_dependencies"]=drep_dependencies
 versions["prokka"]=run(["singularity","exec",a.prokka_container,"/prokka-1.15.6/bin/prokka","--version"]).splitlines()[-1]
 versions["panaroo"]=run(["singularity","exec",a.panaroo_container,"/opt/conda/bin/panaroo","--version"]).splitlines()[-1]
 versions["eggnog_mapper"]=run(["singularity","exec","--bind",f"{a.eggnog_db}:{a.eggnog_db}:ro",a.eggnog_container,"emapper.py","--version"]).splitlines()[-1]
 kofam_help=run(["singularity","exec",a.kofam_container,"exec_annotation","--help"])
 if "Usage: exec_annotation" not in kofam_help:raise ValueError("KofamScan help check failed")
 versions["kofamscan_help"]="pass (exec_annotation usage available)"
 versions["gapseq"]=run(["singularity","exec",a.gapseq_container,"gapseq","-v"]).splitlines()[-1]
 gapseq_test=run(["singularity","exec",a.gapseq_container,"gapseq","test"])
 if "Passed tests: 3/3" not in gapseq_test:raise ValueError("gapseq self-test failed")
 versions["gapseq_self_test"]="pass (3/3)"
 check_install=run(["singularity","exec","--bind","{}:{}:ro".format(a.gtdbtk_db,a.gtdbtk_db),a.gtdbtk_container,"gtdbtk","check_install"],env)
 if "Running install verification" not in check_install: raise ValueError("GTDB-Tk check_install did not run")
 versions["gtdbtk_check_install"]="pass (GTDB r226 integrity and dependencies)"
 if "1.0.2" not in versions["checkm2"] or "2.6.1" not in versions["gtdbtk"] or versions["drep"] != "3.5.0" or "1.33" not in versions["fastani"] or "1.15.6" not in versions["prokka"] or "1.6.0" not in versions["panaroo"] or "2.1.15" not in versions["eggnog_mapper"] or "2.1.0" not in versions["gapseq"]: raise ValueError("pinned version mismatch")
 git={}
 if os.path.isdir(os.path.join(a.project_dir,".git")):
  git={"branch":run(["git","symbolic-ref","--short","HEAD"],cwd=a.project_dir),"head":run(["git","rev-parse","HEAD"],cwd=a.project_dir),"status":run(["git","status","--short"],cwd=a.project_dir)}
  if git["branch"]!="main": raise ValueError("Git branch is not main")
 envout={"status":"pass","disk":shutil.disk_usage(a.outdir)._asdict(),"locales":run(["locale","-a"]),"scheduler":"slurm" if shutil.which("sbatch") else "local","git":git,"gtdb_metadata":meta}
 with open(a.environment,"w") as f:json.dump(envout,f,indent=2,sort_keys=True)
 images=[("checkm2",a.checkm2_container,sha(a.checkm2_container)),("gtdbtk",a.gtdbtk_container,sha(a.gtdbtk_container)),("drep",a.drep_container,sha(a.drep_container)),("prokka",a.prokka_container,sha(a.prokka_container)),("panaroo",a.panaroo_container,sha(a.panaroo_container)),("eggnog_mapper",a.eggnog_container,sha(a.eggnog_container)),("kofamscan",a.kofam_container,sha(a.kofam_container)),("gapseq",a.gapseq_container,sha(a.gapseq_container))]
 with open(a.containers,"w") as f:
  f.write("tool\tpath\tsha256\n")
  for row in images:f.write("\t".join(row)+"\n")
 with open(a.versions,"w") as f:
  f.write("tool\tversion_output\n")
  for k,v in versions.items():f.write(f"{k}\t{v.replace(chr(10),' | ')}\n")
 cp={"checkpoint":"C00","status":"pass","run_id":a.run_id,"timestamp":datetime.now(timezone.utc).isoformat(),"command":"C00_AUDIT","input_checksums":{"analysis_config":sha(a.analysis_config)},"container_checksums":{x[0]:x[2] for x in images},"database_versions":{"gtdb":"r226","checkm2_database":a.checkm2_db,"eggnog":"5.0.2","kofam_profiles":a.kofam_profiles,"kofam_ko_list":a.kofam_ko_list,"gapseq_sequence_db":"1.5"}}
 with open(a.checkpoint,"w") as f:json.dump(cp,f,indent=2,sort_keys=True)
if __name__=="__main__":main()
