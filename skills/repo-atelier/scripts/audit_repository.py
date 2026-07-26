#!/usr/bin/env python3
"""Read-only audit for a product repository's public-facing surface."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote


EXCLUDED_DIRS = {
    ".git",
    ".next",
    ".nuxt",
    ".pytest_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
    "venv",
}

MEDIA_SUFFIXES = {
    ".avif",
    ".gif",
    ".jpeg",
    ".jpg",
    ".mov",
    ".mp4",
    ".png",
    ".svg",
    ".webm",
    ".webp",
}

DYNAMIC_SUFFIXES = {".gif", ".mov", ".mp4", ".webm"}
MARKDOWN_SUFFIXES = {".md", ".mdx", ".markdown"}
MAX_TEXT_BYTES = 2_000_000
MAX_FILES = 30_000

GOVERNANCE_GROUPS = {
    "license": ("license", "license.md", "license.txt", "copying"),
    "contributing": ("contributing.md", "contributing"),
    "security": ("security.md", "security"),
    "code_of_conduct": ("code_of_conduct.md", "code-of-conduct.md"),
    "support": ("support.md", "support"),
    "changelog": ("changelog.md", "changes.md", "history.md"),
}

PRODUCT_DOC_NAMES = {
    "product.md",
    "handoff.md",
    "getting_started.md",
    "getting-started.md",
    "troubleshooting.md",
    "roadmap.md",
}

SENSITIVE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "credentials.json",
    "id_dsa",
    "id_ed25519",
    "id_rsa",
    "secrets.json",
    "service-account.json",
}

SENSITIVE_SUFFIXES = {".key", ".p12", ".pfx", ".pem"}

LOCAL_PATH_PATTERNS = (
    re.compile(r"/Users/[A-Za-z0-9._-]+/[^\s)>'\"]+"),
    re.compile(r"/home/[A-Za-z0-9._-]+/[^\s)>'\"]+"),
    re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\[^\s)>'\"]+"),
)

SECRET_PATTERNS = (
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
)

PLACEHOLDER_PATTERNS = (
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"https?://example\.com", re.IGNORECASE),
    re.compile(r"\byour[-_ ](?:username|org|organization|project)\b", re.IGNORECASE),
    re.compile(r"\bREPLACE[_ -]?ME\b", re.IGNORECASE),
)

MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
HTML_LINK_RE = re.compile(
    r"<(?:img|a|source)\b[^>]*?\b(?:src|href)=[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    path: str | None = None
    line: int | None = None


def run_git(path: Path, *args: str) -> tuple[int, str]:
    try:
        process = subprocess.run(
            ["git", "-C", str(path), *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 127, ""
    return process.returncode, process.stdout.strip()


def find_git_root(path: Path) -> Path | None:
    code, output = run_git(path, "rev-parse", "--show-toplevel")
    if code != 0 or not output:
        return None
    return Path(output).resolve()


def walk_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS)
        for name in sorted(names):
            files.append(Path(current) / name)
            if len(files) >= MAX_FILES:
                return files
    return files


def relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def safe_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_TEXT_BYTES:
            return None
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def normalize_link_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    elif " " in target:
        first, rest = target.split(" ", 1)
        if rest.lstrip().startswith(("\"", "'")):
            target = first
    return unquote(target)


def is_external_or_anchor(target: str) -> bool:
    lowered = target.lower()
    return (
        not target
        or target.startswith("#")
        or lowered.startswith(
            (
                "data:",
                "ftp:",
                "http://",
                "https://",
                "mailto:",
                "tel:",
            )
        )
    )


def scan_markdown_links(
    root: Path, markdown_files: Iterable[Path], findings: list[Finding]
) -> None:
    for document in markdown_files:
        text = safe_text(document)
        if text is None:
            continue
        candidates = list(MARKDOWN_LINK_RE.finditer(text))
        candidates.extend(HTML_LINK_RE.finditer(text))
        for match in candidates:
            target = normalize_link_target(match.group(1))
            if is_external_or_anchor(target):
                continue
            clean = target.split("#", 1)[0].split("?", 1)[0]
            if not clean:
                continue
            if clean.startswith("/"):
                resolved = root / clean.lstrip("/")
            else:
                resolved = document.parent / clean
            if not resolved.exists():
                findings.append(
                    Finding(
                        "error",
                        "broken-relative-link",
                        f"Relative link target does not exist: {target}",
                        relative(root, document),
                        line_number(text, match.start()),
                    )
                )


def scan_text_risks(
    root: Path, markdown_files: Iterable[Path], findings: list[Finding]
) -> None:
    for document in markdown_files:
        text = safe_text(document)
        if text is None:
            continue
        rel = relative(root, document)
        for pattern in LOCAL_PATH_PATTERNS:
            for match in pattern.finditer(text):
                findings.append(
                    Finding(
                        "warning",
                        "local-absolute-path",
                        "Public-facing text appears to contain a machine-local absolute path.",
                        rel,
                        line_number(text, match.start()),
                    )
                )
        for pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                findings.append(
                    Finding(
                        "error",
                        "possible-secret",
                        "Public-facing text contains a string shaped like a credential; value withheld.",
                        rel,
                        line_number(text, match.start()),
                    )
                )


def scan_readme(
    root: Path, readme: Path | None, findings: list[Finding]
) -> dict[str, object]:
    if readme is None:
        findings.append(
            Finding(
                "warning",
                "missing-readme",
                "No root README file was found.",
            )
        )
        return {"path": None, "headings": [], "placeholder_lines": []}

    text = safe_text(readme)
    if text is None:
        findings.append(
            Finding(
                "warning",
                "readme-unreadable",
                "Root README is too large or could not be decoded as UTF-8.",
                relative(root, readme),
            )
        )
        return {"path": relative(root, readme), "headings": [], "placeholder_lines": []}

    headings = [match.group(2).strip() for match in HEADING_RE.finditer(text)]
    placeholder_lines: list[int] = []
    for pattern in PLACEHOLDER_PATTERNS:
        for match in pattern.finditer(text):
            number = line_number(text, match.start())
            placeholder_lines.append(number)
            findings.append(
                Finding(
                    "warning",
                    "placeholder-copy",
                    "README contains placeholder-like copy that should be reviewed.",
                    relative(root, readme),
                    number,
                )
            )

    if len(text.strip()) < 240:
        findings.append(
            Finding(
                "warning",
                "thin-readme",
                "README is very short for a public product surface.",
                relative(root, readme),
            )
        )

    return {
        "path": relative(root, readme),
        "headings": headings,
        "placeholder_lines": sorted(set(placeholder_lines)),
        "bytes": len(text.encode("utf-8")),
    }


def locate_root_readme(root: Path) -> Path | None:
    for candidate in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if candidate.is_file() and candidate.name.lower() in {
            "readme",
            "readme.md",
            "readme.mdx",
            "readme.markdown",
            "readme.txt",
        }:
            return candidate
    return None


def governance_inventory(files: list[Path]) -> dict[str, list[str]]:
    by_name: dict[str, list[str]] = {}
    for path in files:
        by_name.setdefault(path.name.lower(), []).append(path.as_posix())

    result: dict[str, list[str]] = {}
    for group, names in GOVERNANCE_GROUPS.items():
        matches: list[str] = []
        for name in names:
            matches.extend(by_name.get(name, []))
        result[group] = matches
    return result


def pages_signals(root: Path, files: list[Path]) -> list[str]:
    signals: list[str] = []
    candidates = {
        ".github/workflows/pages.yml",
        ".github/workflows/pages.yaml",
        "docs/index.html",
        "index.html",
    }
    relative_files = {relative(root, path) for path in files}
    for candidate in sorted(candidates):
        if candidate in relative_files:
            signals.append(candidate)
    for path in files:
        rel = relative(root, path)
        if rel.startswith(".github/workflows/") and "page" in path.name.lower():
            if rel not in signals:
                signals.append(rel)
    return sorted(signals)


def audit_repository(path: Path) -> dict[str, object]:
    requested = path.expanduser().resolve()
    findings: list[Finding] = []
    git_root = find_git_root(requested)
    root = git_root or requested

    if not requested.exists() or not requested.is_dir():
        return {
            "requested_path": str(requested),
            "root": None,
            "git": {"is_repository": False},
            "findings": [
                asdict(
                    Finding(
                        "error",
                        "invalid-path",
                        "The requested path does not exist or is not a directory.",
                        str(requested),
                    )
                )
            ],
            "summary": {"errors": 1, "warnings": 0, "info": 0},
        }

    if git_root is None:
        findings.append(
            Finding(
                "warning",
                "not-git-repository",
                "The requested directory is not inside a Git checkout; locate the real repository before publishing.",
                str(requested),
            )
        )

    files = walk_files(root)
    if len(files) >= MAX_FILES:
        findings.append(
            Finding(
                "warning",
                "scan-limit",
                f"File scan stopped after {MAX_FILES} files.",
            )
        )

    readme = locate_root_readme(root)
    markdown_files = [
        path for path in files if path.suffix.lower() in MARKDOWN_SUFFIXES
    ]
    scan_markdown_links(root, markdown_files, findings)
    scan_text_risks(root, markdown_files, findings)
    readme_data = scan_readme(root, readme, findings)

    tracked: set[str] = set()
    if git_root:
        code, output = run_git(root, "ls-files")
        if code == 0:
            tracked = {line for line in output.splitlines() if line}

    sensitive_candidates: list[dict[str, object]] = []
    for file in files:
        name = file.name.lower()
        if name in SENSITIVE_NAMES or file.suffix.lower() in SENSITIVE_SUFFIXES:
            rel = relative(root, file)
            is_tracked = rel in tracked
            sensitive_candidates.append({"path": rel, "tracked": is_tracked})
            findings.append(
                Finding(
                    "error" if is_tracked else "warning",
                    "sensitive-filename",
                    (
                        "A tracked file has a sensitive-looking filename."
                        if is_tracked
                        else "An untracked or non-Git file has a sensitive-looking filename; review before publishing."
                    ),
                    rel,
                )
            )

    media: list[dict[str, object]] = []
    for file in files:
        suffix = file.suffix.lower()
        if suffix not in MEDIA_SUFFIXES:
            continue
        rel = relative(root, file)
        try:
            size = file.stat().st_size
        except OSError:
            size = None
        media.append(
            {
                "path": rel,
                "type": suffix.lstrip("."),
                "bytes": size,
                "dynamic": suffix in DYNAMIC_SUFFIXES,
                "tracked": rel in tracked if git_root else None,
            }
        )

    governance_raw = governance_inventory(files)
    governance = {
        key: [relative(root, Path(value)) for value in values]
        for key, values in governance_raw.items()
    }
    product_docs = sorted(
        relative(root, file)
        for file in files
        if file.name.lower() in PRODUCT_DOC_NAMES
    )

    git: dict[str, object] = {"is_repository": git_root is not None}
    if git_root:
        for key, arguments in {
            "head": ("rev-parse", "HEAD"),
            "branch": ("branch", "--show-current"),
            "origin": ("remote", "get-url", "origin"),
            "exact_tag": ("describe", "--tags", "--exact-match"),
        }.items():
            code, output = run_git(root, *arguments)
            git[key] = output if code == 0 and output else None
        code, status = run_git(root, "status", "--short")
        git["dirty"] = bool(status) if code == 0 else None
        git["changed_paths"] = status.splitlines() if code == 0 and status else []

    counts = {
        f"{severity}s": sum(
            1 for finding in findings if finding.severity == severity
        )
        for severity in ("error", "warning", "info")
    }

    public_media = (
        [item for item in media if item["tracked"]]
        if git_root
        else media
    )
    local_only_media = (
        [item for item in media if not item["tracked"]]
        if git_root
        else []
    )

    return {
        "requested_path": str(requested),
        "root": str(root),
        "git": git,
        "readme": readme_data,
        "governance": governance,
        "product_docs": product_docs,
        "media": media,
        "public_media_count": len(public_media),
        "local_only_media_count": len(local_only_media),
        "dynamic_media_count": sum(
            1 for item in public_media if item["dynamic"]
        ),
        "local_dynamic_media_count": sum(
            1 for item in local_only_media if item["dynamic"]
        ),
        "pages_signals": pages_signals(root, files),
        "sensitive_candidates": sensitive_candidates,
        "findings": [asdict(finding) for finding in findings],
        "summary": counts,
    }


def human_report(result: dict[str, object]) -> str:
    lines = [
        "Repository productization audit",
        f"Root: {result.get('root') or 'unresolved'}",
    ]
    git = result.get("git", {})
    if isinstance(git, dict):
        lines.append(
            "Git: "
            + (
                f"{git.get('branch') or '(detached)'} @ {git.get('head') or 'unknown'}"
                if git.get("is_repository")
                else "not detected"
            )
        )
        if git.get("is_repository"):
            lines.append(f"Working tree dirty: {git.get('dirty')}")

    readme = result.get("readme", {})
    if isinstance(readme, dict):
        lines.append(f"README: {readme.get('path') or 'missing'}")

    media = result.get("media", [])
    lines.append(
        f"Media: {result.get('public_media_count', len(media) if isinstance(media, list) else 0)} "
        f"public/tracked, {result.get('local_only_media_count', 0)} local-only; "
        f"{result.get('dynamic_media_count', 0)} public dynamic"
    )
    pages = result.get("pages_signals", [])
    lines.append(
        "Pages signals: "
        + (", ".join(pages) if isinstance(pages, list) and pages else "none")
    )

    findings = result.get("findings", [])
    lines.append("")
    if isinstance(findings, list) and findings:
        lines.append("Findings:")
        for item in findings:
            if not isinstance(item, dict):
                continue
            location = ""
            if item.get("path"):
                location = f" [{item['path']}"
                if item.get("line"):
                    location += f":{item['line']}"
                location += "]"
            lines.append(
                f"- {str(item.get('severity', 'info')).upper()} "
                f"{item.get('code', 'finding')}{location}: {item.get('message', '')}"
            )
    else:
        lines.append("Findings: none")

    summary = result.get("summary", {})
    if isinstance(summary, dict):
        lines.extend(
            [
                "",
                "Summary: "
                f"{summary.get('errors', 0)} errors, "
                f"{summary.get('warnings', 0)} warnings, "
                f"{summary.get('info', 0)} info",
            ]
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit the public-facing surface of a product repository."
    )
    parser.add_argument("path", type=Path, help="Repository or project directory")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = audit_repository(args.path)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(human_report(result))
    summary = result.get("summary", {})
    if isinstance(summary, dict) and summary.get("errors", 0):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
