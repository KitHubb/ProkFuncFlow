#!/usr/bin/env python3
import hashlib,os,subprocess,tempfile,unittest
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def run(script,args):return subprocess.run(['python3',os.path.join(ROOT,'bin',script)]+args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
class FailureFixtures(unittest.TestCase):
 def validate(self,d,rows):
  manifest=os.path.join(d,'m.tsv')
  with open(manifest,'w') as f:
   f.write('genome_id\tstaged_fasta\tdataset\tgenome_type\taccession\tsha256\n')
   for r in rows:f.write('\t'.join(r)+'\n')
  return run('validate_manifest.py',['--manifest',manifest,'--analysis-config',os.path.join(ROOT,'config/analysis.yml'),'--normalized',os.path.join(d,'n'),'--report',os.path.join(d,'r'),'--checkpoint',os.path.join(d,'c'),'--run-id','failure'])
 def test_zero_byte_fasta(self):
  with tempfile.TemporaryDirectory() as d:
   x=os.path.join(d,'x.fna');open(x,'wb').close();self.assertNotEqual(self.validate(d,[['G',x,'SMGC','MAG','NA',hashlib.sha256(b'').hexdigest()]]).returncode,0)
 def test_invalid_alphabet(self):
  with tempfile.TemporaryDirectory() as d:
   x=os.path.join(d,'x.fna');data=b'>x\nACGTZ\n';open(x,'wb').write(data);self.assertNotEqual(self.validate(d,[['G',x,'SMGC','MAG','NA',hashlib.sha256(data).hexdigest()]]).returncode,0)
 def test_corrupt_gzip(self):
  with tempfile.TemporaryDirectory() as d:
   x=os.path.join(d,'x.fna.gz');data=b'not-gzip';open(x,'wb').write(data);self.assertNotEqual(self.validate(d,[['G',x,'SMGC','MAG','NA',hashlib.sha256(data).hexdigest()]]).returncode,0)
 def test_duplicate_content(self):
  with tempfile.TemporaryDirectory() as d:
   data=b'>x\nACGT\n';paths=[]
   for n in ('a.fna','b.fna'):
    x=os.path.join(d,n);open(x,'wb').write(data);paths.append(x)
   sha=hashlib.sha256(data).hexdigest();self.assertNotEqual(self.validate(d,[['A',paths[0],'SMGC','MAG','NA',sha],['B',paths[1],'ELSG','MAG','NA',sha]]).returncode,0)
 def test_missing_qc_row(self):
  with tempfile.TemporaryDirectory() as d:
   manifest=os.path.join(d,'m.tsv');open(manifest,'w').write('genome_id\tdataset\tgenome_type\taccession\tstaged_fasta\tsha256\nG\tSMGC\tMAG\tNA\t/x\tNA\n')
   cm=os.path.join(d,'other.checkm2.tsv');open(cm,'w').write('Completeness\tContamination\n99\t0\n')
   gt=os.path.join(d,'g.tsv');open(gt,'w').write('user_genome\tclassification\nG\td__Bacteria\n')
   r=run('normalize_c02.py',['--manifest',manifest,'--checkm2',cm,'--gtdbtk',gt,'--output',os.path.join(d,'o'),'--report',os.path.join(d,'r'),'--checkpoint',os.path.join(d,'c'),'--run-id','failure']);self.assertNotEqual(r.returncode,0)
 def test_malformed_kofam(self):
  with tempfile.TemporaryDirectory() as d:
   mapping=os.path.join(d,'map.tsv');open(mapping,'w').write('cluster_id\trepresentative_gene\tgenome_id\tgene_id\nC\tg\tG\tg\n')
   egg=os.path.join(d,'egg.tsv');open(egg,'w').write('#query\tDescription\nC\tx\n')
   kof=os.path.join(d,'kof.tsv');open(kof,'w').write('*\tC\tK00001\n')
   r=run('build_function_evidence.py',['--mapping',mapping,'--eggnog',egg,'--kofam',kof,'--evidence',os.path.join(d,'e'),'--ko-matrix',os.path.join(d,'k'),'--checkpoint',os.path.join(d,'c'),'--run-id','failure']);self.assertNotEqual(r.returncode,0)
 def test_broken_panaroo_mapping(self):
  with tempfile.TemporaryDirectory() as d:
   presence=os.path.join(d,'p.csv');open(presence,'w').write('Gene\nA\n');proteins=os.path.join(d,'p.faa');open(proteins,'w').write('>A\nM\n');mapping=os.path.join(d,'m.tsv');open(mapping,'w').write('cluster_id\trepresentative_gene\tgenome_id\tgene_id\nB\tg\tG\tg\n');graph=os.path.join(d,'g.gml');open(graph,'w').write('graph []\n')
   r=run('validate_panaroo.py',['--presence',presence,'--proteins',proteins,'--mapping',mapping,'--graph',graph,'--checkpoint',os.path.join(d,'c'),'--run-id','failure']);self.assertNotEqual(r.returncode,0)
if __name__=='__main__':unittest.main()
