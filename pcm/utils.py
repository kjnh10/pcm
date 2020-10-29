#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
from pathlib import Path


def set_stdin(test_case):
    fdr = os.open(test_case, os.O_RDONLY)
    stdin = sys.stdin.fileno()
    os.dup2(fdr, stdin)


def get_last_modified_file(match_filename_pattern=[], exclude_filename_pattern=[], search_root: Path = Path('.')) -> Path:
    if (type(match_filename_pattern) == str):
        match_filename_pattern = [match_filename_pattern]
    if (type(exclude_filename_pattern) == str):
        exclude_filename_pattern = [exclude_filename_pattern]

    candidates = []
    for m_pat in match_filename_pattern:
        candidates += [(p.stat().st_mtime, p) for p in search_root.rglob(m_pat)]
    for pattern in exclude_filename_pattern:
        next_candidates = []
        for cand in candidates:
            if not re.search(pattern, str(cand[1])):
                next_candidates.append(cand)
        candidates = next_candidates

    candidates.sort(reverse=True)
    if len(candidates) > 0:
        codefile = candidates[0][1]
        return codefile.resolve()
    else:
        raise FileNotFoundError("no valid code file found")
