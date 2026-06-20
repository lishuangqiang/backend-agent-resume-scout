#!/usr/bin/env python3
"""Search GitHub repositories and build a diversified candidate pool.

This helper is intentionally dependency-free. It is used before cloning source
code: collect a broad pool, apply light-weight filters, and print a shortlist
preview for user confirmation.

Examples:
    python backend-agent-project-selector/references/search_github_candidates.py \
        --mode backend-only --output backend-candidate-pool.json \
        --shortlist-output backend-shortlist-preview.md

    python backend-agent-project-selector/references/search_github_candidates.py \
        --mode agent-only --min-stars 500 --per-query 12
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable


GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
GITHUB_REPO_URL = "https://api.github.com/repos/{full_name}"


@dataclass(frozen=True)
class BucketQuery:
    bucket: str
    query: str


BACKEND_QUERIES = [
    BucketQuery("电商交易", "topic:ecommerce stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("电商交易", "spring-boot mall stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("电商交易", "shop springboot stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("工单客服", "topic:helpdesk stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("工单客服", "topic:ticketing-system stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("工单客服", "customer support self-hosted stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("CRM/ERP", "topic:crm stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("CRM/ERP", "topic:erp stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("项目协作", "topic:project-management stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("内容CMS", "topic:cms stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("网盘文件", "topic:file-sharing stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("在线教育", "topic:lms stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("预约排班", "topic:scheduling stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("票据财务", "topic:invoice stars:{stars} pushed:>{pushed_after}"),
]

AGENT_QUERIES = [
    BucketQuery("业务型 Agent", "topic:ai-agent stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("多智能体", "topic:multi-agent stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("自主 Agent", "topic:autonomous-agent stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("企业知识库 Agent", "knowledge agent rag stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("数据分析 Agent", "data agent llm stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("研究报告 Agent", "ai research agent stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("代码 Agent", "coding agent stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("工作流 Agent", "workflow automation agent llm stars:{stars} pushed:>{pushed_after}"),
    BucketQuery("金融 Agent", "stock analysis agent llm stars:{stars} pushed:>{pushed_after}"),
]


BACKEND_INCLUDE = {
    "mall",
    "commerce",
    "ecommerce",
    "shop",
    "order",
    "payment",
    "inventory",
    "stock",
    "crm",
    "erp",
    "helpdesk",
    "support",
    "ticket",
    "project",
    "management",
    "cms",
    "file",
    "storage",
    "lms",
    "learning",
    "invoice",
    "timesheet",
    "booking",
}

AGENT_INCLUDE = {
    "agent",
    "agents",
    "multi-agent",
    "autonomous",
    "research",
    "rag",
    "knowledge",
    "workflow",
    "assistant",
    "data",
    "trading",
    "report",
    "coding",
}

AGENT_BUSINESS_GATE = {
    "业务数据": {
        "database", "data source", "datasource", "dataset", "sql", "analytics",
        "analysis", "document", "knowledge base", "knowledge", "report",
        "research", "trading", "finance", "customer", "ticket", "workflow",
    },
    "状态流转": {
        "workflow", "pipeline", "task", "job", "status", "state", "scheduler",
        "schedule", "dag", "orchestration", "approval", "review", "queue",
    },
    "持久化": {
        "postgres", "postgresql", "mysql", "sqlite", "mongodb", "redis",
        "storage", "vector store", "embedding", "persist", "persistence", "index",
    },
    "工具调用": {
        "tool calling", "tools", "mcp", "api", "connector", "function calling",
        "sandbox", "sql execution", "code execution", "web search", "browser tool",
    },
    "评测": {
        "eval", "evaluation", "benchmark", "metric", "score", "test case",
        "quality", "trace", "observability", "monitoring",
    },
    "用户价值": {
        "enterprise", "business", "customer", "support", "automation", "assistant",
        "report", "research", "trading", "analytics", "analysis", "knowledge",
        "data", "workflow", "devops", "ops",
    },
}

AGENT_TOOLING_DOWNRANK = {
    "framework",
    "sdk",
    "library",
    "toolkit",
    "desktop companion",
    "skill collection",
    "browser",
    "browser automation",
    "developer tool",
    "dev tool",
}

CODING_AGENT_TOOLCHAIN = {
    "coding agent",
    "code agent",
    "claude code",
    "codex",
    "lsp",
    "terminal",
    "worktree",
    "git worktree",
    "browser control",
    "devtools",
}

COMMON_EXCLUDE = {
    "awesome",
    "tutorial",
    "template",
    "demo",
    "example",
    "starter",
    "boilerplate",
    "dashboard",
    "storefront",
    "frontend",
    "theme",
    "ui kit",
    "component",
    "library",
    "sdk",
    "wrapper",
    "extension",
    "browser extension",
    "browser",
    "desktop companion",
    "framework",
    "skill collection",
    "toolkit",
}

COMMON_HARD_EXCLUDE = {
    "awesome",
    "template",
    "boilerplate",
    "dashboard",
    "storefront",
    "frontend",
    "theme",
    "ui kit",
    "component",
    "browser extension",
    "chrome extension",
    "desktop companion",
    "skill collection",
}

BACKEND_EXCLUDE = {
    "iot",
    "embedded",
    "hardware",
    "device management",
    "industrial",
    "scada",
    "mqtt",
    "firmware",
}

AGENT_EXCLUDE = {
    "prompt",
    "prompts",
    "chatgpt clone",
    "browser automation",
    "sidepanel",
    "chrome extension",
    "awesome list",
    "prompt collection",
}


def build_queries(mode: str, min_stars: int, max_stars: int, pushed_after: str) -> list[BucketQuery]:
    star_range = f"{min_stars}..{max_stars}"
    if mode == "backend-only":
        source = BACKEND_QUERIES
    elif mode == "agent-only":
        source = AGENT_QUERIES
    elif mode == "mixed":
        source = AGENT_QUERIES[:5] + BACKEND_QUERIES[:8]
    else:
        source = BACKEND_QUERIES + AGENT_QUERIES[:5]
    return [
        BucketQuery(item.bucket, item.query.format(stars=star_range, pushed_after=pushed_after))
        for item in source
    ]


def repo_text(repo: dict) -> str:
    values = [
        repo.get("full_name", ""),
        repo.get("description") or "",
        repo.get("language") or "",
        " ".join(repo.get("topics") or []),
        repo.get("readme_probe") or "",
    ]
    return " ".join(values).lower()


def count_gate_hits(text: str) -> tuple[int, list[str]]:
    hits: list[str] = []
    for gate_name, keywords in AGENT_BUSINESS_GATE.items():
        if any(keyword in text for keyword in keywords):
            hits.append(gate_name)
    return len(hits), hits


def is_coding_agent_toolchain(text: str) -> bool:
    return any(keyword in text for keyword in CODING_AGENT_TOOLCHAIN)


def score_repo(repo: dict, mode: str) -> tuple[int, list[str]]:
    text = repo_text(repo)
    include = BACKEND_INCLUDE if mode == "backend-only" else AGENT_INCLUDE
    exclude = set(COMMON_EXCLUDE)
    if mode == "backend-only":
        exclude |= BACKEND_EXCLUDE
    elif mode == "agent-only":
        exclude |= AGENT_EXCLUDE

    score = 0
    reasons: list[str] = []
    for word in include:
        if word in text:
            score += 2
            reasons.append(f"命中业务关键词:{word}")
    for word in exclude:
        if word in text:
            score -= 4
            reasons.append(f"降权/排除关键词:{word}")

    if mode == "agent-only":
        gate_count, gate_hits = count_gate_hits(text)
        if gate_count >= 3:
            score += gate_count * 2
            reasons.append(f"业务型Agent门槛:{'/'.join(gate_hits[:4])}")
        else:
            score -= 8
            reasons.append(f"业务型Agent门槛不足:{gate_count}/3")
        tooling_hits = [word for word in AGENT_TOOLING_DOWNRANK if word in text]
        if tooling_hits:
            score -= 4 + len(tooling_hits)
            reasons.append(f"偏框架/工具链:{'/'.join(tooling_hits[:3])}")
        if is_coding_agent_toolchain(text):
            score -= 3
            reasons.append("代码Agent工具链单独降权")

    stars = int(repo.get("stars") or 0)
    if stars >= 1000:
        score += 2
        reasons.append("1k+ star 社区验证")
    if stars > 20000:
        score -= 1
        reasons.append("过热项目轻微降权")

    description = repo.get("description") or ""
    if 20 <= len(description) <= 220:
        score += 1
        reasons.append("描述信息较完整")

    return score, reasons[:8]


def is_filtered(repo: dict, mode: str) -> tuple[bool, str]:
    text = repo_text(repo)
    hard_exclude = set(COMMON_HARD_EXCLUDE)
    if mode == "backend-only":
        hard_exclude |= BACKEND_EXCLUDE
    elif mode == "agent-only":
        hard_exclude |= AGENT_EXCLUDE
    for word in hard_exclude:
        if word in text:
            return True, f"硬排除关键词: {word}"
    if mode == "agent-only":
        gate_count, gate_hits = count_gate_hits(text)
        if gate_count < 2:
            return True, f"业务型Agent强门槛不足: {gate_count}/2 ({'/'.join(gate_hits) or '无'})"
    return False, ""


def github_get(url: str, token: str | None, timeout: int) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "backend-agent-project-selector",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_readme_probe(full_name: str, token: str | None, timeout: int, max_lines: int) -> tuple[str, str]:
    url = f"{GITHUB_REPO_URL.format(full_name=full_name)}/readme"
    try:
        payload = github_get(url, token, timeout)
        content = payload.get("content") or ""
        encoding = payload.get("encoding") or ""
        if encoding != "base64" or not content:
            return "", "README empty or unsupported encoding"
        raw = base64.b64decode(content, validate=False)
        text = raw.decode("utf-8", errors="ignore")
        lines = text.splitlines()[:max_lines]
        return "\n".join(lines), f"README probe {len(lines)} lines"
    except Exception as exc:  # noqa: BLE001 - README probe is best-effort
        return "", f"README probe failed: {exc}"


def search_repositories(
    queries: Iterable[BucketQuery],
    per_query: int,
    token: str | None,
    sleep_seconds: float,
    timeout: int,
    readme_lines: int,
) -> list[dict]:
    seen: dict[str, dict] = {}
    for item in queries:
        params = urllib.parse.urlencode(
            {"q": item.query, "sort": "updated", "order": "desc", "per_page": per_query}
        )
        url = f"{GITHUB_SEARCH_URL}?{params}"
        try:
            payload = github_get(url, token, timeout)
        except Exception as exc:  # noqa: BLE001 - keep searching remaining buckets
            print(f"QUERY_FAILED bucket={item.bucket!r} query={item.query!r} error={exc}", file=sys.stderr)
            time.sleep(sleep_seconds)
            continue

        total = payload.get("total_count", 0)
        print(f"QUERY bucket={item.bucket} total={total} query={item.query}")
        for raw in payload.get("items", []):
            full_name = raw.get("full_name", "")
            if not full_name:
                continue
            record = seen.setdefault(
                full_name,
                {
                    "full_name": full_name,
                    "url": raw.get("html_url"),
                    "stars": raw.get("stargazers_count", 0),
                    "language": raw.get("language"),
                    "pushed_at": raw.get("pushed_at"),
                    "description": raw.get("description"),
                    "topics": raw.get("topics", [])[:16],
                    "readme_probe": "",
                    "readme_probe_status": "not probed",
                    "buckets": [],
                    "queries": [],
                },
            )
            if item.bucket not in record["buckets"]:
                record["buckets"].append(item.bucket)
            record["queries"].append(item.query)
        time.sleep(sleep_seconds)
    if readme_lines > 0:
        for record in seen.values():
            full_name = record.get("full_name") or ""
            probe, status = fetch_readme_probe(full_name, token, timeout, readme_lines)
            record["readme_probe"] = probe
            record["readme_probe_status"] = status
            time.sleep(max(0.05, sleep_seconds / 3))
    return list(seen.values())


def enrich(records: list[dict], mode: str) -> list[dict]:
    enriched = []
    for record in records:
        filtered, filter_reason = is_filtered(record, mode)
        score, reasons = score_repo(record, mode)
        copy = dict(record)
        copy["score"] = score
        copy["filtered"] = filtered
        copy["filter_reason"] = filter_reason
        copy["score_reasons"] = reasons
        copy["bucket"] = " / ".join(copy.get("buckets") or [])
        enriched.append(copy)
    enriched.sort(key=lambda item: (item["filtered"], -item["score"], item.get("full_name", "")))
    return enriched


def pick_shortlist(records: list[dict], limit: int) -> list[dict]:
    shortlist: list[dict] = []
    used_buckets: set[str] = set()
    for record in records:
        if record.get("filtered"):
            continue
        buckets = record.get("buckets") or [record.get("bucket", "")]
        if any(bucket not in used_buckets for bucket in buckets) or len(shortlist) >= len(used_buckets):
            shortlist.append(record)
            used_buckets.update(buckets)
        if len(shortlist) >= limit:
            break
    if len(shortlist) < limit:
        chosen = {item["full_name"] for item in shortlist}
        for record in records:
            if record.get("filtered") or record["full_name"] in chosen:
                continue
            shortlist.append(record)
            if len(shortlist) >= limit:
                break
    return shortlist


def markdown_preview(mode: str, records: list[dict], shortlist: list[dict], output: Path) -> None:
    filtered = [record for record in records if record.get("filtered")]
    lines = [
        "# GitHub 项目短名单确认",
        "",
        f"> 生成时间：{datetime.now(UTC).isoformat()}",
        f"> 推荐模式：{mode}",
        "",
        "## 建议拉取短名单",
        "",
        "| 项目 | 链接 | 分桶 | 语言 | Star | 初筛分 | 选择理由 |",
        "| --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for item in shortlist:
        reasons = "；".join(item.get("score_reasons") or [])
        lines.append(
            f"| {item['full_name']} | {item.get('url')} | {item.get('bucket')} | "
            f"{item.get('language') or ''} | {item.get('stars') or 0} | {item.get('score')} | {reasons} |"
        )

    lines.extend(
        [
            "",
            "## 初筛淘汰样例",
            "",
            "| 项目 | 链接 | 分桶 | 淘汰 / 降权理由 |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in filtered[:20]:
        lines.append(
            f"| {item['full_name']} | {item.get('url')} | {item.get('bucket')} | {item.get('filter_reason')} |"
        )

    lines.extend(
        [
            "",
            "## 下一步",
            "",
            "请先确认短名单方向；确认后再运行 `pull_github_repos.py` 拉取源码并做本地源码验证。",
        ]
    )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search GitHub and build a project candidate pool.")
    parser.add_argument(
        "--mode",
        choices=["agent-only", "backend-only", "mixed", "safe-mode", "challenge-mode"],
        required=True,
        help="Recommendation mode used to choose query buckets and filters.",
    )
    parser.add_argument("--output", type=Path, default=Path("candidate-pool.json"))
    parser.add_argument("--shortlist-output", type=Path, default=Path("shortlist-preview.md"))
    parser.add_argument("--shortlist", type=int, default=4, help="Number of repos to preview before cloning.")
    parser.add_argument("--per-query", type=int, default=10, help="GitHub results per query. Max recommended: 20.")
    parser.add_argument("--min-stars", type=int, default=1000)
    parser.add_argument("--max-stars", type=int, default=50000)
    parser.add_argument("--pushed-after", default="2024-01-01")
    parser.add_argument("--sleep", type=float, default=1.2, help="Delay between GitHub API requests.")
    parser.add_argument("--timeout", type=int, default=35)
    parser.add_argument(
        "--readme-lines",
        type=int,
        default=260,
        help="Fetch and score the first N README lines for stronger project-type filtering. Use 0 to disable.",
    )
    parser.add_argument("--token-env", default="GITHUB_TOKEN", help="Environment variable containing GitHub token.")
    parser.add_argument(
        "--offline-sample",
        action="store_true",
        help="Do not call GitHub; write a small deterministic sample for script validation.",
    )
    return parser.parse_args()


def offline_records(mode: str) -> list[dict]:
    if mode == "agent-only":
        return [
            {
                "full_name": "sample/data-analysis-agent",
                "url": "https://github.com/sample/data-analysis-agent",
                "stars": 1800,
                "language": "Python",
                "pushed_at": "2026-01-01T00:00:00Z",
                "description": "Business data analysis agent with datasource connectors, SQL execution, workflow state, RAG retrieval, sandbox, evaluation benchmark and persistent reports",
                "topics": ["ai-agent", "data-analysis", "rag", "workflow"],
                "readme_probe": "Connect databases and datasets. Persist analysis jobs. Generate SQL, run tools in sandbox, evaluate outputs with benchmark metrics, and produce business reports.",
                "readme_probe_status": "offline sample",
                "buckets": ["数据分析 Agent"],
                "queries": [],
            },
            {
                "full_name": "sample/agent-framework-sdk",
                "url": "https://github.com/sample/agent-framework-sdk",
                "stars": 3200,
                "language": "TypeScript",
                "pushed_at": "2026-01-01T00:00:00Z",
                "description": "Lightweight AI agent framework SDK and toolkit for coding agent browser automation demos",
                "topics": ["ai-agent", "framework", "sdk"],
                "readme_probe": "Framework SDK template for building tools and browser automation examples. No business data, persistence, evaluation or workflow state included.",
                "readme_probe_status": "offline sample",
                "buckets": ["代码 Agent"],
                "queries": [],
            },
        ]
    return [
        {
            "full_name": "sample/shop-backend",
            "url": "https://github.com/sample/shop-backend",
            "stars": 1800,
            "language": "Java",
            "pushed_at": "2026-01-01T00:00:00Z",
            "description": "Spring Boot ecommerce backend with order payment inventory coupon modules",
            "topics": ["ecommerce", "spring-boot"],
            "readme_probe": "Order state machine, payment callback idempotency, inventory lock, coupon settlement, async notification and audit logs.",
            "readme_probe_status": "offline sample",
            "buckets": ["电商交易"],
            "queries": [],
        },
        {
            "full_name": "sample/frontend-dashboard",
            "url": "https://github.com/sample/frontend-dashboard",
            "stars": 3000,
            "language": "TypeScript",
            "pushed_at": "2026-01-01T00:00:00Z",
            "description": "Frontend dashboard template",
            "topics": ["dashboard", "template"],
            "readme_probe": "Frontend dashboard template components",
            "readme_probe_status": "offline sample",
            "buckets": ["内容CMS"],
            "queries": [],
        },
    ]


def main() -> int:
    args = parse_args()
    if args.offline_sample:
        records = offline_records(args.mode)
    else:
        token = os.getenv(args.token_env)
        queries = build_queries(args.mode, args.min_stars, args.max_stars, args.pushed_after)
        records = search_repositories(
            queries,
            args.per_query,
            token,
            args.sleep,
            args.timeout,
            args.readme_lines,
        )

    enriched = enrich(records, args.mode)
    shortlist = pick_shortlist(enriched, args.shortlist)
    args.output.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_preview(args.mode, enriched, shortlist, args.shortlist_output)
    print(f"CANDIDATES: {args.output.resolve()} ({len(enriched)} repos)")
    print(f"SHORTLIST: {args.shortlist_output.resolve()} ({len(shortlist)} repos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
