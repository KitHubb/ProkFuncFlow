#!/usr/bin/env python3
import csv,hashlib,os,sqlite3,subprocess,tempfile,unittest
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
 def test_anvio_validator_strict_and_sensitivity_states(self):
  with tempfile.TemporaryDirectory() as d:
   rep=os.path.join(d,'representatives.tsv')
   with open(rep,'w') as f:f.write('genome_id\nG1\n')
   header='module\tmodule_name\tmodule_definition\tstepwise_module_completeness\tpathwise_module_completeness\tenzyme_hits_in_module\tgene_caller_ids_in_module\twarnings\n'
   modules=os.path.join(d,'G1_modules.txt')
   with open(modules,'w') as f:
    f.write(header);f.write('M1\tone\tK00001\t1.0\t1.0\tK00001\t1\t\n');f.write('M2\ttwo\tK00002 K00003\t0.5\t0.75\tK00002\t2\t\n')
   generic='module\tvalue\nM1\tx\n'
   paths=os.path.join(d,'G1_module_paths.txt');steps=os.path.join(d,'G1_module_steps.txt');hits=os.path.join(d,'G1_hits.txt')
   for x in (paths,steps,hits):open(x,'w').write(generic)
   db=os.path.join(d,'G1-CONTIGS.db');sqlite3.connect(db).close()
   kegg=os.path.join(d,'KEGG');os.makedirs(kegg);mdb=os.path.join(kegg,'MODULES.db')
   con=sqlite3.connect(mdb);con.execute('create table self (key text, value text)');con.execute('insert into self values (?,?)',('content_hash','fixture-hash'));con.commit();con.close()
   cmd=['python3',os.path.join(ROOT,'bin/validate_anvio_metabolism.py'),'--representatives',rep,'--modules',modules,'--module-paths',paths,'--module-steps',steps,'--hits',hits,'--contigs-dbs',db,'--kegg-data-dir',kegg,'--strict-threshold','1.0','--sensitivity-threshold','0.75','--modules-output',os.path.join(d,'out.tsv'),'--missing-output',os.path.join(d,'missing.tsv'),'--paths-output',os.path.join(d,'paths.tsv'),'--steps-output',os.path.join(d,'steps.tsv'),'--hits-output',os.path.join(d,'hits.tsv'),'--database-manifest',os.path.join(d,'db.tsv'),'--checkpoint',os.path.join(d,'C08.json'),'--run-id','unit']
   subprocess.check_call(cmd)
   with open(os.path.join(d,'out.tsv')) as f:states={r['module_id']:r['state'] for r in csv.DictReader(f,delimiter='\t')}
   self.assertEqual(states,{'M1':'complete','M2':'near_complete'})
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
