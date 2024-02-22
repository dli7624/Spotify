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

    pid = ""

    results = sp.user_playlists(user=username)

    for playlist in range(len(results["items"])):
        if results["items"][playlist]["name"].lower() == playlist_name:
            pid = results["items"][playlist]["id"]
            return pid, results["items"][playlist]["name"]

    if pid.strip() == "":
        print("Playlist does not exist.\n")
        exit()


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


def get_uri_data(username, playlist_id, new_tracks):
    """obtain formatted uri data from spotify query to be added to library"""
    full_data = get_playlist_tracks(username, playlist_id)

    uri_data = []

    for song in range(len(full_data)):
        if full_data[song]["track"]["id"] in new_tracks:
            uri_data.append(full_data[song]["track"]["uri"])

    return uri_data


scope = 'playlist-modify-public user-library-modify'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI, scope=scope))

username = input("Enter a username: ")
playlists_names = get_playlists(username)
print(*playlists_names, sep="\n")

playlist_name = input("\nEnter a playlist name from above to add to library: ").lower()

if not playlist_name:
    playlist_name = input("\nEnter a playlist name from above to add to library: ").lower()
else:
    playlist_id, playlist_name = get_playlist_id(playlist_name)

# filter out non-unique songs or run concat playlist through remove duplicates
existing_tracks = get_track_ids(get_library_tracks())
playlist_tracks = get_track_ids(get_playlist_tracks(username, playlist_id))
new_tracks = [song for song in playlist_tracks if song not in existing_tracks]
print(f"{len(new_tracks)} song(s) not already in your saved library have been found in playlist '{playlist_name}'.")

uri_data = get_uri_data(username, playlist_id, new_tracks)

if len(new_tracks) == 0:
    print("No new tracks were found.")
else:
    confirm = input(f"{len(new_tracks)} song(s) from '{playlist_name}' will be saved to your library. "
                    f"Confirm with Y, or leave blank to exit. ").upper()
    if confirm == "Y":
        for song in range(len(uri_data)):
            sp.current_user_saved_tracks_add([uri_data[song]])

        print(f"{len(new_tracks)} song(s) from '{playlist_name}' "
              f"have been saved to your library.")
    else:
        print("No changes will be made.")
        exit()
