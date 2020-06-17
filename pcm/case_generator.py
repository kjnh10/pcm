from pathlib import Path
import sys
from importlib import import_module
import click
from .codefile import CodeFile

class CaseGenerateError(Exception):
    pass

class CaseGenerator(object):
    def __init__(self, codefile: CodeFile, config):
        self.codefile = codefile
        self.generator = None
        self.config = config
        if codefile.extension == 'py':
            sys.path.append(str(codefile.path.parent))
            store = sys.stdout
            sys.stdout = None  # importの際にold format(gen scriptがベタがき)形式だった場合の対応
            try:
                user_gen_script = import_module(codefile.path.stem)
            except Exception:
                sys.stdout = store
                return

            sys.stdout = store
            try:
                self.generator = user_gen_script.generator()
            except AttributeError:
                pass

    def generate_case(self, target: Path):
        if self.generator:
            with open(target, mode='w') as f:
                store = sys.stdout
                sys.stdout = f
                try:
                    self.generator.__next__()
                except StopIteration:
                    sys.stdout = store
                    raise StopIteration
                except Exception as e:
                    sys.stdout = store
                    print(e)
                    raise CaseGenerateError(f'failed running generator() of {self.codefile.path.name}')
                sys.stdout = store
        else:
            gen_result = self.codefile.run(self.config, outfile=target)
            if gen_result.returncode != 0:
                print(gen_result.stderr)
                raise CaseGenerateError(f'failed running generator file {self.codefile.path.name}')
