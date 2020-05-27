import subprocess
import sys
import os
import psutil

# windowsではresource moduleが使用出来ないのでpsutil moduleを使用する。
raise Exception("Not implemented yet")


command = sys.argv[1]
command = ['python', command] if '.py' in command else command

pre_used_memory = psutil.Process().memory_info().peak_wset / (1<<20)

subprocess.run(
        command,
        stdin = open(sys.argv[2], 'r') if sys.argv[2]!='None' else None,
        stdout = subprocess.DEVNULL,
        stderr = subprocess.DEVNULL,
        )

after_used_memory = psutil.Process().memory_info().peak_wset

used_memory = (after_used_memory - pre_used_memory) / (1<<20)
print(used_memory)
