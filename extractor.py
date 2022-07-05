import argparse
import datetime
import json
import requests
import time
parser = argparse.ArgumentParser()
parser.add_argument(
    '--input',
    dest='input',
    type=str,
    required=True,
    # "A json file to be used as input"
)
parser.add_argument(
    '--seen-songs',
    dest='seen_songs',
    type=str,
    required=True,
    # "A json file to be used as input"
)
parser.add_argument(
    '--output',
    dest='output',
    type=str,
    default='res.json',
    # description="Where the updated file should be written to"
)
parser.add_argument(
    '--min-secs',
    dest='min_secs',
    type=int,
    default=5,
    # description="The minimum seconds allowed for a song to be used as data"
)
parser.add_argument(
    '--access-token',
    dest='access_token',
    type=str
)

args = parser.parse_args()
input = args.input
output = args.output
min_secs = args.min_secs
access_token = args.access_token
seen_songs = args.seen_songs


def get_season(now):
    Y = now.year
    seasons = [('winter', (datetime.date(Y,  1,  1),  datetime.date(Y,  3, 20))),
               ('spring', (datetime.date(Y,  3, 21),  datetime.date(Y,  6, 20))),
               ('summer', (datetime.date(Y,  6, 21),  datetime.date(Y,  9, 22))),
               ('autumn', (datetime.date(Y,  9, 23),  datetime.date(Y, 12, 20))),
               ('winter', (datetime.date(Y, 12, 21),  datetime.date(Y, 12, 31)))]
    now = now.date()
    now = now.replace(year=Y)
    return next(season for season, (start, end) in seasons
                if start <= now <= end)


def filter_secs(input):
    if input["msPlayed"] < min_secs * 1000:
        return False
    return True


def append_time_data(item):
    date = datetime.datetime.strptime(
        item['endTime'],  "%Y-%m-%d %H:%M")
    item['minutePlayed'] = date.minute
    item['hourPlayed'] = date.hour
    item['dayPlayed'] = date.day
    item['monthPlayed'] = date.month
    item['yearPlayed'] = date.year
    item['seasonPlayed'] = get_season(date)
    return item


def frequency_calculator(items):
    songsPlayed = len(items)
    freqDict = {}
    for item in items:
        if item['trackName'] in freqDict:
            freqDict[item['trackName']] += 1
        else:
            freqDict[item['trackName']] = 1
    for i, item in enumerate(items):
        items[i]['freqPlayed'] = freqDict[item['trackName']] / songsPlayed
    return items


def request_audio_features(items):
    """
    request the audio features for songs stored in f_in_name and store them in f_out_name

    :param fin_name: name of input file storing songs
    :param fout_name: name of output file where audio features will be stored
    :param rm_features: if you don't want certain features these will be removed
    :return: nothing
    """
    if not access_token:
        return items
    BASE_URL = 'https://api.spotify.com/v1/'
    head = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }
    title_data = {}
    res_data = {}
    ids = []
    songs_file = open(seen_songs, "r")
    songs_data = json.load(songs_file)
    for i, item in enumerate(items):
        print("Getting data for track " + str(i + 1) +
              " out of " + str(len(items)))
        errs = 0
        while True:
            try:
                # getting the track id
                if  item['trackName'] not in title_data and item['trackName'] in songs_data:
                    items[i].update(songs_data[item['trackName']])
                elif item['trackName'] not in title_data and item['trackName'] not in songs_data:
                    feature_req = requests.get(
                        BASE_URL + 'search/?q=' + item['trackName'] + "&type=track&locale=en-US%2Cen%3Bq%3D0.9&offset=0&limit=1", headers=head).json()
                    title_data[item['trackName']
                               ] = feature_req['tracks']['items'][0]["id"]
                    ids.append(feature_req['tracks']['items'][0]["id"])
                    time.sleep(.05)
                    break
                break
            except:
                if errs == 0:
                    print("An error has occurred. Retrying in 3 seconds...")
                    errs += 1
                    time.sleep(3)
                else:
                    print("Cannot extract track data.")
                    break
        if i % 100 == 99 or i == len(items)-1:
            # getting the track features
            feature_req = requests.get(
                BASE_URL + 'audio-features/?ids=' + ",".join(ids), headers=head).json()
            id_data = {}
            for k, v in title_data.items():
                id_data[v] = title_data.get(v, []) + [k]
            if "audio_features" in feature_req:
                for i, feature in enumerate(feature_req["audio_features"]):
                    for title in id_data[ids[i]]:
                        res_data[title] = feature
                        songs_data[title] = feature
            ids = []
    for i, item in reversed(list(enumerate(items))):
        # if track doesn't have data remove it from consideration
        if item['trackName'] not in songs_data or songs_data[item['trackName']] is None:
            items.pop(i)
        else:
            items[i].update(songs_data[item['trackName']])
    output_file = open(seen_songs, "w")
    json.dump(songs_data, output_file)
    return items


def allow_input(item):
    return filter_secs(item)


def append_input(item):
    item = append_time_data(item)
    return item


def append_inputs(items):
    items = frequency_calculator(items)
    items = request_audio_features(items)
    return items


def get_output(items):
    for i, item in reversed(list(enumerate(items))):
        if not allow_input(item):
            items.pop(i)
    for i, item in enumerate(items):
        items[i] = append_input(item)
    items = append_inputs(items)
    return items


input_file = open(input, "r")
input_data = json.load(input_file)
print(input_data)
output_file = open(output, "w")
json.dump(get_output(input_data), output_file)
