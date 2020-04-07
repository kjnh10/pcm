from pathlib import Path
import time
import subprocess
import sys
import pickle
import os
from typing import TYPE_CHECKING, List, Optional, Type
import click
import onlinejudge._implementation.utils as oj_utils
from .utils import get_last_modified_file

class RunResult(object):
    def __init__(self):
        self.returncode = None
        self.stdout = ""
        self.stderr = ""
        self.TLE_flag = None
        self.exec_time = -1
        self.used_memory = -1
        self.judge = "yet"  # set by 'pcm tt'


class CodeFile(object):
    def __init__(self, match_filename_pattern=['*.cpp', '*.py'], exclude_filename_pattern=[], search_root: Path = Path('.')):
        if (match_filename_pattern==''):
            match_filename_pattern = ['*.cpp', '*.py']
        self.path = get_last_modified_file(match_filename_pattern, exclude_filename_pattern, search_root)
        self.code_dir = self.path.parent

        if (self.code_dir/'test').exists():  # online-judge-tools style
            self.prob_dir = self.code_dir
            self.test_dir = self.code_dir / 'test'
            self.bin_dir = self.code_dir / 'bin'
        else:                                # default template style
            self.prob_dir = self.code_dir.parent
            self.test_dir = self.prob_dir / 'test'
            self.bin_dir = self.prob_dir / 'bin'

        self.task_alphabet = self.prob_dir.name
        self.extension = self.path.suffix[1:]  # like 'py', 'cpp'....
        self.oj_problem_class = None
        try:
            with open(self.prob_dir/'.problem_info.pickle', mode='rb') as f:
                self.oj_problem_class = pickle.load(f)
        except Exception as e:
            print('failed to load problem_info.pickle')

    def compile(self, config, force=False) -> Path:
        click.secho('compile start.....', blink=True)
        cnfname = config.pref['test']['compile_command']['configname']
        exefile = self.bin_dir / f'{self.path.name}_{cnfname}.out'
        exefile.parent.mkdir(exist_ok=True)
        if (not force) and (exefile.exists() and self.path.stat().st_mtime <= exefile.stat().st_mtime):
            click.secho(f'compile skipped since {self.path} is older than {exefile.name}')
        else:
            start = time.time()
            command = config.pref['test']['compile_command'][self.extension][cnfname].format(srcpath=str(self.path), outpath=str(exefile)).split()
            proc = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    )
            outs, errs = proc.communicate()
            if proc.returncode:
                click.secho("compile error\n", fg='red')
                sys.exit()

            if outs:
                print(outs.decode('utf-8'))

            click.secho('compile finised')
            print("compile took:{0}".format(time.time() - start) + "[sec]")
        return exefile

    def run(self, config, infile: Path = None) -> RunResult:  
        if self.extension not in config.pref['test']['compile_command']:  # for script language
            return self._run_exe(config, self.path, infile)
        else:
            exefile = self.compile(config)
            return self._run_exe(config, exefile, infile)

    def _run_exe(self, config, exefile: Path, infile: Path = None) -> RunResult: 
        res = RunResult()
        command = []
        if (exefile.suffix=='.py'):
            command.append('python')
        command.append(str(exefile))
        command.append('pcm') # tell the sctipt that pcm is calling

        def popen():
            with open(infile, 'r'):
                pass
            return subprocess.Popen(
                command,
                stdin=open(infile, "r") if infile else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                # shell=True,  # for windows
            )
        proc = popen()

        try:
            start = time.time()
            outs, errs = proc.communicate(timeout=config.pref['test']['timeout_sec'])
            res.exec_time = time.time() - start
            res.TLE_flag = False
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
            res.exe_time = float('inf')
            res.TLE_flag = True
        else:
            # os.wait4()を使うとTLE時のout,errsが取得できなくなるため、TLEでないと判明した場合にのみMemoryの使用量を取得する。
            try:
                proc_for_check_memory = popen()
                ru = os.wait4(proc_for_check_memory.pid, 0)[2]  # windowsの場合はerrorになりそう。
                res.used_memory = ru.ru_maxrss / (1<<10) # MB unit
            except Exception as e:
                pass
        res.returncode = proc.returncode
        res.stdout = outs.decode('utf-8')
        res.stderr = errs.decode('utf-8')
        return res 

    def submit(self, config, language):
        with open(self.path, "r") as f:
            code_string = f.read()

        contest_site = self.oj_problem_class.get_service().get_name()

        if language == 'auto-detect':
            try:
                lang_id = config.pref['submit']['default_lang'][contest_site][self.extension]
            except KeyError as e:
                click.secho(f'{self.extension} not found in possible self.extensions. if you want to add {self.extension}, you can add it in ~/.config/pcm/config.toml', fg='red')
                print('current possible self.extensions')
                print(config.pref['submit']['default_lang'][contest_site])
                return
        else:
            try:
                lang_id = config.pref['submit']['language'][contest_site][language]
            except KeyError as e:
                click.secho(f'{language} not found in possible language. if you want to add {language}, you can add it in ~/.config/pcm/config.toml', fg='red')
                print('current possible language')
                print(config.pref['submit']['language'][contest_site])
                return

        with oj_utils.with_cookiejar(oj_utils.get_default_session()) as session:
            res = self.oj_problem_class.submit_code(code_string, language_id=lang_id, session=session)
            print(res)


