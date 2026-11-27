# 에이전트 작업 규칙 (Claude Code · Codex · Antigravity 공통)

이 레포에서 일하는 에이전트는 아래 규칙을 지킵니다. 규칙과 사용자 요청이 부딪히면 실행하지 말고 사용자에게 먼저 물어봅니다.
사용자(팀원)는 코드를 직접 검증하기 어렵습니다. **에이전트가 "됐다"고 말하는 근거를 숫자로 보여 주는 것**이 이 문서의 목적입니다.

## 0. 이 프로젝트가 하는 일 (모든 작업의 기준)
연구 질문: 신청 시점 정보만 쓸 때, XGBoost에 단조성 제약을 걸면 승인 포트폴리오의 SR(샤프비율)을 얼마나 잃고, 그 대가로 상식에 맞는 거절 사유를 얼마나 얻는가.

| 단계 | 하는 일 | 노트북 |
|---|---|---|
| 3 튜닝 | ② XGBoost 하이퍼파라미터를 Dev 전체 3-겹 CV(logloss)로 1회. ③은 같은 값, ①은 튜닝 없음 | `03_tune` |
| 4 부트스트랩 | SEED 하나로 재표본 B개. 회차마다 전처리·모형을 Train_b에만 맞추고 OOB에서 승인율별 SR 계산 | `02_logit`, `03_xgb`, `04_xgb_mono` |
| 5 승인율 a* | 모형마다 같은 승인율의 SR B개의 **중앙값** 곡선을 만들고 그 최댓값 지점을 a*로 | `06_collect` |
| 6 모델 선택 | 자기 a*에 고정한 회차별 SR을 같은 회차끼리 뺀 차이로 판정 (②−① 2.5% 분위수 > 0, ②−③ 97.5% 분위수 < δ면 ③) | `06_collect` → `selection.json` |
| 6a·6b | Dev 100% 재학습, 선택·a*·δ·파라미터를 해시와 함께 사전 고정 | 모형 노트북, `99_freeze` |
| 7·8 | Test **한 번** 채점: SR·ΔSR, AUC·KS·Brier·logloss, 위반율, Jaccard | `00b_test_prep`, `05_test` |

### 실험 불변 규칙 (어기면 결과 전체가 무효)
1. **Test를 열지 않습니다.** `test_hold/`, `*test*.csv`를 읽는 코드를 만들거나 실행하지 않습니다. `00b_test_prep`·`05_test`의 `DRY_RUN = False` 실행은 사용자가 "사전 고정 끝, 본 Test 실행"이라고 명시했을 때만 합니다.
2. **숫자는 `contract/params.json`에만 둡니다.** 노트북에 SEED, B, 승인율, 하이퍼파라미터, δ 같은 숫자를 직접 쓰지 않고 `00_config`가 만든 전역 변수를 씁니다.
3. **분할을 바꾸지 않습니다.** 부트스트랩 분할은 `make_oob_splits(n, B, seed=SEED)` 하나로만 만들고, 회차마다 시드를 다시 고정하지 않습니다. ①②③의 `split_hash`가 같아야 합니다.
4. **OOB는 평가 전용입니다.** OOB로 조기 종료, 튜닝, 전처리 fit을 하지 않습니다. 전처리는 회차마다 Train_b에만 fit합니다.
5. **②와 ③은 단조 제약만 다릅니다.** 데이터, 분할, 파라미터, 시드를 똑같이 둡니다.
6. **결과를 보고 규칙을 바꾸지 않습니다.** δ, a* 방식, 선택 규칙은 결과를 보기 전에 정합니다. 결과를 본 뒤 떠올린 분석은 "사후 분석"이라고 표시합니다.
7. 이 표와 코드가 다르면 고치지 말고 사용자에게 "설계와 코드가 다르다"고 알립니다.

## 1. 작업 전에 확인
- 사용자에게 **구역**(`core`, `logit`, `xgb`, `eval`)과 **할 일**을 확인합니다. 구역별 파일은 README의 "구역별 파일" 표를 봅니다. README와 노트북 안의 "담당" 표시가 다르면 사용자에게 물어봅니다.
- 자기 구역이 아닌 파일은 고치지 않습니다. 필요하면 사용자에게 "그 구역 담당에게 요청하라"고 알립니다.
- `notebooks/00_config.ipynb`, `notebooks/lib_prep.ipynb`, `contract/`는 `core` 구역만 고칩니다.
- **입력 파일 확인**: 에이전트는 팀 Drive를 직접 볼 수 없습니다(Colab에서만 연결됨). 노트북이 읽는 입력(`raw/`, `data/`, 선행 단계 `outputs/<모형>/`)을 목록으로 적어 사용자에게 보여 주고, Drive `LendingClub/`에 있는지 **사용자에게 확인을 받습니다.** 있다고 추측하지 않습니다.
- 입력 경로는 이전 단계가 저장한 경로(`DATA_DIR`, `OUT_DIR / "<모형>"`, `REPORT_DIR`)와 글자 그대로 같아야 합니다. 다르면 `00_config`의 공용 경로 기준으로 맞춥니다.

## 2. 시작: 항상 최신 main에서 새 브랜치
```bash
git switch main
git pull origin main
git switch -c <구역>/<할-일>      # 예: logit/bootstrap-b100, eval/test-6b
```
- 브랜치 하나 = 할 일 하나. 1~2일 안에 PR을 올릴 크기로 나눕니다.
- 이미 있는 다른 사람 브랜치에서 작업하지 않습니다.

## 3. 커밋: 자기 코드·노트북만, 이름을 지정해서
```bash
git status                       # 바뀐 파일 확인
git add notebooks/02_logit.ipynb # 코드/노트북 파일만 직접 지정
git commit -m "<무엇을 했는지 한 줄>"
```
- `git add .`, `git add -A`, `git commit -a`는 쓰지 않습니다. 다른 구역 파일이 섞여 들어갑니다.
- **데이터와 산출물은 git이 아니라 팀 Drive(`LendingClub/`)에 둡니다.** 이 레포는 public이라 커밋한 파일은 누구나 받을 수 있고, 지워도 기록에 남습니다.
  - `raw/`, `test_hold/`, `data/`, `outputs/`, `report/`, `freeze/`는 절대 커밋하지 않습니다. `git add -f`로 `.gitignore`를 우회하지 않습니다.
  - git에 올리는 것은 노트북(`.ipynb`), 코드, 설정(`contract/`), 문서뿐입니다.
  - 로컬 실행으로 산출물이 생겼으면 커밋 대신 사용자에게 "Drive 공유폴더(`LendingClub/<폴더>/`)에 올리라"고 알립니다(`data/*.parquet`은 `00_config` 해시도 함께 공지).
  - 사람별·버전별 폴더나 접미사(`_v2`, `_new` 등)를 만들지 않고, 공용 경로(`data/`, `outputs/{logit,xgb,xgb_mono,core16,collect}/`, `report/`)에 최신본을 덮어씁니다.
  - 커밋 전에 `git diff --cached --stat`으로 확인하고, **5MB가 넘는 파일이 있으면 멈추고** 사용자에게 물어봅니다.
- **Colab**: 실행 노트북을 새로 만들거나 고칠 때는 첫 코드 셀 맨 위에 아래 코드를 둡니다(로컬에서는 건너뜀).
  ```python
  import sys
  if "google.colab" in sys.modules:
      !curl -sL https://raw.githubusercontent.com/Walnutbrown/kdt14th-lendingclub/main/colab_setup.py -o /content/colab_setup.py
      %run -i /content/colab_setup.py
  ```
  에이전트는 Colab을 실행할 수 없으므로, 푸시 후 사용자에게 Colab 링크(`https://colab.research.google.com/github/Walnutbrown/kdt14th-lendingclub/blob/<브랜치>/<노트북경로>`)로 실행하라고 안내합니다.
- **사람 정보 금지**: 이름, 이메일, 학번, `/Users/<이름>/...` 같은 로컬 경로를 파일·커밋 메시지에 넣지 않습니다. 노트북 출력에 로컬 경로가 찍혔으면 커밋 전에 출력을 지웁니다. 담당자 정보는 팀 Notion에만 있습니다.

## 4. "완료"라고 말하기 전에: 증거
사용자는 코드를 읽고 검증하기 어렵습니다. 아래 증거가 없으면 "완료"가 아니라 "코드만 바꿈, 실행 확인 안 됨"이라고 말합니다.
- **실행했으면** 출력에서 다음을 그대로 옮깁니다: `[config]` 공유해시, `[lib_prep]` 해시, 데이터 행 수, (모형이면) `split_hash`, B, a*, 걸린 시간.
- **실행하지 못했으면** (데이터 없음, Colab 필요 등) 사용자가 무엇을 실행하고 어떤 숫자를 확인하면 되는지 한 줄로 적습니다. 예: "Colab에서 06_collect 실행 → 표 t4b의 a*가 0.4~0.6 사이인지 확인".
- 오래 걸리는 실행(부트스트랩, 튜닝)은 먼저 `B_RUN = 3` 또는 `DRY_RUN = True`로 돌려 회차당 시간을 재고, 전체 예상 시간을 사용자에게 알린 뒤 본 실행합니다.
- 에러, 경고, `assert` 실패는 숨기거나 우회하지 않고 메시지 그대로 보여 줍니다. `assert`를 지우거나 조건을 느슨하게 바꿔 통과시키지 않습니다.

## 5. PR 올리기 전: main 변경 받기
```bash
git fetch origin
git merge origin/main            # rebase 말고 merge
```
- 충돌이 나면 **노트북(.ipynb) JSON을 손으로 합치지 않습니다.** 사용자에게 알리고, 상대 구역 파일이면 그쪽 버전을 그대로 받습니다(`git checkout --theirs <파일>`). 자기 파일이면 사용자와 상의해서 한쪽을 고른 뒤 변경을 다시 적용합니다.

## 6. 푸시와 PR
```bash
git push -u origin <브랜치>
gh pr create --base main --title "<구역>: <할 일>" --body "<무엇을, 왜. 4절의 증거. 결과 파일 경로>"
```
- PR 본문에 바뀐 파일과 4절의 증거(숫자, 그림 경로)를 적습니다.
- PR은 다른 팀원 1명의 승인 또는 레포의 PR 리뷰 봇 승인을 거쳐 merge합니다. 단 **`contract/`, `00_config`, `lib_prep`, `06_collect`, `99_freeze`, `05_test`를 바꾼 PR은 core 담당의 승인이 반드시 필요합니다**(결과 판정에 직접 영향).
- 작업한 에이전트가 자기 PR을 merge하지 않습니다.
- merge 뒤 로컬 정리: `git switch main && git pull origin main && git branch -d <브랜치>`

## 7. 하지 않는 것
- `main`에 직접 커밋·푸시
- `git push --force`, `git reset --hard`, `git rebase`(공유 브랜치), `git push origin --delete`
- 다른 사람 브랜치 삭제, 다른 사람 PR 수정
- 막히면 우회하지 말고 사용자에게 상황과 에러 메시지를 그대로 보여 줍니다.
