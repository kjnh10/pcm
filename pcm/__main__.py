import click# {{{
import os, sys
import shutil
import pathlib
import pickle
import fnmatch
import subprocess
from bs4 import BeautifulSoup
# from pcm.atcoder_tools.core.AtCoder import AtCoder
from onlinejudge.implementation.main import main as oj
import onlinejudge.implementation.utils as oj_utils
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
@click.option('--force/--no-force', default=False)
@pass_config
def prepare(config, task_list_url, contest_dir, force):# {{{
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
@click.argument('code_filename', type=str)
@pass_config
def test(config, code_filename):# {{{
    code_dir = _seach_par_dir(code_filename)
    if code_dir is None:
        return
    test_core(code_dir, code_filename, code_dir + '/' + 'test/')# }}}

def test_core(code_dir, code_filename, testdir):# {{{
    files = os.listdir(testdir)
    files.sort()
    extension = code_filename[code_filename.rfind('.') + 1:]
    for filename in files:
        if not fnmatch.fnmatch(filename, '*.in'):
            continue
        case = filename[:-3]
        codefile = code_dir + '/' + code_filename
        infile = testdir + case + '.in'
        expfile = testdir + case + '.out'  # 拡張子をexpにしたいが。。

        # run program
        click.secho('-'*10 + case + '-'*10, fg='blue')
        if extension == "py":
            outs, errs, TLE_flag = _run_code(codefile, open(infile, "r"))

        elif extension == "cpp":
            try:
                subprocess.run(
                    ['g++', "-o", code_dir + '/a.out' , codefile],
                    stderr=subprocess.STDOUT,
                )
            except:
                print("compile error")
                return

            outs, errs, TLE_flag = _run_code(code_dir + '/a.out', open(infile, "r"))

        # print expected
        with open(expfile, 'r') as f:
            print('*'*7 + ' expected ' + '*'*7)
            exp = f.read()
            print(exp)
            exp = exp.split('\n')

        # print result
        print('*'*7 + ' result ' + '*'*7)
        print(outs)
        res = outs.split('\n')

        # print error message
        if errs != "":
            print("-"*35)
            print(errs)
            err = errs.split('\n')
        else:
            err = None

        # compare result and expected
        if err is not None:
            click.secho('RE\n\n', fg='red')
            continue

        if TLE_flag:
            click.secho('TLE\n\n', fg='red')
            continue

        if len(res) != len(exp):
            click.secho('WA\n\n', fg='red')
            continue
        else:
            for i in range(len(res)):
                if res[i] != exp[i]:
                    click.secho('WA\n\n', fg='red')
                    break
            else:
                click.secho('AC\n\n', fg='green')# }}}

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
    return outs.decode('utf-8'), errs.decode('utf-8'), TLE_flag# }}}
# }}}

# submit{{{
@cli.command()
@click.argument('code_filename', type=str)
@click.argument('task_url', type=str, default='')
@pass_config
def submit(config, code_filename, task_url):
    dir_path = _seach_par_dir(code_filename)
    code_full_path = dir_path + '/' + code_filename
    if task_url == '':
        task_url = _get_task_url(dir_path)
    with open(_pcm_root_dir() + '/contest_info', mode="r") as f:
        contest_url = f.readline()
    contest = Contest(contest_url)
    contest.submit(task_url, code_full_path)
#}}}

# private functions
def _seach_par_dir(code_filename):# {{{
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
    while True:
        if sum([1 if f == '.pcm' else 0 for f in os.listdir('./')]):
            return os.getcwd()
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

def _get_task_url(task_dir_path):# {{{
    with open(task_dir_path + "/.task_info", "r") as f:
        task_url = f.readline()
    return task_url# }}}

class Contest(object):
    def __init__(self, contest_url, work_dir="./"):# {{{
        self.url = contest_url
        self.type = self.__get_type()  # like atcoder, codeforce
        self.name = self.__get_name()
        self.task_list_url = self.__get_task_list_url()
        self.work_dir = os.path.abspath(work_dir + self.name)# }}}

    def prepare(self, force):# {{{
        try:
            os.makedirs(self.work_dir)
        except OSError:
            if force:
                shutil.rmtree(self.work_dir)
                os.makedirs(self.work_dir)
            else:
                print('The specified direcotry already exists.')
                return
        with open(self.work_dir + "/contest_info", mode="w") as f:
            f.write(self.url)

        self.__prepare_tasks()# }}}

    def submit(self, task_url, code_full_path):# {{{
        extension = code_full_path[code_full_path.rfind('.') + 1:]
        if "atcoder" in self.type:
            if extension == 'py':
                oj(['submit', task_url, code_full_path, '-l', '3510'])
                # oj submit https://agc023.contest.atcoder.jp/tasks/agc023_a A/A.py -l 3023
                    # 3023 python3
                    # 3510 pypy3
            elif extension == 'cpp':
                oj(['submit', task_url, code_full_path, '-l', '3003'])
                    # 3029 (C++ (GCC 5.4.1))
                    # 3030 (C++ (Clang 3.8.0))
                    # 3003 (C++14 (GCC 5.4.1))
                    # 3004 (C (Clang 3.8.0))
                    # 3005 (C++14 (Clang 3.8.0))}}}

    def get_answers(self, code_filename):# {{{
        pass# }}}

    def __get_type(self):# {{{
        if "beta.atcoder" in self.url:
            return "beta.atcoder"
        elif "atcoder" in self.url:
            return "atcoder"
        else:
            print("unkonw type of url passed. program will exit")
            sys.exit()# }}}

    def __get_name(self):# {{{
        """
        get contest_name from contest_url
        """
        if self.type == 'atcoder':
            return self.url[self.url.find('//')+2:self.url.find('.')]  # like arc071
        elif self.type == 'beta.atcoder':
            return self.url[self.url.find('contests')+9:self.url.find('tasks')-1]
        else:
            print("unkonw type of url passed. program will exit")
            sys.exit()# }}}

    def __get_task_list_url(self):# {{{
        """
        get task_list_url from contest_url
        """
        if self.type == 'atcoder':
            return self.url + "/assignments"
        elif self.type == 'beta.atcoder':
            return "https://" + self.name + ".contest.atcoder.jp/assignments"
        else:
            print("unkonw type of url passed. program will exit")
            sys.exit()# }}}

    def __get_submittion_url(self, code_filename):# {{{
        return# }}}

    def __get_problem_url(self, code_filename):# {{{
        return# }}}

    def __prepare_tasks(self):  # {{{
        if "atcoder" in self.type:
            base_url = self.task_list_url[:self.task_list_url.rfind("/")]
            task_urls = self.__get_list_of_task_urls()  # returned as relative paths
            config_dir = self.work_dir + '/' + '.pcm'
            os.makedirs(config_dir)
            for task_url, description in task_urls.items():
                task_dir = self.work_dir + '/' + description[0]
                os.makedirs(task_dir)
                os.chdir(task_dir)
                shutil.copy(script_path+'/template/solve.py', description[0] + '.py')
                shutil.copy(script_path+'/template/solve.cpp', description[0] + '.cpp')
                try:
                    oj(['download', base_url + task_url]) # get test cases
                    pathlib.Path(description[1].replace("/", "-")).touch()
                    with open(".task_info", "w") as f:
                        f.write(base_url + task_url)
                except:
                    print("faild preparing: " + base_url + task_url)
        else:
            print("unkonw type of url")
            sys.exit()
            # }}}

    def __get_list_of_task_urls(self):# {{{
        oj(['login', self.task_list_url])
        with oj_utils.with_cookiejar(oj_utils.new_default_session(), path=oj_utils.default_cookie_path) as session:
            task_page_html = oj_utils.request('GET', self.task_list_url, session, allow_redirects=True)
        task_page = BeautifulSoup(task_page_html.content, 'lxml')
        links = task_page.findAll('a')
        task_urls = []

        if "atcoder" in self.type:
            for l in links:
                if l.get_text() in ALPHABETS:
                    task_urls.append(l.get('href'))

            # get title
            tasks = {}
            for url in task_urls:
                for l in links:
                    if l.get('href') == url and l.get_text() in ALPHABETS:
                        alphabet = l.get_text()
                    elif (l.get('href') == url) and (not l.get_text() in ALPHABETS):
                        title = l.get_text()
                tasks[url] = (alphabet, title)

            return tasks
        else:
            print("unkonw type of url")
            print("There seems to be no problems. Check that the url is correct task list url")
            sys.exit()
# }}}
