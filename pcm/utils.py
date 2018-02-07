#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os


def set_stdin(test_case):
    fdr = os.open(test_case, os.O_RDONLY)
    stdin = sys.stdin.fileno()
    os.dup2(fdr, stdin)
