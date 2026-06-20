#!/usr/bin/env python3
"""Clone GitHub repositories for mandatory source-code verification.

This script is intentionally small and dependency-free so the skill can run it
before generating final project recommendations. A repository that is not
successfully cloned by this script must not enter the final recommendation list.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable


GITHUB_URL_RE = re.compile(
    r"(?:https?://github\.com/|git@github\.com:)([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?(?:[/#?].*)?$"
)
GITHUB_SHORT_RE = re.compile(r"^([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?$")
MARKDOWN_GITHUB_RE = re.compile(
    r"(?:https?://github\.com/|git@github\.com:)[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?"
)


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def require_git() -> None:
    result = run(["git", "--version"])
    if result.returncode != 0:
        raise RuntimeError("git is not available on PATH; cannot clone repositories")


def normalize_repo(value: str) -> dict[str, str]:
    raw = value.strip().strip("` ")
    if not raw or raw.startswith("#"):
        raise ValueError("empty repository value")

    match = GITHUB_URL_RE.match(raw) or GITHUB_SHORT_RE.match(raw)
    if not match:
        raise ValueError(f"not a supported GitHub repository reference: {value}")

    owner, repo = match.group(1), match.group(2)
    repo = repo.removesuffix(".git")
    full_name = f"{owner}/{repo}"
    return {
        "input": value,
        "full_name": full_name,
        "clone_url": f"https://github.com/{full_name}.git",
        "html_url": f"https://github.com/{full_name}",
        "safe_dir": f"{owner}__{repo}",
    }


def read_repos_file(path: Path) -> list[str]:
    repos: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        urls = MARKDOWN_GITHUB_RE.findall(stripped)
        if urls:
            repos.extend(urls)
        else:
            repos.append(stripped)
    return repos


def unique_keep_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = value.strip()
        if key and key not in seen:
            seen.add(key)
            result.append(key)
    return result


def git_value(repo_dir: Path, args: list[str]) -> str:
    result = run(["git", *args], cwd=repo_dir)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def clone_repo(repo: dict[str, str], output_dir: Path, depth: int, keep_existing: bool) -> dict[str, str]:
    dest = output_dir / repo["safe_dir"]
    record = {
        "input": repo["input"],
        "full_name": repo["full_name"],
        "html_url": repo["html_url"],
        "clone_url": repo["clone_url"],
        "local_path": str(dest.resolve()),
        "status": "pending",
        "commit": "",
        "branch": "",
        "error": "",
    }

    try:
        if dest.exists() and not keep_existing:
            shutil.rmtree(dest)

        if dest.exists():
            if not (dest / ".git").exists():
                raise RuntimeError(f"target exists but is not a git repository: {dest}")
            fetch = run(["git", "fetch", "--depth", str(depth), "origin"], cwd=dest)
            if fetch.returncode != 0:
                raise RuntimeError(fetch.stderr.strip() or fetch.stdout.strip())
            reset = run(["git", "reset", "--hard", "HEAD"], cwd=dest)
            if reset.returncode != 0:
                raise RuntimeError(reset.stderr.strip() or reset.stdout.strip())
        else:
            clone = run(["git", "clone", "--depth", str(depth), repo["clone_url"], str(dest)])
            if clone.returncode != 0:
                raise RuntimeError(clone.stderr.strip() or clone.stdout.strip())

        record["commit"] = git_value(dest, ["rev-parse", "HEAD"])
        record["branch"] = git_value(dest, ["branch", "--show-current"])
        record["status"] = "cloned"
    except Exception as exc:  # noqa: BLE001 - manifest should preserve the exact failure
        record["status"] = "failed"
        record["error"] = str(exc)
    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clone GitHub repositories before final source-code verification."
    )
    parser.add_argument(
        "--repo",
        action="append",
        default=[],
        help="GitHub repository URL or owner/repo. Can be provided multiple times.",
    )
    parser.add_argument(
        "--repos-file",
        type=Path,
        help="UTF-8 text/Markdown file containing GitHub URLs or owner/repo values.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(".repo-source-cache"),
        help="Directory where repositories will be cloned. Default: .repo-source-cache",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("repo-source-manifest.json"),
        help="Path to write clone results manifest. Default: repo-source-manifest.json",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=1,
        help="git clone/fetch depth. Default: 1",
    )
    parser.add_argument(
        "--keep-existing",
        action="store_true",
        help="Reuse existing clone directories and fetch updates instead of deleting them first.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        require_git()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    raw_repos = list(args.repo)
    if args.repos_file:
        raw_repos.extend(read_repos_file(args.repos_file))
    raw_repos = unique_keep_order(raw_repos)
    if not raw_repos:
        print("ERROR: provide at least one --repo or --repos-file", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, str]] = []
    for raw_repo in raw_repos:
        try:
            repo = normalize_repo(raw_repo)
            record = clone_repo(repo, args.output_dir, args.depth, args.keep_existing)
        except Exception as exc:  # noqa: BLE001 - manifest should preserve malformed input
            record = {
                "input": raw_repo,
                "full_name": "",
                "html_url": "",
                "clone_url": "",
                "local_path": "",
                "status": "failed",
                "commit": "",
                "branch": "",
                "error": str(exc),
            }
        records.append(record)
        print(f"{record['status'].upper()}: {record.get('full_name') or raw_repo} -> {record.get('local_path')}")
        if record["error"]:
            print(f"  error: {record['error']}", file=sys.stderr)

    manifest = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "output_dir": str(args.output_dir.resolve()),
        "all_ok": all(record["status"] == "cloned" for record in records),
        "repos": records,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"MANIFEST: {args.manifest.resolve()}")
    return 0 if manifest["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
