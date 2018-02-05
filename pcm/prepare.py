#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import pathlib
import requests
import subprocess
from bs4 import BeautifulSoup

ALPHABETS = {chr(i) for i in range(65, 65+26)}
script_path = os.path.abspath(os.path.dirname(__file__))  # script path

force = True
task_list_url = 'https://beta.atcoder.jp/contests/abc001/tasks'
con_dir = 'abc001'


def main():
    # args = sys.argv
    # task_list_url = sys.argv[1]
    # if len(args) >= 3:
    #     con_dir = sys.argv[2]
    # else:
    #     con_dir = './contest'

    try:
        os.makedirs(con_dir)
    except OSError:
        if force:
            shutil.rmtree(con_dir)
            os.makedirs(con_dir)
        else:
            print('The specified direcotry already exists.')
            return
    
    os.chdir(con_dir)
    root = os.getcwd()
    tasks = getAtcoderURL(task_list_url)
    base_url = 'https://beta.atcoder.jp'
    for url, description in tasks.items():
        print(url, description)
        task_dir = root + '/' + description[0]
        os.makedirs(task_dir)
        os.chdir(task_dir)
        subprocess.call(['oj', 'download', base_url + url])  # get test cases
        print(script_path)
        shutil.copy(script_path+'/template.py', './' + description[0] + '.py')
        pathlib.Path(description[1]).touch()


def getAtcoderURL(task_list_url):  # {{{
    task_page_html = requests.get(task_list_url)
    task_page = BeautifulSoup(task_page_html.content, 'lxml')
    links = task_page.findAll('a')
    task_urls = []
    for l in links:
        if l.get_text() in ALPHABETS:
            task_urls.append(l.get('href'))

    # get title
    tasks = {}
    for url in task_urls:
        for l in links:
            if l.get('href') == url and l.get_text() in ALPHABETS:
                alphabet = l.get_text()
            elif (l.get('href') == url) and (not l.get_text() in ALPHABETS):
                title = l.get_text()
        tasks[url] = (alphabet, title)

    return tasks  # }}}


if __name__ == '__main__':
    main()


