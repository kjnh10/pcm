import click  # {{{
import os, sys
import shutil
from pathlib import Path
import requests
import fnmatch
import pickle
import subprocess
import signal
import toml
import time
import re
from typing import TYPE_CHECKING, List, Optional, Type
from bs4 import BeautifulSoup
from onlinejudge._implementation.main import main as oj
import onlinejudge._implementation.utils as oj_utils
import onlinejudge.service.atcoder
script_path = Path(os.path.abspath(os.path.dirname(__file__)))  # script path}}}
from .codefile import CodeFile
from .utils import get_last_modified_file

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

# prepare contest: pp {{{
@cli.command()
@click.argument('contest_identifier', type=str, default='abc001')
@click.option('-n', '--work_dir_name', type=str, default='')
@click.option('--force/--no-force', "-f/-nf", default=False)
@pass_config
def pp(config, contest_identifier, work_dir_name, force):
    contest = Contest(contest_identifier, work_dir=work_dir_name)
    contest.prepare(force)
# }}}

# prepare problem: ppp {{{
@cli.command()
@click.argument('task_url', type=str, default='')
@click.option('-n', '--prob_name', type=str, default='')
@click.option('--force/--no-force', "-f/-nf", default=False)
@pass_config
def ppp(config, task_url, prob_name, force):
    # TODO: 実装をppと統一する。pppをベースにしたい。
    # TODO: task_info_mapのようなものを生成する。submitを行えるようにするため。
    if prob_name == '':
        if task_url != '':
            prob_name = task_url[task_url.rfind('/')+1:]
        else:
            prob_name = 'prob'

    if Path(prob_name).exists():
        if force:
            Path(prob_name).rmdir()
        else:
            print(f'{prob_name} directory already exists')
            return

    _prepare_problem(prob_name=prob_name)
    os.chdir(prob_name)
    if task_url != '':
        shutil.rmtree('./test')
        oj(['download', task_url]) # get test cases

@pass_config
def _prepare_problem(config, prob_name):
    shutil.copytree(config.pref['template_dir'], f'{prob_name}/')
# }}}

# test: tt {{{
@cli.command()
@click.argument('code_filename', type=str, default='')
@click.option('--case', '-c', type=str, default='')
@click.option('--debug/--nodebug', '-d/-nd', default=True)
@click.option('--timeout', '-t', type=float, default=-1)
@click.option('--by', '-b', type=str, default='naive.*')
@pass_config
def tt(config, code_filename:str, case:str, by:str, debug:bool, timeout:float): # {{{
    if (timeout!=-1):
        config.pref['test']['timeout_sec']=timeout
    solve_codefile = CodeFile(code_filename)
    test_dir = solve_codefile.test_dir

    if case == '': # test all case
        _test_all_case(solve_codefile, debug)
    else:
        if case in set(map(str, range(1, 101))):
            case = f'sample-{case}'
            infile = test_dir / f"{case}.in"
            expfile = test_dir / f"{case}.out"
            if (not infile.exists()):
                click.secho(f"{infile.name} not found.", fg='yellow')
                return
        elif Path(case).suffix in ['.py']:
            # for random test
            naive_codefile = CodeFile(by)
            subprocess.run(f"python {test_dir/case} > {test_dir/'random.in'} ", shell=True)
            case = 'random'
            infile = test_dir / f"{case}.in"
            expfile = test_dir / f"{case}.out"
            returncode, outs, errs, TLE_flag = _run_code(naive_codefile, infile=infile)
            with open(expfile, mode='w') as f:
                if TLE_flag:
                    f.write('TLE for naive code. if you extend timeout time, use -t option like -t 5')
                else:
                    f.write(outs)
        else:
            infile = test_dir / f"{case}.in"
            expfile = test_dir / f"{case}.out"

        _test_case(solve_codefile, case, infile, expfile, debug)
# }}}

def _test_all_case(codefile: CodeFile, debug=True) -> bool: # {{{
    files = os.listdir(codefile.test_dir)
    files.sort()
    res = True
    for filename in files:
        if not fnmatch.fnmatch(filename, '*.in'):
            continue
        case = filename[:-3]
        infile = codefile.test_dir / f"{case}.in"
        expfile = codefile.test_dir / f"{case}.out"  # 拡張子をexpにしたいが。。
        if not _test_case(codefile, case, infile, expfile, debug):
            res = False
    return res
# }}}

def _test_case(codefile: CodeFile, case_name: str, infile: Path, expfile: Path, debug=True) -> str: # {{{
    # run program
    click.secho('-'*10 + case_name + '-'*10, fg='blue')
    returncode, outs, errs, TLE_flag = _run_code(codefile, infile=infile)

    # print input
    with open(infile, 'r') as f:
        print('*'*7 + ' input ' + '*'*7)
        print(f.read())

    # print expected
    try:
        with open(expfile, 'r') as f:
            print('*'*7 + ' expected ' + '*'*7)
            exp = f.read()
            print(exp)
            exp = exp.split('\n')
    except FileNotFoundError:
        print('*'*7 + ' expected ' + '*'*7)
        click.secho(f"expected file: {expfile} not found\n", fg='yellow')
        exp = ['']

    # print result
    print('*'*7 + ' stdout ' + '*'*7)
    print(outs)
    stdout = outs.split('\n')

    # print stderr message
    print('*'*7 + ' stderr ' + '*'*7)
    for line in errs.split('\n'):
        line = line.replace(str(codefile.code_dir), "")
        click.secho(line, fg='yellow')

    # compare result and expected
    if TLE_flag:
        click.secho('TLE\n', fg='red')
        return "TLE"

    if returncode != 0:
        SIGMAP = dict(
            (int(k), v) for v, k in reversed(sorted(signal.__dict__.items()))
            if v.startswith('SIG') and not v.startswith('SIG_')
        )
        click.secho(f'RE', fg='red')
        click.secho(f':{SIGMAP[abs(returncode)]}' if abs(returncode) in SIGMAP.keys() else str(abs(returncode)), fg='red')
        print('\n')
        return "RuntimeError"

    # 最後の空白行は無視する。
    if (stdout[-1]==''): stdout.pop()
    if (exp[-1]==''): exp.pop()

    if len(stdout) != len(exp):
        click.secho('WA\n', fg='red')
        return outs
    else:
        for i in range(len(stdout)):
            if stdout[i].replace('\r', '') != exp[i]:
                click.secho('WA\n\n', fg='red')
                return outs
        else:
            click.secho('AC\n', fg='green')
    return outs
# }}}

@pass_config
def _run_code(config, codefile : CodeFile, infile : Path, debug=True):  # {{{
    if codefile.path.suffix == ".py":
        return _run_exe(exefile=codefile.path, input_file=open(infile, "r"))
    elif codefile.path.suffix == ".cpp":
        click.secho('compile start.....', blink=True)
        exe = codefile.bin_dir / f'{codefile.stem}.out'
        exe.parent.mkdir(exist_ok=True)
        if (exe.exists() and codefile.path.stat().st_mtime <= exe.stat().st_mtime):
            click.secho(f'compile skipped since {codefile.path} is older than {codefile.path.stem}.out')
        else:
            start = time.time()
            command = [
                    'g++',
                    str(codefile.path),
                    "-o", str(exe),
                    '-std=c++14',
                    ]
            command.append('-DPCM') # for dump
            command.append('-Wall') # for debug
            if debug:
                command.append('-fsanitize=undefined') # 未定義動作の検出
                command.append('-fsanitize=address') #
                # command.append('-g3') # for gdb
                # command.append('-D_GLIBCXX_DEBUG')
                # command.append('-O2')

            proc = subprocess.Popen(
                    command,  # g++ solve.cpp -o {codefile.path.stem}.out -std=c++14 -DPCM -Wall -fsanitize=undefined
                    stdout=subprocess.PIPE,
                    )
            outs, errs = proc.communicate()
            if proc.returncode:
                click.secho("compile error\n", fg='red')
                sys.exit()

            if outs:
                print(outs.decode('utf-8'))

            click.secho('compile finised')
            elapsed_time = time.time() - start
            print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
        return _run_exe(exe, open(infile, "r"))
    else:
        raise Exception(f"{codefile.path} is not a valid code file")
    # }}}

@pass_config
def _run_exe(config, exefile, input_file):# {{{
    command = []
    if (exefile.suffix=='.py'):
        command.append('python')
    command.append(str(exefile))
    command.append('pcm') # tell the sctipt that pcm is calling
    proc = subprocess.Popen(
        command,
        stdin=input_file,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        # shell=True,  # for windows
    )
    try:
        outs, errs = proc.communicate(timeout=config.pref['test']['timeout_sec'])
        TLE_flag = False
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
        TLE_flag = True
    return (proc.returncode, outs.decode('utf-8'), errs.decode('utf-8'), TLE_flag)  # }}}

# }}}

# random test: rt {{{
@cli.command()
@click.argument('code_filename', type=str, default='')
@click.option('--by', '-b', type=str, default='naive.*')
@click.option('--generator', '-g', type=str, default='gen.py')
@click.option('--debug/--nodebug', '-d/-nd', default=True)
@click.option('--timeout', '-t', type=float, default=-1)
@pass_config
def rt(config, code_filename:str, by:str, generator:str, debug:bool, timeout:float):# {{{
    if (timeout!=-1):
        config.pref['test']['timeout_sec']=timeout
    solve_codefile = CodeFile(exclude_filename_pattern=by)
    naive_codefile = CodeFile(match_filename_pattern=by)
    test_dir = solve_codefile.test_dir

    case_generator_file = test_dir / generator
    infile = test_dir / "random.in"

    while True:
        subprocess.run(f"python {str(case_generator_file)} > {str(infile)}", shell=True)
        if (not infile.exists()):
            click.secho(f"{infile.name} not found.", fg='yellow')
            return

        if (by=='large'):
            out1 = _test_case(code_dir, code_filename, 'random', infile, '', debug)
            if (out1 in ('TLE', 'RuntimeError')):
                return 0;
        else:
            out1 = _test_case(solve_codefile, f'random-{code_filename}', infile, '', debug)
            out2 = _test_case(naive_codefile, f'random-{by}', infile, '', debug)
            print(f"{solve_codefile.path.name}: {out1}")
            print(f"{naive_codefile.path.name}: {out2}")
            if (out1!=out2):
                with open(test_dir/'random.out', mode='w') as f:
                    f.write(out2)
                return 0;
# }}}
# }}}

# submit: sb {{{
@cli.command()
@click.argument('code_filename', type=str, default="")
@click.option('--language', '-l', default='auto-detect')
@click.option('--pretest/--no-pretest', '-t/-nt', default=True)
@click.option('--debug/--nodebug', '-d/-nd', default=False)
@pass_config
def sb(config, code_filename, language, pretest, debug):
    if (not pretest) and (not click.confirm('Are you sure to submit?')):  # no-pretestの場合は遅延を避けるため最初に質問する。
        return

    codefile = CodeFile(code_filename)
    extension = codefile.path.suffix[1:]
    contest = _reload_contest_class()

    with open(codefile.path, "r") as f:
        code_string = f.read()

    if pretest:
        click.secho("pretest started\n", fg='green')
        if not _test_all_case(codefile, debug):
            click.secho("pretest not passed and exit", fg="red")
            return

    if (not pretest) or (click.confirm('Are you sure to submit?')):  # pretestの場合は最終確認をする。
        contest.submit(codefile.task_alphabet, extension, code_string, language)
#}}}

# get answers: ga {{{
@cli.command()
@pass_config
@click.option('--limit_count', '-c', type=int, default=5)
@click.option('--extension', '-e', type=str, default='cpp')
def ga(config, limit_count, extension):
    contest = _reload_contest_class()
    contest.get_answers(limit_count, extension)
# }}}

# private functions
def _search_parent_dir(code_filename):# {{{
    contest_dir = _pcm_root_dir()
    if contest_dir is None:
        return None

    for base_dir, _sub_dirs, files in os.walk(contest_dir):
        for f in files:
            if f == code_filename:
                return base_dir
    else:
        print("not found: " + code_filename + " in " + contest_dir)
        sys.exit()
# }}}

def _pcm_root_dir():# {{{
    pwd = os.getcwd() # 最後には元のdirecotryに戻るため保存しておく。
    while True:
        if sum([1 if f == '.pcm' else 0 for f in os.listdir('./')]):
            now = os.getcwd()
            os.chdir(pwd)
            return Path(now)
        else:
            if os.getcwd() == "/":
                print("it seems you aren't in directory maintained by pcm")
                sys.exit()
            try:
                os.chdir('../')
            except:
                print("it seems you aren't in directory maintained by pcm")
                sys.exit()
            # }}}

def _reload_contest_class():  # {{{
    contest_dir = _pcm_root_dir()
    with open(contest_dir / '.pcm/.contest_info', mode="r") as f:
        contest_url = f.readline()
    return Contest(contest_url, contest_dir)
# }}}


class Contest(object):
    def __init__(self, contest_identifier, work_dir=""):# {{{
        if contest_identifier[:3] in ("abc", "arc", "agc"):
            self.url = f"https://atcoder.jp/contests/{contest_identifier}"
        else:
            self.url = contest_identifier
        self.type = self.__get_type()  # like atcoder, codeforces
        self.name = self.__get_name()  # like agc023
        with oj_utils.with_cookiejar(oj_utils.get_default_session()) as session:
            self.session = session
            if not self.__is_logined():
                click.secho(f'you are not logged in to {self.type}. if you want to join a contest realtime or submit, you need to "oj login"', fg='red')
        self.work_dir = Path(os.path.abspath(work_dir if work_dir else self.name))
        self.config_dir = self.work_dir / '.pcm'
        self.task_info_cache = self.work_dir / ".pcm/task_info_map"
        self.task_list_url = self.__get_task_list_url()
        self.task_info_map = self.__get_task_info_map()  # {task_id:{url:<url>, description:<description>}}
    # }}}

    def prepare(self, force):# {{{
        try:
            os.makedirs(self.work_dir)
        except OSError:
            if force:
                shutil.rmtree(self.work_dir)
                os.makedirs(self.work_dir)
            else:
                click.secho('The specified direcotry already exists.', fg='red')
                return

        os.makedirs(self.config_dir)
        with open(self.config_dir / ".contest_info", mode="w") as f:
            f.write(self.url)

        self.task_info_map = self.__get_task_info_map()  # 古いバージョンの形式のcacheが入っている可能性があるためprepareの時はもう一度読み込む。
        with open(self.task_info_cache, mode='wb') as f:
            pickle.dump(self.task_info_map, f)

        self.__prepare_tasks()
        # }}}

    @pass_config
    def submit(config, self, task_id: str, extension: str, code: str, language: str): # {{{
        if language == 'auto-detect':
            try:
                lang_id = config.pref['submit']['default_lang'][self.type][extension]
            except KeyError as e:
                click.secho(f'{extension} not found in possible extensions. if you want to add {extension}, you can add it in ~/.config/pcm/config.toml', fg='red')
                print('current possible extensions')
                print(config.pref['submit']['default_lang'][self.type])
                return
        else:
            try:
                lang_id = config.pref['submit']['language'][self.type][language]
            except KeyError as e:
                click.secho(f'{language} not found in possible language. if you want to add {language}, you can add it in ~/.config/pcm/config.toml', fg='red')
                print('current possible language')
                print(config.pref['submit']['language'][self.type])
                return

        if self.type=='atcoder':
            problem_id = self.task_info_map[task_id]["problem_id"]
            res = onlinejudge.service.atcoder.AtCoderProblem(contest_id=self.name, problem_id=problem_id).submit_code(code=code, language_id=lang_id, session=self.session)
            print(res)
        elif self.type=='codeforces':
            # TODO: onlinejudgeの機能を使用するようにする。
            base_submit_url = f"http://codeforces.com/contest/{self.name}/submit"
            # get csrf_token
            r = self.session.get(base_submit_url)
            soup = BeautifulSoup(r.text, "lxml")
            csrf_token = soup.find(name="span", class_="csrf-token").get('data-csrf')
            assert(csrf_token)
            payload = {
                        "csrf_token":csrf_token,
                        "ftaa":"2gm68wq1kofdqv7d71",
                        "bfaa":"37ed9af431852dbdb93c7ef8bfed8a9d",
                        "action":"submitSolutionFormSubmitted",
                        "submittedProblemIndex":task_id,
                        "programTypeId":lang_id,
                        "source":code,
                        "tabSize":"4",
                        "sourceFile":"",
                    }
            r = self.session.post(
                    base_submit_url,
                    params = payload,
                    )
            soup = BeautifulSoup(r.text, "lxml")
            error = soup.find(class_="error for__source")
            if error:
                click.secho(error.text, fg='red')
            elif(r.url[r.url.rfind("/")+1:]=="my"):  # if submitted successfully, returned url will be http://codeforces.com/contest/****/my
                print(r.url)
                click.secho('successfully submitted maybe...', fg='green')
            else:
                click.secho('submittion failed maybe...', fg='red')
        else:
            print("not implemeted for contest type: {self.type}")
            sys.exit()
            # }}}

    def get_answers(self, limit_count, extension):  # {{{
        if self.type=='atcoder':
            # get redcoderlist
            excelent_users = []
            for page in [1, 2, 3, 4]:
                rank_url = f"https://atcoder.jp/ranking?page={page}"
                rank_page = BeautifulSoup(requests.get(rank_url).content, 'lxml')
                excelent_users_buf = [tag.get('href') for tag in rank_page.findAll('a', class_='username')]
                excelent_users += [l[l.rfind('/')+1:] for l in excelent_users_buf]
            print(len(excelent_users), excelent_users)
        elif self.type=='codeforces':
            # get redcoderlist
            rank_url = 'http://codeforces.com/ratings/page/1'
            rank_page = BeautifulSoup(requests.get(rank_url).content, 'lxml')
            excelent_users = [tag.get('href') for tag in rank_page.findAll('a') if '/profile/' in tag.get('href')]
            excelent_users = set([l[l.rfind('/')+1:] for l in excelent_users])

        task_ids = self.task_info_map.keys()
        for task_id in task_ids:
            self.__get_answer(extension=extension, task_id=task_id, limit_count=limit_count, candidate_users=excelent_users)

    def __get_answer(self, extension, task_id, limit_count, candidate_users):
            answer_dir = self.work_dir / task_id / "answers"
            if not os.path.exists(answer_dir):
                os.makedirs(answer_dir)

            if self.type=='atcoder':
                if extension == "cpp":
                    lang_code="3003"
                elif extension == "py":
                    lang_code="3023"
                    # 3510 for pypy

                problem_id = self.task_info_map[task_id]["problem_id"]
                count = 0
                page = 1
                while count < limit_count:
                    all_answer_url = f"https://beta.atcoder.jp/contests/{self.name}/submissions?"
                    all_answer_url += f"f.Language={lang_code}&f.Status=AC&f.Task={problem_id}&f.User=&orderBy=created&page={page}"
                    #like https://beta.atcoder.jp/contests/abc045/submissions?f.Language=3003&f.Status=AC&f.Task=abc045_a&f.User=&orderBy=created&page=1
                    print('GET ' + all_answer_url)
                    all_answer_page = BeautifulSoup(requests.get(all_answer_url).content, 'lxml')
                    links = all_answer_page.findAll('a')

                    if all_answer_page.find('div', class_='panel-body') is not None: # 回答が尽きた場合
                        click.secho('There seems to be no enough answers for your request.', fg='yellow')
                        break;

                    for l in links:
                        link_url = l.get('href')
                        if l.get_text() in ("Detail", "詳細"):
                            answer_id = link_url[link_url.rfind("/")+2:]
                            answer_url = "https://beta.atcoder.jp" + l.get('href')
                            answer_page = BeautifulSoup(requests.get(answer_url).content, 'lxml')
                            A = answer_page.findAll('a')
                            for a in A:
                                link = a.get('href')
                                if "users" in str(link):
                                    user_name = link[link.rfind('/')+1:]

                            if (user_name in candidate_users) or True:  # fileter 条件
                                answer = answer_page.find(id='submission-code').get_text()
                                with open(answer_dir / f"{answer_id}_{user_name}.{extension}", mode='w') as f:
                                    f.write(answer)
                                count += 1

                        if count == limit_count:
                            break
                    page += 1;
            else:
                # codeforcesはseleniumを使わないととれなそう。
                raise Exception(f'not implemented for {self.type} yet.')
    # }}}

    def __get_type(self):# {{{
        if "atcoder" in self.url:
            return "atcoder"
        elif "codeforces" in self.url:
            return "codeforces"
        else:
            click.secho(f"unknown type of url: {self.url}", fg='red')
            sys.exit()# }}}

    def __get_name(self):# {{{
        """
        get contest_name from contest_url
        """
        if self.type == 'atcoder':
            return self.url[self.url.rfind('/')+1 : ]  # like arc071
        elif self.type == 'codeforces':
            start = self.url.find('contest')+8
            return self.url[start:]
        else:
            click.secho(f"unknown type of url: {self.url}", fg='red')
            sys.exit()# }}}

    def __get_task_list_url(self):# {{{
        """
        get task_list_url from contest_url
        """
        if self.type == 'atcoder':
            return self.url + "/tasks"
        elif self.type == 'codeforces':
            return self.url  # codeforcesはproblemsがindex pageになっている。
        else:
            click.secho(f"unknown type of url: {self.url}", fg='red')
            sys.exit()# }}}

    def __is_logined(self):# {{{
        resp = self.session.request('GET', self.url)
        if self.type == 'atcoder':
            click.secho(f'login status in __is_logined(): {"Sign Out" in resp.text}', fg='green')
            return ("Sign Out" in resp.text)
        elif self.type == 'codeforces':
            click.secho(f'login status in __is_logined(): {"Logout" in resp.text}', fg='green')
            return ("Logout" in resp.text)
# }}}

    def __get_task_info_map(self):# {{{
        # reload cache if it exists.
        if os.path.exists(self.task_info_cache):
            with open(self.task_info_cache, mode='rb') as f:
                try:
                    task_info_map = pickle.load(f)
                    assert task_info_map != {} # 前回のフォルダが壊れていて空のcacheがおいてある場合は例外を発生させる。
                    click.secho("reloaded cache", fg='yellow')
                    return task_info_map
                except:
                    click.secho(f"{self.task_info_cache} is broken, so will try to retrieve info", fg='yellow')

        task_page_html = self.session.request('GET', self.task_list_url)
        task_page = BeautifulSoup(task_page_html.content, 'lxml')
        links = task_page.findAll('a')

        task_urls = []
        if (self.type=='atcoder') or (self.type=='codeforces'):
            for l in links:
                if re.match(r"[A-Z][1-2]?$", l.get_text().strip()):
                    task_urls.append(l.get('href'))

            # get task_id, description
            task_info_map = {}
            for url in task_urls:
                description = ""
                for l in links:
                    link_text = l.get_text().strip()  # like A or A1
                    if l.get('href') == url and re.match(r"[A-Z][1-2]?$", link_text):
                        task_id = link_text
                    elif (l.get('href') == url):
                        description = link_text

                task_info_map[task_id] = {'url':url, 'description':description, 'problem_id':url[url.rfind("/")+1:]}

            try:
                with open(self.task_info_cache, mode='wb') as f:
                    pickle.dump(task_info_map, f)
            except:
                click.secho("caching task_info_map failed", fg='yellow')

            return task_info_map
        else:
            click.secho(f"unknown type of url: {self.url}", fg='red')
            print("There seems to be no problems. Check that the url is correct task list url")
            sys.exit()

    # }}}

    @pass_config
    def __prepare_tasks(config, self):  # {{{
        if self.type == 'atcoder':
            base_url = "https://atcoder.jp"
        elif self.type == 'codeforces':
            base_url = "http://codeforces.com"
        else:
            click.secho(f"unknown type of url: {self.url}", fg='red')
            sys.exit()

        for task_id, task_info in self.task_info_map.items():
            task_url = base_url + task_info['url']
            task_dir = self.work_dir / task_id

            shutil.copytree(config.pref['template_dir'], f'{task_dir}/')
            os.chdir(task_dir)

            try:
                subprocess.run(f"rm {task_dir/'test'}/sample*", shell=True)  # gen.pyは消さないようにする。
                click.secho(f"oj will try to download {task_url}...", fg='yellow')
                oj(['download', task_url]) # get test cases
                Path(task_info['description'].replace("/", "-")).touch()
            except:
                click.secho("failed preparing: " + base_url + task_info['url'], fg='red')
    # }}}

# vim:set foldmethod=marker:
