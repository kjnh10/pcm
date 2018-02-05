import click
import os
import shutil
import pathlib
import requests
import subprocess
from bs4 import BeautifulSoup
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
@pass_config
def test(config):
    pass
