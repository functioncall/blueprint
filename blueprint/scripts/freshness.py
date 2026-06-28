#!/usr/bin/env python3
"""Freshness check for a master diagram file (cache invalidation).

Cheap, git-only, NO agents. Compares the master's stored git_sha to HEAD; if the
repo moved, finds which scenarios' source_paths were touched, so only those need
re-research. Prints JSON the skill acts on (reuse / ask-before-refresh).

Usage:  python3 freshness.py <master.json> [repo_dir]
Exit 0 + {"status":"fresh"}            -> reuse the cache, render, done.
Exit 0 + {"status":"stale", ...}       -> ask before re-researching the listed scenarios.
Exit 0 + {"status":"no_provenance"}    -> first build (no git_sha yet) -> full discovery.
"""
import json
import os
import subprocess
import sys


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args],
                          capture_output=True, text=True).stdout.strip()


def touched(paths, changed):
    """A scenario/actor is stale if any changed file is at/under one of its paths."""
    hits = []
    for cf in changed:
        for p in paths:
            pp = p.rstrip("/")
            # exact file, or a file UNDER a directory path. NOT a bare prefix —
            # else source_path "src/store" wrongly matches changed "src/storefront.ts".
            if cf == pp or cf.startswith(pp + "/"):
                hits.append(cf)
                break
    return hits


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: freshness.py <master.json> [repo_dir]")
    master = json.load(open(sys.argv[1]))
    repo = sys.argv[2] if len(sys.argv) > 2 else "."

    sha = master.get("provenance", {}).get("git_sha", "")
    if not sha or sha == "GIT_SHA_AT_BUILD":
        print(json.dumps({"status": "no_provenance",
                          "note": "no git_sha — first build, run full discovery"}))
        return

    head = git(repo, "rev-parse", "HEAD")
    if not head:
        print(json.dumps({"status": "unknown", "note": "not a git repo / git unavailable"}))
        return
    if head == sha:
        print(json.dumps({"status": "fresh", "head": head}))
        return

    # is the stored sha reachable? if not (rebase/shallow), treat everything stale.
    anc = subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", sha, "HEAD"])
    if anc.returncode != 0:
        ids = [s["id"] for s in master.get("scenarios", [])]
        print(json.dumps({"status": "stale", "head": head, "reason": "sha unreachable",
                          "stale_scenarios": ids, "changed_files": []}))
        return

    changed = [l for l in git(repo, "diff", "--name-only", f"{sha}..HEAD").splitlines() if l]
    stale, detail = [], {}
    for sc in master.get("scenarios", []):
        hits = touched(sc.get("source_paths", []), changed)
        if hits:
            stale.append(sc["id"])
            detail[sc["id"]] = sorted(set(hits))[:8]

    print(json.dumps({
        "status": "stale" if stale else "fresh",
        "head": head,
        "stale_scenarios": stale,
        "by_scenario": detail,
        "total_changed": len(changed),
    }, indent=2))


if __name__ == "__main__":
    main()
