from pathlib import Path
from .utils import get_last_modified_file

class CodeFile(type(Path())):
    def __init__(self, match_filename_pattern=['*.cpp', '*.py'], exclude_filename_pattern=[]):
        if (match_filename_pattern==''):
            match_filename_pattern = ['*.cpp', '*.py']
        self.path = get_last_modified_file(match_filename_pattern, exclude_filename_pattern)
        self.code_dir = self.path.parent
        self.prob_dir = self.code_dir.parent
        self.test_dir = self.prob_dir / 'test'
        self.bin_dir = self.prob_dir / 'bin'
        self.task_alphabet = self.prob_dir.name


class RunResult(object):
    def __init__(self):
        self.returncode = None
        self.stdout = ""
        self.stderr = ""
        self.TLE_flag = None
        self.exec_time = -1
