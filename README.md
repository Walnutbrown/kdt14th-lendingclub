# lendingclub 프로젝트 폴더 (2026-11-25)

코드는 이 GitHub 레포가 기준입니다. 데이터와 산출물(`raw/`, `data/`, `outputs/`, `freeze/`, `test_hold/`, `report/`)은 모두 팀 Drive에 둡니다. AI 에이전트(Claude Code, Codex, Antigravity)로 작업할 때의 규칙은 [AGENTS.md](AGENTS.md)에 있습니다.

## 필요한 패키지
Python 3.10, `pip install -r requirements.txt` (검증된 버전 고정). Colab에는 optuna만 없습니다(`pip install optuna`).

## Git 작업 방식 (GitHub 레포)

### 구역별 파일
자기 구역 파일만 고칩니다. 다른 구역 파일에 고칠 점이 있으면 그 구역 담당에게 요청합니다. 누가 어느 구역을 맡는지와 할 일 목록은 팀 Notion에서 관리합니다(이 레포에는 사람 정보를 두지 않습니다).

| 구역 | 코드 (레포) | 산출물 (Drive) | 보고서 |
|---|---|---|---|
| `core` | `00_config`, `lib_prep`, `01_prep`, `01b_eda_audit`, `99_freeze`, `00b_test_prep`, `contract/`, `colab_setup.py`, `README.md`, `AGENTS.md` | `data/`, `freeze/`, `test_hold/` | 본문, 표 1~3 |
| `logit` | `02_logit`, `06_collect`, `lib_engine`, `model_template` | `outputs/logit/`, `outputs/collect/` | 표 4, 그림 2~4, 부록 D·E |
| `xgb` | `03_tune`, `03_xgb`, `04_xgb_mono` | `contract/xgb_params.json`(03_tune 출력), `outputs/xgb/`, `outputs/xgb_mono/` | 부록 B·C |
| `eval` | `05_test`, `lib_eval_add` | `report/tables/`·`report/figures/`의 Test 결과 | 표 5~9·A, 그림 5~8 |

- 함께 쓰는 파일: `07_core16`(①은 logit 담당, ②③은 xgb 담당이 실행, 결과 `outputs/core16/`), `lib_eval`(core 담당이 작성하고 eval 담당이 검증). 이 두 파일은 한 사람의 PR이 `main`에 합쳐진 뒤에 다음 사람이 브랜치를 땁니다.
- `contract/`는 core만 고치지만 `contract/xgb_params.json`은 예외로 03_tune(xgb)이 씁니다. 그 값을 `contract/params.json`의 `XGB_PARAMS`에 옮기는 것은 core가 합니다.
- 결과 판정에 직접 영향을 주는 `contract/`, `00_config`, `lib_prep`, `06_collect`, `99_freeze`, `05_test`를 바꾼 PR은 구역과 상관없이 core 담당이 승인합니다.

### 브랜치
작업 하나마다 `main`에서 브랜치를 새로 따고, PR로 합친 뒤 지웁니다(합치면 GitHub가 자동으로 지움).
- 이름: `<구역>/<할 일>`. 예: `logit/bootstrap-b100`, `xgb/mono-constraints`, `eval/test-6b`, `core/config-hash`
- 하루 이틀 안에 PR을 올릴 수 있는 크기로 나눕니다. 오래 열어 두면 `main`과 멀어져서 충돌이 납니다.

```bash
git clone https://github.com/Walnutbrown/kdt14th-lendingclub.git # 처음 한 번
git switch main && git pull                                       # 작업 시작할 때마다
git switch -c logit/bootstrap-b100                                # 새 작업 브랜치
# ... 노트북 수정·실행 ...
git add notebooks/02_logit.ipynb && git commit -m "B=100 bootstrap 코드 정리"
git push -u origin logit/bootstrap-b100                           # 그다음 GitHub에서 PR 생성
```

- `git add .` 대신 자기 담당 코드/노트북만 add합니다.
- 데이터와 산출물(`raw/`, `test_hold/`, `data/`, `outputs/`, `report/`, `freeze/`)은 git에 올라가지 않습니다(`.gitignore`). 로컬에서 실행해 산출물이 생기면 팀 Drive 공유폴더에 직접 올립니다.

## 처음 한 번
1. 레포를 clone하고 패키지를 설치합니다: `git clone https://github.com/Walnutbrown/kdt14th-lendingclub.git` → `pip install -r requirements.txt`
2. 데이터는 팀 Drive에서 받아 같은 경로에 넣습니다(위치는 팀 Notion의 LendingClub 페이지 "데이터 위치").
   - `raw/us_treasury_3y_5y_monthly.csv` (모두)
   - `raw/lending_club_2020_train_new.csv` (01_prep을 돌리는 core만)
   - `data/dev_X_raw.parquet`, `data/dev_meta.parquet` (모두)
3. `contract/`의 약속 파일은 레포에 이미 들어 있습니다.

## 실행 규칙
- 노트북은 `notebooks/` 안에서 실행하고, 첫 칸은 다음 세 줄입니다.
  ```
  SKIP_LIB_TESTS = True
  %run -i ./00_config.ipynb
  %run -i ./lib_prep.ipynb
  ```
- 실행하면 `[config] 공유해시`(= OOB 공통 설정 해시)·`전체해시`와 `[lib_prep] 해시`가 출력됩니다. 개발 중에는 구역별 독립 설정(`XGB_PARAMS`, `DELTA`, `B_TEST`, `EXPLAIN`, `ROBUST`, `STAGE`)을 바꿔도 공유해시가 유지되어 무관한 모형 결과를 막지 않습니다.
- **실험 숫자·파라미터 수정**: `00_config.ipynb`를 열지 않고 **`contract/params.json`**의 값만 수정하면 됩니다(미결 확정 시 `"PENDING"`에서 해당 키만 삭제). 로컬 시험용 JSON을 따로 쓸 때는 `LC_PARAMS_JSON` 환경변수로 경로를 지정할 수 있습니다.
- `00_config`와 `lib_prep`은 core 담당만 고칩니다.
- Colab: 첫 코드 칸 맨 위에 아래 코드를 둡니다(로컬에서는 건너뜀). Drive를 마운트하고, 레포를 받고, Drive의 `raw/`·`data/`(투입)와 `outputs/`·`report/`·`freeze/`·`test_hold/`(산출)를 연결하고, optuna·한글 글꼴을 설치한 뒤 `notebooks/`로 이동합니다. 처음 한 번은 Drive 웹에서 공유받은 `LendingClub` 폴더(편집자 권한 필요)를 "바로가기 추가 → 내 드라이브"로 넣어 둡니다.
  - 기능 브랜치의 `00_config`·`lib_*`을 시험할 때는 `colab_setup.py` 실행 전에 `os.environ["LC_BRANCH"] = "<브랜치명>"`을 지정합니다.
  ```python
  import sys
  if "google.colab" in sys.modules:
      !curl -sL https://raw.githubusercontent.com/Walnutbrown/kdt14th-lendingclub/main/colab_setup.py -o /content/colab_setup.py
      %run -i /content/colab_setup.py
  ```
  실행 결과는 팀 Drive 공유폴더에 바로 자동 저장(덮어쓰기)되며 git에 올리지 않습니다(사람별·버전별 폴더를 따로 만들지 않고 아래 "노트북 순서" 표의 정해진 경로 위에 최신본을 그대로 덮어씁니다). Colab에서 수정한 노트북/코드만 브랜치에 올릴 때는 `save_results("<구역>/<할 일>", ["notebooks/..."], "메시지")`를 씁니다(Colab 왼쪽 열쇠 아이콘 보안 비밀에 `GH_TOKEN` 1회 등록).

## 노트북 순서
위에서 아래로 실행합니다. 각 노트북은 앞 단계의 출력 경로를 그대로 읽습니다.

| 단계 | 노트북 | 구역 | 읽는 것 | 쓰는 것 |
|---|---|---|---|---|
| 준비 | `01_prep` | core | `raw/lending_club_2020_train_new.csv`, `raw/us_treasury_3y_5y_monthly.csv` | `data/dev_X_raw.parquet`, `data/dev_meta.parquet`, `contract/` |
| 준비 | `01b_eda_audit` | core | `raw/` | 보고서 표 1~3 |
| 3 튜닝 | `03_tune` | xgb | `data/` | `contract/xgb_params.json` |
| 4 부트스트랩 | `02_logit` · `03_xgb` · `04_xgb_mono` | logit · xgb · xgb | `data/` | `outputs/logit/` · `outputs/xgb/` · `outputs/xgb_mono/` |
| 민감도 | `07_core16` | logit·xgb | `data/` | `outputs/core16/` |
| 5·6 a*·선택 | `06_collect` | logit | `outputs/{logit,xgb,xgb_mono}/` | `outputs/collect/selection.json`, 표 4, 그림 2~4 |
| 6b 사전 고정 | `99_freeze` | core | 위 전부 | `freeze/freeze_<시각>/FREEZE_RECORD.json` |
| 7 Test 준비 | `00b_test_prep` | core | `raw/lending_club_2020_test_new.csv`, `freeze/` | `test_hold/test_X_raw.parquet`, `test_meta.parquet`, `test_prep_meta.json` |
| 7·8 Test 평가 | `05_test` | eval | `test_hold/`, `outputs/*/`, `freeze/` | `report/tables/`, `report/figures/` (표 5~9·A, 그림 5~8) |

함수만 담은 노트북(직접 실행하지 않고 `%run`으로 불러 씀): `00_config`(설정 로더, 값은 `contract/params.json`), `lib_prep`(전처리), `lib_engine`(부트스트랩·SR 곡선), `lib_eval`·`lib_eval_add`(Test 평가). `model_template`은 모형 노트북의 원본입니다.

## 폴더
`raw/` 원본 CSV · `data/` 01_prep 출력 · `contract/` 설정·범주·열 순서·부호 · `outputs/` 모형별 결과 · `freeze/` 사전 고정 기록 · `test_hold/` Test parquet · `report/` 보고서 표·그림 (`contract/` 말고는 모두 Drive에만 있음)
