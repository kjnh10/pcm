import click  # {{{
import os, sys
import shutil
import pathlib
import requests
import fnmatch
import pickle
import subprocess
import signal
from bs4 import BeautifulSoup
# from pcm.atcoder_tools.core.AtCoder import AtCoder
from onlinejudge.implementation.main import main as oj
import onlinejudge.implementation.utils as oj_utils
import onlinejudge.atcoder
ALPHABETS = [chr(i) for i in range(ord('A'), ord('Z')+1)]  # can also use string module
script_path = os.path.abspath(os.path.dirname(__file__))  # script path}}}

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
    config.verbose = verbose
    if home_directory is None:
        home_directory = '.'
    config.home_directory = home_directory
# }}}

# sub command
# sample{{{
@cli.command()
@click.option('--string', default='World', help='This is  the thing that is greeted.')
@click.option('--repeat', default=1, help='How many times you should be greeted.')
@click.argument('out', type=click.File('w'), default='-', required=False)
@pass_config
def sample(config, string, repeat, out):
    """This script greets you."""
    if config.verbose:
        click.echo('We are in verbose mode')
    click.echo('Home directory is %s' % config.home_directory)
    for x in range(repeat):
        click.echo('Hello %s!' % string, file=out)# }}}

# init{{{
@cli.command()
@pass_config
def init(config):
    """This command will make current dir pcm work-space"""
    os.makedirs('./.pcm')# }}}

# prepare{{{
@cli.command()
@click.argument('task_list_url', type=str, default='')
@click.argument('contest_dir', type=str, default='')
@click.option('--force/--no-force', "-f/-nf", default=False)
@pass_config
def pp(config, task_list_url, contest_dir, force): # {{{
    if task_list_url == '':
        _prepare_template()
        return

    contest = Contest(task_list_url)
    contest.prepare(force)
# }}}

def _prepare_template():# {{{
    shutil.copytree(script_path+'/template/', './tmp/prob1/')
    shutil.copytree(script_path+'/template/', './tmp/prob2/')
    os.makedirs('./tmp/.pcm')# }}}

# }}}

# test{{{
@cli.command()
@click.argument('code_filename', type=str, default='')
@click.option('--case', '-c', type=str, default='')
@click.option('--debug/--nodebug', '-', default=True)
@pass_config
def tt(config, code_filename, case, debug):# {{{
    config.debug_mode = debug
    code_dir, code_filename, test_dir = _get_code_info(code_filename)

    if case == '': # test all case
        _test_task(code_dir, code_filename, test_dir)
    else:
        if case == 'd':
            case = 'sample-1'
        infile = test_dir + case + '.in'
        expfile = test_dir + case + '.out'
        _test_case(code_dir, code_filename, case, infile, expfile)
# }}}

def _test_task(code_dir, code_filename, testdir):# {{{
    files = os.listdir(testdir)
    files.sort()
    res = True
    for filename in files:
        if not fnmatch.fnmatch(filename, '*.in'):
            continue
        case = filename[:-3]
        infile = testdir + case + '.in'
        expfile = testdir + case + '.out'  # 拡張子をexpにしたいが。。
        if not _test_case(code_dir, code_filename, case, infile, expfile):
            res = False
    return res
# }}}

def _test_case(code_dir, code_filename, case, infile, expfile):# {{{
    codefile = code_dir + '/' + code_filename
    extension = code_filename[code_filename.rfind('.') + 1:]

    # run program
    click.secho('-'*10 + case + '-'*10, fg='blue')
    if extension == "py":
        returncode, outs, errs, TLE_flag = _run_code(codefile, open(infile, "r"))

    elif extension == "cpp":
        try:
            subprocess.run(
                [
                    'g++',
                    "-o", code_dir + '/a.out' ,
                    codefile,
                    '-std=c++14',
                    '-g3',
                    '-Wall',
                    '-fsanitize=undefined', # 未定義動作の検出
                    '-D_GLIBCXX_DEBUG',
                    '-DPCM'  # macro
                 ],
                stderr=subprocess.STDOUT,
                check=True,
            )
        except:
            click.secho("compile error\n", fg='red')
            sys.exit()

        returncode, outs, errs, TLE_flag = _run_code(code_dir + '/a.out', open(infile, "r"))

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
        exp = ""

    # print result
    print('*'*7 + ' stdout ' + '*'*7)
    print(outs)
    stdout = outs.split('\n')

    # print error message
    print('*'*7 + ' stderr ' + '*'*7)
    print(errs)

    # compare result and expected
    if TLE_flag:
        click.secho('TLE\n', fg='red')
        return False

    if returncode != 0:
        SIGMAP = dict(
            (int(k), v) for v, k in reversed(sorted(signal.__dict__.items()))
            if v.startswith('SIG') and not v.startswith('SIG_')
        )
        click.secho(f'RE', fg='red')
        click.secho(f':{SIGMAP[abs(returncode)]}' if abs(returncode) in SIGMAP.keys() else str(abs(returncode)), fg='red')
        print('\n')
        return False

    if len(stdout) != len(exp):
        click.secho('WA\n', fg='red')
        return False
    else:
        for i in range(len(stdout)):
            if stdout[i] != exp[i]:
                click.secho('WA\n\n', fg='red')
                return False
        else:
            click.secho('AC\n', fg='green')
    return True
# }}}

def _run_code(code_filename, input_file):# {{{
    proc = subprocess.Popen(
        [
            code_filename,
            "pcm"  # tell the sctipt that pcm is calling
        ],
        stdin=input_file,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        outs, errs = proc.communicate(timeout=2)
        TLE_flag = False
    except subprocess.TimeoutExpired as e:
        proc.kill()
        outs, errs = proc.communicate()
        TLE_flag = True
    return proc.returncode, outs.decode('utf-8'), errs.decode('utf-8'), TLE_flag  # }}}

def _get_code_info(code_filename):# {{{
    # when code_filename not specified
    if code_filename == "":
        p = list(pathlib.Path('.').glob('*.cpp'))
        if len(p)>0:
            code_filename = str(p[0])
            code_dir = os.getcwd()
            test_dir = f"{code_dir}/test/"
            click.secho(f"you did not specify code_filename.so pcm will use {code_filename}\n", fg='yellow')
        else:
            click.secho("you are not in a pcm validproblem directory", fg='red')
            return
    else:
        code_dir = _search_parent_dir(code_filename)
        if code_dir is None:
            return
        test_dir = f"{code_dir}/test/"
    return code_dir, code_filename, test_dir# }}}
# }}}

# submit{{{
@cli.command()
@click.argument('code_filename', type=str, default="")
@click.option('--pretest/--no-pretest', '-t/-nt', default=True)
@pass_config
def sb(config, code_filename, pretest):
    contest = _reload_contest_class()
    code_dir, code_filename, test_dir = _get_code_info(code_filename)

    task_id = code_dir[code_dir.rfind('/')+1:]
    extension = code_filename[code_filename.rfind('.') + 1:]
    with open(code_dir + '/' + code_filename, "r") as f:
        code = f.read()

    if pretest:
        click.secho("pretest started\n", fg='green')
        if not _test_task(code_dir, code_filename, code_dir + '/' + 'test/'):
            click.secho("pretest not passed and exit", fg="red")
            return

    if click.confirm('Are you sure to submit?'):
        contest.submit(task_id, extension, code)
#}}}

# get answers{{{
@cli.command()
@pass_config
def ga(config, limit_count=5):
    contest = _reload_contest_class()
    contest.get_answers(limit_count)
# }}}

# get template{{{
@cli.command()
@click.argument('extension', type=str, default='cpp')
@click.option('--new/--replace', '-n/-r', default=False)
@pass_config
def gt(config, extension, new):
    if new:
        if not os.path.exists(f"solve.{extension}"):
            shutil.copy(script_path+f'/template/solve.{extension}', f"solve.{extension}")
            click.secho(f"generated new solve.{extension}", fg='green')
        else:
            click.secho(f"already existed", fg='green')
        return

    p = list(pathlib.Path('.').glob("*.cpp"))
    if len(p)>0:
        filename = str(p[0])
        shutil.copy(script_path+f'/template/solve.{extension}', filename)
        click.secho(f"overrided {filename} with template", fg='green')
    else:
        shutil.copy(script_path+f'/template/solve.{extension}', f"solve.{extension}")
        click.secho(f"not found {extension} file\n", fg='red')
        click.secho(f"generated new solve.{extension}", fg='green')

    # vscodeのsettingも更新する。
    shutil.copytree(script_path+f'/template/.vscode/', ".vscode/")
    click.secho(f"copied .vscode/", fg='green')

# }}}
#}}}

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
            return now
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
    with open(contest_dir + '/.pcm/.contest_info', mode="r") as f:
        contest_url = f.readline()
    return Contest(contest_url, contest_dir)
# }}}

class Contest(object):
    def __init__(self, contest_url, work_dir=""):# {{{
        self.url = contest_url
        self.type = self.__get_type()  # like atcoder, codeforces
        self.name = self.__get_name()  # like agc023
        self.work_dir = work_dir if work_dir!="" else os.path.abspath("./" + self.name)  # 指定されていなければカレントフォルダ
        self.config_dir = self.work_dir + '/.pcm'
        self.task_info_cache = self.work_dir + "/.pcm/task_info_map"
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
        with open(self.config_dir + "/.contest_info", mode="w") as f:
            f.write(self.url)

        self.task_info_map = self.__get_task_info_map()  # 古いバージョンの形式のcacheが入っている可能性があるためprepareの時はもう一度読み込む。
        with open(self.task_info_cache, mode='wb') as f:
            pickle.dump(self.task_info_map, f)

        self.__prepare_tasks()
        # }}}

    def submit(self, task_id, extension, code):# {{{
        if "atcoder" in self.type:
            ext_to_lang_id = {'py': '3510', 'cpp': '3003'}  # pypy3, (C++14 (GCC 5.4.1))
            lang_id = ext_to_lang_id[extension]
        else:
            print("not implemeted for contest type: {self.type}")
            sys.exit()
        with oj_utils.with_cookiejar(oj_utils.new_default_session(), path=oj_utils.default_cookie_path) as session:
            problem_id = self.task_info_map[task_id]["problem_id"]
            onlinejudge.atcoder.AtCoderProblem(contest_id=self.name, problem_id=problem_id).submit(code, lang_id, session)# }}}

    def get_answers(self, limit_count):  # {{{
        if "atcoder" in self.type:
            task_ids = self.task_info_map.keys()
            for task_id in task_ids:
                self.__get_answer(extension="cpp", task_id=task_id, limit_count=limit_count)
                self.__get_answer(extension="py",  task_id=task_id, limit_count=limit_count) # 3510 for pypy

    def __get_answer(self, extension, task_id, limit_count):
            answer_dir = self.work_dir + "/" + task_id + "/answers/"
            if not os.path.exists(answer_dir):
                os.makedirs(answer_dir)

            if "atcoder" in self.type:
                if extension == "cpp":
                    lang_code="3003"
                elif extension == "py":
                    lang_code="3023"

                problem_id = self.task_info_map[task_id]["problem_id"]
                all_answer_url = f"https://beta.atcoder.jp/contests/{self.name}/submissions?"
                all_answer_url += f"f.Language={lang_code}&f.Status=AC&f.Task={problem_id}&f.User=&orderBy=created&page=1"
                # like https://beta.atcoder.jp/contests/abc045/submissions?f.Language=3003&f.Status=AC&f.Task=abc045_a&f.User=&orderBy=created&page=1

                print('GET ' + all_answer_url)
                all_answer_page_html = requests.get(all_answer_url)
                all_answer_page = BeautifulSoup(all_answer_page_html.content, 'lxml')
                links = all_answer_page.findAll('a')

                count = 0
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
                        answer = answer_page.find(id='submission-code').get_text()
                        with open(answer_dir + answer_id + "_" + user_name + "." + extension, mode='w') as f:
                            f.write(answer)
                        count += 1
                    if count >= limit_count:
                        break
                else:
                    click.secho('There seems to be no answers you request. Maybe wrong url.', fg='red')
    # }}}

    def __get_type(self):# {{{
        if "beta.atcoder" in self.url:
            return "beta.atcoder"
        elif "atcoder" in self.url:
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
            return self.url[self.url.find('//')+2:self.url.find('.')]  # like arc071
        elif self.type == 'beta.atcoder':
            start = self.url.find('contests')+9
            return self.url[start:start+6]
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
            return self.url + "/assignments"
        elif self.type == 'beta.atcoder':
            return "https://" + self.name + ".contest.atcoder.jp/assignments"
        elif self.type == 'codeforces':
            return self.url  # codeforcesはproblemsがindex pageになっている。
        else:
            click.secho(f"unknown type of url: {self.url}", fg='red')
            sys.exit()# }}}

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

        oj(['login', self.task_list_url])
        with oj_utils.with_cookiejar(oj_utils.new_default_session(), path=oj_utils.default_cookie_path) as session:
            task_page_html = oj_utils.request('GET', self.task_list_url, session, allow_redirects=True)
        task_page = BeautifulSoup(task_page_html.content, 'lxml')
        links = task_page.findAll('a')

        task_urls = []
        if ("atcoder" in self.type) or (self.type=='codeforces'):
            for l in links:
                if l.get_text().strip() in ALPHABETS:
                    task_urls.append(l.get('href'))

            # get task_id, description
            task_info_map = {}
            for url in task_urls:
                description = ""
                for l in links:
                    link_text = l.get_text().strip()
                    if l.get('href') == url and link_text in ALPHABETS:
                        task_id = link_text
                    elif (l.get('href') == url) and (not link_text in ALPHABETS): # 問題名がA,B,C,D・だととれない。。
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

    def __prepare_tasks(self):  # {{{
        if "atcoder" in self.type:
            base_url = self.task_list_url[:self.task_list_url.rfind("/")]
        elif self.type == 'codeforces':
            base_url = "http://codeforces.com"
        else:
            click.secho(f"unknown type of url: {self.url}", fg='red')
            sys.exit()

        for task_id, task_info in self.task_info_map.items():
            task_url = base_url + task_info['url']
            task_dir = self.work_dir + '/' + task_id
            os.makedirs(task_dir)
            os.chdir(task_dir)
            shutil.copy(script_path+'/template/solve.py', task_id + '.py')
            shutil.copy(script_path+'/template/solve.cpp', task_id + '.cpp')
            shutil.copytree(script_path+'/template/.vscode/', '.vscode/')
            try:
                click.secho(f"oj will try to download {task_url}...", fg='yellow')
                oj(['download', task_url]) # get test cases
                pathlib.Path(task_info['description'].replace("/", "-")).touch()
            except:
                click.secho("failed preparing: " + base_url + task_info['url'], fg='red')
            # }}}
# vim:set foldmethod=marker:
