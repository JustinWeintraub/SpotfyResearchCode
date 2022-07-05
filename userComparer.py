import pandas as pd
from scipy.spatial.distance import euclidean, pdist, squareform
import json
import os
import numpy as np

def create_matrix(users, songs):
  userData = {}
  userNames = []
  for song in songs:
    userData[song] = []
    for user in users:
      if song in user['songs']:
        userData[song].append(user['songs'][song]['totalSeen'])
      else: 
        userData[song].append(0)
  for user in users:
    userNames.append(user['name'])
  df = pd.DataFrame.from_dict(userData)
  df.index = userNames
  return df

def similarity_func(u, v):
    return 1/(1+euclidean(u,v))

def calculate_similarity(users, songs, res):
  df = create_matrix(users, songs)
  dists = pdist(df, similarity_func)
  dfEuclid = pd.DataFrame(squareform(dists), columns=df.index, index=df.index)
  np.fill_diagonal(dfEuclid.values, 1)
  similarityJson = dfEuclid.to_json()
  res['euclideanDistance'] = similarityJson
  return res
  #squareform(pdist(DF_var, metric='euclidean'))

def get_frequency(users, songs, res):
  songInfo = []
  for song in songs:
    totalSeen = 0
    for user in users:
      if song in user['songs']:
        totalSeen += user['songs'][song]["totalSeen"]
    songInfo.append({song: totalSeen})
  songInfo.sort(key=lambda x: list(x.values())[0], reverse=True)
  res['totalSeen'] = songInfo
  return res

def generate_users():
  users = []
  for user in os.listdir("./data/users"):
    userFile = open("./data/users/"+user+"/collective.json", "r")
    userData = json.load(userFile)
    userData['name'] = user
    users.append(userData)
  return users


users = generate_users()
songs_file = open("./data/songs.json", "r")
songs = json.load(songs_file)
res = {}
res = calculate_similarity(users, songs, res)
res = get_frequency(users, songs, res)

output_file = open("./data/userTrends.json", "w")
json.dump(res, output_file)