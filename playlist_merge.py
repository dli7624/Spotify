import spotipy
from spotipy.oauth2 import SpotifyOAuth
from creds import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI


def get_playlists(username):
    """gets available playlists from user's profile"""
    playlists_names = []

    playlists = sp.user_playlists(username)
    for playlist in range(len(playlists["items"])):
        playlists_names.append(playlists["items"][playlist]["name"])

    playlists_names.sort(key=str.lower)

    return playlists_names


def get_playlist_tracks(username, playlist_id):
    """gets list of tracks from a user's playlist"""

    results = sp.user_playlist_tracks(username, playlist_id)
    tracks = results["items"]
    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])

    return tracks


def get_playlist_id(playlist_name):
    """gets playlist ID from playlist name given"""

    id = ""

    results = sp.user_playlists(user=username)
    for playlist in range(len(results["items"])):
        if results["items"][playlist]["name"] == playlist_name:
            id = results["items"][playlist]["id"]

    if id.strip() == "":
        print("Playlist does not exist.\n")
        return False
    else:
        return id


def get_track_ids(playlist_tracks):
    """gets unique track IDs from list of track names"""

    global track_ids

    for song in range(len(playlist_tracks)):
        # removes local files as local files have no unique ID
        if playlist_tracks[song]["track"]["id"] and not playlist_tracks[song]["track"]["is_local"]:
            track_ids.append(playlist_tracks[song]["track"]["id"])

    return track_ids


def add_tracks_to_playlist(song_ids, new_playlist_id):
    """add all songs to a playlist while circumventing 100 song API limit"""

    global track_ids

    i = 0
    increment = 99

    while i < len(song_ids) + increment:
        try:
            sp.playlist_add_items(new_playlist_id, song_ids[i: i + increment])
        except spotipy.exceptions.SpotifyException:
            pass

        i += increment

    print(f"{len(track_ids)} songs have been added to {new_playlist}.")


continue_combining = True
track_ids = []

scope = 'playlist-modify-public'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI, scope=scope))

username = input("Enter a username: ")

while continue_combining:
    playlists_names = get_playlists(username)
    print(*playlists_names, sep="\n")
    playlist_name = input("\nEnter a playlist name from above to combine (case sensitive), or leave blank to stop: ")
    if playlist_name == '':
        continue_combining = False
    else:
        playlist_id = get_playlist_id(playlist_name)
        if playlist_id:
            playlist_tracks = get_playlist_tracks(username=username, playlist_id=playlist_id)
            get_track_ids(playlist_tracks)

while True:
    new_playlist = input("Enter a name for your new playlist: ")

    if new_playlist.strip() == "":
        print("Playlist name cannot be blank.")
    if new_playlist.strip() != "":
        break

sp.user_playlist_create(user=username, name=new_playlist)
new_playlist_id = get_playlist_id(new_playlist)
add_tracks_to_playlist(track_ids, new_playlist_id)
