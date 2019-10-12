import os
import shutil
from pathlib import Path
import subprocess
from pcm.__main__ import cli, pp, ppp, sb, tt, ga
import click
from click.testing import CliRunner
import re

script_path = Path(os.path.dirname(__file__))

def test_pp():
    shutil.rmtree(script_path / 'tmp/test_pp/abc001', ignore_errors=True)
    os.chdir(script_path / 'tmp' / 'test_pp')
    
    proc = __run_command('pcm pp abc001')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))

    res = __is_same_dir(
            script_path/'tmp/test_pp/abc001',
            script_path/'tmp/test_pp/expected_abc001'
            )
    assert(res==True)

    shutil.rmtree(script_path / 'tmp/test_pp/abc001', ignore_errors=True)


def test_tt():
    os.chdir(script_path / 'tmp/test_tt/abc001/A/codes')
    os.utime('solve.cpp', None)  # update st_mtime for solve.cpp to be used

    proc = __run_command('pcm tt')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))
    assert(len(re.findall(r'.*solve\.cpp.*', proc.stdout.decode('utf-8'), re.MULTILINE))>=1)
    assert(len(re.findall('^--AC.*', proc.stdout.decode('utf-8'), re.MULTILINE))==1)
    assert(len(re.findall('^--WA.*', proc.stdout.decode('utf-8'), re.MULTILINE))==2)


def test_tt_python():
    os.chdir(script_path / 'tmp/test_tt/abc001/A/codes')
    proc = __run_command('pcm tt solve.py')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))
    assert(len(re.findall('^--AC.*', proc.stdout.decode('utf-8'), re.MULTILINE))==1)
    assert(len(re.findall('^--WA.*', proc.stdout.decode('utf-8'), re.MULTILINE))==2)


def test_tt_TLE():
    os.chdir(script_path / 'tmp/test_tt/abc001/A/codes')
    proc = __run_command('pcm tt solve_TLE.py')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))
    assert(len(re.findall('^--TLE.*', proc.stdout.decode('utf-8'), re.MULTILINE))==3)


def test_sb_atcoder():
    os.chdir(script_path / 'tmp/test_sb/abc001/A/codes')
    os.utime('solve.cpp', None)  # update st_mtime for solve.py to be used
    runner = CliRunner()
    result = runner.invoke(cli, args=['sb'], input='y')
    print(result.stdout)
    assert(result.exception == None)
    assert(re.search('.*AtCoderSubmission.from_url(.*)', result.stdout, re.S)!=None)


def __run_command(command, stdin=None, check=True):
    res = subprocess.run(
            command,
            stdin = stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=check,
            shell=True,
            )
    return res


def __is_same_dir(A, B):
    A_files = set()
    for p in A.glob("**/*"):
        if p.is_file():
            A_files.add(str(p.relative_to(A)))

    B_files = set()
    for p in B.glob("**/*"):
        if p.is_file():
            B_files.add(str(p.relative_to(B)))

    if (A_files==B_files):
        return True
    else:
        return False


if __name__ == "__main__":
    test_tt_TLE()
