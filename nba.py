from datetime import date, timedelta
import json
import urllib.request
import urllib.error

import boto3

bucket_name = 'nba-pbp-logs'
base_url = 'http://data.nba.net/data/10s/prod/v1/{date}/{game_number}_'
pbp_url = base_url + 'pbp_{part}.json'

# Just the 15-16 season for now
date_window = (date(2016, 1, 23), date(2016, 4, 13))
date_delta = date_window[1] - date_window[0]
date_range = (date_window[0] + timedelta(days=x) for x in range(date_delta.days + 1))

counter = 657
def do_game(date, game_number):
    global counter
    plays = []
    for pbp in range(1, 5):
        url = pbp_url.format(date=date, game_number=game_number, part=pbp)
        plays += json.load(urllib.request.urlopen(url))['plays']
    print(plays)
    counter += 1
    return plays

s3 = boto3.resource('s3')
def upload_logs(plays, game_number):
    obj = s3.Object(bucket_name, 'games/{}.json'.format(game_number))
    return obj.put(ContentType='application/json', Body=json.dumps(plays))

success = 0
for d in date_range:
    date_url = d.strftime('%Y%m%d')
    year = d.strftime('%y')
    try:
        while True:
            game_number = '00215{cnt:05d}'.format(cnt=counter)
            plays = do_game(date_url, game_number)
            upload_logs(plays, game_number)
            success += 1
    except urllib.error.HTTPError as e:
        if e.code == 404:
            continue
        else:
            raise e

print(success)
