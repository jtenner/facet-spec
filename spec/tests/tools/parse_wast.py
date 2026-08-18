#!/usr/bin/env python3
"""Parse every Facet WAST script with wasm-tools.

This is syntax/encoding validation only; execution requires a Facet runtime
adapter. Auxiliary modules emitted by ``json-from-wast`` are isolated in a
temporary directory and never written into the source tree.
"""
from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wasm-tools", default="wasm-tools")
    args = parser.parse_args()

    failed: list[tuple[Path, str]] = []
    tests = sorted(ROOT.rglob("*.wast"))
    with tempfile.TemporaryDirectory(prefix="facet-wast-") as temporary:
        output_root = Path(temporary)
        for index, wast in enumerate(tests):
            wasm_dir = output_root / f"modules-{index}"
            wasm_dir.mkdir()
            json_output = output_root / f"test-{index}.json"
            process = subprocess.run(
                [
                    args.wasm_tools,
                    "json-from-wast",
                    "--wasm-dir",
                    str(wasm_dir),
                    "-o",
                    str(json_output),
                    str(wast),
                ],
                capture_output=True,
                text=True,
            )
            if process.returncode:
                failed.append((wast, process.stderr or process.stdout))

    if failed:
        for path, error in failed:
            print(f"{path}:\n{error}")
        return 1
    print(f"parsed {len(tests)} WAST tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
