"""Colab 준비: Drive 마운트 → 레포 clone/pull → Drive 입출력(raw·data·outputs·report·freeze·test_hold) 연결 → optuna·한글 글꼴 → notebooks/로 이동.

노트북 첫 칸 (Colab에서만, 로컬 Jupyter는 기존 세 줄 그대로):
    !curl -sL https://raw.githubusercontent.com/Walnutbrown/kdt14th-lendingclub/main/colab_setup.py -o /content/colab_setup.py
    %run -i /content/colab_setup.py
    SKIP_LIB_TESTS = True
    %run -i ./00_config.ipynb
    %run -i ./lib_prep.ipynb

처음 한 번: Drive 웹에서 공유받은 'LendingClub' 폴더(편집자 권한 필요) → 오른쪽 클릭 → '바로가기 추가' → '내 드라이브'.
산출물(outputs/, report/, freeze/, test_hold/)은 Drive 공유폴더에 바로 자동 저장되며 git에 올리지 않습니다.
코드/노트북을 Colab에서 바로 push할 때만 save_results("logit/bootstrap-b100", ["notebooks/02_logit.ipynb"], "메시지") 사용
(Colab 왼쪽 열쇠 아이콘 '보안 비밀'에 GH_TOKEN 등록 필요: GitHub → Settings → Developer settings → Personal access tokens).
"""
import hashlib
import os
import shutil
import subprocess

REPO_URL = "github.com/Walnutbrown/kdt14th-lendingclub.git"
REPO = os.environ.get("LC_REPO", "/content/kdt14th-lendingclub")
BRANCH = os.environ.get("LC_BRANCH", "main").strip() or "main"
DRIVE_ROOT = os.environ.get("LC_DRIVE", "/content/drive/MyDrive/LendingClub")
IN_LINKS = {"raw": "raw", "data": ".ipynb/lendingclub/data"}   # 투입: Drive에 이미 있어야 함
OUT_LINKS = {"outputs": "outputs", "report": "report",         # 산출: 기존 Drive 폴더에 바로 덮어쓰기
             "freeze": "freeze", "test_hold": "test_hold"}     # 99_freeze 기록·00b Test parquet: 세션이 바뀌어도 05_test가 읽도록 Drive에 둠
BLOCKED_GIT_PREFIXES = ("raw/", "data/", "test_hold/", "outputs/", "report/", "freeze/")
NANUM = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"


def _sh(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, cwd=cwd, text=True, capture_output=True)
    if r.returncode:
        raise RuntimeError(f"실패: {cmd.split('@')[-1]}\n{r.stderr.strip()}")   # 토큰이 들어간 앞부분은 출력하지 않음
    return r.stdout.strip()


def _file_sha256(path, chunk_size=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            buf = f.read(chunk_size)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def _same_file(p1, p2):
    return os.path.getsize(p1) == os.path.getsize(p2) and _file_sha256(p1) == _file_sha256(p2)


def _find_conflicts(src_dir, dst_dir):
    """src_dir와 dst_dir 양쪽에 모두 존재하면서 내용이 다른 파일의 상대경로 목록을 반환한다."""
    conflicts = []
    for root, _, files in os.walk(src_dir):
        rel = os.path.relpath(root, src_dir)
        for name in sorted(files):
            rel_path = name if rel == "." else os.path.join(rel, name)
            src_f, dst_f = os.path.join(src_dir, rel_path), os.path.join(dst_dir, rel_path)
            if os.path.exists(dst_f) and not _same_file(src_f, dst_f):
                conflicts.append(rel_path)
    return conflicts


def _copy_missing(src_dir, dst_dir):
    """src_dir의 파일 중 dst_dir에 없는 것만 복사한다(Drive 기존 파일은 덮어쓰지 않음)."""
    for root, _, files in os.walk(src_dir):
        rel = os.path.relpath(root, src_dir)
        out_dir = dst_dir if rel == "." else os.path.join(dst_dir, rel)
        os.makedirs(out_dir, exist_ok=True)
        for name in files:
            src_f, dst_f = os.path.join(root, name), os.path.join(out_dir, name)
            if not os.path.exists(dst_f):
                shutil.copy2(src_f, dst_f)


from google.colab import drive  # noqa: E402  (Colab 전용)

drive.mount("/content/drive")
if not os.path.isdir(DRIVE_ROOT):
    raise FileNotFoundError(f"{DRIVE_ROOT} 없음. Drive 웹에서 LendingClub 폴더를 '내 드라이브'에 바로가기 추가하세요.")

if os.path.isdir(f"{REPO}/.git"):
    # 심볼릭 링크가 있으면 git pull/switch 충돌을 막기 위해 잠시 해제 후 복구
    for rel in (*IN_LINKS, *OUT_LINKS):
        dst = os.path.join(REPO, rel)
        if os.path.islink(dst):
            os.unlink(dst)
    subprocess.run("git checkout -q -- outputs report", shell=True, cwd=REPO, capture_output=True)
    _sh(f"git fetch -q origin {BRANCH}", cwd=REPO)
    _sh(f"git checkout -q -B {BRANCH} origin/{BRANCH}", cwd=REPO)
else:
    _sh(f"git clone -q --branch {BRANCH} https://{REPO_URL} {REPO}")

for rel, src in IN_LINKS.items():
    dst, target = os.path.join(REPO, rel), os.path.join(DRIVE_ROOT, src)
    if not os.path.isdir(target):
        raise FileNotFoundError(f"Drive에 {target} 없음")
    if os.path.islink(dst):
        os.unlink(dst)
    if os.path.exists(dst):  # 직접 넣어 둔 폴더는 건드리지 않음
        print(f"[colab_setup] {rel}/ 가 이미 있어 Drive 연결을 건너뜀")
    else:
        os.symlink(target, dst)

# 복사와 삭제를 시작하기 전에 OUT_LINKS 전체에서 내용이 다른 동명 파일 충돌을 먼저 검사한다.
_conflicts = []
for rel, src in OUT_LINKS.items():
    dst, target = os.path.join(REPO, rel), os.path.join(DRIVE_ROOT, src)
    if os.path.isdir(dst) and not os.path.islink(dst) and os.path.isdir(target):
        for c in _find_conflicts(dst, target):
            _conflicts.append((rel, os.path.join(dst, c), os.path.join(target, c)))
if _conflicts:
    details = "\n".join(f" - [{rel}] 로컬: {src_f}  ≠  Drive: {dst_f}" for rel, src_f, dst_f in _conflicts)
    raise FileExistsError(
        "로컬 폴더와 Drive 폴더에 내용이 다른 동명 파일이 있어 두 사본을 모두 보존하고 중단했습니다.\n"
        f"{details}\n"
        "유지할 쪽을 고른 뒤 나머지 사본(로컬 또는 Drive)을 삭제/이동하고 다시 실행하세요."
    )

for rel, src in OUT_LINKS.items():
    dst, target = os.path.join(REPO, rel), os.path.join(DRIVE_ROOT, src)
    os.makedirs(target, exist_ok=True)
    if os.path.islink(dst):
        os.unlink(dst)
    elif os.path.isdir(dst):
        _copy_missing(dst, target)   # 레포의 기존 요약표 등이 Drive에 없을 때만 보존
        shutil.rmtree(dst)
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
COLAB_SETUP_INFO = {
    "branch": _sh("git branch --show-current", cwd=REPO),
    "head": _sh("git rev-parse HEAD", cwd=REPO),
}
print(
    f"[colab_setup] 브랜치 {COLAB_SETUP_INFO['branch']} ({COLAB_SETUP_INFO['head'][:8]})"
    f" | raw·data·outputs·report·freeze·test_hold → {DRIVE_ROOT} | 위치 {os.getcwd()}"
)


def save_results(branch, paths, message, max_mb=5):
    """노트북/코드(paths)를 branch에 커밋하고 push한다. 데이터·산출물·5MB 넘는 파일은 막는다."""
    from google.colab import userdata
    token = userdata.get("GH_TOKEN")
    git = lambda c: _sh(f"git {c}", cwd=REPO)  # noqa: E731
    if git("branch --show-current") != branch:
        git(f"switch -c {branch}" if branch not in git("branch --list").split() else f"switch {branch}")
    git("add -- " + " ".join(paths))
    for f in git("diff --cached --name-only").splitlines():
        full = os.path.join(REPO, f)
        size_mb = os.path.getsize(full) / 1e6 if os.path.exists(full) else 0.0
        if size_mb > max_mb or f.startswith(BLOCKED_GIT_PREFIXES):
            git("reset -q")
            raise ValueError(f"{f} ({size_mb:.1f}MB)는 git에 올리지 않습니다. Drive에 저장됩니다.")
    # 작성자는 공용 이름으로 둔다 (레포에 사람 정보를 남기지 않음)
    git(f'-c user.name=lendingclub-colab -c user.email=colab@users.noreply.github.com commit -q -m "{message}"')
    git(f"push -q https://x-access-token:{token}@{REPO_URL} {branch}")   # 토큰을 .git/config에 저장하지 않음
    print(f"push 완료. PR 만들기: https://github.com/Walnutbrown/kdt14th-lendingclub/compare/{branch}?expand=1")
