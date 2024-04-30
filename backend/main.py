import os

from flask import Flask, json, jsonify, session, redirect, url_for, request
from flask_cors import CORS

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = os.urandom(64)

client_id  = "1f117b3fc0d34eabbf29b976c4725b4b"
client_secret = "6e673f232a3c42dcb2f6b916e341bccc"
redirect_uri = "http://localhost:5000/callback"
scope = "playlist-read-private"

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True #should be false
)

sp = Spotify(auth_manager=sp_oauth)

@app.route("/authorize_spotify")
def authorize_spotify():
    auth_url = sp_oauth.get_authorize_url()
    return jsonify({"auth_url": auth_url})

@app.route("/callback")
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    token_info_str = json.dumps(token_info)
    origin = request.headers.get('Origin', '*')
    # Store the token_info in the session
    session['spotify_token'] = token_info
    close_window_script = f"""
    <script>
    window.opener.postMessage({token_info_str}, "{origin}");
    window.close();
    </script>
    """

    return close_window_script

@app.route("/get_playlists")
def get_playlists():
    cached_token = cache_handler.get_cached_token()
    print("Cached Token:", cached_token)  # Check the cached token
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    playlists = sp.current_user_playlists()
    playlists_info = [(pl['name'], pl['external_urls']['spotify']) for pl in playlists['items']]
    playlists_html = '<br>'.join(f'{name}: {url}' for name, url in playlists_info)
    print(playlists_info)

    return playlists_html

@app.route("/get_playlist_tracks/<playlist_id>")
def get_playlist_tracks(playlist_id):
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    # Retrieve tracks from the playlist
    tracks = sp.playlist_tracks(playlist_id)

    # Extract track information
    track_info = [(track['track']['name'], track['track']['artists'][0]['name']) for track in tracks['items']]
    tracks_html = '<br>'.join(f'{name} by {artist}' for name, artist in track_info)

    return tracks_html


@app.route('/logout')
def logout():
    session.clear
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)