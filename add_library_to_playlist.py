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


def get_library_tracks():
    """gets list of tracks from a user's saved library"""

    results = sp.current_user_saved_tracks()
    tracks = results["items"]
    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])

    return tracks


def get_track_ids(playlist_tracks):
    """gets unique track IDs from list of track names"""

    track_ids = []

    for song in range(len(playlist_tracks)):
        # removes local files as local files have no unique ID
        if playlist_tracks[song]["track"]["id"] and not playlist_tracks[song]["track"]["is_local"]:
            track_ids.append(playlist_tracks[song]["track"]["id"])

    return track_ids


def get_playlist_tracks(username, playlist_id):
    """gets list of tracks from a user's playlist"""

    results = sp.user_playlist_tracks(username, playlist_id)
    tracks = results["items"]
    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])

    return tracks


def add_tracks_to_playlist(song_ids, playlist_id):
    """add all songs to a playlist while circumventing 100 song API limit"""

    i = 0
    increment = 99

    while i < len(song_ids) + increment:
        try:
            sp.playlist_add_items(playlist_id, song_ids[i: i + increment])
        except spotipy.exceptions.SpotifyException:
            pass

        i += increment


scope = 'playlist-modify-public user-library-read'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI, scope=scope))

username = input("Enter a username: ")

saved_tracks = get_library_tracks()
saved_track_ids = get_track_ids(saved_tracks)
print(f"{len(saved_track_ids)} non-local songs have been found in your saved library.")

playlists_names = get_playlists(username)
print(*playlists_names, sep="\n")

playlist_name = input("\nEnter a playlist name from above to add library songs to (case sensitive): ")

if not playlist_name:
    playlist_name = input("\nEnter a playlist name from above to add library songs to (case sensitive): ")
else:
    playlist_id = get_playlist_id(playlist_name)

# filter out non-unique songs or run concat playlist through remove duplicates
existing_tracks = get_track_ids(get_playlist_tracks(username, playlist_id))
saved_track_ids = [song for song in saved_track_ids if song not in existing_tracks]
print(f"{len(saved_track_ids)} songs not already in playlist '{playlist_name}' have been found in your library.")

confirm = input(f"{len(saved_track_ids)} songs will be added to your playlist "
                f"'{playlist_name}'. Confirm with Y, or leave blank to exit. ").upper()
if confirm == "Y":
    add_tracks_to_playlist(saved_track_ids, playlist_id)
    print(f"{len(saved_track_ids)} songs have been added to your playlist '{playlist_name}'.")
else:
    print("No changes will be made.")
    exit()
