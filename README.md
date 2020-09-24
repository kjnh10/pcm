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
pip install pcm

# if you want to develop
git clone https://github.com/kjnh10/pcm.git
cd pcm
pip install --editable ./
```

## Usage Sample

```bash
# prepare your work space. (only for Atcoder and codeforces)
pcm pp https://atcoder.jp/contests/abc001
# pcm pp http://codeforces.com/contest/1138
# By default, the work space is prepared at ~/procon-work/
# if you set [prepare.custom_hook_command], the command will be triggerd.
# you can shortcut for abc, arc, agc like below.
# pcm pp abc001
# to join a contest on realtime, you need to login 'oj login https://atcoder.jp' or 'oj login https://codeforces.com' beforehand.

# edir your A/solve.py or A/solve.cpp with your favorite editor

cd ~/procon-work/abc001/A # you need to be in ~/procon-work/abc001/A or ~/procon-work/abc001/A/codes to test and submit codes for problem A.

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

when you submit your code having #include <atcoder/...> but service and language is not for ac-library, your code will be expanded using expander.py from ac-library.

cd ../abc001/B  # continue to next problem..
.
.
.

```

you can also specify single problem with ppp command
```bash
pcm ppp https://atcoder.jp/contests/caddi2018/tasks/caddi2018_a -n A
```

or you can start browser integration mode. (using ![competitive-companion](https://github.com/jmerle/competitive-companion))
```bash
# you have to install node beforehand
cd <pcm installed dirctory>/pcm/pcm/cc_server
npm install
# you have to install competitive companion as a browser extension.

pcm ss  # start server for competitive companion
# when you click the competitive companion button, the work space will be created.
# internally, pcm ppp <problem-url> will be executed.
```

## Work dirctory structure

``` bash

tree  # at abc001/
├── abc001_1
│   ├── codes
│   │   ├── solve.cpp
│   │   └── solve.py
│   ├── test
│   │   ├── c1.in  # for custom test
│   │   ├── c1.out
│   │   ├── gen.py
│   │   ├── judge.cpp
│   │   ├── judge.py
│   │   ├── sample-1.in
│   │   ├── sample-1.out
│   │   ├── sample-2.in
│   │   ├── sample-2.out
│   │   ├── sample-3.in
│   │   └── sample-3.out
│   └── 積雪深差
├── abc001_2
│   ├── codes
│   │   ├── solve.cpp
│   │   └── solve.py
│   ├── test
│   │   ├── c1.in
│   │   ├── c1.out
│   │   ├── gen.py
│   │   ├── judge.cpp
│   │   ├── judge.py
│   │   ├── sample-1.in
│   │   ├── sample-1.out
│   │   ├── sample-2.in
│   │   ├── sample-2.out
│   │   ├── sample-3.in
│   │   └── sample-3.out
│   └── 視程の通報
├── abc001_3
├     ....
└── abc001_4
```

'codes' direcotry is copied from `pcm/pcm/template/codes`.  
if you want to customize template, you can put your template in `~/.config/pcm/template/codes`.  
if `~/.config/pcm/template/codes` exists, 'codes' will be copied from this directory.  
Or you can also specify any direcotry you like as you will see below.  

## Customization

you can customeize your setting by putting `~/.config/pcm/config.toml`.
you can refer the default setting file which is in '{your-pcm-installed-path}/pcm/config.toml'

```toml
template_dir = '~/.config/pcm/template'  # if this directory does not exist or not specified, default template directory will be used
contest_root_dir = '~/procon-work/{service_name}'
# contest_root_dir = '.'
problem_root_dir = '~/procon-work/{service_name}/{contest_id}'
# problem_root_dir = '.'

[prepare]
  [prepare.custom_hook_command]
  # after = 'nvim {dirname} -c "args **/solve.cpp" -c "tab all" -c ""'

[ppp]
  [ppp.custom_hook_command]
  # after = 'code "{dirname}" -g {dirname}/codes/solve.cpp:6 {dirname}/test/gen.py -r'
  # after = 'nvim {dirname} -c "args **/solve.cpp" -c "tab all" -c ""'

[submit]
  [submit.default_lang.AtCoder]
  cpp = 'gcc_acl'
  py = 'pypy'

  [submit.default_lang.Codeforces]
  cpp = 'gcc'
  py = 'pypy'

  [submit.default_lang.yukicoder]
  cpp = 'cpp17'
  py  = 'pypy3'


  [submit.language.AtCoder]
  gcc = '4003'       # C++17 (GCC 9.2.1)
  gcc_acl = '4101'   # GCC 9.2.1 with AC Library v1.1
  clang = '4004'     # C++17 (Glang 10.0.0)
  clang_acl = '4102' # Clang 10.0.0 with AC Library v1.1
  py = '4006'        # python 3.8.2
  pypy = '4047'      # pypy3

  [submit.language.Codeforces]
  gcc = '54'         # GNU G++17 7.3.0
  clang = '52'       # Clang++17 Diagnostics
  py = '31'
  py3 = '31'
  pypy = '41'

[test]
  timeout_sec=2
  max_memory=256
  limit_height_max_output=200
  limit_width_max_output=45

  [test.compile_command]
  configname = 'standard_17'  # specify the profile used by default for tt and sb

  [test.compile_command.cpp]  # for tt command, you can change the compile command by --cc option. like 'pcm tt -c 1 --cc v5'
  standard_17 = """g++ {srcpath} -o {outpath} \
               -std=c++17 \
               -I {pcm_dir_path}/lang_library/cplusplus/ac-library \
               -Wall -D_GLIBCXX_DEBUG -fuse-ld=gold
            """

  debug = """g++ {srcpath} -o {outpath} \
            -std=c++17 \
            -DPCM -Wall -fsanitize=address -fsanitize=undefined -D_GLIBCXX_DEBUG -fuse-ld=gold \
            -I {pcm_dir_path}/lang_library/cplusplus/ac-library \
            -g
            """

  clang = """clang++ {srcpath} -o {outpath} \
          -std=c++17 \
          -I {pcm_dir_path}/lang_library/cplusplus/ac-library \
          -DPCM -Wall -D_GLIBCXX_DEBUG -fuse-ld=lld
          """

  atcoder = """g++-9 {srcpath} -o {outpath} \
                 -std=gnu++17 -Wall -Wextra -O2 -march=native -mtune=native -DEVAL\
                 -I/opt/boost/gcc/include -L/opt/boost/gcc/lib \
                 -I {pcm_dir_path}/lang_library/cplusplus/ac-library \
            """

  simple = "g++ {srcpath} -o {outpath} -std=c++14"
```

## Contribution
Feel free to send pull requests or raise issues.

## Licence
MIT License
