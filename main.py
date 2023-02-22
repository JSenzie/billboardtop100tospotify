from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

client_ID = os.getenv('client_ID')
client_secret = os.getenv('client_secret')
redirect_uri = "http://localhost:8888/callback"

prompt = input("What year would you like to travel to? Enter YYYY-MM-DD: ")
billboard_URL = f"https://www.billboard.com/charts/hot-100/{prompt}/"

site_data = requests.get(billboard_URL).text
soup = BeautifulSoup(site_data, "html.parser")

songs = soup.select(selector="li h3")
song_list = [song.getText().strip() for song in songs[0:100]]


scope = "playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_ID,
                                               client_secret=client_secret,
                                               scope=scope,
                                               redirect_uri=redirect_uri,
                                               show_dialog=True,
                                               cache_path="token.txt"))

user_id = sp.current_user()["id"]
URI_list = []

for track in song_list:
    result = sp.search(f"track: {track} year: {prompt[0:4]}")

    try:
        URI_list.append(result["tracks"]["items"][0]["uri"])
    except IndexError:
        try:
            formatted_track = (track.split('(', 1)[0]).replace("'", "")
            result = sp.search(f"track: {formatted_track} year: {prompt[0:4]}")
            URI_list.append(result["tracks"]["items"][0]["uri"])
        except IndexError:
            pass


playlist_result = sp.user_playlist_create(user=user_id,
                                          name=f"{prompt} Billboard 100",
                                          public=False,
                                          collaborative=False,
                                          description="Top songs for the year provided")

sp.playlist_add_items(playlist_id=playlist_result["id"], items=URI_list, position=None)
