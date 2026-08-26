#!/usr/bin/env python3
"""Tests for the source-level Facet import coverage scanner."""

from __future__ import annotations

import unittest

from check_suite import parse_sexpr
from report_import_coverage import directly_invoked_facet_imports


class DirectInvocationCoverageTests(unittest.TestCase):
    def test_counts_call_in_same_module(self) -> None:
        roots = parse_sexpr(
            """
            (module
              (import "facet" "abi_version" (func $target (result i32)))
              (func (export "run") (result i32)
                (call $target)))
            """
        )

        self.assertEqual(
            directly_invoked_facet_imports(roots),
            {"abi_version"},
        )

    def test_counts_return_call_in_same_module(self) -> None:
        roots = parse_sexpr(
            """
            (module
              (import "facet" "handle_close" (func $target (param i32) (result i32)))
              (func (export "run") (param i32) (result i32)
                (return_call $target (local.get 0))))
            """
        )

        self.assertEqual(
            directly_invoked_facet_imports(roots),
            {"handle_close"},
        )

    def test_does_not_merge_local_ids_across_modules(self) -> None:
        roots = parse_sexpr(
            """
            (module $A
              (import "facet" "abi_version" (func $shared (result i32))))
            (module $B
              (func $shared (result i32) (i32.const 0))
              (func (export "run") (result i32)
                (call $shared)))
            """
        )

        self.assertEqual(directly_invoked_facet_imports(roots), set())


if __name__ == "__main__":
    unittest.main()
