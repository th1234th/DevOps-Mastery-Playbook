#!/usr/bin/env python3
"""Check relative Markdown links that point to local files."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parent.parent
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
CODE_BLOCK_PATTERN = re.compile(r"```.*?```", re.DOTALL)


def main() -> int:
    errors: list[str] = []
    for markdown_file in sorted(ROOT.rglob("*.md")):
        text = CODE_BLOCK_PATTERN.sub("", markdown_file.read_text(encoding="utf-8"))
        for match in LINK_PATTERN.finditer(text):
            destination = match.group(1).strip().split(maxsplit=1)[0].strip("<>")
            if not destination or destination.startswith(("https://", "http://", "mailto:", "#")):
                continue
            local_path = unquote(destination.split("#", maxsplit=1)[0].split("?", maxsplit=1)[0])
            if not local_path:
                continue
            target = (markdown_file.parent / local_path).resolve()
            if not target.is_relative_to(ROOT) or not target.exists():
                relative_source = markdown_file.relative_to(ROOT)
                errors.append(f"{relative_source}: missing or out-of-repo link: {destination}")

    if errors:
        print("Local Markdown link check failed:", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1

    print("Local Markdown links are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())