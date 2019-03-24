import click  # {{{
import os, sys
import shutil
import pathlib
import requests
import fnmatch
import pickle
import subprocess
import signal
from . import config
from bs4 import BeautifulSoup
# from pcm.atcoder_tools.core.AtCoder import AtCoder
from onlinejudge._implementation.main import main as oj
import onlinejudge._implementation.utils as oj_utils
import onlinejudge.service.atcoder
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
@click.option('-n', '--prob_name', type=str, default='prob')
@pass_config
def ppp(config, task_url, prob_name):
    _prepare_problem(prob_name)
    os.chdir(prob_name)
    if task_url != '':
        shutil.rmtree('./test')
        oj(['download', task_url]) # get test cases

def _prepare_problem(prob_name):
    shutil.copytree(script_path+'/template/', f'./{prob_name}/')
    if not os.path.exists('./.pcm'):
        os.makedirs('./.pcm')
# }}}

# test: tt {{{
@cli.command()
@click.argument('code_filename', type=str, default='')
@click.option('--case', '-c', type=str, default='')
@click.option('--debug/--nodebug', '-d/-nd', default=True)
@pass_config
def tt(config, code_filename, case, debug):# {{{
    task_id, code_dir, code_filename, test_dir = _get_code_info(code_filename)
    if config.verbose:
        print('code_dir: ' + code_dir)
        print('code_filename: ' + code_filename)
        print('test_dir: ' + test_dir)

    if case == '': # test all case
        _test_task(code_dir, code_filename, test_dir, debug)
    else:
        if case in ("1", "2", "3", "4", "5", "6"):
            case = f'sample-{case}'
        infile = test_dir + case + '.in'
        expfile = test_dir + case + '.out'
        _test_case(code_dir, code_filename, case, infile, expfile, debug)
# }}}

def _test_task(code_dir, code_filename, testdir, debug=True):# {{{
    files = os.listdir(testdir)
    files.sort()
    res = True
    for filename in files:
        if not fnmatch.fnmatch(filename, '*.in'):
            continue
        case = filename[:-3]
        infile = testdir + case + '.in'
        expfile = testdir + case + '.out'  # 拡張子をexpにしたいが。。
        if not _test_case(code_dir, code_filename, case, infile, expfile, debug):
            res = False
    return res
# }}}

def _test_case(code_dir, code_filename, case, infile, expfile, debug=True):# {{{
    codefile = code_dir + '/' + code_filename
    extension = code_filename[code_filename.rfind('.') + 1:]

    # run program
    click.secho('-'*10 + case + '-'*10, fg='blue')
    if extension == "py":
        returncode, outs, errs, TLE_flag = _run_code(codefile, open(infile, "r"))

    elif extension == "cpp":
        click.secho('compile start.....', blink=True)
        command = [
                'g++',
                "-o", code_dir + '/a.out' ,
                codefile,
                '-std=c++14',
                '-O2',
                '-g3',
                '-fsanitize=undefined', # 未定義動作の検出
                # '-D_GLIBCXX_DEBUG',
                ]
        if debug:
            command.append('-DPCM') # for debug
            command.append('-Wall') # for debug

        proc = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                )
        outs, errs = proc.communicate()
        if proc.returncode:
            click.secho("compile error\n", fg='red')
            print(errs.decode('utf-8').replace(code_dir, ""))
            sys.exit()

        if outs:
            print(outs.decode('utf-8'))
        click.secho('compile finised')

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
    print(errs.replace(code_dir, ""))

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
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
        TLE_flag = True
    return proc.returncode, outs.decode('utf-8'), errs.decode('utf-8'), TLE_flag  # }}}
# }}}

# submit: sb {{{
@cli.command()
@click.argument('code_filename', type=str, default="")
@click.option('--pretest/--no-pretest', '-t/-nt', default=True)
@click.option('--debug/--nodebug', '-d/-nd', default=False)
@pass_config
def sb(config, code_filename, pretest, debug):
    contest = _reload_contest_class()
    task_id, code_dir, code_filename, test_dir = _get_code_info(code_filename)

    extension = code_filename[code_filename.rfind('.') + 1:]
    with open(code_dir + '/' + code_filename, "r") as f:
        code = f.read()

    if pretest:
        click.secho("pretest started\n", fg='green')
        if not _test_task(code_dir, code_filename, test_dir, debug):
            click.secho("pretest not passed and exit", fg="red")
            return

    if click.confirm('Are you sure to submit?'):
        contest.submit(task_id, extension, code)
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

# get template: gt {{{
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
    shutil.copy(script_path+'/template/dump.hpp', 'dump.hpp')
    click.secho(f"copied .vscode and dump.hpp", fg='green')

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

def _get_code_info(code_filename):# {{{
    if code_filename == "": # when code_filename not specified
        code_dir = os.getcwd()
        try:
            code_filename = _get_last_modified_file()
            click.secho(f"you did not specify code_filename.so pcm will use {code_filename}\n which is the one you updated at last", fg='yellow')
        except:
            click.secho("you are not in a pcm valid problem directory", fg='red')
            return

    elif os.path.exists(f'./{code_filename}'): # まずはcurrent directory以下を探す。
        code_dir = os.getcwd()
    else:
        code_dir = _search_parent_dir(code_filename)
        if code_dir is None:
            click.secho("you are not in a pcm managed directory", fg='red')
            return

    prob_dir = code_dir[:code_dir.rfind('/')]
    test_dir = f"{prob_dir}/test/"
    task_id = prob_dir[prob_dir.rfind('/')+1:]
    return task_id, code_dir, code_filename, test_dir
    # }}}

def _get_last_modified_file():# {{{
    candidates = []
    candidates += [(p.stat().st_mtime, str(p)) for p in pathlib.Path('.').glob(f'*.cpp')]
    candidates += [(p.stat().st_mtime, str(p)) for p in pathlib.Path('.').glob(f'*.py')]
    candidates.sort(reverse=True)
    if len(candidates)>0:
        code_filename = str(candidates[0][1])
        return code_filename
    else:
        raise Exception("no valid code file found")
# }}}

class Contest(object):
    def __init__(self, contest_identifier, work_dir=""):# {{{
        if contest_identifier[:3] in ("abc", "arc", "agc"):
            self.url = f"https://atcoder.jp/contests/{contest_identifier}"
        else:
            self.url = contest_identifier
        self.type = self.__get_type()  # like atcoder, codeforces
        self.name = self.__get_name()  # like agc023
        self.session = requests.session()
        self.__login(self.session)
        self.work_dir = os.path.abspath(work_dir if work_dir else self.name)
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
        if self.type=='atcoder':
            ext_to_lang_id = {'py': '3510', 'cpp': '3003'}  # pypy3, (C++14 (GCC 5.4.1))
            lang_id = ext_to_lang_id[extension]
            problem_id = self.task_info_map[task_id]["problem_id"]
            with oj_utils.with_cookiejar(oj_utils.get_default_session(), path=oj_utils.default_cookie_path) as session:
                onlinejudge.service.atcoder.AtCoderProblem(contest_id=self.name, problem_id=problem_id).submit_code(code, lang_id, session)
        elif self.type=='codeforces':
            base_submit_url = f"http://codeforces.com/contest/{self.name}/submit"
            ext_to_lang_id = {
                    'py': '31', # python3,   pypy=>41
                    'cpp': '50',  # GNU G++14 6.4.0
                    }
            lang_id = ext_to_lang_id[extension]

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
            for page in [1, 2]:
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
            answer_dir = self.work_dir + "/" + task_id + "/answers/"
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
                            if user_name in candidate_users:
                                answer = answer_page.find(id='submission-code').get_text()
                                with open(answer_dir + answer_id + "_" + user_name + "." + extension, mode='w') as f:
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
        if self.type == 'atcoder':
            click.secho(f'login status in __get_task_info_map(): {"Sign Out" in task_page_html.text}', fg='green')
        elif self.type == 'codeforces':
            click.secho(f'login status in __get_task_info_map(): {"Logout" in task_page_html.text}', fg='green')

        task_page = BeautifulSoup(task_page_html.content, 'lxml')
        links = task_page.findAll('a')

        task_urls = []
        if (self.type=='atcoder') or (self.type=='codeforces'):
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
        if self.type == 'atcoder':
            base_url = "https://atcoder.jp"
        elif self.type == 'codeforces':
            base_url = "http://codeforces.com"
        else:
            click.secho(f"unknown type of url: {self.url}", fg='red')
            sys.exit()

        for task_id, task_info in self.task_info_map.items():
            task_url = base_url + task_info['url']
            task_dir = self.work_dir + '/' + task_id
            shutil.copytree(script_path+'/template/', f'{task_dir}/')
            os.chdir(task_dir)

            try:
                shutil.rmtree(f"{task_dir}/test") # templateからのコピーでtest directoryが作られているので消しておく。
                click.secho(f"oj will try to download {task_url}...", fg='yellow')
                oj(['download', task_url]) # get test cases
                pathlib.Path(task_info['description'].replace("/", "-")).touch()
            except:
                click.secho("failed preparing: " + base_url + task_info['url'], fg='red')
    # }}}

    def __login(self, session):# {{{
        if self.type == 'atcoder':
            LOGIN_URL = "https://atcoder.jp/login"

            # csrf_token取得
            r = session.get(LOGIN_URL)
            s = BeautifulSoup(r.text, 'lxml')
            csrf_token = s.find(attrs={'name': 'csrf_token'}).get('value')

            # パラメータセット
            login_info = {
                "csrf_token": csrf_token,
                "username": config.atcoder_username,
                "password": config.atcoder_password
            }
        elif self.type == 'codeforces':
            LOGIN_URL = "http://codeforces.com/enter"

            # csrf_token取得
            r = session.get(LOGIN_URL)
            s = BeautifulSoup(r.text, 'lxml')
            csrf_token = s.find(attrs={'class': 'csrf-token'}).get('data-csrf')

            # パラメータセット
            login_info = {
                'csrf_token': csrf_token,
                'action': 'enter',
                'ftaa' : 'jp14jktv73egplz2is',
                'bfaa' : 'cc5b70fc5cbc458bb9c010b167bc3592',
                'handleOrEmail': config.codeforces_username,
                'password': config.codeforces_password,
                'remember': 'on',
                '_tta': '376'
            }
        else:
            raise Exception('not implemented')

        result = session.post(LOGIN_URL, data=login_info)
        result.raise_for_status()
        if self.type == 'atcoder':
            click.secho(f'login status in __login(): {"Sign Out" in result.text}', fg='green')
        elif self.type == 'codeforces':
            click.secho(f'login status in __login(): {"Logout" in result.text}', fg='green')

# }}}
# vim:set foldmethod=marker:
