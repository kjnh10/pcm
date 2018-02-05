#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import fnmatch
import subprocess

if len(sys.argv) != 1:
    exe = sys.argv[1]
else:
    exe = './submission.py'
exedir = exe[:exe.rfind('/')]
testdir = exedir + '/test/'


def set_stdin(test_case):
    fdr = os.open(test_case, os.O_RDONLY)
    stdin = sys.stdin.fileno()
    os.dup2(fdr, stdin)


if __name__ == '__main__':
    # auto test. For now, this is not used using oj test
    files = os.listdir(testdir)
    for filename in files:
        filepath = os.path.join(testdir, filename)
        if not fnmatch.fnmatch(filename, '*.in'):
            continue
        case = filename[:-3]
        infile = testdir + case + '.in'
        resfile = testdir + case + '.res'
        expfile = testdir + case + '.out'
        print('-'*10 + case + '-'*10)
        with open(resfile, 'w') as f:
            subprocess.call(['python', exe, case + '.in'],
                            stdout=f,
                            stderr=subprocess.STDOUT)
        with open(resfile, 'r') as f:
            res = f.read()
            print('*'*7 + ' output ' + '*'*7)
            print(res)
            res = res.split('\n')
        with open(expfile, 'r') as f:
            print('*'*7 + ' expected ' + '*'*7)
            exp = f.read()
            print(exp)
            exp = exp.split('\n')

        if len(res) != len(exp):
            print('result:WA\n\n')
            continue
        else:
            for i in range(len(res)):
                if res[i] != exp[i]:
                    print('result:WA\n\n')
                    break
            else:
                print('result:AC\n\n')

