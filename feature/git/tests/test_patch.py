# git diff -U0 -w --no-color | git apply --cached --ignore-whitespace --unidiff-zero -
TEST_OLD_PATCHSET_WITH_WHITESPACE_CHANGE = """diff --git a/.github/workflows/testing.yml b/.github/workflows/testing.yml
index 20da85c6f..4242ad452 100644
--- a/.github/workflows/testing.yml
+++ b/.github/workflows/testing.yml
@@ -23,7 +23,8 @@ jobs:
         - "3.9"
 
     steps:
-      - uses: actions/checkout@v4
+      - uses: actions/
+          checkout@v4
       - name: Checkout full upstream repo
         run: |
           git remote set-url origin https://github.com/intel/dffml
"""
TEST_NEW_PATCHSET_WITH_WHITESPACE_CHANGE = """diff --git a/.github/workflows/testing.yml b/.github/workflows/testing.yml
index 20da85c6f..4242ad452 100644
--- a/.github/workflows/testing.yml
+++ b/.github/workflows/testing.yml
@@ -23,7 +23,8 @@ jobs:
         - "3.9"
 
     steps:
       - uses: actions/checkout@v4
       - name: Checkout full upstream repo
         run: |
           git remote set-url origin https://github.com/intel/dffml
"""
TEST_OLD_PATCHSET_ONLY_WHITESPACE_CHANGE = """diff --git a/.github/workflows/testing.yml b/.github/workflows/testing.yml
index 20da85c6f..4242ad452 100644
--- a/.github/workflows/testing.yml
+++ b/.github/workflows/testing.yml
@@ -23,7 +23,8 @@ jobs:
         - "3.9"
 
     steps:
-      - uses: actions/checkout@v4
+      - uses: actions/
+          checkout@v4
       - name: Checkout full upstream repo
         run: |
           git remote set-url origin https://github.com/intel/dffml
"""
TEST_NEW_PATCHSET_ONLY_WHITESPACE_CHANGE = """diff --git a/.github/workflows/testing.yml b/.github/workflows/testing.yml
index 20da85c6f..4242ad452 100644
--- a/.github/workflows/testing.yml
+++ b/.github/workflows/testing.yml
@@ -23,7 +23,8 @@ jobs:
         - "3.9"
 
     steps:
       - uses: actions/checkout@v4
       - name: Checkout full upstream repo
         run: |
           git remote set-url origin https://github.com/intel/dffml
"""
import unittest
import pprint

import io
import contextlib
from typing import Union, IO

import unidiff
import unidiff.patch


def remove_whitespace(original: Union[list[str], str]) -> str:
    if original and isinstance(original[0], unidiff.patch.Line):
        original = list([line.value for line in original])
    if isinstance(original, list):
        line_ending = "\n"
        CRLF = "\r\n"
        if any([CRLF in line for line in original]):
            line_ending = CRLF
        original = line_ending.join(original)
    return original.replace("\r", "").replace("\n", "").replace(" ", "").replace("\t", "")


def without_whitespace_changes(old_patchset: Union[IO, str]) -> str:
    with contextlib.ExitStack() as exit_stack:
        # Support for string or file object as input
        if isinstance(old_patchset, str):
            old_patchset = exit_stack.enter_context(io.StringIO(old_patchset))
        patchset = unidiff.PatchSet(old_patchset)
    for patch in patchset:
        for hunk in patch:
            added = []
            removed = []
            current_added = []
            current_removed = []
            for line in hunk:
                if line.line_type not in ("+", "-"):
                    continue
                # TODO Support for only added or just removed, rather than just
                # modifications>
                if (
                    current_added
                    and current_removed
                    and line.target_line_no is None
                ):
                    added.append(current_added)
                    removed.append(current_removed)
                    current_added = []
                    current_removed = []
                (
                    current_added if line.line_type == "+" else current_removed
                ).append(line)
            if current_added and current_removed:
                added.append(current_added)
                removed.append(current_removed)
            for current_added, current_removed in zip(added, removed):
                # Detect and avoid whitespace only changes
                if remove_whitespace(current_removed) == remove_whitespace(current_added):
                    # Remove changes to only whitespace
                    for line in current_added:
                        del hunk[hunk.index(line)]
                    # Add back changed lines as context
                    for line in current_removed:
                        line.line_type = " "
                for (source_i, source_line), (target_i, target_line) in zip(
                    enumerate(current_removed),
                    enumerate(current_added),
                ):
                    # TODO Handle more than left indent changes
                    source_left_indent_count = len(source_line.value) - len(
                        source_line.value.lstrip()
                    )
                    target_left_indent_count = len(target_line.value) - len(
                        target_line.value.lstrip()
                    )
                    tab_or_space = source_line.value[0]
                    if source_left_indent_count != target_left_indent_count:
                        target_line.value = (
                            tab_or_space * source_left_indent_count
                            + target_line.value.lstrip()
                        )
    return str(patchset)


class TestWithoutWhitespaceChanges(unittest.TestCase):
    def test_indent_spaces(self):
        self.maxDiff = None
        old_patchset = TEST_OLD_PATCHSET_WITH_WHITESPACE_CHANGE
        new_patchset_should_be = TEST_NEW_PATCHSET_WITH_WHITESPACE_CHANGE
        new_patchset = without_whitespace_changes(old_patchset)
        self.assertEqual(new_patchset, new_patchset_should_be)

    def test_remove_whitespace_only_changes(self):
        self.maxDiff = None
        old_patchset = TEST_OLD_PATCHSET_ONLY_WHITESPACE_CHANGE
        new_patchset_should_be = TEST_NEW_PATCHSET_ONLY_WHITESPACE_CHANGE
        new_patchset = without_whitespace_changes(old_patchset)
        self.assertEqual(new_patchset, new_patchset_should_be)
