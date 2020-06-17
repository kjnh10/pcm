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
    shutil.rmtree(script_path / 'data/test_pp/abc001', ignore_errors=True)
    os.chdir(script_path / 'data' / 'test_pp')
    
    proc = __run_command('pcm pp abc001')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))

    res = __is_same_dir(
            script_path/'data/test_pp/abc001',
            script_path/'data/test_pp/expected_abc001'
            )
    assert(res==True)

    shutil.rmtree(script_path / 'data/test_pp/abc001', ignore_errors=True)


def test_tt():
    os.chdir(script_path / f'data/test_tt/abc001/A/codes')
    os.utime('solve.cpp', None)  # update st_mtime for solve.cpp to be compiled

    proc = __run_command('pcm tt -cc simple')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))
    assert(len(re.findall(r'.*solve\.cpp.*', proc.stdout.decode('utf-8'), re.MULTILINE))>=1)
    assert(len(re.findall('^--AC.*', proc.stdout.decode('utf-8'), re.MULTILINE))==1)
    assert(len(re.findall('^--WA.*', proc.stdout.decode('utf-8'), re.MULTILINE))==2)


def test_tt_specify_name():
    os.chdir(script_path / f'data/test_tt/abc001/A/codes')
    os.utime('solve.cpp', None)  # update st_mtime for solve.cpp, but should not be used

    proc = __run_command('pcm tt solve_AC.py')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))
    assert(len(re.findall('^--AC.*', proc.stdout.decode('utf-8'), re.MULTILINE))==3)


def test_tt_python():
    os.chdir(script_path / f'data/test_tt/abc001/A/codes')
    proc = __run_command('pcm tt solve.py')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))
    assert(len(re.findall('^--AC.*', proc.stdout.decode('utf-8'), re.MULTILINE))==1)
    assert(len(re.findall('^--WA.*', proc.stdout.decode('utf-8'), re.MULTILINE))==2)


def test_tt_casegen():
    os.chdir(script_path / f'data/test_tt/abc001/A/codes')

    proc = __run_command('pcm tt solve_AC.py -c gen.py --by naive_AC.py')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))
    assert(len(re.findall('^--AC.*', proc.stdout.decode('utf-8'), re.MULTILINE))==1)
    assert(len(re.findall('^--WA.*', proc.stdout.decode('utf-8'), re.MULTILINE))==0)


def test_tt_casegen_ranged_loop():
    os.chdir(script_path / f'data/test_tt/abc001/A/codes')
    proc = __run_command('pcm tt solve_AC.py -c range_gen.py --by naive_AC.py --loop')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))
    assert(len(re.findall('^--AC.*', proc.stdout.decode('utf-8'), re.MULTILINE))==25)


def test_tt_TLE():
    os.chdir(script_path / f'data/test_tt/abc001/A/codes')
    proc = __run_command('pcm tt solve_TLE.py')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))
    assert(len(re.findall('^--TLE.*', proc.stdout.decode('utf-8'), re.MULTILINE))==3)


def test_tt_RE():
    os.chdir(script_path / f'data/test_tt/abc001/A/codes')
    proc = __run_command('pcm tt solve_RE.py')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))
    assert(len(re.findall('^--RE.*', proc.stdout.decode('utf-8'), re.MULTILINE))==3)


def test_tt_MLE():
    if os.name != "posix":
        # windowsではメモリ取得が出来ていないのでテストをskipする。
        return 0

    os.chdir(script_path / f'data/test_tt/abc001/A/codes')
    proc = __run_command('pcm tt solve_MLE.py -t 10')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))
    assert(len(re.findall('^--MLE.*', proc.stdout.decode('utf-8'), re.MULTILINE))==3)


def test_tr_AC():
    os.chdir(script_path / f'data/test_tr/F/codes')
    proc = __run_command('pcm tr AC.cpp -c 1 --by judge.py -cc simple')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))
    assert(len(re.findall('^--AC.*', proc.stdout.decode('utf-8'), re.MULTILINE))==1)


def test_tr_WA():
    os.chdir(script_path / f'data/test_tr/F/codes')
    proc = __run_command('pcm tr WA.cpp -c 1 --by judge.py -cc simple')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))
    assert(len(re.findall('^--WA.*', proc.stdout.decode('utf-8'), re.MULTILINE))==1)


def test_tr_RE():
    os.chdir(script_path / f'data/test_tr/F/codes')
    proc = __run_command('pcm tr RE.cpp -c 1 --by judge.py -cc simple')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))
    assert(len(re.findall('^--RE.*', proc.stdout.decode('utf-8'), re.MULTILINE))==1)


def test_tr_TLE():
    os.chdir(script_path / f'data/test_tr/F/codes')
    proc = __run_command('pcm tr TLE.cpp -c 1 --by judge.py -cc simple')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))
    assert(len(re.findall('^--TLE.*', proc.stdout.decode('utf-8'), re.MULTILINE))==1)


def test_tr_AC():
    os.chdir(script_path / f'data/test_tr/F/codes')
    proc = __run_command('pcm tr AC.cpp -c gen.py --by judge.py -cc simple')
    print('---------stdout-------------')
    print(proc.stdout.decode('utf-8'))
    print('---------stderr-------------')
    print(proc.stderr.decode('utf-8'))
    assert(len(re.findall('^--AC.*', proc.stdout.decode('utf-8'), re.MULTILINE))==1)


def test_sb_atcoder():
    os.chdir(script_path / f'data/test_sb/abc166_a/codes')
    os.utime('solve.py', None)  # update st_mtime for solve.py to be used
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

    print(A_files - B_files)
    print(B_files - A_files)
    if (A_files==B_files):
        return True
    else:
        return False


if __name__ == "__main__":
    # test_tt()
    pass
