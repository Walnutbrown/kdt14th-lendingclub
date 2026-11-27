"""Colab 준비: Drive 마운트 → 레포 clone/pull → Drive의 raw/·data/ 연결 → optuna·한글 글꼴 → notebooks/로 이동.

노트북 첫 칸 (Colab에서만, 로컬 Jupyter는 기존 세 줄 그대로):
    !curl -sL https://raw.githubusercontent.com/Walnutbrown/kdt14th-lendingclub/main/colab_setup.py -o /content/colab_setup.py
    %run -i /content/colab_setup.py
    SKIP_LIB_TESTS = True
    %run -i ./00_config.ipynb
    %run -i ./lib_prep.ipynb

처음 한 번: Drive 웹에서 공유받은 'LendingClub' 폴더 → 오른쪽 클릭 → '바로가기 추가' → '내 드라이브'.
결과 저장: save_results("logit/bootstrap-b100", ["outputs/logit", "report/figures"], "B=100 결과")
           (Colab 왼쪽 열쇠 아이콘 '보안 비밀'에 GH_TOKEN 등록 필요: GitHub → Settings → Developer settings → Personal access tokens)
"""
import os
import subprocess

REPO_URL = "github.com/Walnutbrown/kdt14th-lendingclub.git"
REPO = os.environ.get("LC_REPO", "/content/kdt14th-lendingclub")
DRIVE_ROOT = os.environ.get("LC_DRIVE", "/content/drive/MyDrive/LendingClub")
LINKS = {"raw": "raw", "data": ".ipynb/lendingclub/data"}   # 레포 경로 → DRIVE_ROOT 아래 경로
NANUM = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"


def _sh(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, cwd=cwd, text=True, capture_output=True)
    if r.returncode:
        raise RuntimeError(f"실패: {cmd.split('@')[-1]}\n{r.stderr.strip()}")   # 토큰이 들어간 앞부분은 출력하지 않음
    return r.stdout.strip()


from google.colab import drive  # noqa: E402  (Colab 전용)

drive.mount("/content/drive")
if not os.path.isdir(DRIVE_ROOT):
    raise FileNotFoundError(f"{DRIVE_ROOT} 없음. Drive 웹에서 LendingClub 폴더를 '내 드라이브'에 바로가기 추가하세요.")

if os.path.isdir(f"{REPO}/.git"):
    _sh("git pull -q", cwd=REPO)
else:
    _sh(f"git clone -q https://{REPO_URL} {REPO}")

for rel, src in LINKS.items():
    dst, target = os.path.join(REPO, rel), os.path.join(DRIVE_ROOT, src)
    if not os.path.isdir(target):
        raise FileNotFoundError(f"Drive에 {target} 없음")
    if os.path.islink(dst):
        os.remove(dst)
    if os.path.exists(dst):  # 직접 넣어 둔 폴더는 건드리지 않음
        print(f"[colab_setup] {rel}/ 가 이미 있어 Drive 연결을 건너뜀")
    else:
        os.symlink(target, dst)

try:
    import optuna  # noqa: F401
except ImportError:
    _sh("pip -q install optuna")
if not os.path.exists(NANUM) and os.path.exists("/usr/bin/apt-get"):
    _sh("apt-get -qq install -y fonts-nanum")
if os.path.exists(NANUM):
    from matplotlib import font_manager
    font_manager.fontManager.addfont(NANUM)   # 등록해 두면 lib_engine·lib_eval 모두 NanumGothic을 찾음

os.chdir(f"{REPO}/notebooks")
print(f"[colab_setup] 브랜치 {_sh('git branch --show-current', cwd=REPO)} | raw·data → {DRIVE_ROOT} | 위치 {os.getcwd()}")


def save_results(branch, paths, message, max_mb=5):
    """paths를 branch에 커밋하고 push한다. 데이터·5MB 넘는 파일은 막는다. 이후 GitHub에서 PR을 만든다."""
    from google.colab import userdata
    token = userdata.get("GH_TOKEN")
    git = lambda c: _sh(f"git {c}", cwd=REPO)  # noqa: E731
    if git("branch --show-current") != branch:
        git(f"switch -c {branch}" if branch not in git("branch --list").split() else f"switch {branch}")
    git("add -- " + " ".join(paths))
    for f in git("diff --cached --name-only").splitlines():
        size_mb = os.path.getsize(os.path.join(REPO, f)) / 1e6
        if size_mb > max_mb or f.startswith(("raw/", "data/", "test_hold/")):
            git("reset -q")
            raise ValueError(f"{f} ({size_mb:.1f}MB)는 git에 올리지 않습니다. Drive에 두세요.")
    # 작성자는 공용 이름으로 둔다 (레포에 사람 정보를 남기지 않음)
    git(f'-c user.name=lendingclub-colab -c user.email=colab@users.noreply.github.com commit -q -m "{message}"')
    git(f"push -q https://x-access-token:{token}@{REPO_URL} {branch}")   # 토큰을 .git/config에 저장하지 않음
    print(f"push 완료. PR 만들기: https://github.com/Walnutbrown/kdt14th-lendingclub/compare/{branch}?expand=1")
