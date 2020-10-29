import os

from pcm.__main__ import prepare, sb, test

from onlinejudge.implementation.main import main as oj

os.chdir("/home/koji0708/go/src/github.com/kjnh10/pcw/work/atcoder")

# oj(['download', 'https://arc096.contest.atcoder.jp/tasks/arc096_a'])
prepare(['https://arc096.contest.atcoder.jp'])
