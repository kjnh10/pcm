## Overview

This is a command line tool to manage programming contest and provides some commands like below.

* prepare your work directory for a contest. of course downloading samples.
* test your code with sample case.
* submit yourcode to the contest site. (only for AtCoder and codeforces for now)

Actually, this is just a my own wrapper of kmyk/online-judge-tools.  


## Installation

```bash
cd <anywhere you like>
git clone https://github.com/kjnh10/pcm.git
cd pcm
pip install ./
# pip install --editable ./ # if you want to customize, use this one.
```

Though mainly tested for ubuntu or mac, this will also work for windows.

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

# test your code
pcm tt  # for all sample cases
pcm tt -c 1  # to test #1 case
pcm tt -t 3  # set TLE time to 3 sec. (The default is 2 sec.)

# submit your code
pcm sb  # with test before submitting. you can't submit if tests fail.
pcm sb -nt  # wihtout test.


cd ../abc001/B
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
│   ├── codes
│   │   ├── a.out
│   │   ├── cxx-prettyprint
│   │   │   └── prettyprint.hpp
│   │   ├── dump.hpp
│   │   ├── solve.cpp
│   │   └── solve.py
│   ├── test
│   │   ├── sample-1.in
│   │   ├── sample-1.out
│   │   ├── sample-2.in
│   │   ├── sample-2.out
│   │   ├── sample-3.in
│   │   └── sample-3.out
│   └── 積雪深差
├── B
│   ├── codes
│   │   ├── a.out
│   │   ├── cxx-prettyprint
│   │   │   └── prettyprint.hpp
│   │   ├── dump.hpp
│   │   ├── solve.cpp
│   │   └── solve.py
│   ├── test
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
├     ....
```

'codes' direcotry is copied from `pcm/pcm/template/codes`.  
if you want to customize template, you can put your template in `~/.config/pcm/template/codes`.  
if `~/.config/pcm/template/codes` exists, 'codes' will be copied from this directory.  
Or you can also specify any direcotry you like as you will see below.  

## Customization

you can customeize your setting by putting `~/.config/pcm/config.toml`.

``` toml
template_dir = '~/.config/pcm/template'  # you may copy sample template from pcm/pcm/template_sample at first.

[submit]
  [submit.language.atcoder]
  cpp = '3003' # C++14 (GCC 5.4.1)
  py = '3510'  # pypy

  [submit.language.codeforces]
  cpp = '50'  # GNU G++14 6.4.0
  py = '41'   # pypy if you prefer python3, use '31'

[test]
  timeout_sec=2
```

## Contribution
Feel free to send pull requests or raise issues.

## Licence
MIT License
