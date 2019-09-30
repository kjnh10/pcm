[!(https://img.shields.io/pypi/v/pcm)](https://pypi.org/project/pcm/)

## Overview

This is a command line tool to manage programming contest and provides some commands like below.

* prepare your work directory for a contest. of course downloading samples. (only for AtCoder and codeforces for now)
* prepare your work directory for a problem. of course downloading samples. (for any contest kmyk/online-judge-tools works for)
* test your code with sample case.
* test your code with randomly genarated cases.
* submit yourcode to the contest site. (only for AtCoder and codeforces for now)

This is just my own wrapper of [kmyk/online-judge-tools](https://github.com/kmyk/online-judge-tools).  

## Demo
![screencast](https://github.com/kjnh10/pcm/blob/sample-gif-test/demo.gif)

## Installation
You need python3. (tested for Linux and Windows.)

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

# Edir your A/solve.py or A/solve.cpp with your favorite editor

cd abc001/A # you need in abc001/A direcotry to test and submit codes for problem A.

# test your code with downloaded cases and handmade cases.
pcm tt  # for all sample cases
pcm tt -c 1  # to test #1 case
pcm tt -t 3  # set TLE time to 3 sec. (The default is 2 sec.)
pcm tt -c 1 -t 3 # of course, you can specify multiple options.

# test your code with randomly genarated cases. (checking your code in contest with your naive code, finding errors after contest with a AC code, hacks)
# At first you need to write test/gen.py
# If you write naive.cpp or naive.py, exp file will be automatically genarated
pcm tt -c gen.py  # gen.py will make random.in and naive.cpp or naive.py will make random.out with random.in. then test.
pcm tt -c gen.py --by naive2.cpp  # also you can specify naive code file for generating expected with --by option. this is same for rt command below.
pcm rt  # cotinue genarating a case and compare you code result and naive code result until they are different.
pcm rt -nc # --nocompare option: cotinue genarating a case without executing naive code and comparing. This is for testing large case (which is TLE for naive code) in terms of TLE, overflow and so on.

# submit your code
pcm sb solve.py  # with test before submitting. you can't submit if tests fail.
# pcm sb  # you can omit filename, then pcm will submit the file you edited last.
# pcm sb -nt  # wihtout test.
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

``` toml
template_dir = '~/.config/pcm/template'

[submit]
  [submit.default_lang.atcoder]
  cpp = '3003' # C++14 (GCC 5.4.1)
  py = '3510'  # pypy

  [submit.default_lang.codeforces]
  cpp = '50'  # GNU G++14 6.4.0
  py = '41'   # pypy if you prefer python3, use '31'

  [submit.language.atcoder]  # you can use this keys like 'pcm sb -l pypy'
  gcc = '3003'
  clang = '3004'
  py = '3023'
  py3 = '3023'
  pypy = '3510'

  [submit.language.codeforces]
  py = '31'
  py3 = '31'
  pypy = '41'
  gcc = '50'
  clang = '52'

[test]
  timeout_sec=2
```

## Contribution
Feel free to send pull requests or raise issues.

## Licence
MIT License
