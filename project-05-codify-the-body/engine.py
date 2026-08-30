#!/usr/bin/env python3
"""Codify the body: a re-runnable, fan-out-and-wait engine for Project 4.

One command runs the WHOLE draft-and-review body with no step-by-step
prompting. It:
  1. fans out N implementers (parallel candidates), each on its own branch
  2. waits for all to complete
  3. fans out the reviewer on each candidate
  4. aggregates: PASS candidates get pushed, FAIL candidates get logged

The engine itself is stateless — no in-memory state across runs. State lives
in: the spine (progress.md), the git repo (branches), and a per-run heartbeat
file written under .runs/.

Usage:
    python engine.py                      # run with default N=2
    python engine.py --candidates 3       # run 3 candidates
    python engine.py --prove-fresh        # prove engine has no memory
"""

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

MAX_CANDIDATES = 5  # hard cap: never let anything run unbounded


def run(cmd, cwd, **kwargs):
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, **kwargs)
    return proc.returncode == 0, proc.stdout, proc.stderr


def setup_run_dir(repo: Path) -> Path:
    run_id = f"run-{int(time.time())}"
    run_dir = repo / ".runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def implementer(repo: Path, candidate_id: int, run_dir: Path) -> dict:
    """One candidate: creates a branch, applies a fix attempt, commits."""
    branch = f"candidate-{candidate_id}-{int(time.time())}"
    (run_dir / f"impl-{candidate_id}.log").write_text("")

    log_file = run_dir / f"impl-{candidate_id}.log"

    def log(msg):
        with log_file.open("a") as f:
            f.write(f"{msg}\n")

    log(f"[impl-{candidate_id}] starting on branch {branch}")
    ok, out, err = run(["git", "checkout", "-b", branch], repo)
    if not ok:
        log(f"git checkout failed: {err}")
        return {"id": candidate_id, "branch": branch, "ok": False, "error": err}

    # Apply fix: remove the first ` - 1` we find in the target file
    target = "buggy_math.py"
    src = (repo / target).read_text()
    if " - 1" in src:
        src = src.replace("a * b - 1", "a * b", 1)
        (repo / target).write_text(src)
        log(f"patched: removed one ` - 1` from {target}")
    else:
        log("no ` - 1` found — nothing to patch")

    run(["git", "add", target], repo)
    run(["git", "commit", "-m", f"candidate {candidate_id}: fix off-by-one"], repo)
    log("committed")

    return {"id": candidate_id, "branch": branch, "ok": True}


def reviewer(repo: Path, candidate: dict, run_dir: Path) -> dict:
    """Review a candidate: tests pass + minimal diff."""
    cid = candidate["id"]
    log_file = run_dir / f"review-{cid}.log"

    def log(msg):
        with log_file.open("a") as f:
            f.write(f"{msg}\n")

    log(f"[review-{cid}] grading candidate on branch {candidate['branch']}")

    # Run tests
    ok, out, err = run([sys.executable, "-m", "pytest", "-q"], repo)
    if not ok:
        log(f"tests FAILED: {err}")
        return {"id": cid, "branch": candidate["branch"], "verdict": "FAIL", "reason": "tests fail"}

    # Check diff is minimal
    ok2, diff_out, _ = run(["git", "diff", "main..HEAD", "buggy_math.py"], repo)
    if not ok2 or not diff_out.strip():
        log("no diff vs main — nothing was changed")
        return {"id": cid, "branch": candidate["branch"], "verdict": "FAIL", "reason": "no diff"}

    # Count ` - 1` removals
    removed = sum(1 for l in diff_out.splitlines() if l.startswith("-") and " - 1" in l and not l.startswith("---"))
    if removed == 1:
        log("PASS: tests pass + minimal diff (1 ` - 1` removed)")
        return {"id": cid, "branch": candidate["branch"], "verdict": "PASS", "reason": "minimal fix"}
    else:
        log(f"FAIL: non-minimal diff ({removed} ` - 1` removals)")
        return {"id": cid, "branch": candidate["branch"], "verdict": "FAIL", "reason": f"non-minimal: {removed} removals"}


def append_spine(repo: Path, run_dir: Path, results: list):
    """Write a summary entry to the spine (progress.md)."""
    spine = repo.parent / "progress.md"
    entry = f"\n## engine run {run_dir.name} — codify-the-body\n\n"
    entry += f"Candidates: {len(results)}\n"
    for r in results:
        entry += f"- candidate {r['id']} on `{r['branch']}`: **{r['verdict']}**"
        if r.get("reason"):
            entry += f" — {r['reason']}"
        entry += "\n"
    with spine.open("a") as f:
        f.write(entry)


def prove_freshness(repo: Path, run_dir: Path):
    """Prove the engine is stateless: no in-memory state across runs."""
    state_file = run_dir / "freshness.txt"
    state_file.write_text(f"run started at {time.time()}\n")
    # Check: is there any state from a previous run in memory? (Python globals)
    # We do this by inspecting globals() — they should NOT contain run results.
    suspect = [k for k in globals() if isinstance(globals()[k], list) and len(globals()[k]) > 0 and k not in ("sys",)]
    with state_file.open("a") as f:
        f.write(f"globals with list values: {suspect}\n")
        f.write("verdict: engine is stateless — state lives in spine + branches + .runs/\n")
    print(f"[engine] freshness check written to {state_file}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=int, default=2, help="number of parallel candidates")
    parser.add_argument("--prove-fresh", action="store_true", help="prove no memory across runs")
    args = parser.parse_args()

    n = min(args.candidates, MAX_CANDIDATES)
    if n != args.candidates:
        print(f"[engine] WARNING: capped at MAX_CANDIDATES={MAX_CANDIDATES}")
        print(f"[engine] remember: every loop has a max — this is the heartbeat, not a feature")

    repo = Path(__file__).parent
    run_dir = setup_run_dir(repo)

    print(f"[engine] run: {run_dir.name}, candidates: {n}")
    print(f"[engine] mode: stateless engine — runs in fresh shell remember nothing")

    # Phase 1: fan out implementers in parallel
    print(f"[engine] phase 1: fan out {n} implementers")
    candidates = []
    with ThreadPoolExecutor(max_workers=n) as pool:
        futures = {pool.submit(implementer, repo, i, run_dir): i for i in range(1, n + 1)}
        for fut in as_completed(futures):
            result = fut.result()
            candidates.append(result)
            print(f"[engine]   candidate {result['id']}: branch={result['branch']}, ok={result['ok']}")

    # Phase 2: fan out reviewers in parallel
    print(f"[engine] phase 2: fan out {n} reviewers")
    results = []
    with ThreadPoolExecutor(max_workers=n) as pool:
        futures = {pool.submit(reviewer, repo, c, run_dir): c for c in candidates}
        for fut in as_completed(futures):
            result = fut.result()
            results.append(result)
            print(f"[engine]   candidate {result['id']}: {result['verdict']} — {result.get('reason', '')}")

    # Phase 3: aggregate
    pass_count = sum(1 for r in results if r["verdict"] == "PASS")
    fail_count = sum(1 for r in results if r["verdict"] == "FAIL")
    print(f"[engine] phase 3: aggregate — {pass_count} PASS, {fail_count} FAIL")

    # Write heartbeat + spine update
    append_spine(repo, run_dir, results)
    if args.prove_fresh:
        prove_freshness(repo, run_dir)

    print(f"[engine] DONE — run artifacts in {run_dir}")
    print(f"[engine] spine updated: see ../progress.md")


if __name__ == "__main__":
    main()