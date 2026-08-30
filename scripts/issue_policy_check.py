#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / 'AGENTS.md'

if not AGENTS.exists():
    print('AGENTS.md is missing; cannot validate issue policy.')
    sys.exit(1)

text = AGENTS.read_text(encoding='utf-8')

if 'use labels instead' not in text.lower():
    print('AGENTS.md does not declare the label-based issue policy.')
    sys.exit(1)

# Accept title styles without the old prefixes, but reject explicit Future:/Parent: prefixes.
for bad_prefix in ('Future:', 'Parent:'):
    if re.search(rf'^{re.escape(bad_prefix)}', text, re.MULTILINE):
        print(f'Found forbidden issue title prefix in AGENTS.md: {bad_prefix}')
        sys.exit(1)

print('Issue policy check passed: label-based naming is declared and prefixes are not used.')
