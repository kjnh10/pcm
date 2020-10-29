import os
import shutil
import subprocess

from pcm.__main__ import ga, pp, ppp, sb, tt

# work_dir = "/Users/koji0708/go/src/github.com/kjnh10/pcw/work/atcoder"
# work_dir = "/home/koji0708/go/src/github.com/kjnh10/pcw/work/atcoder"
# work_dir = "/home/vagrant/go/src/github.com/kjnh10/pcw/work/atcoder"
work_dir = "/home/koji0708/Dropbox/01_projects/2018/pcw/work/atcoder/agc"


def get_all(type, start, end):
    for num in range(start, end):
        os.chdir(work_dir)
        snum = str(num).zfill(3)
        print(f"start {snum}")

        if os.path.exists(work_dir + f"/{type}{snum}"):
            # print("skip")
            # continue

            print("deleted")
            shutil.rmtree(work_dir + f"/{type}{snum}")

        subprocess.run(
            ["pcm", "pp", f"https://{type}{snum}.contest.atcoder.jp"],
            stderr=subprocess.STDOUT,
            check=True,
        )
        # prepare([f"https://{type}{snum}.contest.atcoder.jp"])  # sys.exit()の使用の影響でループが止まる。

        os.chdir(work_dir + f"/{type}{snum}")
        try:
            subprocess.run(
                ["pcm", "ga"],
                stderr=subprocess.STDOUT,
                check=True,
            )
        except:
            print("getting answers failed")
    print("finish")


if __name__ == '__main__':
    # get_all('abc', 14, 42)
    # get_all('arc', 1, 99)
    get_all('agc', 1, 27)
