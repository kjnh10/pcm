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


@cli.command()
@pass_config
def init(config):
    """This command will make current dir pcm work-space"""
    os.makedirs('./.pcm')


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


@cli.command()
@click.argument('filename', type=str)
@pass_config
def test(config, filename):
    while True:
        if sum([1 if f == '.pcm' else 0 for f in os.listdir('./')]):
            contest_dir = os.getcwd()
            break
        else:
            try:
                os.chdir('../')
                if os.getcwd() == '/':
                    print("it seems you aren't in directory maintained by pcm")
                    return
            except:
                print("it seems you aren't in directory maintained by pcm")
                return
    for root, dirs, files in os.walk(contest_dir):
        for f in files:
            if f == filename:
                os.chdir(root)
                test_core(root, filename, root + '/' + 'test/')
                return
    else:
        print("not found: " + filename + " in " + contest_dir)
def test_core(code_dir, code_filename, testdir):
    os.chdir(code_dir)
    files = os.listdir(testdir)
    files.sort()
    extension = code_filename[code_filename.rfind('.') + 1:]
    for filename in files:
        if not fnmatch.fnmatch(filename, '*.in'):
            continue
        case = filename[:-3]
        codefile = code_dir + '/' + code_filename
        infile = testdir + case + '.in'
        resfile = testdir + case + '.res'
        expfile = testdir + case + '.out'
        click.secho('-'*10 + case + '-'*10, fg='blue')

        # run program and write to resfile
        with open(resfile, 'w') as resf:
            if extension == "py":
                subprocess.run(
                    [
                        codefile,
                        "pcm"  # tell pcm is calling
                    ],
                    stdin=open(infile, "r"),
                    stdout=resf,
                    stderr=subprocess.STDOUT
                )
            elif extension == "cpp":
                try:
                    subprocess.run(['g++', "-o", code_dir + '/a.out' , codefile], stderr=subprocess.STDOUT)
                except:
                    "compile error"
                    return
                else:
                    subprocess.run(
                        [
                            code_dir + '/a.out',
                            'pcm',  # tell pcm is calling
                        ],
                        stdin=open(infile, "r"),
                        stdout=resf,
                        stderr=subprocess.STDOUT
                    )

        # print expected
        with open(expfile, 'r') as f:
            print('*'*7 + ' expected ' + '*'*7)
            exp = f.read()
            print(exp)
            exp = exp.split('\n')

        # print result
        with open(resfile, 'r') as resf:
            res = resf.read()
            print('*'*7 + ' output ' + '*'*7)
            print(res)
            res = res.split('\n')

        # compare result and expected
        if len(res) != len(exp):
            click.secho('result:WA\n\n', fg='red')
            continue
        else:
            for i in range(len(res)):
                if res[i] != exp[i]:
                    click.secho('result:WA\n\n', fg='red')
                    break
            else:
                click.secho('result:AC\n\n', fg='green')
