import sys
import os
import fnmatch
import traceback


def set_stdin_sandbox(test_name="testcase1"):
    scrdir = os.path.dirname(__file__)
    fdr = os.open(scrdir + '/test/' + test_name, os.O_RDONLY)
    stdin = sys.stdin.fileno()
    os.dup2(fdr, stdin)

