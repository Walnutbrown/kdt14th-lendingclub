# lendingclub 프로젝트 폴더 (2026-11-25)

Drive를 마운트하지 않고, 이 폴더를 각자 내려받아 씁니다. .py 파일은 없고 노트북만 있습니다.

## 필요한 패키지
numpy, pandas, pyarrow(parquet), scikit-learn(1.2 이상), xgboost, optuna(03_tune), matplotlib, shap(6-C). Colab에는 optuna만 없습니다(`pip install optuna`).

## Git 작업 방식 (GitHub 레포)

### 구역별 파일
자기 구역 파일만 고칩니다. 다른 구역 파일에 고칠 점이 있으면 그 구역 담당에게 요청합니다. 누가 어느 구역을 맡는지와 할 일 목록은 팀 Notion에서 관리합니다(이 레포에는 사람 정보를 두지 않습니다).

| 구역 | 파일 |
|---|---|
| `core` | `00_config`, `lib_prep`, `00b_test_prep`, `01_prep`, `01b_eda_audit`, `06_collect`, `99_freeze`, `contract/`, 보고서 본문 |
| `logit` | `02_logit`, `lib_engine`, `model_template`, `outputs/logit/`, 표 4, 그림 2~4, 부록 D·E |
| `xgb` | `03_tune`, `03_xgb`, `04_xgb_mono`, 부록 B·C |
| `eval` | `05_test`, `lib_eval_add`, 표 5~8, 그림 5~8 |

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
git add notebooks/02_logit.ipynb outputs/logit/ && git commit -m "B=100 bootstrap 결과"
git push -u origin logit/bootstrap-b100                           # 그다음 GitHub에서 PR 생성
```

- `git add .` 대신 자기 담당 파일만 add합니다.
- 데이터(`raw/`, `test_hold/`, `data/*.parquet`)는 git에 올라가지 않습니다(`.gitignore`).

## 처음 한 번
1. 팀 Drive `.ipynb/2026-11-25/lendingclub/` 폴더를 통째로 내려받아 원하는 곳에 둡니다. 결정 문서는 같은 날짜 폴더의 `decisions/`에 있습니다.
2. 팀 Drive `raw/`에서 내려받아 `raw/`에 넣습니다.
   - `us_treasury_3y_5y_monthly.csv` (모두)
   - `lending_club_2020_train.csv` (01_prep 담당 core 담당만)
   - test 파일은 넣지 않습니다. 넣으면 00_config가 멈춥니다.
3. `contract/`와 `report/`의 요약표는 이미 들어 있습니다(2026-11-25 실제 Dev로 생성). `data/`의 parquet 두 개는 core 담당이 `01_prep`을 돌려 Drive에 올리면 받아 같은 위치에 넣습니다.

## 실행 규칙
- 노트북은 `notebooks/` 안에서 실행하고, 첫 칸은 다음 세 줄입니다.
  ```
  SKIP_LIB_TESTS = True
  %run -i ./00_config.ipynb
  %run -i ./lib_prep.ipynb
  ```
- 실행하면 `[config] 해시`와 `[lib_prep] 해시`가 출력됩니다. 공지된 해시와 다르면 옛 파일입니다.
- `00_config`와 `lib_prep`은 core 담당만 고칩니다.
- Colab: 폴더를 `/content/lendingclub`으로 올리고, 첫 칸 맨 위에 `%cd /content/lendingclub/notebooks`. 세션이 끝나면 지워지므로 `outputs/`는 내려받아 둡니다.

## 노트북
- `00_config` 공통 설정 (core 담당)
- `lib_prep` 공통 전처리 함수 (core 담당)
- `01_prep` Dev 데이터, 약속 파일, 요약표 (core 담당)
- `01b_eda_audit` 보고서용 표 1~3 (core 담당, 원본 CSV 필요)
- `model_template` 02_logit, 03_xgb, 04_xgb_mono의 원본

## 폴더
`raw/` 원본 CSV · `data/` 01_prep 출력 · `contract/` 범주·열 순서·부호 · `outputs/` 모형별 결과 · `report/` 보고서 표·그림
