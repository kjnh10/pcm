import os
import fnmatch

# reserved = os.getcwd()
s_path = os.path.dirname(__file__)  # script path
testdir = s_path[:s_path.rfind("/")] + "/test/"
# os.chdir(testdir)

files = os.listdir(testdir)
for filename in files:
    filepath = os.path.join(testdir, filename)
    if fnmatch.fnmatch(filename, "testcase?*.txt"):
        with open(filepath, 'w'):
            pass  # clear file contents.
    else:
        # os.remove(filepath)
        pass
