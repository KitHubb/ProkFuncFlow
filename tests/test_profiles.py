#!/usr/bin/env python3
import os,subprocess,unittest
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def config(profile):
 return subprocess.check_output(['nextflow','config','-profile',profile],cwd=ROOT,env=dict(os.environ,LC_ALL='C')).decode('utf-8','replace')
class ProfileTests(unittest.TestCase):
 def test_external_docker_uses_oci_images(self):
  out=config('external,docker,local')
  self.assertIn('docker {\n   enabled = true',out)
  self.assertIn('quay.io/biocontainers/checkm2:1.0.2--pyh7cba7a3_0',out)
  self.assertIn('quay.io/biocontainers/anvio-minimal:8--pyhdfd78af_0',out)
  self.assertIn('skip_c00 = true',out)
  self.assertIn('singularity {\n   enabled = false',out)
 def test_external_singularity_uses_oci_images(self):
  out=config('external,singularity,local')
  self.assertIn('singularity {\n   enabled = true',out)
  self.assertIn('docker://quay.io/biocontainers/gapseq:2.1.0--hdfd78af_0',out)
  self.assertIn('docker {\n   enabled = false',out)
 def test_server_uses_prepulled_sif(self):
  out=config('server,local')
  self.assertIn("checkm2_container = '/data/software/singularity/checkm2_1.0.2.sif'",out)
  self.assertIn("cacheDir = '/data/software/singularity'",out)
  self.assertIn('skip_c00 = false',out)
  self.assertIn('docker {\n   enabled = false',out)
if __name__=='__main__':unittest.main()
