#!/usr/bin/env python
# -*- coding: utf-8 -*-

IN = 'sample-1.in'  # sample case for local test
def local_test():
    try:
        from pcm.utils import set_stdin
        import sys
        if len(sys.argv) == 1:
            set_stdin(os.path.dirname(__file__) + '/test/' + IN)
    except:
        pass


import sys
import os
import time
import re
from pydoc import help
import string
import math
import numpy as np
from operator import itemgetter
from collections import Counter
from collections import deque
from collections import defaultdict as dd
import fractions
from heapq import heappop, heappush, heapify
import array
from bisect import bisect_left, bisect_right, insort_left, insort_right
from copy import deepcopy as dcopy
import itertools
sys.setrecursionlimit(10**7)
INF = 10**20
GOSA = 1.0 / 10**10
MOD = 10**9+7
def LI(): return [int(x) for x in sys.stdin.readline().split()]
def LI_(): return [int(x)-1 for x in sys.stdin.readline().split()]
def LF(): return [float(x) for x in sys.stdin.readline().split()]
def LS(): return sys.stdin.readline().split()
def I(): return int(sys.stdin.readline())
def F(): return float(sys.stdin.readline())
def DP(N, M, first): return [[first] * M for n in range(N)]
def DP3(N, M, L, first): return [[[first] * L for n in range(M)] for _ in range(N)]


def solve():
    print(input())


if __name__ == "__main__":
    local_test()
    preprocess()
    solve()

