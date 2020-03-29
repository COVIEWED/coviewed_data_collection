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
            "-a",
            "--after_date",
            help="after date - format %Y-%m-%dT%H:%M:%S",
            required=True,
            type=lambda s: dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
            )
    parser.add_argument(
            "-b",
            "--before_date",
            help="before date - format %Y-%m-%dT%H:%M:%S",
            required=True,
            type=lambda s: dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
            )
    parser.add_argument(
            "-s",
            "--subreddit",
            help="please provide the subreddtit",
            required=True,
            )
    parser.add_argument(
            "--size",
            default=1000
            )
    parser.add_argument(
            "-o",
            "--output_file",
            help="provide an alternative name for the ouput_file",
            type=str
            )
    parser.add_argument(
            "-v",
            "--verbose",
            help="shows output",
            action='store_true'
            )
    args = parser.parse_args()

    after_unixtime = int(time.mktime(args.after_date.timetuple()))
    before_unixtime = int(time.mktime(args.before_date.timetuple()))

    if args.output_file:
        output_file = args.output_file
    else:
        output_file = "_".join(
                [
                    "Subreddit",
                    str(args.subreddit),
                    str(args.after_date),
                    str(args.before_date)
                ]
                ) +".tsv"
        output_file = output_file.replace(" ","T")
        output_file = os.path.join('data', output_file)

    url = 'https://api.pushshift.io/reddit/search/submission/?subreddit={}&sort=desc&sort_type=created_utc&size={}&after={}'.format(args.subreddit, args.size, after_unixtime)


    if args.verbose:
        print(args.after_date)
        print(after_unixtime, end='\n'*2)
        print(args.before_date)
        print(before_unixtime, end='\n'*2)
        print(args.subreddit, end='\n'*2)
        print(output_file, end='\n'*2)
        print(url, end='\n'*2)
    

    subreddit_data = []
    prev_before_unixtime = None
    while prev_before_unixtime != before_unixtime:
        response = requests.get('{}&before={}'.format(url,before_unixtime))
        assert response.status_code == 200
        data = json.loads(response.text)
        for d in data['data']:
            subreddit_data.append(d)
        prev_before_unixtime = before_unixtime
        before_unixtime = int(d['created_utc'])
        if args.verbose:
            print("%20i"%len(subreddit_data), end=' ')
            print(dt.datetime.fromtimestamp(int(subreddit_data[0]['created_utc'])).strftime('%Y-%m-%d %H:%M:%S'), end=' ')
            print(dt.datetime.fromtimestamp(int(subreddit_data[-1]['created_utc'])).strftime('%Y-%m-%d %H:%M:%S'))
        time.sleep(1)
    

    subreddit_data_df = pd.DataFrame(
            [[d['id'], d['created_utc'], d['url']] for d in subreddit_data],
            columns=['id','created_utc','url']
            )

    if args.verbose:
        print(dt.datetime.fromtimestamp(int(subreddit_data[0]['created_utc'])).strftime('%Y-%m-%d %H:%M:%S'))
        print(dt.datetime.fromtimestamp(int(subreddit_data[-1]['created_utc'])).strftime('%Y-%m-%d %H:%M:%S'))
        print(len(subreddit_data_df))
    
    subreddit_data_df.to_csv(output_file, sep='\t', index_label=False, index=False)
    

