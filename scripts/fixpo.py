#!/usr/bin/env python3
"""One-shot: clean up broken \"...\" escapes in .po files and dedupe Memory entries.

This was caused by an earlier shell-escaping mishap. Safe to re-run."""
import os
import re
import sys

BASE = "/var/www/olymp.oshsu.kg"

for lang in ("ru", "ky"):
    p = os.path.join(BASE, f"locale/{lang}/LC_MESSAGES/django.po")
    with open(p, encoding="utf-8") as f:
        s = f.read()

    # 1. Replace literal `msgstr \"X\"` (escaped quotes) with `msgstr "X"`.
    s = re.sub(r'msgstr \\"([^"\\\n]+)\\"', r'msgstr "\1"', s)

    # 2. Remove duplicate "Memory" entries — keep only the first.
    blocks = re.findall(r'msgid "Memory"\nmsgstr "[^"]*"\n?', s)
    if len(blocks) > 1:
        first = blocks[0]
        # Replace all blocks first, then prepend one back at end
        for b in blocks:
            s = s.replace(b, "", 1)
        s = s.rstrip() + "\n\n" + first.rstrip() + "\n"

    with open(p, "w", encoding="utf-8") as f:
        f.write(s)
    print(lang, "fixed; Memory blocks found:", len(blocks))
