import requests, os, json
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

LAST_FM_USERNAME = os.getenv("LAST_FM_USERNAME")
API_KEY = os.getenv("API_KEY")
APPLICATION_ID = os.getenv("APPLICATION_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("USER_ID")

def getUserInfo():
    getUserData = requests.get(url=f"http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={LAST_FM_USERNAME}&api_key={API_KEY}&format=json")
    userData = getUserData.json()
    scrobbles = int(userData["user"]["playcount"])
    totalArtists = int(userData["user"]["artist_count"])
    totalTracks = int(userData["user"]["track_count"])
    totalAlbums = int(userData["user"]["album_count"])
    return scrobbles, totalArtists, totalTracks, totalAlbums

def getLovedTracksCount():
    getLoved = requests.get(url=f"http://ws.audioscrobbler.com/2.0/?method=user.getlovedtracks&user={LAST_FM_USERNAME}&api_key={API_KEY}&format=json&limit=1")
    lovedData = getLoved.json()
    lovedCount = int(lovedData["lovedtracks"]["@attr"]["total"])
    return lovedCount

def getWeeklyScrobbleCount():
    getWeekly = requests.get(url=f"http://ws.audioscrobbler.com/2.0/?method=user.getweeklytrackchart&user={LAST_FM_USERNAME}&api_key={API_KEY}&format=json")
    weeklyData = getWeekly.json()
    weeklyScrobbles = sum(int(track["playcount"]) for track in weeklyData["weeklytrackchart"]["track"])
    return weeklyScrobbles

def update():
    scrobbles, totalArtists, totalTracks, totalAlbums = getUserInfo()
    lovedCount = getLovedTracksCount()
    weeklyScrobbles = getWeeklyScrobbleCount()
    jsonData = {"scrobbles": scrobbles, "weeklyScrobbles": weeklyScrobbles, "artistsScrobbled": totalArtists, "tracksScrobbled": totalTracks, "albumsScrobbled": totalAlbums, "lovedTracks": lovedCount, "updatedAt": datetime.now(timezone.utc).isoformat()}
    os.makedirs("docs", exist_ok=True)
    with open("docs/data.json", "w") as f:
        json.dump(jsonData, f, indent=2)
    jsonString = {"data":{"dynamic":[{"type":2,"name":"scrobbles","value":scrobbles},{"type":2,"name":"weeklyscrobbles","value":weeklyScrobbles},{"type":2,"name":"artistscrobbled","value":totalArtists},{"type":2,"name":"tracksscrobbled","value":totalTracks},{"type":2,"name":"albumsscrobbled","value":totalAlbums},{"type":2,"name":"lovedtracks","value":lovedCount}]}}
    r = requests.patch(url=f"https://discord.com/api/v9/applications/{APPLICATION_ID}/users/{USER_ID}/identities/0/profile", headers={"Content-Type": "application/json", "Authorization": f"Bot {BOT_TOKEN}", "User-Agent": "DiscordBot (https://github.com/discord/discord-api-docs, 1.0.0)"}, data=json.dumps(jsonString))

    print(r.status_code, r.text)
    
update()