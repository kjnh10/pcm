#!/usr/bin/env python
# -*- coding: utf-8 -*-

import array
import fractions
import itertools
import math
import os
import re
import string
import sys  # {{{
import time
from bisect import bisect_left, bisect_right, insort_left, insort_right
from collections import Counter
from collections import defaultdict as dd
from collections import deque
from copy import deepcopy as dcopy
from heapq import heapify, heappop, heappush
from inspect import currentframe
from operator import itemgetter
from pydoc import help

# }}}

# pre-defined{{{
sys.setrecursionlimit(10**7)
INF = 10**20
GOSA = 1.0 / 10**10
MOD = 10**9 + 7
ALPHABETS = [chr(i) for i in range(ord('a'), ord('z') + 1)]  # can also use string module


def LI():
    return [int(x) for x in sys.stdin.readline().split()]


def LI_():
    return [int(x) - 1 for x in sys.stdin.readline().split()]


def LF():
    return [float(x) for x in sys.stdin.readline().split()]


def LS():
    return sys.stdin.readline().split()


def I():
    return int(sys.stdin.readline())


def F():
    return float(sys.stdin.readline())


def DP(N, M, first):
    return [[first] * M for n in range(N)]


def DP3(N, M, L, first):
    return [[[first] * L for n in range(M)] for _ in range(N)]


# }}}


def solve():
    return 0


if __name__ == "__main__":  # {{{
    solve()

# vim: set foldmethod=marker: }}}
