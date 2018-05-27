import click
import os
import shutil
import pathlib
import fnmatch
import subprocess
from bs4 import BeautifulSoup
# from pcm.atcoder_tools.core.AtCoder import AtCoder
from onlinejudge.implementation.main import main as oj
import onlinejudge.implementation.utils as oj_utils

ALPHABETS = {chr(i) for i in range(65, 65+26)}
script_path = os.path.abspath(os.path.dirname(__file__))  # script path
class Config(object):
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


# sample
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
        click.echo('Hello %s!' % string, file=out)


# init
@cli.command()
@pass_config
def init(config):
    """This command will make current dir pcm work-space"""
    os.makedirs('./.pcm')


# prepare
@cli.command()
@click.argument('task_list_url', type=str, default='')
@click.argument('contest_dir', type=str, default='')
@click.option('--force/--no-force', default=False)
@pass_config
def prepare(config, task_list_url, contest_dir, force):
    if task_list_url == '':
        _prepare_template()
        return

    if contest_dir == '':
        contest_dir = task_list_url[task_list_url.find('//')+2:task_list_url.find('.')]

    try:
        os.makedirs(contest_dir)
    except OSError:
        if force:
            shutil.rmtree(contest_dir)
            os.makedirs(contest_dir)
        else:
            print('The specified direcotry already exists.')
            return

    _getAtcoderTask(task_list_url, contest_dir)
def _prepare_template():
    shutil.copytree(script_path+'/template/', './tmp/prob1/')
    shutil.copytree(script_path+'/template/', './tmp/prob2/')
    os.makedirs('./tmp/.pcm')

def _getAtcoderTask(task_list_url, contest_dir):
    atcoder_base_url = task_list_url[:task_list_url.rfind("/")]
    os.chdir(contest_dir)
    root = os.getcwd()
    tasks = _getAtcoderTasksURL(task_list_url)
    if tasks == {}:
        print("There seems to be no problems. Check that the url is correct task list url")
        return

    config_dir = root + '/' + '.pcm'
    os.makedirs(config_dir)
    for task_url, description in tasks.items():
        task_dir = root + '/' + description[0]
        os.makedirs(task_dir)
        os.chdir(task_dir)
        shutil.copy(script_path+'/template/solve.py', './' + description[0] + '.py')
        shutil.copy(script_path+'/template/solve.cpp', './' + description[0] + '.cpp')
        try:
            oj(['download', atcoder_base_url + task_url]) # get test cases
            pathlib.Path(description[1].replace("/", "-")).touch()
            with open("./.task_info", "w") as f:
                f.write(atcoder_base_url + task_url)
        except:
            pass
def _getAtcoderTasksURL(task_list_url):
    oj(['login', task_list_url])
    with oj_utils.with_cookiejar(oj_utils.new_default_session(), path=oj_utils.default_cookie_path) as session:
        task_page_html = oj_utils.request('GET', task_list_url, session, allow_redirects=True)
    task_page = BeautifulSoup(task_page_html.content, 'lxml')
    links = task_page.findAll('a')
    task_urls = []
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

    return tasks  # }}}


# test
@cli.command()
@click.argument('code_filename', type=str)
@pass_config
def test(config, code_filename):
    code_dir = _seach_par_dir(code_filename)
    if code_dir is None:
        return
    test_core(code_dir, code_filename, code_dir + '/' + 'test/')
def test_core(code_dir, code_filename, testdir):
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
                click.secho('AC\n\n', fg='green')
def _run_code(code_filename, input_file):
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
    return outs.decode('utf-8'), errs.decode('utf-8'), TLE_flag


# submit
@cli.command()
@click.argument('code_filename', type=str)
@click.argument('task_url', type=str, default='')
@pass_config
def submit(config, code_filename, task_url):
    dir_path = _seach_par_dir(code_filename)
    extension = code_filename[code_filename.rfind('.') + 1:]
    if dir_path is None:
        return

    if task_url == '':
        task_url = _get_task_url(dir_path)

    if extension == 'py':
        oj(['submit', task_url, dir_path + '/' + code_filename, '-l', '3023'])
        # oj submit https://agc023.contest.atcoder.jp/tasks/agc023_a A/A.py -l 3023
            # 3023 python3
            # 3510 pypy3
            # 3029 (C++ (GCC 5.4.1))
            # 3030 (C++ (Clang 3.8.0))
            # 3003 (C++14 (GCC 5.4.1))
            # 3004 (C (Clang 3.8.0))
            # 3005 (C++14 (Clang 3.8.0))


# private functions
def _seach_par_dir(code_filename):
    contest_dir = _pcm_root_dir()
    if contest_dir is None:
        return None

    for base_dir, _sub_dirs, files in os.walk(contest_dir):
        for f in files:
            if f == code_filename:
                return base_dir
    else:
        print("not found: " + code_filename + " in " + contest_dir)
        return None
def _pcm_root_dir():
    while True:
        if sum([1 if f == '.pcm' else 0 for f in os.listdir('./')]):
            return os.getcwd()
        else:
            if os.getcwd() == "/":
                print("it seems you aren't in directory maintained by pcm")
                return None
            try:
                os.chdir('../')
            except:
                print("it seems you aren't in directory maintained by pcm")
                return None
def _get_task_url(task_dir_path):
    with open(task_dir_path + "/.task_info", "r") as f:
        task_url = f.readline()
    return task_url


class Contest():
    def __init__(self, contest_url):
        self.name = ""
        self.task_list_url = ""
        self.task_list_url = ""

    def get_submittion_url(self, code_filename):
        return

    def get_problem_url(self, code_filename):
        return

