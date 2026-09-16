# ProkFuncFlow

Nextflow DSL2 workflow for checkpointed Lawsonella genome analysis: uniform QC/taxonomy, filtering, dRep, Prokka, Panaroo pangenomics, genome-resolved KEGG module reconstruction with anvi'o, per-genome gapseq modeling, and clade-aware summaries.

## Scientific separation of evidence

- Panaroo representative proteins are annotated with eggNOG-mapper and KofamScan only for nonredundant pangenome comparison and cluster-to-gene-to-genome projection.
- Every dRep representative genome is independently processed with `anvi-run-kegg-kofams` and `anvi-estimate-metabolism`; these genome-resolved results are the production KEGG MODULE evidence.
- gapseq runs per representative proteome and provides sequence-supported reactions, transporters, draft models, and separately labeled gap-filled reactions.
- The former project-written KEGG definition parser is not connected to production workflows.

The same immutable anvi'o KEGG directory must be used for KOfam annotation and module estimation. C00 records the anvi'o container SHA-256 and `MODULES.db` SHA-256.

## Runtime configurations

Configuration is split by installation type:

- `external`: GitHub users; pinned Quay Biocontainers images and user-supplied database paths.
- `docker`: enables Docker and read-only database mounts. Images are pulled automatically when absent.
- `singularity`: enables Singularity and converts `docker://quay.io/...` images to cached SIF files automatically.
- `server`: this Lawsonella server's pre-pulled SIF images and `/data/Reference` databases.
- `local`: the bounded local-process executor; combine it with one installation/runtime profile.

For an external installation, copy `conf/external.example.config` to a private location and replace all placeholder database paths. Large/reference or licensed databases are deliberately not downloaded by the workflow.

### External containers

The external profiles pin these images in `conf/containers.config`. All references below use the `quay.io/biocontainers/` registry.

| Analysis | Pinned image |
|---|---|
| Genome quality | `checkm2:1.0.2--pyh7cba7a3_0` |
| Taxonomy | `gtdbtk:2.6.1--pyh1f0d9b5_2` |
| Dereplication | `drep:3.5.0--pyhdfd78af_0` |
| Gene annotation | `prokka:1.15.6--pl5321hdfd78af_0` |
| Pangenome | `panaroo:1.6.0--pyhdfd78af_0` |
| Broad functional annotation | `eggnog-mapper:2.1.15--pyhdfd78af_0` |
| KO annotation | `kofamscan:1.3.0--hdfd78af_2` |
| Metabolic models | `gapseq:2.1.0--hdfd78af_0` |
| Genome-resolved KEGG modules | `anvio-minimal:8--pyhdfd78af_0` |

Docker uses these OCI references directly; Singularity pulls them via `docker://` and caches SIF conversions. Containers are not substitutes for reference databases: external users must separately configure CheckM2, GTDB-Tk, eggNOG, Kofam, and anvi'o KEGG data. The pinned gapseq image contains its bacterial sequence database and default `gut.csv` medium. All nine commands passed the server SIF smoke test, and Quay-to-SIF auto-pull was tested with Panaroo. Docker execution was not tested on this server because Docker is not installed.

Docker example:

```bash
git clone https://github.com/KitHubb/ProkFuncFlow.git
cd ProkFuncFlow
cp conf/external.example.config my.config
# Edit my.config first.
nextflow -c my.config run main.nf -profile external,docker,local \
  --manifest /absolute/path/genomes.tsv --run_id RUN_ID \
  --outdir /absolute/path/results --run_downstream true
```

Singularity example:

```bash
export NXF_SINGULARITY_CACHEDIR=/absolute/path/singularity-cache
nextflow -c my.config run main.nf -profile external,singularity,local \
  --manifest /absolute/path/genomes.tsv --run_id RUN_ID \
  --outdir /absolute/path/results --run_downstream true
```

Server example:

```bash
LC_ALL=C nextflow run main.nf -profile server,local ...
```

External profiles skip the server-only C00 SIF checksum audit. Use the portable container smoke test below to verify pulled images; server runs retain the full C00 audit.

## Tests

Tests that do not download containers or databases:

```bash
python3 -m unittest discover -s tests -v
nextflow config -profile external,docker,local >/dev/null
nextflow config -profile external,singularity,local >/dev/null
nextflow config -profile server,local >/dev/null
```

Container command smoke test (pulls missing OCI images for external profiles):

```bash
# Docker
nextflow run tests/container_smoke.nf -profile external,docker,local

# Singularity
nextflow run tests/container_smoke.nf -profile external,singularity,local

# This server's pre-pulled SIF files
LC_ALL=C nextflow run tests/container_smoke.nf -profile server,local
```

GitHub Actions runs Python failure/logic tests and resolves all three configuration modes on every push and pull request. The full container smoke test remains explicit because the nine bioinformatics images are large.

## Production entrypoint

```bash
LC_ALL=C nextflow run main.nf -profile server,local \
  --manifest /absolute/path/candidate_manifest.tsv \
  --analysis_config config/analysis.yml \
  --clade_map /absolute/path/clades.tsv \
  --run_id RUN_ID --outdir /absolute/path/results/RUN_ID \
  --run_downstream true
```

If `--clade_map` is omitted, all representatives are `unassigned` and inferential clade comparisons are disabled. The default gapseq medium is the gapseq 2.1.0 image's `gut.csv`; override both `--gapseq_medium` and `--gapseq_medium_name` for a validated scenario.

## C05-C10 from validated C04 outputs

```bash
LC_ALL=C nextflow run downstream.nf -profile server,local -resume \
  --representatives_manifest /absolute/path/representative_genomes.tsv \
  --clusters_manifest /absolute/path/cluster_membership.tsv \
  --clade_map /absolute/path/clades.tsv \
  --run_id RUN_ID --outdir /absolute/path/results/RUN_ID
```

Primary KEGG module state uses strict pathwise completeness `1.0`. A `0.75` threshold is retained only as a labeled sensitivity result. Both pathwise and stepwise scores, module paths, module steps, KOfam hits, warnings, and database hashes are published.

Every validator writes a checkpoint JSON only after its acceptance checks pass. Results, work directories, databases, SIF images, and licensed KEGG content are intentionally excluded from Git.

---

# ProkFuncFlow — 한국어 안내

Lawsonella 유전체의 품질·분류, 필터링, dRep 중복 제거, Prokka 유전자 주석, Panaroo 범유전체, anvi'o 기반 유전체별 KEGG 모듈, gapseq 대사모델, clade별 요약을 수행하는 Nextflow DSL2 워크플로입니다.

## 분석 근거의 구분

- Panaroo 대표 단백질의 eggNOG-mapper·KofamScan 결과는 범유전체 기능 비교와 유전자–클러스터–유전체 연결에 사용합니다.
- 생산용 KEGG MODULE 결과는 각 dRep 대표 유전체에 `anvi-run-kegg-kofams`와 `anvi-estimate-metabolism`을 독립적으로 실행해 얻습니다.
- gapseq의 서열 근거 반응·수송체 후보·draft 모델과 gap filling으로 추가된 반응은 구분해 기록합니다.
- KOfam 주석과 모듈 추정에는 동일한 버전으로 고정된 anvi'o KEGG 데이터 디렉터리를 사용합니다. C00에는 anvi'o 컨테이너와 `MODULES.db`의 SHA-256을 기록합니다.

## 설정과 외부 컨테이너

GitHub 사용자에게는 `external`과 실행기인 `docker` 또는 `singularity`를 조합합니다. 이 서버에서는 기존 SIF와 DB 경로가 설정된 `server`를 사용합니다. `local`은 로컬 실행 자원 제한 프로필입니다. 외부 사용자는 `conf/external.example.config`를 복사해 본인 DB 경로를 입력해야 합니다. 워크플로는 대형 참조 DB나 라이선스가 필요한 데이터를 자동 다운로드하지 않습니다.

다음 고정 이미지는 모두 `quay.io/biocontainers/`에 있습니다.

| 분석 | 이미지 태그 |
|---|---|
| 유전체 품질 | `checkm2:1.0.2--pyh7cba7a3_0` |
| 분류 | `gtdbtk:2.6.1--pyh1f0d9b5_2` |
| 중복 제거 | `drep:3.5.0--pyhdfd78af_0` |
| 유전자 주석 | `prokka:1.15.6--pl5321hdfd78af_0` |
| 범유전체 | `panaroo:1.6.0--pyhdfd78af_0` |
| 광범위 기능 주석 | `eggnog-mapper:2.1.15--pyhdfd78af_0` |
| KO 주석 | `kofamscan:1.3.0--hdfd78af_2` |
| 대사모델 | `gapseq:2.1.0--hdfd78af_0` |
| 유전체별 KEGG 모듈 | `anvio-minimal:8--pyhdfd78af_0` |

Docker는 OCI 이미지를 직접 사용하고 Singularity는 필요할 때 내려받아 SIF로 캐시합니다. CheckM2, GTDB-Tk, eggNOG, Kofam, anvi'o KEGG 참조 DB는 별도 준비가 필요합니다. gapseq 기본 세균 서열 DB와 `gut.csv` 배지는 고정 이미지에 포함됩니다. 서버 SIF 9개의 명령 smoke test와 Panaroo의 Quay→SIF 자동 다운로드는 검증했지만, 이 서버에는 Docker가 없어 실제 Docker 실행은 검증하지 못했습니다.

## 실행

외부 사용자는 저장소를 clone하고 `conf/external.example.config`의 경로를 수정한 사본을 `my.config`로 준비합니다.

```bash
# Docker
nextflow -c my.config run main.nf -profile external,docker,local \
  --manifest /absolute/path/genomes.tsv --run_id RUN_ID \
  --outdir /absolute/path/results --run_downstream true

# Singularity
export NXF_SINGULARITY_CACHEDIR=/absolute/path/singularity-cache
nextflow -c my.config run main.nf -profile external,singularity,local \
  --manifest /absolute/path/genomes.tsv --run_id RUN_ID \
  --outdir /absolute/path/results --run_downstream true

# 기존 서버
LC_ALL=C nextflow run main.nf -profile server,local \
  --manifest /absolute/path/candidate_manifest.tsv \
  --run_id RUN_ID --outdir /absolute/path/results/RUN_ID \
  --run_downstream true
```

`--clade_map`이 없으면 대표 유전체는 `unassigned`로 처리하고 clade 간 추론 비교를 비활성화합니다. gapseq 기본 배지는 이미지의 `gut.csv`이며, 다른 배지를 쓰려면 `--gapseq_medium`과 `--gapseq_medium_name`을 함께 지정합니다. 검증된 C04 결과에서 C05–C10만 실행할 때는 `downstream.nf`에 `--representatives_manifest`와 `--clusters_manifest`를 전달합니다. KEGG 모듈의 기본 완성 기준은 pathwise 1.0이며 0.75는 민감도 분석용입니다.

## 테스트

```bash
# 이미지·DB 다운로드 없이 정적/단위 테스트
python3 -m unittest discover -s tests -v
nextflow config -profile external,docker,local >/dev/null
nextflow config -profile external,singularity,local >/dev/null
nextflow config -profile server,local >/dev/null

# 누락된 외부 이미지를 다운로드하는 컨테이너 명령 smoke test
nextflow run tests/container_smoke.nf -profile external,docker,local
nextflow run tests/container_smoke.nf -profile external,singularity,local

# 기존 서버 SIF 테스트
LC_ALL=C nextflow run tests/container_smoke.nf -profile server,local
```

GitHub Actions는 push와 pull request마다 Python 실패·논리 테스트와 세 설정 모드의 해석을 검사합니다. 전체 컨테이너 smoke test는 이미지가 크므로 명시적으로 실행합니다. 외부 프로필은 서버 전용 C00 SIF checksum 감사를 건너뛰고, 서버 프로필은 C00 감사를 유지합니다. 결과·작업 디렉터리·DB·SIF·라이선스가 필요한 KEGG 데이터는 Git에 포함하지 않습니다.
