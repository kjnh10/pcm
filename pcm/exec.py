import subprocess
import sys
import resource
# resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrssは最初に実行したプロセスの情報しかとれないようなので
# compileの子プロセスなども本体の方では走る可能性があるのでこちらで単独で実行する事でsolution codeのstaticを取得する。

command = sys.argv[1]
command_list = ['python', command] if '.py' in command else [command]

subprocess.run(
        command_list,
        stdin = open(sys.argv[2], 'r') if sys.argv[2]!='None' else None,
        stdout = subprocess.DEVNULL,
        stderr = subprocess.DEVNULL,
        )

rs = resource.getrusage(resource.RUSAGE_CHILDREN)
used_memory = rs.ru_maxrss / (1<<10) # MB unit
print(used_memory)

# print(rs.ru_utime)  # 大体本体の時間と一致するがとりあえずこちらは使用しない。
# print(rs.ru_stime)
