import subprocess
import sys
try:
    import resource
except:
    pass
import psutil

# resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrssは最初に実行したプロセスの情報しかとれないようなので
# compileの子プロセスなども本体の方では走る可能性があるのでこちらで単独で実行する事でsolution codeのstaticを取得する。
# psutil for windows

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

try:
    rs = resource.getrusage(resource.RUSAGE_CHILDREN)
    used_memory = rs.ru_maxrss / (1<<10) # MB unit
except:
    used_memory = (after_used_memory - pre_used_memory) / (1<<20)
print(used_memory)
# print(rs.ru_utime)  # 大体本体の時間と一致するがとりあえずこちらは使用しない。
# print(rs.ru_stime)
