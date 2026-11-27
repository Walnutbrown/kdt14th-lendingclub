# 에이전트 작업 규칙 (Claude Code · Codex 공통)

이 레포에서 git 작업을 하는 에이전트는 아래 규칙을 지킵니다. 규칙과 사용자 요청이 부딪히면 실행하지 말고 사용자에게 먼저 물어봅니다.

## 0. 작업 전에 확인
- 사용자에게 **구역**(`core`, `logit`, `xgb`, `eval`)과 **할 일**을 확인합니다. 구역별 파일은 README의 "구역별 파일" 표를 봅니다.
- 자기 구역이 아닌 파일은 고치지 않습니다. 필요하면 사용자에게 "그 구역 담당에게 요청하라"고 알립니다.
- `notebooks/00_config.ipynb`, `notebooks/lib_prep.ipynb`, `contract/`는 `core` 구역만 고칩니다.

## 1. 시작: 항상 최신 main에서 새 브랜치
```bash
git switch main
git pull origin main
git switch -c <구역>/<할-일>      # 예: logit/bootstrap-b100, eval/test-6b
```
- 브랜치 하나 = 할 일 하나. 1~2일 안에 PR을 올릴 크기로 나눕니다.
- 이미 있는 다른 사람 브랜치에서 작업하지 않습니다.

## 2. 커밋: 자기 파일만, 이름을 지정해서
```bash
git status                       # 바뀐 파일 확인
git add notebooks/02_logit.ipynb outputs/logit/   # 파일을 직접 지정
git commit -m "<무엇을 했는지 한 줄>"
```
- `git add .`, `git add -A`, `git commit -a`는 쓰지 않습니다. 다른 구역 파일이 섞여 들어갑니다.
- **데이터는 git이 아니라 팀 Drive에 둡니다.** 이 레포는 public이라 커밋한 파일은 누구나 받을 수 있고, 지워도 기록에 남습니다.
  - 원본(`raw/`), Test(`test_hold/`), 중간 데이터(`data/*.parquet`)는 절대 커밋하지 않습니다. `git add -f`로 `.gitignore`를 우회하지 않습니다.
  - parquet을 새로 만들었으면 커밋 대신 사용자에게 "Drive `data/`에 올리고 `00_config`가 출력한 해시를 공지하라"고 알립니다.
  - git에 올리는 것은 `outputs/`, `report/`의 작은 결과물(표 CSV, json, 그림, 모델)뿐입니다.
  - 커밋 전에 `git diff --cached --stat`으로 확인하고, **5MB가 넘는 파일이 있으면 멈추고** 사용자에게 물어봅니다.
- **사람 정보 금지**: 이름, 이메일, 학번, `/Users/<이름>/...` 같은 로컬 경로를 파일·커밋 메시지에 넣지 않습니다. 노트북 출력에 로컬 경로가 찍혔으면 커밋 전에 `~`로 바꾸거나 출력을 지웁니다. 담당자 정보는 팀 Notion에만 있습니다.

## 3. PR 올리기 전: main 변경 받기
```bash
git fetch origin
git merge origin/main            # rebase 말고 merge
```
- 충돌이 나면 **노트북(.ipynb) JSON을 손으로 합치지 않습니다.** 사용자에게 알리고, 상대 구역 파일이면 그쪽 버전을 그대로 받습니다(`git checkout --theirs <파일>`). 자기 파일이면 사용자와 상의해서 한쪽을 고른 뒤 변경을 다시 적용합니다.

## 4. 푸시와 PR
```bash
git push -u origin <브랜치>
gh pr create --base main --title "<구역>: <할 일>" --body "<무엇을, 왜. 결과 파일 경로>"
```
- PR 본문에 바뀐 파일과 확인한 결과(숫자, 그림 경로)를 적습니다.
- 자기 PR을 스스로 merge하지 않습니다. 다른 팀원 1명이 승인해야 merge됩니다.
- merge되면 GitHub 브랜치는 자동으로 지워집니다. 로컬은 이렇게 정리합니다:
  ```bash
  git switch main && git pull origin main && git branch -d <브랜치>
  ```

## 5. 하지 않는 것
- `main`에 직접 커밋·푸시
- `git push --force`, `git reset --hard`, `git rebase`(공유 브랜치), `git push origin --delete`
- 다른 사람 브랜치 삭제, 다른 사람 PR 수정
- 막히면 우회하지 말고 사용자에게 상황과 에러 메시지를 그대로 보여 줍니다.
