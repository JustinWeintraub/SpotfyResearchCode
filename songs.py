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

song_data = ["danceability", "energy", "key", "loudness", "mode", "speechiness", "acousticness", "instrumentalness", "liveness","valence", "tempo", "duration_ms"]  
def get_cumulative_and_average_stats(items, res):
  for item in items:
    for key in item.keys():
        try: 
          if key not in song_data:
            continue
          value = float(item[key])
          res[key] = item[key]
        except:
          pass
  return res



def calculate_song_frequency(items, res):
  songData = {} 
  for item in items:
    if item['trackName'] in songData:
      songData[item['trackName']].append(item)
    else:
      songData[item['trackName']] = [item]
  for song in songData.keys():
    res[song] = get_cumulative_and_average_stats(songData[song], {})
  return res


def calculate_trends(items):
    res = {}
    res = calculate_song_frequency(items, res)
    return res


input_file = open(input, "r")
input_data = json.load(input_file)

res = calculate_trends(input_data)

output_file = open("songs.json", "w")
json.dump(res, output_file)
