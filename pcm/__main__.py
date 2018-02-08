import click
import os
import shutil
import pathlib
import requests
import fnmatch
import subprocess
from bs4 import BeautifulSoup
# from pcm.atcoder_tools.core.AtCoder import AtCoder
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


# subcommand sample{{{
@cli.command()
@click.option('--string', default='World',
              help='This is  the thing that is greeted.')
@click.option('--repeat', default=1,
              help='How many times you should be greeted.')
@click.argument('out', type=click.File('w'), default='-',
                required=False)
@pass_config
def sample(config, string, repeat, out):
    """This script greets you."""
    if config.verbose:
        click.echo('We are in verbose mode')
    click.echo('Home directory is %s' % config.home_directory)
    for x in range(repeat):
        click.echo('Hello %s!' % string, file=out)  # }}}


# init{{{
@cli.command()
@pass_config
def init(config):
    """This command will make current dir pcm work-space"""
    os.makedirs('./.pcm')
# }}}


# prepare{{{
@cli.command()
@click.argument('task_list_url', type=str)
@click.argument('contest_dir', type=str)
@click.option('--force/--no-force', default=False)
@pass_config
def prepare(config, task_list_url, contest_dir, force):
    try:
        os.makedirs(contest_dir)
    except OSError:
        if force:
            shutil.rmtree(contest_dir)
            os.makedirs(contest_dir)
        else:
            print('The specified direcotry already exists.')
            return

    os.chdir(contest_dir)
    root = os.getcwd()
    tasks = getAtcoderURL(task_list_url)
    base_url = 'https://beta.atcoder.jp'
    config_dir = root + '/' + '.pcm'
    os.makedirs(config_dir)
    for url, description in tasks.items():
        task_dir = root + '/' + description[0]
        os.makedirs(task_dir)
        os.chdir(task_dir)
        subprocess.call(['oj', 'download', base_url + url])  # get test cases
        shutil.copy(script_path+'/template.py', './' + description[0] + '.py')
        pathlib.Path(description[1]).touch()


def getAtcoderURL(task_list_url):
    task_page_html = requests.get(task_list_url)
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


# test{{{
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
                # subprocess.call(['oj', 'test', '-c', tmp])
                test_core(root, root + '/' + 'test/', filename)


def test_core(exedir, testdir, code):
    os.chdir(exedir)
    files = os.listdir(testdir)
    files.sort()
    for filename in files:
        if not fnmatch.fnmatch(filename, '*.in'):
            continue
        case = filename[:-3]
        # infile = testdir + case + '.in'
        resfile = testdir + case + '.res'
        expfile = testdir + case + '.out'
        click.secho('-'*10 + case + '-'*10, fg='blue')
        with open(resfile, 'w') as f:
            subprocess.call(' '.join([exedir + '/' + code,
                                      'pcm',  # tell pcm is calling
                                      '<',
                                      testdir + case + '.in'],
                                     ),
                            stdout=f,
                            stderr=subprocess.STDOUT, shell=True)
        with open(resfile, 'r') as f:
            res = f.read()
            print('*'*7 + ' output ' + '*'*7)
            print(res)
            res = res.split('\n')
        with open(expfile, 'r') as f:
            print('*'*7 + ' expected ' + '*'*7)
            exp = f.read()
            print(exp)
            exp = exp.split('\n')

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
# }}}
