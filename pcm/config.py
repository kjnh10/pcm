from typing import *


class Config(object):
    def __init__(self):
        self.verbose: bool = False
        self.pref: MutableMapping[str, Any]
        self.home_directory: Path
