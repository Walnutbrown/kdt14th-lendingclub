# lendingclub 프로젝트 폴더 (2026-11-25)

코드는 이 GitHub 레포가 기준입니다. 데이터와 산출물(`raw/`, `data/`, `outputs/`, `report/`)은 모두 팀 Drive에 둡니다. AI 에이전트(Claude Code, Codex, Antigravity)로 작업할 때의 규칙은 [AGENTS.md](AGENTS.md)에 있습니다.

## 필요한 패키지
Python 3.10, `pip install -r requirements.txt` (검증된 버전 고정). Colab에는 optuna만 없습니다(`pip install optuna`).

## Git 작업 방식 (GitHub 레포)

### 구역별 파일
자기 구역 파일만 고칩니다. 다른 구역 파일에 고칠 점이 있으면 그 구역 담당에게 요청합니다. 누가 어느 구역을 맡는지와 할 일 목록은 팀 Notion에서 관리합니다(이 레포에는 사람 정보를 두지 않습니다).

| 구역 | 파일 |
|---|---|
| `core` | `00_config`, `lib_prep`, `00b_test_prep`, `01_prep`, `01b_eda_audit`, `99_freeze`, `contract/`, 보고서 본문 |
| `logit` | `02_logit`, `06_collect`, `lib_engine`, `model_template`, `outputs/logit/`, 표 4, 그림 2~4, 부록 D·E |
| `xgb` | `03_tune`, `03_xgb`, `04_xgb_mono`, `outputs/xgb/`, 부록 B·C |
| `eval` | `05_test`, `05b_explain`, `lib_eval_add`, `outputs/eval/`, 표 5~8, 그림 5~8 |

함께 쓰는 파일: `07_core16`(①은 logit 담당, ②③은 xgb 담당이 실행), `lib_eval`(core 담당이 작성하고 eval 담당이 검증). 이 두 파일은 한 사람의 PR이 `main`에 합쳐진 뒤에 다음 사람이 브랜치를 땁니다.

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
- 실행하면 `[config] 공유해시`(= OOB 공통 설정 해시)·`전체해시`와 `[lib_prep] 해시`가 출력됩니다. 개발 중에는 구역별 독립 설정(`XGB_PARAMS`, `DELTA`, `B_TEST`, `EXPLAIN`, `ROBUST`, `STAGE`)을 바꿔도 공유해시가 유지되어 무관한 모형 결과를 막지 않습니다. 최종 통합·사전 고정(`99_freeze`)에서는 모형별 범위 해시·파일 sha256·`selection.json`을 모두 검증하고, `00b_test_prep`·`05_test`는 `FREEZE_RECORD.json` 검증을 통과해야 Test를 엽니다.
- `00_config`와 `lib_prep`은 core 담당만 고칩니다.
- Colab: 첫 칸 맨 위에 아래 두 줄을 더합니다. Drive를 마운트하고, 레포를 받고, Drive의 `raw/`·`data/`(투입)와 `outputs/`·`report/`(산출)를 연결하고, optuna·한글 글꼴을 설치한 뒤 `notebooks/`로 이동합니다. 처음 한 번은 Drive 웹에서 공유받은 `LendingClub` 폴더(편집자 권한 필요)를 "바로가기 추가 → 내 드라이브"로 넣어 둡니다.
  - 기능 브랜치의 `00_config`·`lib_*`을 시험할 때는 `colab_setup.py` 실행 전에 `os.environ["LC_BRANCH"] = "<브랜치명>"`을 지정합니다.
  ```
  !curl -sL https://raw.githubusercontent.com/Walnutbrown/kdt14th-lendingclub/main/colab_setup.py -o /content/colab_setup.py
  %run -i /content/colab_setup.py
  ```
  실행 결과(`outputs/`, `report/`)는 팀 Drive 공유폴더에 바로 자동 저장(덮어쓰기)되며 git에 올리지 않습니다(사람별·버전별 폴더를 따로 만들지 않고 정해진 경로 `outputs/{logit,xgb,xgb_mono,core16,collect}/`, `report/` 위에 최신본을 그대로 덮어씁니다). Colab에서 수정한 노트북/코드만 브랜치에 올릴 때는 `save_results("<구역>/<할 일>", ["notebooks/..."], "메시지")`를 씁니다(Colab 왼쪽 열쇠 아이콘 보안 비밀에 `GH_TOKEN` 1회 등록).

## 노트북
- `00_config` 공통 설정 (core 담당)
- `lib_prep` 공통 전처리 함수 (core 담당)
- `01_prep` Dev 데이터, 약속 파일, 요약표 (core 담당)
- `01b_eda_audit` 보고서용 표 1~3 (core 담당, 원본 CSV 필요)
- `model_template` 02_logit, 03_xgb, 04_xgb_mono의 원본

## 폴더
`raw/` 원본 CSV · `data/` 01_prep 출력 · `contract/` 범주·열 순서·부호 · `outputs/` 모형별 결과 · `report/` 보고서 표·그림
