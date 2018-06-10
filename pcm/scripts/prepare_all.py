from pcm.__main__ import prepare, sb, test, ga
import os
import subprocess

work_dir = "/home/koji0708/go/src/github.com/kjnh10/pcw/work/atcoder"

def get_all(type, start, end):
    for num in range(start, end):
        os.chdir(work_dir)
        snum = str(num).zfill(3)
        # prepare([f"https://{type}{snum}.contest.atcoder.jp"])  # sys.exit()の使用の影響でループが止まる。
        subprocess.run(
            ["pcm", "prepare", f"https://{type}{snum}.contest.atcoder.jp"],
            stderr=subprocess.STDOUT,
            check=True,
            )
        os.chdir(work_dir + f"/{type}{snum}")
        subprocess.run(
            ["pcm", "ga"],
            stderr=subprocess.STDOUT,
            check=True,
            )

if __name__ == '__main__':
    get_all('abc', 50, 52)
