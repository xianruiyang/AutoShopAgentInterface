#!/usr/bin/env python3
"""Validate the distributable autoshop-agent-interface skill package."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "scripts/autoshop-agent.exe",
    "references/AutoShopAgentWorkflow.md",
    "references/AutoShopWorkspaceJsonReference.md",
    "references/AutoShopCliCommands.md",
    "references/AutoShopCliTesting.md",
    "references/AutoShopLiteStFormat.md",
    "references/AutoShopUiRefresh.md",
    "references/AutoShopSkillPathPolicy.md",
    "references/AutoShopEthercatSlaveTemplates.md",
    "references/AutoShopH5uQuickReference.md",
    "references/AutoShopH5uEasyProgrammingApplicationManual.md",
    "references/AutoShopH5uPlcInstructionManualCn.md",
    "references/AutoShopH5uSeriesUserManualCn.md",
    "references/AutoShopH5uSeriesBrochureEn.md",
]

TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt", ".ps1", ".st"}
DRIVE_PATH_RE = re.compile(r"\b[A-Za-z]:\\")
BANNED_FRAGMENTS = [
    "C:\\Users\\Admin",
    "F:\\program\\PLC",
    "D:\\program\\PLC",
    "AutoShopAgentInterfaceDev",
    "AutoShopAgentInterfaceWork",
    "PS20190609",
    "DESKTOP-QCNC9PH",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_privacy_hits(root: Path) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = read_text(path)
        rel = path.relative_to(root).as_posix()
        for line_no, line in enumerate(text.splitlines(), 1):
            reasons: list[str] = []
            if DRIVE_PATH_RE.search(line):
                reasons.append("drive-path")
            for fragment in BANNED_FRAGMENTS:
                if fragment in line:
                    reasons.append(fragment)
            if reasons:
                hits.append({"file": rel, "line": line_no, "reasons": sorted(set(reasons))})
    return hits


def get_cli_version(root: Path) -> str | None:
    exe = root / "scripts" / "autoshop-agent.exe"
    if not exe.exists():
        return None
    completed = subprocess.run(
        [str(exe), "version"],
        cwd=str(root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    output = (completed.stdout or completed.stderr).strip()
    if completed.returncode != 0:
        raise RuntimeError(f"version command failed with {completed.returncode}: {output}")
    return output


def validate(root: Path, expect_version: str | None) -> tuple[int, dict[str, object]]:
    missing = [name for name in REQUIRED_FILES if not (root / name).exists()]
    privacy_hits = find_privacy_hits(root)
    version = get_cli_version(root)
    version_ok = expect_version is None or version == expect_version
    ok = not missing and not privacy_hits and version_ok
    report: dict[str, object] = {
        "root": str(root),
        "ok": ok,
        "missing": missing,
        "privacyHits": privacy_hits,
        "version": version,
        "expectVersion": expect_version,
        "versionOk": version_ok,
    }
    return (0 if ok else 1), report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="skill package root")
    parser.add_argument("--expect-version", help="expected autoshop-agent.exe version")
    parser.add_argument("--json", action="store_true", help="print JSON report")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    code, report = validate(root, args.expect_version)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif code == 0:
        print(f"ok: {root}")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2), file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
