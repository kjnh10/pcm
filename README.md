[![PyPI](https://img.shields.io/pypi/pyversions/pcm.svg)](#)
[![PyPI](https://img.shields.io/pypi/status/pcm.svg)](#)
[![PyPI](https://img.shields.io/pypi/v/pcm)](https://pypi.org/project/pcm/)
[![PyPI](https://img.shields.io/pypi/l/pcm.svg)](#)

## Overview

This is a command line tool to manage programming contest and provides some commands like below.

* prepare your work directory for a contest. of course downloading samples. (only for AtCoder and codeforces for now)
* prepare your work directory for a problem. of course downloading samples. (for any contest kmyk/online-judge-tools works for)
* test your code with sample case.
* test your code with randomly genarated cases.
* submit your code to the contest site. (only for AtCoder and codeforces for now)

You can use this library with any language, but for languages other than .py and .cpp extension file, you need to add some settings to **~/.config/pcm/config.toml**

This is just my own wrapper of [kmyk/online-judge-tools](https://github.com/kmyk/online-judge-tools).  

## Demo
![screencast](https://github.com/kjnh10/pcm/blob/sample-gif-test/demo.gif)

## Installation
You need python 3.6 later (tested for Linux and Windows.)

```bash
pip install pcm # That's it.Done.

# if you want to develop
git clone https://github.com/kjnh10/pcm.git
cd pcm
pip install --editable ./
```

## Usage Sample

```bash
cd your/workdirectory

# prepare your work space. (only for Atcoder and codeforces)
pcm pp https://atcoder.jp/contests/abc001
# pcm pp http://codeforces.com/contest/1138
# you can shortcut for abc, arc, agc like below.
# pcm pp abc001
# to join a contest on realtime, you need to login 'oj login https://atcoder.jp' or 'oj login https://codeforces.com' beforehand.

# edir your A/solve.py or A/solve.cpp with your favorite editor

cd abc001/A # you need to be in abc001/A or abc001/A/codes to test and submit codes for problem A.

# test your code with downloaded cases and handmade cases.
pcm tt <filename>          # test filename for all sample cases. <filename> (like solve.cpp) will be searched under current directory recursively.
# pcm tt                   # you can omit <filename>. last updated file within *.cpp and *.py files under current directory recursively will be selected.
# pcm tt --case sample-1   # test #1 case
# pcm tt -c sample-1       # shortcut version
# pcm tt -c 1              # shorter version
# pcm tt -t 3              # you can set TLE time limit. in this sample to 3 second. (default is 2 second.)
# pcm tt -c 1 -t 3         # of course, you can specify multiple options. this is same for other commands.
# pcm tt -lh 200 -lw 100   # you can change output size.

# test your code with randomly genarated cases. (checking your code in contest with your naive code, finding errors after contest with a AC code, and even Hacks)
# at first you need to write test/gen.py.
pcm tt -c gen.py                       # gen.py will make random.in and naive.cpp or naive.py will make random.out with random.in. then test.
pcm tt -c gen.py --by naive.cpp        # you can use naive code file for generating expected file with --by option.
pcm tt -c gen.py --by naive.cpp --loop # you can continue random test until find a failed test case.
pcm tt -c gen.py --loop                # you can continue random test until find a failed test case without comparing with naive code. this will stop only when RE, TLE
pcm tt -c gen.py -b naive.cpp -l       # you can shortcut

# submit your code
pcm sb solve.py  # submit your code after testing. you can't submit if tests fail.
# pcm sb         # you can omit filename, then pcm will submit the file you edited last.
# pcm sb -nt     # wihtout test.
# pcm sb -l py3  # you can specify language. see /pcm/config.toml for other language you can use.

cd ../abc001/B  # continue to next problem..
.
.
.

```

you can also specify single problem with ppp command
```bash
pcm ppp https://atcoder.jp/contests/caddi2018/tasks/caddi2018_a -n A
```

or you can start browser integration mode. (using ![competitive-companion](https://github.com/jmerle/competitive-companion)
```bash
# you have to install node beforehand
# you have to install competitive companion as a browser extension.
pcm ss  # start server for competitive companion
# when you click the competitive companion button, the work space will be created.
# internally, pcm ppp <problem-url> will be executed.
```

## Work dirctory structure

``` bash

tree  # at abc001/
.
├── A
│   ├── bin
│   ├── codes
│   │   ├── lib
│   │   │   ├── dump.hpp
│   │   │   └── prettyprint.hpp
│   │   ├── naive.cpp
│   │   ├── naive.py
│   │   ├── solve.cpp
│   │   └── solve.py
│   ├── test
│   │   ├── gen.py
│   │   ├── sample-1.in
│   │   ├── sample-1.out
│   │   ├── sample-2.in
│   │   ├── sample-2.out
│   │   ├── sample-3.in
│   │   └── sample-3.out
│   └── 積雪深差
├── B
│   ├── bin
│   ├── codes
│   │   ├── lib
│   │   │   ├── dump.hpp
│   │   │   └── prettyprint.hpp
│   │   ├── naive.cpp
│   │   ├── naive.py
│   │   ├── solve.cpp
│   │   └── solve.py
│   ├── test
│   │   ├── gen.py
│   │   ├── sample-1.in
│   │   ├── sample-1.out
│   │   ├── sample-2.in
│   │   ├── sample-2.out
│   │   ├── sample-3.in
│   │   └── sample-3.out
│   └── 視程の通報
├── C
├     ....
└── D
```

'codes' direcotry is copied from `pcm/pcm/template/codes`.  
if you want to customize template, you can put your template in `~/.config/pcm/template/codes`.  
if `~/.config/pcm/template/codes` exists, 'codes' will be copied from this directory.  
Or you can also specify any direcotry you like as you will see below.  

## Customization

you can customeize your setting by putting `~/.config/pcm/config.toml`.

```toml
template_dir = '~/.config/pcm/template'  # if this directory does not exist or not specified, default template directory will be used

contest_root_dir = '~/Desktop/procon-work/{service_name}'  # root dir for pcm pp
# contest_root_dir = '.'
problem_root_dir = '~/Desktop/procon-work/{service_name}/{contest_id}'  # root dir for pcm ppp
# problem_root_dir = '.'

[prepare]
  [prepare.custom_hook_command]
  # after = 'nvim {dirname} -c "args **/solve.cpp" -c "tab all" -c ""'

[ppp]
  [ppp.custom_hook_command]
  after = 'code "{dirname}" -g {dirname}/codes/solve.cpp:6 {dirname}/test/gen.py -r'  # open working direcotry by vscode after ppp
  # after = 'nvim {dirname} -c "args **/solve.cpp" -c "tab all" -c ""'

[submit]
  [submit.default_lang.AtCoder]
  cpp = '3003' # C++14 (GCC 5.4.1)
  py = '3510'  # pypy

  [submit.default_lang.Codeforces]
  cpp = '50'  # GNU G++14 6.4.0
  py = '41'   # pypy if you prefer python3, use '31'

  [submit.language.AtCoder]
  gcc = '3003'
  clang = '3004'
  py = '3023'
  py3 = '3023'
  pypy = '3510'

  [submit.language.Codeforces]
  gcc = '50'
  clang = '52'
  py = '31'
  py3 = '31'
  pypy = '41'

[test]
  timeout_sec=2
  max_memory=256

  [test.compile_command]
  configname = 'standard_14'  # specify the profile used by default for tt and sb

  [test.compile_command.cpp]  # for tt command, you can change the compile command by --cc option. like 'pcm tt -c 1 --cc v5'
  standard_14 = """g++-9 {srcpath} -o {outpath} \
               -std=c++14 \
               -include bits/stdc++.h \
               -DPCM -Wall -fsanitize=address -fsanitize=undefined -D_GLIBCXX_DEBUG -fuse-ld=gold
            """

  debug = """g++ {srcpath} -o {outpath} \
            -std=c++14 \
             -include bits/stdc++.h \
            -DPCM -Wall -fsanitize=address -fsanitize=undefined -D_GLIBCXX_DEBUG -fuse-ld=gold \
            -g
            """

  v5 = """g++ {srcpath} -o {outpath} \
          -std=c++14 \
          -include bits/stdc++.h \
          -DPCM -Wall -fsanitize=address -fsanitize=undefined -D_GLIBCXX_DEBUG
          """

  fast = """g++ {srcpath} -o {outpath} \
          -std=c++14 \
          -include bits/stdc++.h \
          """

  clang = """clang++ {srcpath} -o {outpath} \
          -stdlib=libc++ \
          -DPCM -Wall
          """
```

## Contribution
Feel free to send pull requests or raise issues.

## Licence
MIT License
