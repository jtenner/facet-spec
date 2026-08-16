#!/usr/bin/env python3
"""Install the staged WPSI conformance-suite archive into the repository."""

from __future__ import annotations

import base64
import gzip
import hashlib
import io
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
PART_GLOB = "wpsi-suite.part*"
EXPECTED_ARCHIVE_SHA256 = "a93644129db95e157d5c859a66daf60788ec5c17dd25dfba4e3df77847af8ba1"
EXPECTED_MEMBER_COUNT = 206
# This workflow cannot safely publish another workflow with every GitHub token
# configuration. The steady-state conformance workflow is added after bootstrap.
DEFERRED_PATHS = {".github/workflows/conformance-suite.yml"}


def main() -> None:
    parts = sorted((ROOT / ".github" / "scripts").glob(PART_GLOB))
    if not parts:
        raise SystemExit("no staged WPSI suite archive parts were found")

    encoded = "".join(part.read_text(encoding="ascii").strip() for part in parts)
    archive = base64.b64decode(encoded, validate=True)
    actual_sha256 = hashlib.sha256(archive).hexdigest()
    if actual_sha256 != EXPECTED_ARCHIVE_SHA256:
        raise SystemExit(
            "staged WPSI suite archive digest mismatch: "
            f"got {actual_sha256}, want {EXPECTED_ARCHIVE_SHA256}"
        )

    payload = gzip.decompress(archive)
    installed = 0
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:") as tar:
        members = tar.getmembers()
        if len(members) != EXPECTED_MEMBER_COUNT:
            raise SystemExit(
                f"archive contains {len(members)} members, want {EXPECTED_MEMBER_COUNT}"
            )

        root = ROOT.resolve()
        for member in members:
            if not member.isfile():
                raise SystemExit(f"unsupported non-file archive member: {member.name}")
            if member.name in DEFERRED_PATHS:
                continue

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
            installed += 1

    print(
        f"installed {installed} WPSI conformance-suite files "
        f"({len(DEFERRED_PATHS)} deferred)"
    )


if __name__ == "__main__":
    main()
