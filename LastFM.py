import urllib.request
import json
from datetime import datetime, timedelta
"""
I know Last.fm was used before to get Spotify data so I looked more into it and the information we can get from it.
I'm not sure if we're even going to use any of this so I didn't write a lot of methods, but there's lots of different methods 
we can create given a username. I wrote two methods but any other methods we want to create would follow a similar format.
Last.fm also has a lot of good data visualization that I didn't look too much into but that could also be useful if we're interested.
"""
#API Key I generated using my Last.fm account, this is only needed to access the API
lastfm_key = "0f82f9ea7fb563406980a171b38af1cd"

#given a username and time period it returns the total number of songs listened to in a given period
# we could change the time to be more relevant to WPI
def playcount(lastfm_username, period):
    # build URL
    url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=" + lastfm_username + "&api_key=" + lastfm_key

    # work out the current time
    start_time = None
    time_now = datetime.now()

    # sets time period based on given parameter
    if period == "today":
        start_time = time_now.replace(hour=0, minute=0)

    if period == "this_month":
        start_time = time_now.replace(day=1, hour=0, minute=0)

    if period == "this_year":
        start_time = time_now.replace(month=1, day=1, hour=0, minute=0)

    if period == "this_week":
        start_time = time_now.replace(hour=0, minute=0)
        start_time = start_time - timedelta(days=start_time.weekday())

    if period == "last30days":
        start_time = time_now.replace(hour=0, minute=0)
        start_time = start_time - timedelta(days=30)

    if period == "last7days":
        start_time = time_now.replace(hour=0, minute=0)
        start_time = start_time - timedelta(days=7)

    # if start_time has been set then append it to the url
    if start_time is not None:
        start_timestamp = datetime.timestamp(start_time)
        start_timestamp = int(start_timestamp)
        url = (url + "&from=" + str(start_timestamp)) + "&format=json"

    # download the raw json object and parse the json data
    data = urllib.request.urlopen(url).read().decode()
    obj = json.loads(data)

    # extract relevant data
    output = obj['recenttracks']['@attr']['total']

    return output
print(playcount("leahmaciel","last7days"))

#given a username it returns the last played song including its title, artist, and album
def lastplayed(lastfm_username):
    # build URL
    url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=" + lastfm_username + "&api_key=" + lastfm_key + "&format=json"

    # download the raw json object and parse the json data
    data = urllib.request.urlopen(url).read().decode()
    obj = json.loads(data)

    # extract relevant data
    lastplayed_trackname = obj['recenttracks']['track'][0]['name']
    lastplayed_artist = obj['recenttracks']['track'][0]['artist']['#text']
    lastplayed_album = obj['recenttracks']['track'][0]['album']['#text']
    return lastplayed_trackname, lastplayed_artist, lastplayed_album
print(lastplayed("leahmaciel"))
