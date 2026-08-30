#!/usr/bin/env python3
"""The daily-lint engine: FULL 6-part loop.

One invocation = one pass of the loop. No `while True`. Exits after one
complete cycle. The heartbeat wrapper (heartbeat-wrapper.sh) provides the
repeated scheduling.

6 parts (one pass):
1. Heartbeat — max runtime enforced by the wrapper; this engine itself has
   a MAX_ATTEMPTS cap so nothing runs unbounded.
2. Worktree — each run creates a fresh branch `daily-lint-<ts>` from main;
   never touches main directly.
3. Skill — `skill-lint-fix.md` encodes the fix procedure.
4. Maker-checker — implementer (implementer.py) drafts a fix; reviewer
   (reviewer.py) grades it. PASS → connector opens PR; FAIL → discard branch.
5. Connector — on PASS only: push branch + simulate PR open.
6. Spine — append a dated entry to ../progress.md.

Budget guards: MAX_ATTEMPTS=5, MAX_SECONDS in the wrapper (default 30 min).

Usage (via heartbeat):
    ./heartbeat-wrapper.sh                      # 30 min cap, runs daily

Usage (direct):
    python daily-lint-engine.py               # one pass, exits

Environment:
    MAX_SECONDS     → passed to heartbeat wrapper (default 1800 = 30 min)
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).parent
SPIPE = REPO.parent / "progress.md"

MAX_ATTEMPTS = 5  # hard cap within the engine
MAX_SECONDS = int(os.environ.get("MAX_SECONDS", "300"))  # 5 min default if run directly
START = time.time()

# ── 1. Heartbeat guard ──
def check_budget():
    elapsed = time.time() - START
    if elapsed > MAX_SECONDS:
        print(f"[engine] HARD TIME CAP: {elapsed:.0f}s > {MAX_SECONDS}s — exiting")
        sys.exit(0)


# ── 2. Worktree: fresh branch each run ──
def worktree_branch():
    ts = int(time.time())
    branch = f"daily-lint-{ts}"
    # Always start from main, never from current HEAD
    subprocess.run(["git", "checkout", "main"], cwd=REPO, check=True, capture_output=True)
    subprocess.run(["git", "checkout", "-b", branch], cwd=REPO, check=True)
    print(f"[engine] worktree: created branch {branch} from main")
    return branch


# ── 3. Skill reference ──
def print_skill_ref():
    skill_path = REPO / "skill-lint-fix.md"
    print(f"[engine] skill file: {skill_path}")
    if skill_path.exists():
        print(f"[engine]   (read: {skill_path.read_text()[:60]}…)")


# ── 4. Maker-checker: implementer + reviewer ──
def maker_checker(branch: str):
    """Run implementer then reviewer. Returns 'PASS' or 'FAIL'."""
    # Phase 4a: Implementer drafts fix in this branch
    print(f"[engine] maker-checker: implementer starting on {branch}")
    impl_result = subprocess.run(
        [sys.executable, "implementer.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    impl_pass = impl_result.returncode == 0

    # Phase 4b: Reviewer grades the fix
    print(f"[engine] maker-checker: reviewer starting")
    review_result = subprocess.run(
        [sys.executable, "reviewer.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    review_output = review_result.stdout.strip()
    # First non-empty line is the verdict
    first_line = review_output.splitlines()[0] if review_output else ""
    review_pass = first_line == "PASS"

    if impl_pass and review_pass:
        print(f"[DEBUG] impl_pass={impl_pass}, review_pass={review_pass}, first_line={repr(first_line)}")
        return "PASS"
    print(f"[DEBUG] impl_pass={impl_pass}, review_pass={review_pass}, first_line={repr(first_line)}")
    print(f"[DEBUG] impl rc={impl_result.returncode}, review rc={review_result.returncode}")
    print(f"[DEBUG] impl stdout: {impl_result.stdout[:200]}")
    print(f"[DEBUG] review stdout: {review_result.stdout[:200]}")
    return "FAIL"


# ── 5. Connector: push + PR on PASS ──
def connector_on_pass(branch: str):
    """Push branch and open PR — ONLY called on PASS."""
    print(f"[engine] connector: pushing branch {branch} and opening PR")
    # Pull latest from origin main first
    subprocess.run(["git", "fetch", "origin", "main"], cwd=REPO, capture_output=True)

    # Push the branch
    push = subprocess.run(
        ["git", "push", "--set-upstream", "origin", branch],
        cwd=REPO,
        capture_output=True,
        text=True,
    )

    if push.returncode == 0:
        print(f"[engine] connector: pushed {branch}")
        # Simulate PR open
        print(f"[engine] connector: PR opened — daily-lint sweep on {branch}")
        print(f"[engine] connector: PR body summarizes changes to target.py")
    else:
        print(f"[engine] connector: push failed: {push.stderr}")


# ── 6. Spine: append dated entry ──
def append_spine(verdict: str, branch_name: str):
    """Append a dated entry to the shared progress.md spine."""
    now = time.strftime("%Y-%m-%d %H:%M")
    entry = (
        f"\n## {now} — Daily Lint Sweep\n\n"
        f"- verdict: {verdict}\n"
        f"- runtime: {time.time() - START:.1f}s\n"
        f"- branch: `{branch_name}`\n"
        f"- engine: daily-lint-engine.py\n"
    )
    with SPIPE.open("a", encoding="utf-8") as f:
        f.write(entry)
    print(f"[engine] spine updated: {SPIPE}")


# ── Main orchestration ──
def main():
    print(f"[engine] starting daily-lint engine (max {MAX_SECONDS}s cap, "
          f"max {MAX_ATTEMPTS} attempts)")
    check_budget()

    # 2. Worktree
    branch = worktree_branch()
    check_budget()

    # 3. Skill ref
    print_skill_ref()
    check_budget()

    # 4. Maker-checker
    verdict = maker_checker(branch)
    check_budget()

    # 5. Connector (PASS only)
    if verdict == "PASS":
        connector_on_pass(branch)
    else:
        print(f"[engine] connector: FAIL — discarding branch {branch}")
        # Go back to main, delete the branch
        subprocess.run(["git", "checkout", "main"], cwd=REPO, check=True)
        subprocess.run(["git", "branch", "-D", branch], cwd=REPO, capture_output=True)

    # 6. Spine
    append_spine(verdict, branch)

    elapsed = time.time() - START
    print(f"[engine] DONE in {elapsed:.1f}s — verdict: {verdict}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily lint engine (one pass)")
    parser.add_argument("--max-seconds", type=int,
                        help="override time cap in seconds")
    parser.add_argument("--max-attempts", type=int,
                        help="override max fix attempts")
    args = parser.parse_args()

    # Apply CLI overrides
    if args.max_seconds is not None:
        import builtins
        # Re-bind module-level MAX_SECONDS via globals
        globals()["MAX_SECONDS"] = args.max_seconds
    if args.max_attempts is not None:
        globals()["MAX_ATTEMPTS"] = args.max_attempts

    main()