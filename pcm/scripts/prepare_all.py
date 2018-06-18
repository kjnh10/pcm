from pcm.__main__ import pp, sb, tt, ga
import os
import subprocess

# work_dir = "/Users/koji0708/go/src/github.com/kjnh10/pcw/work/atcoder"
work_dir = "/home/koji0708/go/src/github.com/kjnh10/pcw/work/atcoder"

def get_all(type, start, end):
    for num in range(start, end):
        os.chdir(work_dir)
        snum = str(num).zfill(3)
        print(f"start {snum}")

        if os.path.exists(work_dir + f"/{type}{snum}"):
        #     print("skip")
        #     continue
        #
        # subprocess.run(
        #     ["pcm", "prepare", f"https://{type}{snum}.contest.atcoder.jp"],
        #     stderr=subprocess.STDOUT,
        #     check=True,
        #     )
        # # prepare([f"https://{type}{snum}.contest.atcoder.jp"])  # sys.exit()の使用の影響でループが止まる。

            os.chdir(work_dir + f"/{type}{snum}")
            subprocess.run(
                ["pcm", "ga"],
                stderr=subprocess.STDOUT,
                check=True,
                )
    print("finish")

if __name__ == '__main__':
    get_all('abc', 88, 100)
    get_all('arc', 1, 99)
