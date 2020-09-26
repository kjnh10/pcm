import click  # {{{
import os, sys
import shutil
from pathlib import Path
import requests
import fnmatch
import pickle
import subprocess
import signal
import textwrap
import toml
import time
import urllib
import re
import tempfile
import hashlib
from colorama import init, Fore, Back, Style
from typing import TYPE_CHECKING, List, Optional, Type

# pylint: disable=unused-import,ungrouped-imports
try:
    import onlinejudge._implementation.utils as oj_utils
    import onlinejudge.service.atcoder
    import onlinejudge.dispatch
except ModuleNotFoundError:
    import json
    print(json.dumps({
        "status": "error",
        "messages": ["Due to a known bug, the online-judge-tools is not yet properly installed. Please re-run $ pip3 install --force-reinstall online-judge-api-client"],
        "result": None,
    }))
    raise SystemExit(1)
# pylint: enable=unused-import,ungrouped-importsrom bs4 import BeautifulSoup

script_path = Path(os.path.abspath(os.path.dirname(__file__)))  # script path}}}
from .codefile import CodeFile, RunResult, JudgeResult
from .case_generator import CaseGenerator, CaseGenerateError

# set click
class Config(object):# {{{
    def __init__(self):
        self.verbose = False

pass_config = click.make_pass_decorator(Config, ensure=True)
@click.group()
@click.option('--verbose', is_flag=True)
@click.option('--home-directory', type=click.Path())
@pass_config
def cli(config, verbose, home_directory):
    # read config from setting file 
    default_config_path = Path(os.path.dirname(__file__)) / 'config.toml'
    tmp_config = toml.load(open(default_config_path))

    user_config_path = Path.home() / '.config/pcm/config.toml'
    if os.path.exists(user_config_path):
        user_config = toml.load(open(user_config_path))
        def merge(current, new):
            for key, value in new.items():
                if (type(value)==dict):
                    merge(current[key], new[key])
                else:
                    current[key] = value
        merge(tmp_config, user_config)
    else:
        pass
    config.pref = tmp_config

    if os.path.exists(Path(config.pref['template_dir']).expanduser()):
        config.pref['template_dir'] = Path(config.pref['template_dir']).expanduser()
    else:
        config.pref['template_dir'] = Path(script_path / 'default_template')

    # read from command line
    config.verbose = verbose
    if home_directory is None:
        home_directory = '.'
    config.home_directory = home_directory
# }}}

# sub command
# init{{{
@cli.command()
@pass_config
def init(config):
    """This command will make current dir pcm work-space"""
    os.makedirs('./.pcm')# }}}

# prepare problem: login {{{
@cli.command()
@click.argument('url', type=str)
@pass_config
def login(config, url):
    subprocess.run(f'oj login {url}', shell=True)
# }}}

# prepare contest: pp {{{
@cli.command()
@click.argument('contest_id_or_url', type=str, default='abc001')
@click.option('-c/-nc', '--current_dir/--no-current_dir', type=bool, default=False)
@click.option('-n', '--work_dir_name', type=str, default='')
@click.option('--force/--no-force', "-f/-nf", default=False)
@pass_config
def pp(config, contest_id_or_url, current_dir, work_dir_name, force):
    contest_url = ""
    if contest_id_or_url[:3] in ("abc", "arc", "agc"):
        contest_url = f"https://atcoder.jp/contests/{contest_id_or_url}"
    else:
        contest_url = contest_id_or_url

    contest = onlinejudge.dispatch.contest_from_url(contest_url)
    if not contest:
        click.secho(f"{contest_id_or_url} is not valid.", fg='yellow')
        return 0

    problems = []
    with oj_utils.with_cookiejar(oj_utils.get_default_session()) as session:
        problems = contest.list_problems(session=session)

    if current_dir:
        config.pref['contest_root_dir'] = '.'
    work_dir = get_work_directory(problems[0], from_pp=True).parent
    if work_dir_name:
        work_dir.name = work_dir_name

    already_exist = False
    try:
        os.makedirs(work_dir)
    except OSError:
        if force:
            shutil.rmtree(work_dir)
            os.makedirs(work_dir)
        else:
            click.secho('The specified direcotry already exists.', fg='red')
            already_exist = True

    if not already_exist:
        for problem in problems:
            _prepare_problem(problem.get_url(), from_pp=True)

    try:
        cstr = config.pref['prepare']['custom_hook_command']['after'].format(dirname=work_dir.resolve())
        print(cstr)
        subprocess.run(cstr, shell=True)
    except Exception as e:
        if config.verbose:
            print(e)
# }}}

# prepare problem: ppp {{{
@cli.command()
@click.argument('task_url', type=str, default='')
@click.option('-c/-nc', '--current_dir/--no-current_dir', type=bool, default=False)
@click.option('-n', '--prob_name', type=str, default='')
@click.option('--force/--no-force', "-f/-nf", default=False)
@click.option('--execute_hook/--no-execute_hook', default=True)
@pass_config
def ppp(config, task_url, current_dir, prob_name, force, execute_hook):
    if current_dir:
        config.pref['problem_root_dir'] = '.'
    work_dir = _prepare_problem(task_url, prob_name, force)

    # execute custom_hook_command
    if not execute_hook: return 0
    try:
        cstr = config.pref['ppp']['custom_hook_command']['after'].format(dirname=work_dir.resolve())
        print(cstr)
        subprocess.run(cstr, shell=True)
    except Exception as e:
        if config.verbose:
            print(e)


@pass_config
def _prepare_problem(config, task_url, prob_name='', force=False, from_pp=False):
    problem_dir = None
    problem_title = None
    if task_url != '':
        problem = onlinejudge.dispatch.problem_from_url(task_url)
        problem_dir = get_work_directory(problem, from_pp=from_pp)
        try:
            problem_data = problem.download_data()
            problem_title = problem_data.name
        except:
            pass
    else:
        problem_dir = Path('./prob').resolve()

    if prob_name:
        problem_dir = problem_dir.parent / prob_name

    if Path(problem_dir).exists():
        if force:
            shutil.rmtree(problem_dir)
        else:
            print(f'{problem_dir} directory already exists')
            return problem_dir

    problem_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(config.pref['template_dir'], f'{problem_dir}/')
    # download sample cases
    if task_url:
        _download_sample(task_url, problem_dir)
        if problem_title:
            with open(problem_dir / problem_title,"w"):pass
    return problem_dir
# }}}

@pass_config
def get_work_directory(config, problem: onlinejudge.type.Problem, from_pp) -> Path:# {{{
    # prepare params
    service = problem.get_service()

    for name in ('contest_id', 'contest_slug'):
        contest_id = getattr(problem, name, None)
        if contest_id:
            break
    else:
        contest_id = ''

    for name in ('problem_id', 'problem_slug', 'problem_no', 'task_id', 'task_slug', 'task_no', 'alphabet', 'index'):
        problem_id = getattr(problem, name, None)
        if problem_id:
            break
    else:
        problem_id, = urllib.parse.urlparse(problem.get_url()).path.lstrip('/').replace('/', '-'),

    params = {
        'service_name': service.get_name(),
        'service_domain': urllib.parse.urlparse(service.get_url()).netloc,
        'contest_id': contest_id,
        'problem_id': problem_id,
    }

    # generate the path
    problem_directory = Path(config.pref['problem_root_dir'].format(**params)).expanduser() / str(problem_id)
    if not from_pp:
        return problem_directory.resolve()
    else:
        contest_directory = Path(config.pref['contest_root_dir'].format(**params)).expanduser() / str(contest_id) / str(problem_id)
        return contest_directory.resolve()# }}}

# start server for competitive companion: ss {{{
@cli.command()
@pass_config
def ss(config):
    subprocess.run(f"node {script_path / 'cc_server/index.js'}", shell=True)
# }}}

# prepare problem: dl {{{
@cli.command()
@click.argument('task_url', type=str)
@pass_config
def dl(config, task_url):
    try:
        solve_codefile = CodeFile("")
    except FileNotFoundError as e:
        print("you are not in pcm-problem directory")
        exit()
    _download_sample(task_url, solve_codefile.prob_dir)


def _download_sample(task_url, problem_dir):
    to_restore = Path('.').resolve()

    os.chdir(problem_dir) # prob_dirにいることが仮定されている
    subprocess.run(f"rm test/sample*", shell=True)
    problem = onlinejudge.dispatch.problem_from_url(task_url)
    if not problem:
        click.secho(f"{task_url} is not valid.", fg='yellow')
        sys.exit()

    if 'hackerrank' not in task_url:
        # problem.download_sample_cases()
        subprocess.run(['oj', 'download', task_url])
    else:
        subprocess.run(['oj', 'download', task_url, '--system'])

    problem = onlinejudge.dispatch.problem_from_url(task_url)
    with open('./.problem_info.pickle', mode='wb') as f:
        # problem directory直下にdumpしておく。
        pickle.dump(problem, f)
    os.chdir(to_restore)

# }}}

# compile: compile {{{
@cli.command()
@click.argument('code_filename', type=str, default='')
@click.option('--compile_command_configname', '-cc', type=str, default='')
@pass_config
def compile(config, code_filename, compile_command_configname):
    if compile_command_configname:
        config.pref['test']['compile_command']['configname'] = compile_command_configname
    CodeFile(code_filename).compile(config)
#}}}

# compile: bundle {{{
@cli.command()
@click.argument('code_filename', type=str, default='')
@click.option('--include_acl', '-acl/-nacl', type=bool, default=False)
@click.option('--clipboard', '-c/-nc', type=bool, default=True)
@pass_config
def bd(config, code_filename, include_acl, clipboard):
    if include_acl:
        acl_dir_path = f'{os.path.dirname(__file__)}//lang_library/cplusplus/ac-library'
        subprocess.run(' '.join(['python', f'{acl_dir_path}/expander.py', str(CodeFile(code_filename).path), '--lib', acl_dir_path]), shell=True)
        command = ['oj-bundle', str(CodeFile(code_filename).path.parent / 'combined.cpp')]
    else:
        command = ['oj-bundle', str(CodeFile(code_filename).path)]

    if clipboard:
        command += ['|', 'xsel', '--clipboard', '--input']
    subprocess.run(' '.join(command), shell=True)
#}}}

# compile: precompile {{{
@cli.command()
@click.option('--extension', '-e', type=str, default='cpp')
@click.option('--compile_command_configname', '-cc', type=str, default='')
@click.option('--force/--no-force', "-f/-nf", default=False)
@pass_config
def precompile(config, extension, compile_command_configname, force):
    if compile_command_configname:  # precompile for default profile
        _precompile(config.pref['test']['compile_command']['configname'], extension, force)
    else:
        for confname in config.pref['test']['compile_command'][extension].keys():
            _precompile(confname, extension, force)

@pass_config
def _precompile(config, cnfname, extension, force):
    click.secho(f'precompile started for {cnfname} for {extension}......', fg='yellow')
    print('-----------------------------------------------------------------')

    try:
        command_str = config.pref['test']['compile_command'][extension][cnfname].format(
            srcpath= "____",
            outpath= "____", 
            config_dir_path='~/.config/pcm',
            pcm_dir_path=os.path.dirname(__file__),
        )
        command = command_str.split()
        command_hash = hashlib.md5(command_str.encode()).hexdigest()
        include_idx = command.index('-include')
        header_filepath = Path(command[include_idx+1]).expanduser();
        outpath = Path(str(header_filepath) + f'.gch/{cnfname}.ver-{command_hash}')
        if outpath.exists() and (not force):
            click.secho(f'precompile:[{cnfname}] skipped since the string of [{cnfname}] has not changed.\n', fg='green')
            return 0

        make_precompiled_header_command = config.pref['test']['compile_command'][extension][cnfname].format(
            srcpath=str(header_filepath),
            outpath=str(outpath),
            config_dir_path='~/.config/pcm',
            pcm_dir_path=os.path.dirname(__file__),
        ).split()
        del make_precompiled_header_command[include_idx:include_idx+2]
        outpath.parent.mkdir(parents=True, exist_ok=True)
        for p in outpath.parent.glob(f'{cnfname}.ver-*'):
            p.unlink()

        print(make_precompiled_header_command) # sudo -x c++-headerは不要そう
        proc = subprocess.run(make_precompiled_header_command)
    except Exception as e:
        click.secho(f'precompile:[{cnfname}] failed.', fg='red')
        print(e)
    else:
        click.secho(f'precompile:[{cnfname}] successed. {header_filepath}.gch/{cnfname} has been created', fg='green')

    print('')
    return 0
#}}}

# test: tt {{{
@cli.command()
@click.argument('code_filename', type=str, default='')
@click.option('--compile_command_configname', '-cc', type=str, default='')
@click.option('--case', '-c', type=str, default='')
@click.option('--timeout', '-t', type=float, default=-1)
@click.option('--by', '-b', type=str, default=None)
@click.option('--loop/--noloop', '-l/-nl', default=False)
@click.option('--limit_height_max_output', '-lh', type=int, default=0)
@click.option('--limit_width_max_output', '-lw', type=int, default=0)
@pass_config
def tt(  # {{{
        config,
        code_filename: str,
        compile_command_configname:
        str,
        case: str,
        timeout: float,
        by: str,
        loop: bool,
        limit_height_max_output: int,
        limit_width_max_output: int,
        ):
    if (timeout != -1):
        config.pref['test']['timeout_sec'] = timeout
    if compile_command_configname:
        config.pref['test']['compile_command']['configname'] = compile_command_configname
    if limit_height_max_output:
        config.pref['test']['limit_height_max_output'] = limit_height_max_output
    if limit_width_max_output:
        config.pref['test']['limit_width_max_output'] = limit_width_max_output

    if Path(case).suffix not in ['.py', '.cpp']:
        solve_codefile = CodeFile(code_filename)
        test_dir = solve_codefile.test_dir
        if case == '':  # test all case
            _test_all_case(solve_codefile)
        else:
            if case == 'dry':  # execute code when there is no test case file
                tmpfileobject = tempfile.NamedTemporaryFile()
                infile = Path(tmpfileobject.name)
                expfile = Path(tmpfileobject.name)
            elif case in set(map(str, range(1, 101))):
                case = f'sample-{case}'
                infile = test_dir / f"{case}.in"
                expfile = test_dir / f"{case}.out"
                if (not infile.exists()):
                    click.secho(f"{infile.name} not found.", fg='yellow')
                    return 1
            else:
                infile = test_dir / f"{case}.in"
                expfile = test_dir / f"{case}.out"
                if not infile.exists():
                    click.secho(f"{infile.name} not found.", fg='yellow')
                    return 1

            _test_case(solve_codefile, case, infile, expfile)
    else:
        # random test
        solve_codefile = CodeFile(code_filename, exclude_filename_pattern=([case, by] if by else [case]))
        test_dir = solve_codefile.test_dir
        if by:
            if (by in ['judge.cpp', 'judge.py']):
                click.secho('maybe you should use [tr] command for reactive test', fg='yellow')
                exit()
            try:
                naive_codefile = CodeFile(match_filename_pattern=by)
            except FileNotFoundError:
                click.secho(f'naive code file not found by {by}', fg='yellow')
                return 1

        case_generator = CaseGenerator(CodeFile(case, search_root=solve_codefile.prob_dir), config)
        finished_count = 0
        while True:
            try:
                case_generator.generate_case(target=test_dir/'r.in')
            except StopIteration:
                click.secho(f'all {finished_count} cases specified by {case_generator.codefile.path.name} finished.', fg='green')
                break
            except CaseGenerateError as e:
                click.secho(f"case generating faild. check your {case_generator.codefile.path.name}", fg='red')
                exit()

            infile = test_dir / "r.in"
            expfile = test_dir / "r.out"
            if expfile.exists(): expfile.unlink()

            if by:
                run_result = naive_codefile.run(config, infile)
                with open(expfile, mode='w') as f:
                    if run_result.TLE_flag:
                        f.write('TLE for naive code. if you extend timeout time, use -t option like -t 5\n')
                    elif run_result.returncode != 0:
                        f.write('Some error happens when executing your naive code.\n')
                    else:
                        f.write(run_result.stdout)

            run_result = _test_case(solve_codefile, f'random-{code_filename}', infile, expfile)
            okresult = [JudgeResult.AC, JudgeResult.TLENAIVE, JudgeResult.NOEXP]
            if not (run_result.judge in okresult):
                if by or loop:  # compareもloopも行わない場合は単に生成して試したいだけの場合が多いので保存しない。
                    num_to_save = 1
                    L = [f.stem for f in test_dir.glob('r*.in')]
                    L.sort()
                    if (L):
                        last_num = L[-1].replace('r', '').replace('.in', '')
                        num_to_save = (0 if last_num == "" else int(last_num)) + 1

                    shutil.copyfile(infile, test_dir/f'r{num_to_save}.in')
                    print(f'input of this case saved to r{num_to_save}.in')
                    if (expfile.exists()):
                        shutil.copyfile(expfile, test_dir/f'r{num_to_save}.out')
                        print(f'expected of this case saved to r{num_to_save}.out')
                return 1

            finished_count += 1
            if (not loop): return 0
# }}}

def _test_all_case(codefile: CodeFile) -> bool: # {{{
    files = os.listdir(codefile.test_dir)
    files.sort()
    res = True
    case_cnt = 0
    ac_cnt = 0
    noexp_cnt = 0
    exec_times = []
    used_memories = []
    for filename in files:
        if not fnmatch.fnmatch(filename, '*.in'):
            continue
        case = filename[:-3]
        infile = codefile.test_dir / f"{case}.in"
        expfile = codefile.test_dir / f"{case}.out"  # 拡張子をexpにしたいが。。

        with open(infile, mode='r') as f:
            if (f.readline()==''):  # infileが空の場合は無視。個別のテストケースでは実行したい場合もあるのでこちらにのみチェックをいれる。
                continue

        case_cnt += 1
        run_result = _test_case(codefile, case, infile, expfile)
        exec_times.append(run_result.exec_time)
        used_memories.append(run_result.used_memory)
        if run_result.judge == JudgeResult.AC:
            ac_cnt += 1
        elif run_result.judge == JudgeResult.NOEXP:
            noexp_cnt += 1
        else:
            res = False
    if (ac_cnt == case_cnt):
        click.secho(f'{ac_cnt}/{case_cnt} cases passed', fg='green')
    elif (ac_cnt + noexp_cnt == case_cnt):
        click.secho(f'{ac_cnt}/{case_cnt} cases passed', fg='yellow')
        click.secho(f'{noexp_cnt}/{case_cnt} cases have no expected answer', fg='yellow')
    else:
        click.secho(f'{ac_cnt}/{case_cnt} cases passed', fg='red')

    print('[max exec time]: {:.3f}'.format(max(exec_times)), '[sec]')
    print('[max used memory]: {:.3f}'.format(max(used_memories)), '[MB]')
    return res
# }}}

@pass_config
def _test_case(config, codefile: CodeFile, case_name: str, infile: Path, expfile: Path) -> RunResult: # {{{
    # run program
    click.secho('-'*10 + case_name + '-'*10, fg='blue')
    run_result = codefile.run(config, infile)
    print(f"exec time: {run_result.exec_time} [sec]")
    print(f"memory usage: {run_result.used_memory} [MB]")

    def smart_print(strs, func=print, limit_of_lines=config.pref['test']['limit_height_max_output'], limit_of_width=config.pref['test']['limit_width_max_output']):
        n = len(strs)
        x = limit_of_lines
        y = limit_of_width
        def print_line(line):
            if len(line) <= 2*y:
                func(line)
            else:
                func(line[:y] + ' ~~~ ' + line[len(line)-y:len(line)])

        if n <= 2*x:
            for line in lines:
                print_line(line)
        else:
            for i in range(0, x):
                print_line(lines[i])
            print_line("~~~")
            print_line("~~~")
            for i in range(n-x, n):
                print_line(lines[i])

    # print input
    with open(infile, 'r') as f:
        print('*'*7 + ' input ' + '*'*7)
        lines  = f.read().split('\n')
        smart_print(lines, limit_of_lines=10)

    # print expected
    expfile_exist = True
    try:
        with open(expfile, 'r') as f:
            print('*'*7 + ' expected ' + '*'*7)
            exp_str = f.read()
            lines  = exp_str.split('\n')
            smart_print(lines)
            exp = exp_str.split('\n')
    except FileNotFoundError:
        print('*'*7 + ' expected ' + '*'*7)
        click.secho(f"expected file:[{expfile.name}] not found\n", fg='yellow')
        exp = ['']
        expfile_exist = False

    # print result
    print('*'*7 + ' stdout ' + '*'*7)
    lines  = run_result.stdout.split('\n')
    smart_print(lines)
    stdout = run_result.stdout.split('\n')

    # print stderr message
    print('*'*7 + ' stderr ' + '*'*7)
    lines = run_result.stderr.split('\n')
    def print_stderr(line):
        line = line.replace(str(codefile.code_dir), "")
        click.secho(line, fg='yellow')
    smart_print(lines, func=print_stderr)

    for line in run_result.stderr.split('\n'):
        if re.search('runtime error', line):
            click.secho('--RE--\n', fg='red')
            run_result.judge = JudgeResult.RE
            return run_result

    # compare result and expected
    if run_result.TLE_flag:
        click.secho('--TLE--\n', fg='red')
        run_result.judge = JudgeResult.TLE
        return run_result

    if run_result.returncode != 0:
        SIGMAP = dict(
            (int(k), v) for v, k in reversed(sorted(signal.__dict__.items()))
            if v.startswith('SIG') and not v.startswith('SIG_')
        )
        click.secho(f'--RE--', fg='red')
        click.secho(f':{SIGMAP[abs(run_result.returncode)]}' if abs(run_result.returncode) in SIGMAP.keys() else str(abs(run_result.returncode)), fg='red')
        print('\n')
        run_result.judge = JudgeResult.RE
        return run_result

    if run_result.used_memory > config.pref['test']['max_memory']:
        click.secho('--MLE--\n', fg='red')
        run_result.judge = JudgeResult.MLE
        return run_result

    # 最後の空白行は無視する。
    while stdout and stdout[-1] == '': stdout.pop()
    while exp and exp[-1] == '': exp.pop()

    if not expfile_exist:
        click.secho('--NOEXP--\n', fg='yellow')
        run_result.judge = JudgeResult.NOEXP
    elif len(exp) == 0:
        click.secho('--WA--\n', fg='red')
        run_result.judge = 'WA'
    elif re.search('TLE.*naive.*', exp[0]):
        click.secho('TLENAIVE\n', fg='yellow')
        run_result.judge = JudgeResult.TLENAIVE
    elif len(stdout) != len(exp):
        click.secho('--WA--\n', fg='red')
        run_result.judge = JudgeResult.WA
    else:
        for i in range(len(stdout)):
            if stdout[i].replace('\r', '').rstrip() != exp[i].rstrip():
                click.secho('--WA--\n\n', fg='red')
                run_result.judge = JudgeResult.WA
                break
        else:
            click.secho('--AC--\n', fg='green')
            run_result.judge = JudgeResult.AC
    return run_result
# }}}

# }}}

# test-reactive: tr {{{
@cli.command()
@click.argument('code_filename', type=str, default='')
@click.option('--compile_command_configname', '-cc', type=str, default='')
@click.option('--case', '-c', type=str, default='')
@click.option('--timeout', '-t', type=float, default=-1)
@click.option('--by', '-b', type=str, default='judge.py')
@click.option('--loop/--noloop', '-l/-nl', default=False)
@pass_config
def tr(config, code_filename: str, compile_command_configname: str, case: str, timeout: float, by: str, loop: bool):  # {{{
    if (timeout != -1):
        config.pref['test']['timeout_sec'] = timeout
    if compile_command_configname:
        config.pref['test']['compile_command']['configname'] = compile_command_configname

    try:
        solve_codefile = CodeFile(code_filename, exclude_filename_pattern = [by if by else None])
    except FileNotFoundError:
        click.secho(f'solve code file not found by {code_filename}', fg='yellow')
        return 1

    try:
        judge_codefile = CodeFile(by, search_root=solve_codefile.prob_dir)
    except FileNotFoundError:
        click.secho(f'judge code file not found by {by}', fg='yellow')
        return 1

    test_dir = solve_codefile.test_dir

    if Path(case).suffix not in ['.py', '.cpp']:
        if case == '':  # test all case
            click.secho('test for all case is not impremented for reactive test just for simplicity', fg='yellow')
            return 0
        else:
            if case in set(map(str, range(1, 101))):
                case = f'sample-{case}'
                infile = test_dir / f"{case}.in"
                if (not infile.exists()):
                    click.secho(f"{infile.name} not found.", fg='yellow')
                    return 1
            else:
                infile = test_dir / f"{case}.in"
                if not infile.exists():
                    click.secho(f"{infile.name} not found.", fg='yellow')
                    return 1

            _test_interactive_case(solve_codefile, judge_codefile, infile, case)
    else:
        # random test
        case_generator = CaseGenerator(CodeFile(case, search_root=solve_codefile.prob_dir), config)
        finished_count = 0
        while True:
            try:
                case_generator.generate_case(target=test_dir/'r.in')
            except StopIteration:
                click.secho(f'all {finished_count} cases specified by {case_generator.codefile.path.name} finished.', fg='green')
                break
            except CaseGenerateError:
                click.secho(f"case generating faild. check your {case_generator.codefile.path.name}", fg='red')
                exit()

            infile = test_dir / f"r.in"
            run_result = _test_interactive_case(solve_codefile, judge_codefile, infile, f'random-{code_filename}')
            if run_result.judge != JudgeResult.AC:
                if loop:  # loopを行わない場合は単に生成して試したいだけの場合が多いので保存しない。
                    num_to_save = 1
                    L = [f.stem for f in test_dir.glob('r*.in')]
                    L.sort()
                    if (L):
                        last_num = L[-1].replace('r', '').replace('.in', '')
                        num_to_save = (0 if last_num == "" else int(last_num)) + 1

                    shutil.copyfile(infile, test_dir/f'r{num_to_save}.in')
                    print(f'input of this case saved to r{num_to_save}.in')
                return 1

            finished_count += 1
            if (not loop): return 0

    return 0
# }}}

@pass_config
def _test_interactive_case(config, codefile: CodeFile, judgefile: CodeFile, infile: Path, case_name: str) -> RunResult: # {{{
    # run program
    click.secho('-'*10 + case_name + '-'*10, fg='blue')
    run_result = codefile.run_interactive(config, judgefile, infile)

    # print input
    with open(infile, 'r') as f:
        print('*'*7 + ' input ' + '*'*7)
        print(f.read())

    with open(run_result.stderr_filepath, 'r') as f:
        print('*'*7 + ' stderr ' + '*'*7)
        for line in f.read().split('\n'):
            if re.search(r'.*\[.*judge.*\].*', line):
                click.secho(line, fg='yellow')
            else:
                click.secho(line, fg='cyan')

    if (run_result.judge == JudgeResult.AC):
        click.secho('--AC--\n', fg='green')
    else:
        click.secho(f'--{run_result.judge.__str__().replace("JudgeResult.", "")}--\n', fg='red')

    print({f"judge_thread.return_code: {run_result.judge_thread.return_code}"})
    print({f"solution_thread.return_code: {run_result.solution_thread.return_code}"})
    print({f"judge_thread.error_message: {run_result.judge_thread.error_message}"})
    print({f"solution_thread.error_message: {run_result.solution_thread.error_message}"})
    return run_result
# }}}

# }}}

# debug: db {{{
@cli.command()
@click.argument('code_filename', type=str, default='')
@click.option('--compile_command_configname', '-cc', type=str, default='debug')
@click.option('--case', '-c', type=str, default='')
@click.option('--timeout', '-t', type=float, default=-1)
@pass_config
def db(config, code_filename: str, compile_command_configname: str, case: str, timeout: float):  
    if (timeout != -1):
        config.pref['test']['timeout_sec'] = timeout
    config.pref['test']['compile_command']['configname'] = compile_command_configname

    solve_codefile = CodeFile(code_filename)
    if solve_codefile.extension != 'cpp':
        click.secho('db command is only for c++.')
        exit()
    exefile = solve_codefile.compile(config)

    test_dir = solve_codefile.test_dir
    if case == '':  # test all case
        click.secho('need to specify --case <casename>', fg='yellow')
        exit()

    if case == 'dry':  # execute code when there is no test case file
        tmpfileobject = tempfile.NamedTemporaryFile()
        infile = Path(tmpfileobject.name)
        expfile = Path(tmpfileobject.name)
    elif case in set(map(str, range(1, 101))):
        case = f'sample-{case}'
        infile = test_dir / f"{case}.in"
        expfile = test_dir / f"{case}.out"
        if (not infile.exists()):
            click.secho(f"{infile.name} not found.", fg='yellow')
            return 1
    else:
        infile = test_dir / f"{case}.in"
        expfile = test_dir / f"{case}.out"
        if not infile.exists():
            click.secho(f"{infile.name} not found.", fg='yellow')
            return 1

    tmp_run_script_path = Path(f'{script_path}/tmp/run_gdb.py')
    tmp_run_script_path.parent.mkdir(exist_ok=True)
    with open(tmp_run_script_path, mode='w') as f:
        contents = f"""
        import gdb
        import re
        gdb.execute('file {exefile.absolute()}')
        o = gdb.execute('run < {infile.absolute()}', to_string=True)
        print(o)

        try:
            bt = gdb.execute('bt', to_string=True)
            print('----------back trace-------------------')
            print(bt)
        except Exception as e:
            print("No stack")

        gdb.execute('quit')
        """
        f.write(textwrap.dedent(contents))

    proc = subprocess.run(['gdb', '-x', tmp_run_script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print('----------------------stdout------------------------------------')
    stdout = proc.stdout.decode('utf8')
    stdout = stdout.replace(str(solve_codefile.path.parent), '')
    start = False
    for line in stdout.split('\n'):
        if start: print(re.sub(f'({solve_codefile.path.name}:\d*)', Fore.YELLOW + r'\1' + Style.RESET_ALL, line))
        if re.match(r'Type .* to search for commands related to .*.', line): start = True

    print('----------------------stderr------------------------------------')
    print(re.sub(f'({solve_codefile.path.name}:\d*)', Fore.YELLOW + r'\1' + Style.RESET_ALL, proc.stderr.decode('utf8')))
    
# }}} 

# submit: sb {{{
@cli.command()
@click.argument('code_filename', type=str, default="")
@click.option('--language', '-l', default='auto-detect')
@click.option('--pretest/--no-pretest', '-t/-nt', default=True)
@pass_config
def sb(config, code_filename, language, pretest):
    if (not pretest) and (not click.confirm('Are you sure to submit?')):  # no-pretestの場合は遅延を避けるため最初に質問する。
        return
    codefile = CodeFile(code_filename)

    if pretest:
        click.secho("pretest started\n", fg='green')
        if not _test_all_case(codefile):
            click.secho("pretest not passed and exit", fg="red")
            return

    if (not pretest) or (click.confirm('Are you sure to submit?')):  # pretestの場合は最終確認をする。
        codefile.submit(config, language)
#}}}

# get answers: ga {{{
@cli.command()
@pass_config
@click.argument('code_filename', type=str, default='')
@click.option('--limit_count', '-c', type=int, default=5)
def ga(config, code_filename, limit_count):
    solve_codefile = CodeFile(code_filename)
    service = solve_codefile.oj_problem_class.get_service().get_name()
    lang_id = config.pref['submit']['default_lang'][service][solve_codefile.extension]
    count = 0
    for submission in solve_codefile.oj_problem_class.iterate_submissions_where(status='AC', order='created', language_id=lang_id):
        submission_data = submission.download_data()
        with open(solve_codefile.code_dir / f"ans.{submission_data.user_id}.{solve_codefile.extension}", mode='wb') as f:
            f.write(submission_data.source_code)
        print(f'downloaded ans.{submission_data.user_id}.{solve_codefile.extension}')

        count += 1
        if (count >= limit_count):
            break
# }}}

# get answers: viz {{{
@cli.command()
@click.option('--directed', '-d/-nd', type=bool, default=False)
@click.option('--in_index_base', '-i', type=int, default=1)
@click.option('--out-index-base', '-o', type=int, default=0)
@pass_config
def viz(config, directed, in_index_base, out_index_base):
    from graphviz import Digraph, Graph

    firstline = input().split()
    G = None
    n, m = -1, -1
    if (len(firstline) == 1):
        # this is tree
        G = Graph()
        n = int(firstline[0])
        m = n-1
    else:
        n, m = map(int, firstline)
        if directed:
            G = Digraph()
        else:
            G = Graph()

    for i in range(n):
        G.node(str(i))

    for i in range(m):
        u, v = map(int, input().split())
        u -= 1
        v -= 1
        G.edge(str(u), str(v), cost='1')

    output_filepath = os.path.expanduser('~/Dropbox/graph')
    G.render(output_filepath, view=True)
# }}}


# vim:set foldmethod=marker:
