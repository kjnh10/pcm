from pathlib import Path
from .utils import get_last_modified_file
import onlinejudge.dispatch
import onlinejudge._implementation.utils as oj_utils
import click
import pickle


class CodeFile(object):
    def __init__(self, match_filename_pattern=['*.cpp', '*.py'], exclude_filename_pattern=[], search_root: Path = Path('.')):
        if (match_filename_pattern==''):
            match_filename_pattern = ['*.cpp', '*.py']
        self.path = get_last_modified_file(match_filename_pattern, exclude_filename_pattern, search_root)
        self.code_dir = self.path.parent

        if (self.code_dir/'test').exists():  # online-judge-tools style
            self.prob_dir = self.code_dir
            self.test_dir = self.code_dir / 'test'
            self.bin_dir = self.code_dir / 'bin'
        else:                                # default template style
            self.prob_dir = self.code_dir.parent
            self.test_dir = self.prob_dir / 'test'
            self.bin_dir = self.prob_dir / 'bin'

        self.task_alphabet = self.prob_dir.name
        self.extension = self.path.suffix[1:]  # like 'py', 'cpp'....
        self.oj_problem_class = None
        try:
            with open(self.prob_dir/'.problem_info.pickle', mode='rb') as f:
                self.oj_problem_class = pickle.load(f)
        except Exception as e:
            print('failed to load problem_info.pickle')


    def submit(self, config, language):
        with open(self.path, "r") as f:
            code_string = f.read()

        contest_site = self.oj_problem_class.get_service().get_name()

        if language == 'auto-detect':
            try:
                lang_id = config.pref['submit']['default_lang'][contest_site][self.extension]
            except KeyError as e:
                click.secho(f'{self.extension} not found in possible self.extensions. if you want to add {self.extension}, you can add it in ~/.config/pcm/config.toml', fg='red')
                print('current possible self.extensions')
                print(config.pref['submit']['default_lang'][contest_site])
                return
        else:
            try:
                lang_id = config.pref['submit']['language'][contest_site][language]
            except KeyError as e:
                click.secho(f'{language} not found in possible language. if you want to add {language}, you can add it in ~/.config/pcm/config.toml', fg='red')
                print('current possible language')
                print(config.pref['submit']['language'][contest_site])
                return

        with oj_utils.with_cookiejar(oj_utils.get_default_session()) as session:
            res = self.oj_problem_class.submit_code(code_string, language_id=lang_id, session=session)
            print(res)


class RunResult(object):
    def __init__(self):
        self.returncode = None
        self.stdout = ""
        self.stderr = ""
        self.TLE_flag = None
        self.exec_time = -1
        self.used_memory = -1
        self.judge = "yet"  # set by 'pcm tt'
