#!/usr/bin/env python3
"""Render the project resume pack as an Apple-inspired PDF.

This renderer intentionally uses HTML/CSS and a local Chromium-compatible
browser instead of ReportLab so the output can have a more refined editorial
layout: large hero typography, soft cards, generous whitespace, subtle gradients,
and print-accurate colors.

Usage:
    python backend-agent-project-selector/references/markdown_to_apple_pdf.py \
        backend-agent-project-resume-pack.md \
        --output backend-agent-project-resume-pack.pdf \
        --html-output backend-agent-project-resume-pack.apple.html
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
UNORDERED_RE = re.compile(r"^\s*[-*+]\s+(.+)$")
ORDERED_RE = re.compile(r"^\s*\d+[.)]\s+(.+)$")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
PROJECT_RE = re.compile(r"^推荐项目\s*(\d+)[:：]\s*(.+)$")


CSS = r"""
:root {
  --paper: #ffffff;
  --ink: #1d1d1f;
  --muted: #6e6e73;
  --quiet: #86868b;
  --line: #d2d2d7;
  --line-soft: #ececf0;
  --surface: #f5f5f7;
  --blue: #0066cc;
  --blue-soft: #e8f2ff;
}

@page {
  size: A4;
  margin: 16mm 17mm 17mm;
}

* {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  padding: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
    "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  -webkit-font-smoothing: antialiased;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

body {
  font-size: 10.3pt;
  line-height: 1.74;
  letter-spacing: -0.012em;
}

a {
  color: var(--blue);
  text-decoration: none;
}

code {
  padding: 1px 4px 2px;
  border-radius: 5px;
  background: var(--surface);
  color: #333336;
  font-family: "SF Mono", Consolas, Menlo, monospace;
  font-size: 0.88em;
}

strong {
  color: var(--ink);
  font-weight: 720;
}

.cover {
  min-height: 264mm;
  padding: 18mm 0 0;
  break-after: page;
}

.cover-inner {
  position: relative;
}

.eyebrow {
  margin-bottom: 20mm;
  color: var(--quiet);
  font-size: 8pt;
  font-weight: 720;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.eyebrow::before {
  content: "";
  display: inline-block;
  width: 6px;
  height: 6px;
  margin-right: 9px;
  border-radius: 999px;
  background: var(--blue);
  vertical-align: 1px;
}

.cover h1 {
  max-width: 154mm;
  margin: 0 0 8mm;
  color: #111113;
  font-size: 39pt;
  line-height: 1.04;
  font-weight: 790;
  letter-spacing: -0.058em;
}

.hero-lead {
  max-width: 144mm;
  margin: 0 0 20mm;
  color: #515154;
  font-size: 13pt;
  line-height: 1.58;
  letter-spacing: -0.022em;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12mm;
  padding-top: 10mm;
  border-top: 1px solid var(--line);
}

.hero-card {
  min-height: 46mm;
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
}

.hero-card .label {
  margin-bottom: 4mm;
  color: var(--quiet);
  font-size: 7.8pt;
  font-weight: 760;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.hero-card .name {
  margin: 0 0 4mm;
  color: var(--ink);
  font-size: 19pt;
  line-height: 1.14;
  font-weight: 760;
  letter-spacing: -0.045em;
}

.hero-card .desc {
  margin: 0;
  color: #5f5f64;
  font-size: 9.7pt;
  line-height: 1.62;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0 12mm;
  margin-top: 17mm;
  border-top: 1px solid var(--line-soft);
}

.meta-card {
  padding: 5mm 0;
  border: 0;
  border-bottom: 1px solid var(--line-soft);
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.meta-key {
  display: block;
  margin-bottom: 1.5mm;
  color: var(--quiet);
  font-size: 7.2pt;
  font-weight: 760;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.meta-value {
  color: var(--ink);
  font-size: 9.3pt;
  line-height: 1.48;
}

.content {
  position: relative;
}

.section-panel,
.project-section {
  margin: 0 0 11mm;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  break-inside: auto;
}

.section-panel {
  padding-top: 2mm;
}

.project-section {
  break-before: page;
  padding-top: 0;
}

.project-section::before,
.project-section.agent-project::before {
  content: none;
}

.project-kicker,
.section-kicker {
  margin-bottom: 3mm;
  padding-bottom: 3mm;
  border-bottom: 1px solid var(--line);
  color: var(--quiet);
  font-size: 7.8pt;
  font-weight: 760;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

h2 {
  margin: 0 0 7mm;
  color: #111113;
  font-size: 24pt;
  line-height: 1.08;
  font-weight: 780;
  letter-spacing: -0.052em;
  break-after: avoid;
}

h3 {
  margin: 9mm 0 3mm;
  padding-top: 4mm;
  border-top: 1px solid var(--line-soft);
  color: #111113;
  font-size: 13.4pt;
  line-height: 1.22;
  font-weight: 740;
  letter-spacing: -0.032em;
  break-after: avoid;
}

h4 {
  display: block;
  margin: 5mm 0 3mm;
  color: var(--blue);
  font-size: 9.4pt;
  line-height: 1.35;
  font-weight: 720;
  letter-spacing: -0.012em;
  break-after: avoid;
}

p {
  margin: 0 0 4mm;
  color: #343437;
}

.lede {
  margin: 0 0 6mm;
  padding: 0 0 6mm;
  border-bottom: 1px solid var(--line-soft);
  color: #303033;
  font-size: 11.4pt;
  line-height: 1.72;
}

ul {
  margin: 0 0 5mm;
  padding: 0;
  list-style: none;
}

li {
  position: relative;
  margin: 0 0 2.8mm;
  padding-left: 5.2mm;
  color: #303033;
}

li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0.72em;
  width: 3.5px;
  height: 3.5px;
  border-radius: 999px;
  background: var(--blue);
}

.li-key {
  color: var(--ink);
  font-weight: 720;
}

.feature-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0;
  margin-top: 0;
  counter-reset: feature;
  border-top: 1px solid var(--line-soft);
}

.feature-list li {
  min-height: 0;
  margin: 0;
  padding: 4.2mm 0 4.2mm 12mm;
  border: 0;
  border-bottom: 1px solid var(--line-soft);
  border-radius: 0;
  background: transparent;
  break-inside: avoid;
}

.feature-list li::before {
  display: none;
}

.feature-list .step-number {
  position: absolute;
  left: 0;
  top: 4.4mm;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 7mm;
  height: 7mm;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: #fff;
  color: var(--blue);
  font-size: 7pt;
  font-weight: 760;
  letter-spacing: -0.02em;
}

.evidence-list {
  padding: 4mm 0 0;
  border-top: 1px solid var(--line-soft);
  border-radius: 0;
  background: transparent;
}

.evidence-list li:last-child,
.feature-list li:last-child {
  margin-bottom: 0;
}

.project-section > ul:first-of-type {
  display: block;
  margin-bottom: 7mm;
  padding-bottom: 2mm;
  border-bottom: 1px solid var(--line-soft);
}

.project-section > ul:first-of-type li {
  margin: 0 0 2.2mm;
  padding: 0 0 0 5.2mm;
  border-radius: 0;
  background: transparent;
  break-inside: avoid;
}

.project-section > ul:first-of-type li::before {
  left: 0;
  top: 0.72em;
}

.final-note {
  margin-top: 5mm;
  padding-top: 7mm;
  border-top: 2px solid var(--ink);
  background: transparent;
}

.watermark {
  position: fixed;
  right: 17mm;
  bottom: 8mm;
  color: rgba(110, 110, 115, 0.68);
  font-size: 7.1pt;
  letter-spacing: 0.02em;
}
"""


def inline_markdown(text: str) -> str:
    escaped = html.escape(text, quote=False)

    escaped = LINK_RE.sub(
        lambda match: (
            f'<a href="{html.escape(match.group(2), quote=True)}">'
            f"{html.escape(match.group(1), quote=False)}</a>"
        ),
        escaped,
    )
    escaped = BOLD_RE.sub(r"<strong>\1</strong>", escaped)
    escaped = INLINE_CODE_RE.sub(r"<code>\1</code>", escaped)
    return escaped


def strip_inline_markup(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    return text.strip()


def extract_document(markdown_text: str) -> tuple[str, list[tuple[str, str]], list[str]]:
    lines = markdown_text.splitlines()
    title = "项目选择与简历写法包"
    index = 0
    if lines and lines[0].startswith("# "):
        title = lines[0].removeprefix("# ").strip()
        index = 1

    meta: list[tuple[str, str]] = []
    while index < len(lines):
        line = lines[index].strip()
        if line.startswith("## "):
            break
        unordered = UNORDERED_RE.match(lines[index])
        if unordered:
            item = strip_inline_markup(unordered.group(1))
            if "：" in item:
                key, value = item.split("：", 1)
            elif ":" in item:
                key, value = item.split(":", 1)
            else:
                key, value = "说明", item
            meta.append((key.strip(), value.strip()))
        index += 1

    return title, meta, lines[index:]


def extract_project_titles(lines: list[str]) -> list[str]:
    titles: list[str] = []
    for line in lines:
        match = re.match(r"^##\s+推荐项目\s*\d+[:：]\s*(.+)$", line.strip())
        if match:
            titles.append(match.group(1).strip())
    return titles


def bullet_html(items: list[tuple[str, str]], context: str) -> str:
    if not items:
        return ""
    classes = ["feature-list"] if context in {"features", "suggestions"} else []
    if context == "evidence":
        classes.append("evidence-list")
    class_attr = f' class="{" ".join(classes)}"' if classes else ""
    rendered = [f"<ul{class_attr}>"]

    for raw_item, item_context in items:
        text = raw_item.strip()
        number = None
        number_match = re.match(r"^(\d+)[.)]\s*(.+)$", text)
        if number_match:
            number, text = number_match.group(1), number_match.group(2)

        if context in {"features", "suggestions"} or item_context in {"features", "suggestions"}:
            number_html = f'<span class="step-number">{html.escape(number or "•")}</span>'
            rendered.append(f"<li>{number_html}<span>{inline_markdown(text)}</span></li>")
            continue

        if "：" in text and len(strip_inline_markup(text.split("：", 1)[0])) <= 16:
            key, value = text.split("：", 1)
            rendered.append(
                "<li>"
                f'<span class="li-key">{inline_markdown(key)}</span>：{inline_markdown(value)}'
                "</li>"
            )
        else:
            rendered.append(f"<li>{inline_markdown(text)}</li>")

    rendered.append("</ul>")
    return "\n".join(rendered)


def paragraph_html(lines: list[str], first_in_section: bool) -> str:
    if not lines:
        return ""
    text = " ".join(line.strip() for line in lines).strip()
    cls = ' class="lede"' if first_in_section else ""
    return f"<p{cls}>{inline_markdown(text)}</p>"


def context_from_heading(text: str) -> str:
    if "代码验证摘要" in text:
        return "evidence"
    if "负责功能" in text or "技术难点" in text:
        return "features"
    if "建议简历功能点" in text:
        return "suggestions"
    return "default"


def render_body(lines: list[str]) -> str:
    parts: list[str] = ['<main class="content">']
    section_open = False
    current_context = "default"
    current_list: list[tuple[str, str]] = []
    paragraph_lines: list[str] = []
    first_paragraph_in_section = False

    def flush_list() -> None:
        nonlocal current_list
        if current_list:
            parts.append(bullet_html(current_list, current_context))
            current_list = []

    def flush_paragraph() -> None:
        nonlocal paragraph_lines, first_paragraph_in_section
        if paragraph_lines:
            parts.append(paragraph_html(paragraph_lines, first_paragraph_in_section))
            paragraph_lines = []
            first_paragraph_in_section = False

    for line in lines:
        stripped = line.strip()
        heading = HEADING_RE.match(line)
        unordered = UNORDERED_RE.match(line)
        ordered = ORDERED_RE.match(line)

        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            text = heading.group(2).strip()

            if level == 2:
                if section_open:
                    parts.append("</section>")
                project = PROJECT_RE.match(text)
                if project:
                    project_number = project.group(1)
                    project_name = project.group(2)
                    project_class = "agent-project" if "GPT" in project_name or "Research" in project_name else "backend-project"
                    parts.append(f'<section class="project-section {project_class}">')
                    parts.append(f'<div class="project-kicker">PROJECT {project_number.zfill(2)}</div>')
                    parts.append(f"<h2>{inline_markdown(project_name)}</h2>")
                else:
                    final_class = " final-note" if "最终建议" in text else ""
                    parts.append(f'<section class="section-panel{final_class}">')
                    parts.append('<div class="section-kicker">REPORT SECTION</div>')
                    parts.append(f"<h2>{inline_markdown(text)}</h2>")
                section_open = True
                current_context = "default"
                first_paragraph_in_section = True
                continue

            if level == 3:
                current_context = context_from_heading(text)
                parts.append(f"<h3>{inline_markdown(text)}</h3>")
                first_paragraph_in_section = False
                continue

            if level >= 4:
                current_context = context_from_heading(text)
                parts.append(f"<h4>{inline_markdown(text)}</h4>")
                first_paragraph_in_section = False
                continue

        if unordered or ordered:
            flush_paragraph()
            raw_item = unordered.group(1) if unordered else ordered.group(1)
            current_list.append((raw_item, current_context))
            continue

        flush_list()
        paragraph_lines.append(stripped)

    flush_paragraph()
    flush_list()
    if section_open:
        parts.append("</section>")
    parts.append("</main>")
    return "\n".join(parts)


def render_cover(title: str, meta: list[tuple[str, str]], project_titles: list[str]) -> str:
    project_one = project_titles[0] if project_titles else "传统后端项目"
    project_two = project_titles[1] if len(project_titles) > 1 else "业务型 Agent 项目"
    meta_cards = "\n".join(
        "<div class=\"meta-card\">"
        f"<span class=\"meta-key\">{html.escape(key)}</span>"
        f"<span class=\"meta-value\">{inline_markdown(value)}</span>"
        "</div>"
        for key, value in meta[:4]
    )

    return f"""
<section class="cover">
  <div class="cover-inner">
    <div class="eyebrow">Source Verified Pack</div>
    <h1>{inline_markdown(title)}</h1>
    <p class="hero-lead">用更克制的 Apple Editorial 版式重排项目推荐报告：大标题、细线、留白与清晰层级，让源码验证信息和简历改造路线更像正式作品集文档。</p>

    <div class="hero-grid">
      <article class="hero-card backend">
        <div class="label">Backend System</div>
        <h2 class="name">{inline_markdown(project_one)}</h2>
        <p class="desc">交易链路、库存、搜索、缓存、MQ 和权限系统，负责承接传统后端工程能力。</p>
      </article>
      <article class="hero-card agent">
        <div class="label">Agent Workflow</div>
        <h2 class="name">{inline_markdown(project_two)}</h2>
        <p class="desc">检索、浏览、来源筛选、上下文压缩、报告生成和多 Agent 编排，负责体现 AI 应用落地能力。</p>
      </article>
    </div>

    <div class="meta-grid">{meta_cards}</div>
  </div>
</section>
"""


def render_html(markdown_text: str, document_title: str | None = None) -> str:
    title, meta, body_lines = extract_document(markdown_text)
    if document_title:
        title = document_title
    project_titles = extract_project_titles(body_lines)
    body = render_body(body_lines)
    cover = render_cover(title, meta, project_titles)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>{CSS}</style>
</head>
<body>
  {cover}
  {body}
  <div class="watermark">backend-agent-project-selector · source verified</div>
</body>
</html>
"""


def find_browser(explicit_browser: str | None = None) -> str:
    candidates: list[str] = []
    if explicit_browser:
        candidates.append(explicit_browser)
    env_browser = os.environ.get("CHROME_PATH") or os.environ.get("EDGE_PATH")
    if env_browser:
        candidates.append(env_browser)
    candidates.extend(
        [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ]
    )
    for command in ("chrome", "chrome.exe", "msedge", "msedge.exe", "chromium", "chromium-browser"):
        resolved = shutil.which(command)
        if resolved:
            candidates.append(resolved)

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
    raise FileNotFoundError("No local Chrome or Edge browser found for PDF printing.")


def print_pdf(html_path: Path, output_path: Path, browser: str | None = None) -> None:
    browser_path = find_browser(browser)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html_uri = html_path.resolve().as_uri()

    with tempfile.TemporaryDirectory(prefix="apple-pdf-profile-") as profile_dir:
        common_args = [
            browser_path,
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            f"--user-data-dir={profile_dir}",
            "--print-to-pdf-no-header",
            "--no-pdf-header-footer",
            f"--print-to-pdf={output_path.resolve()}",
            html_uri,
        ]
        attempts = ["--headless=new", "--headless"]
        last_error: subprocess.CalledProcessError | None = None
        for headless_flag in attempts:
            try:
                subprocess.run([common_args[0], headless_flag, *common_args[1:]], check=True)
                if output_path.exists() and output_path.stat().st_size > 0:
                    return
            except subprocess.CalledProcessError as exc:
                last_error = exc
        if last_error:
            raise last_error
        raise RuntimeError(f"PDF was not created: {output_path}")


def default_pdf_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}-apple.pdf")


def default_html_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}.apple.html")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render Markdown as an Apple-inspired PDF.")
    parser.add_argument("input", type=Path, help="Path to the Markdown file.")
    parser.add_argument("--output", "-o", type=Path, help="Output PDF path.")
    parser.add_argument("--html-output", type=Path, help="Optional HTML preview path.")
    parser.add_argument("--title", help="Override the document title.")
    parser.add_argument("--browser", help="Path to Chrome or Edge executable.")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.input.exists():
        raise FileNotFoundError(f"Markdown file not found: {args.input}")

    markdown_text = args.input.read_text(encoding="utf-8")
    html_text = render_html(markdown_text, args.title)
    html_path = args.html_output or default_html_path(args.input)
    pdf_path = args.output or default_pdf_path(args.input)

    html_path.write_text(html_text, encoding="utf-8")
    print_pdf(html_path, pdf_path, args.browser)
    print(f"HTML written: {html_path.resolve()}")
    print(f"PDF written: {pdf_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



