# Active task

- objective: implement and verify C00-C02 with a four-genome smoke test
- run_id: `smoke_c00_c02_batch`
- completed checkpoints: C00 pass, C01 pass, C02 pass
- input manifest SHA-256: `09813e2605833fc6f4536d452fd8e1a9885952e96cb348715391b2dbaebf0dad`
- validation: 4 unique FASTAs; 4 CheckM2 rows; 4 GTDB-Tk r226 outcomes; zero unclassified/tool failures
- active jobs: none
- known limitation: smoke External row lacks curated genome type/accession columns and is conservatively normalized as `other_reference`/`NA`
- next action: review diff, then implement C03 inclusion policy and freeze
