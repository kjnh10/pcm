from pathlib import Path
import time
import subprocess
import sys
import pickle
import os
import contextlib
from typing import TYPE_CHECKING, List, Optional, Type, Generator, Tuple, Any
from .interactive_runner import SubprocessThread
import click
import onlinejudge._implementation.utils as oj_utils
from .utils import get_last_modified_file
from enum import IntEnum


class JudgeResult(IntEnum):
    AC = 0
    WA = 1
    RE = 2
    CE = 3
    TLE = -2
    MLE = 4
    QLE = 5  # Query limit exceeded
    AIE = 6  # Additional input error
    NOEXP = 98
    TLENAIVE = 99
    YET = 100


class RunResult(object):
    def __init__(self):
        self.returncode: int = None
        self.stdout: str = ""
        self.stderr: str = ""
        self.stderr_filepath: Path = None
        self.TLE_flag: bool = False
        self.exec_time: float = -1
        self.used_memory: float = -1
        self.judge: JudgeResult = JudgeResult.YET  # set by 'pcm tt'


class CodeFile(object):
    def __init__(self, match_filename_pattern=['*.cpp', '*.py'], exclude_filename_pattern=[], search_root: Path = Path('.')):
        if (match_filename_pattern == ''):
            match_filename_pattern = ['*.cpp', '*.py']
        self.path = get_last_modified_file(match_filename_pattern, exclude_filename_pattern, search_root)
        self.code_dir = self.path.parent

        if (self.code_dir/'test').exists():  # online-judge-tools style
            self.prob_dir = self.code_dir
            self.test_dir = self.code_dir / 'test'
            self.bin_dir = self.code_dir / '.bin'
        else:                                # default template style
            self.prob_dir = self.code_dir.parent
            self.test_dir = self.prob_dir / 'test'
            self.bin_dir = self.prob_dir / '.bin'

        self.task_alphabet = self.prob_dir.name
        self.extension = self.path.suffix[1:]  # like 'py', 'cpp'....
        self.oj_problem_class = None
        try:
            with open(self.prob_dir/'.problem_info.pickle', mode='rb') as f:
                self.oj_problem_class = pickle.load(f)
        except Exception as e:
            pass
            # print('failed to load problem_info.pickle')

    def compile(self, config, force=False) -> Path:
        click.secho('compile start.....', blink=True)
        cnfname = config.pref['test']['compile_command']['configname']
        exefile = self.bin_dir / f'{self.path.name}_{cnfname}.out'
        exefile.parent.mkdir(exist_ok=True)
        if (not force) and (exefile.exists() and self.path.stat().st_mtime <= exefile.stat().st_mtime):
            click.secho(f'compile skipped since {self.path} is older than {exefile.name}')
        else:
            start = time.time()
            command = config.pref['test']['compile_command'][self.extension][cnfname].format(
                srcpath=str(self.path),
                outpath=str(exefile),
                code_dir_path=str(self.path.parent),
                config_dir_path='~/.config/pcm',
                pcm_dir_path=os.path.dirname(__file__),
            ).split()
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

    def run(self, config, infile: Path = None, outfile: Path = None) -> RunResult:  
        if self.extension not in config.pref['test']['compile_command']:  # for script language
            return self._run_exe(config, self.path, infile, outfile)
        else:
            exefile = self.compile(config)
            return self._run_exe(config, exefile, infile, outfile)

    def _run_exe(self, config, exefile: Path, infile: Path = None, outfile: Path = None, args: List = []) -> RunResult: 
        # gen.pyもこれで実行される。
        res = RunResult()
        command = self._get_command_string_to_run(exefile, args=args)

        def popen():
            return subprocess.Popen(
                command,
                stdin=open(infile, "r") if infile else None,
                stdout=open(outfile, "w") if outfile else subprocess.PIPE,
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
            try:
                # get memory usage
                # 別プロセスで起動した方がとりやすそうなのでexec.pyでもう一度runし直している。
                executer = "exec.py" if os.name == "posix" else "exec_windows.py"
                proc_mem = subprocess.Popen(
                        ["python", f"{os.path.dirname(__file__)}/{executer}", str(exefile), str(infile)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                        )
                stdout_mem, stderr_mem = proc_mem.communicate()
                res.used_memory = float((stdout_mem.decode('utf-8').replace('\n', '')))
            except Exception as e:
                pass

        res.returncode = proc.returncode
        res.stdout = None if outfile else outs.decode('utf-8')
        res.stderr = errs.decode('utf-8')
        return res

    def run_interactive(self, config, judgefile, infile: Path):
        res = RunResult()
        res.stderr_filepath = self.code_dir / '.stderr.log'
        solution_exefile = self.to_exefile(config)
        judge_exefile = judgefile.to_exefile(config)
        sol_args = self._get_command_string_to_run(solution_exefile)
        judge_args = self._get_command_string_to_run(judge_exefile)

        with open(res.stderr_filepath, 'w') as stderr_file:
            t_judge = SubprocessThread(
                judge_args,
                stderr_pipe=stderr_file,
                )
            t_sol = SubprocessThread(
                sol_args,
                stdin_pipe=t_judge.p.stdout,
                stdout_pipe=t_judge.p.stdin,
                stderr_pipe=stderr_file,
                )
            t_case = SubprocessThread(
                ['cat', str(infile)],
                stdout_pipe=t_judge.p.stdin,
                stderr_pipe=stderr_file,
                )

            t_case.start()
            time.sleep(0.2)

            t_sol.start()
            t_judge.start()
            t_sol.join()
            t_judge.join()

            res.judge_thread = t_judge
            res.solution_thread = t_sol
            if t_sol.return_code == -2:
                res.judge = JudgeResult.TLE
            elif t_sol.return_code != 0:
                res.judge = JudgeResult.RE
            else:
                try:
                    res.judge = JudgeResult(t_judge.return_code)
                except Exception as e:
                    res.judge = t_judge.return_code

            return res

    def to_exefile(self, config):
        if self.extension not in config.pref['test']['compile_command']:  # for script language
            return self.path
        else:
            return self.compile(config)

    def _get_command_string_to_run(self, exefile: Path, args: List = []):
        command = []
        if (exefile.suffix == '.py'):
            command.append('python')
        command.append(str(exefile))
        for arg in args:
            command.append(arg)
        return command

    def submit(self, config, language):
        contest_site = self.oj_problem_class.get_service().get_name()

        if language == 'auto-detect':
            try:
                lang_id = config.pref['submit']['default_lang'][contest_site][self.extension]
            except KeyError as e:
                click.secho(f'{self.extension} not found in possible self.extensions. if you want to add {self.extension}, you can add it in ~/.config/pcm/config.toml', fg='red')
                print('current possible self.extensions')
                print(config.pref['submit']['default_lang'][contest_site])
                return
            try:
                service = self.oj_problem_class.get_service().get_name()
                lang_id = config.pref['submit']['language'][service][lang_id]
            except:
                pass
        else:
            try:
                lang_id = config.pref['submit']['language'][contest_site][language]
            except KeyError as e:
                click.secho(f'{language} not found in possible language. if you want to add {language}, you can add it in ~/.config/pcm/config.toml', fg='red')
                print('current possible language')
                print(config.pref['submit']['language'][contest_site])
                return

        code_string = self.bundle(include_acl = (False if (contest_site == 'AtCoder' and lang_id in ['4003', '4004']) else True))
        with oj_utils.with_cookiejar(oj_utils.get_default_session()) as session:
            try:
                res = self.oj_problem_class.submit_code(code_string, language_id=lang_id, session=session)
            except AssertionError as e:
                click.secho('maybe language_id is not valid.', fg='yellow')
                print(e)
                exit()
            else:
                print(res)

    def bundle(self, include_acl = True):
        if self.extension == "cpp":
            tmp_expanded_code_file = f'{self.path.parent}/.last_submit_code'
            oj_bundle_commands = []
            if include_acl:
                print('expanding ac-library because the language you are specifying does not have acl env')
                acl_dir_path = f'{os.path.dirname(__file__)}//lang_library/cplusplus/ac-library'
                proc = subprocess.Popen(' '.join(['python', f'{acl_dir_path}/expander.py', str(self.path), '--lib', acl_dir_path]), shell=True, stderr=subprocess.PIPE)
                outs, errs = proc.communicate()
                if proc.returncode:
                    click.secho("expander.py error")
                    print(errs)
                    exit()
                oj_bundle_commands = ['oj-bundle', str(self.path.parent / 'combined.cpp'), '>', tmp_expanded_code_file]
            else:
                oj_bundle_commands = ['oj-bundle', str(self.path), '>', tmp_expanded_code_file]

            proc = subprocess.Popen(' '.join(oj_bundle_commands), shell=True, stderr=subprocess.PIPE)
            outs, errs = proc.communicate()
            if proc.returncode:
                click.secho("oj-bundle error")
                print(errs)
                exit()
            with open(tmp_expanded_code_file, "r") as f:
                return f.read()
        else:
            with open(self.path, "r") as f:
                return f.read()

    def __str__(self):
        return str(self.path)
