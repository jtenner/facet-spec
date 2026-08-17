#!/usr/bin/env python3
"""Install the validated WPSI conformance-suite payload.

This is a one-shot repository bootstrap helper. The payload is split into
small text blobs solely to cross the GitHub connector boundary; the resulting
suite contains ordinary reviewable source files and no generated archive.
"""

from __future__ import annotations

import base64
import hashlib
import io
import lzma
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
PART_GLOB = "wpsi-final.part*"
EXPECTED_PARTS = 8
EXPECTED_ARCHIVE_SHA256 = "ff8b34eaafe4b8ea6d4de15d7b12379f3a5865cbc22e514048d56024afadfff6"
EXPECTED_MEMBER_COUNT = 194
DEFERRED_PATHS = {
    ".github/workflows/conformance-suite.yml",
    "spec/tests/tools/__pycache__/check_suite.cpython-313.pyc",
}


def main() -> None:
    script_dir = ROOT / ".github" / "scripts"
    parts = sorted(script_dir.glob(PART_GLOB))
    if len(parts) != EXPECTED_PARTS:
        raise SystemExit(
            f"found {len(parts)} staged payload parts, expected {EXPECTED_PARTS}"
        )

    encoded = "".join(part.read_text(encoding="ascii").strip() for part in parts)
    archive = base64.b64decode(encoded, validate=True)
    actual_sha256 = hashlib.sha256(archive).hexdigest()
    if actual_sha256 != EXPECTED_ARCHIVE_SHA256:
        raise SystemExit(
            "staged WPSI suite digest mismatch: "
            f"got {actual_sha256}, expected {EXPECTED_ARCHIVE_SHA256}"
        )

    payload = lzma.decompress(archive)
    installed = 0
    root = ROOT.resolve()

    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:") as tar:
        members = tar.getmembers()
        if len(members) != EXPECTED_MEMBER_COUNT:
            raise SystemExit(
                f"archive contains {len(members)} members, "
                f"expected {EXPECTED_MEMBER_COUNT}"
            )

        for member in members:
            if member.name in DEFERRED_PATHS:
                continue
            if not member.isfile():
                raise SystemExit(f"unsupported archive member: {member.name}")

            target = (ROOT / member.name).resolve()
            try:
                target.relative_to(root)
            except ValueError as error:
                raise SystemExit(
                    f"archive member escapes repository root: {member.name}"
                ) from error

            source = tar.extractfile(member)
            if source is None:
                raise SystemExit(f"archive member has no contents: {member.name}")

            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read())
            target.chmod(member.mode & 0o777)
            installed += 1

    print(f"installed {installed} WPSI conformance-suite source files")


if __name__ == "__main__":
    main()
