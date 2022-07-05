import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument(
    '--input',
    dest='input',
    type=str,
    required=True,
    # "A json file to be used as input"
)
parser.add_argument(
    '--output',
    dest='output',
    type=str,
    default='user-res.json',
    # description="Where the updated file should be written to"
)

args = parser.parse_args()
input = args.input
output = args.output

def get_cumulative_and_average_stats(items, res, get_cumulative, get_average):
  res['cumulative'] = {}
  res['average'] = {}
  for item in items:
    for key in item.keys():
        try: 
          if key not in get_average:
            continue
          value = float(item[key])
          if key in res['cumulative']: 
            res['cumulative'][key] += value
          else:
            res['cumulative'][key] = value
        except:
          pass
  for i, key in reversed(list(enumerate(res['cumulative'].keys()))):
    res['average'][key] = res['cumulative'][key] / len(items)     
    if key not in get_cumulative:
      del res['cumulative'][key]
  res['totalSeen'] = len(items)
  return res



def calculate_song_frequency(items, res):
  songData = {} 
  get_cumulative = ["msPlayed"]
  get_average = ["msPlayed", "minutePlayed", "hourPlayed", "dayPlayed", "monthPlayed", "yearPlayed"]  
  for item in items:
    if item['trackName'] in songData:
      songData[item['trackName']].append(item)
    else:
      songData[item['trackName']] = [item]
  res['songs'] = {}
  for song in songData.keys():
    res['songs'][song] = get_cumulative_and_average_stats(songData[song], {}, get_cumulative, get_average)
  return res


def calculate_trends(items):
    res = {}
    res = calculate_song_frequency(items, res)
    get_cumulative = ["msPlayed"]
    get_average = ["msPlayed", "minutePlayed", "hourPlayed", "dayPlayed", "monthPlayed", "yearPlayed", "danceability", "energy", "key", "loudness", "mode", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"]  
    res = get_cumulative_and_average_stats(items, res, get_cumulative, get_average)
    return res


input_file = open(input, "r")
input_data = json.load(input_file)

res = calculate_trends(input_data)

output_file = open(output, "w")
json.dump(res, output_file)
