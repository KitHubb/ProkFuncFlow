#!/usr/bin/env python3
import csv,hashlib,os,subprocess,tempfile,unittest
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class WorkflowLogicTests(unittest.TestCase):
 def test_module_operators(self):
  with tempfile.TemporaryDirectory() as d:
   ev=os.path.join(d,'e.tsv');out=os.path.join(d,'o.tsv');cp=os.path.join(d,'c.json')
   with open(ev,'w') as f:f.write('genome_id\tgene_id\tcluster_id\tevidence_source\tko\tec\treaction\tscore\tthreshold\tevalue\tdescription\nG1\tg1\tc1\tKofam\tK02834\t-\t-\t100\t10\t1e-9\tx\n')
   subprocess.check_call(['python3',os.path.join(ROOT,'bin/reconstruct_modules.py'),'--evidence',ev,'--definitions',os.path.join(ROOT,'tests/fixtures/module_definitions.synthetic.tsv'),'--output',out,'--checkpoint',cp,'--run-id','unit','--definition-version','synthetic-v1'])
   with open(out) as f:rows=list(csv.DictReader(f,delimiter='\t'))
   states={r['module_id']:r['state'] for r in rows}
   self.assertEqual(states,{'SYN001':'incomplete','SYN002':'complete','SYN003':'incomplete','SYN004':'incomplete'})
 def test_duplicate_manifest_fixture_fails(self):
  with tempfile.TemporaryDirectory() as d:
   fa=os.path.join(d,'x.fna')
   with open(fa,'w') as f:f.write('>x\nACGT\n')
   with open(fa,'rb') as f:sha=hashlib.sha256(f.read()).hexdigest()
   manifest=os.path.join(d,'m.tsv')
   with open(manifest,'w') as f:f.write('genome_id\tstaged_fasta\tdataset\tgenome_type\taccession\tsha256\nDUP\t%s\tSMGC\tMAG\tNA\t%s\nDUP\t%s\tSMGC\tMAG\tNA\t%s\n'%(fa,sha,fa,sha))
   result=subprocess.run(['python3',os.path.join(ROOT,'bin/validate_manifest.py'),'--manifest',manifest,'--analysis-config',os.path.join(ROOT,'config/analysis.yml'),'--normalized',os.path.join(d,'n'),'--report',os.path.join(d,'r'),'--checkpoint',os.path.join(d,'c'),'--run-id','failure'],stderr=subprocess.PIPE)
   self.assertNotEqual(result.returncode,0);self.assertIn(b'duplicate',result.stderr)
if __name__=='__main__':unittest.main()
