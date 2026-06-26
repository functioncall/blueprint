#!/usr/bin/env python3
"""Stamp the current git HEAD into a master file's provenance, so the freshness
check has a baseline. Run right after discovery writes/refreshes the master.
Usage: python3 stamp_provenance.py <master.json> [repo_dir]"""
import json
import subprocess
import sys


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: stamp_provenance.py <master.json> [repo_dir]")
    path = sys.argv[1]
    repo = sys.argv[2] if len(sys.argv) > 2 else "."
    head = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    if not head:
        raise SystemExit("not a git repo / git unavailable — cannot stamp")
    m = json.load(open(path))
    m.setdefault("provenance", {})["git_sha"] = head
    json.dump(m, open(path, "w"), indent=2)
    print(f"stamped {path} @ {head[:10]}")


if __name__ == "__main__":
    main()
