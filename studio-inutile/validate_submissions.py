#!/usr/bin/env python3
"""
Studio Validator for Software Inutile (1-File Web Applets)
Checks:
  1. Required files (index.html + applet.manifest.json)
  2. Strict 10 KB (10,240 bytes) size cap on index.html
  3. Zero external dependencies (no http(s):// scripts, stylesheets, or @import)
  4. Zero explicit UI elements (<button>, <input>, <select>, <textarea>)
  5. Valid JSON manifest structure & postMessage bridge hooks
"""

import json
import re
import sys
from pathlib import Path

SUBMISSIONS_DIR = Path("./submissions")
MAX_BYTES = 10 * 1024  # 10 KB strict cap

# Patterns that violate the "Balsa & Silk Thread" rules
EXTERNAL_ASSET_RE = re.compile(
    r"""(?:src|href)\s*=\s*["']\s*(?:https?:)?//|@import\s+(?:url\()?["']?\s*(?:https?:)?//""",
    re.IGNORECASE,
)
EXPLICIT_UI_RE = re.compile(
    r"""<\s*(?:button|input|select|textarea)\b""",
    re.IGNORECASE,
)


def validate_manifest(manifest_path: Path) -> tuple[list[str], list[str], str]:
    errors = []
    warnings = []
    entrypoint = "index.html"

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"Invalid JSON syntax in applet.manifest.json: {e}"], [], entrypoint

    if not isinstance(data, dict):
        return ["Manifest root must be a JSON object."], [], entrypoint

    # Validate top-level 'applet' metadata
    applet = data.get("applet")
    if not isinstance(applet, dict):
        errors.append("Missing required 'applet' object in manifest.")
    else:
        for field in ("id", "name", "description", "author"):
            val = applet.get(field)
            if not isinstance(val, str) or not val.strip():
                errors.append(f"Missing or empty 'applet.{field}' string.")
        if "entrypoint" in applet:
            entrypoint = applet["entrypoint"]

    # Validate 'stateSchema'
    state_schema = data.get("stateSchema")
    if not isinstance(state_schema, dict) or state_schema.get("type") != "object":
        errors.append("Missing or invalid 'stateSchema' (must have type: 'object').")

    # Validate 'actions'
    actions = data.get("actions")
    if not isinstance(actions, dict) or len(actions) == 0:
        warnings.append("No 'actions' defined; conversational host cannot send air drafts.")
    else:
        for action_name, action_def in actions.items():
            if not isinstance(action_def, dict) or "inputSchema" not in action_def:
                errors.append(f"Action '{action_name}' is missing 'inputSchema'.")

    return errors, warnings, entrypoint


def validate_html(html_path: Path) -> tuple[list[str], list[str], int]:
    errors = []
    warnings = []

    if not html_path.exists():
        return [f"Missing entrypoint file: {html_path.name}"], [], 0

    raw_bytes = html_path.read_bytes()
    size_bytes = len(raw_bytes)

    # 1. Size cap check
    if size_bytes > MAX_BYTES:
        over = size_bytes - MAX_BYTES
        errors.append(
            f"Size limit exceeded: {size_bytes:,} bytes ({size_bytes / 1024:.2f} KB) — "
            f"{over:,} bytes over the 10 KB cap."
        )

    content = raw_bytes.decode("utf-8", errors="replace")

    # 2. Zero-external-dependency check
    ext_matches = EXTERNAL_ASSET_RE.findall(content)
    if ext_matches:
        errors.append(
            f"External network asset(s) detected ({len(ext_matches)} match(es)). "
            "All code and assets must be self-contained."
        )

    # 3. Zero-explicit-UI check
    ui_matches = EXPLICIT_UI_RE.findall(content)
    if ui_matches:
        errors.append(
            f"Explicit UI tag(s) detected ({', '.join(set(ui_matches))}). "
            "No buttons, inputs, or menus allowed."
        )

    # 4. Host bridge check (soft warning so standalone files still pass)
    if "postMessage" not in content:
        warnings.append("No 'postMessage' call found; applet won't report state to the host.")

    return errors, warnings, size_bytes


def main() -> int:
    if not SUBMISSIONS_DIR.exists():
        print(f"Directory not found: {SUBMISSIONS_DIR.resolve()}")
        return 1

    folders = sorted(
        p for p in SUBMISSIONS_DIR.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    )

    if not folders:
        print(f"No student submission folders found in {SUBMISSIONS_DIR}/")
        return 0

    print(f"Auditing {len(folders)} submission(s) in {SUBMISSIONS_DIR}/\n" + "=" * 60)

    total_failed = 0

    for folder in folders:
        manifest_path = folder / "applet.manifest.json"
        errors = []
        warnings = []
        entrypoint = "index.html"

        if not manifest_path.exists():
            errors.append("Missing required 'applet.manifest.json'.")
        else:
            m_err, m_warn, entrypoint = validate_manifest(manifest_path)
            errors.extend(m_err)
            warnings.extend(m_warn)

        h_err, h_warn, size_bytes = validate_html(folder / entrypoint)
        errors.extend(h_err)
        warnings.extend(h_warn)

        status = "PASS" if not errors else "FAIL"
        if errors:
            total_failed += 1

        size_str = f"{size_bytes / 1024:.2f} KB" if size_bytes else "0 KB"
        print(f"[{status}] {folder.name:<20} ({size_str} / 10.00 KB)")

        for err in errors:
            print(f"   ✗ ERROR: {err}")
        for warn in warnings:
            print(f"   ! WARN:  {warn}")

    print("=" * 60)
    print(f"Summary: {len(folders) - total_failed} passed, {total_failed} failed.")
    return 1 if total_failed else 0


if __name__ == "__main__":
    sys.exit(main())
