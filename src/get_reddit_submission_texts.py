# -*- coding: utf-8 -*-
__title__ = 'coviewed_data_collection from Reddit'
__author__ = 'Dietrich Trautmann'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020, Dietrich Trautmann'


import os
import json
import time
import argparse
import requests
import pandas as pd
import datetime as dt



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
            "-s",
            "--subreddit",
            help="please provide the subreddtit",
            required=True,
            )
    parser.add_argument(
            "-v",
            "--verbose",
            help="shows output",
            action='store_true'
            )
    args = parser.parse_args()


    tsv_files = [f for f in os.listdir('data/') \
            if args.subreddit in f and f.endswith('.tsv')]
    print(len(tsv_files))


    all_urls = []
    for tsv_file in sorted(tsv_files):
        tsv_data = pd.read_csv(os.path.join('data',tsv_file), sep='\t')
        urls = tsv_data.url.values.tolist()
        print("%6i"%len(urls), tsv_file)
        all_urls+=urls
    print(len(all_urls))


    with open('settings/exclude_domains.txt') as f:
        exclude_domains = f.readlines()
    exclude_domains = [d.strip() for d in exclude_domains]
    print(exclude_domains)


    target_urls = []
    for url in all_urls:
        D = [domain in url for domain in exclude_domains]
        if len(set(D)) == 1 and list(set(D))[0] == False:
            target_urls.append(url)
    print(len(target_urls))
    target_urls = list(set(target_urls))
    print(len(target_urls))

    with open('data/news_urls.txt','w') as f:
        for url in target_urls:
            f.writelines(url)
            f.writelines('\n')
