from datetime import datetime
import os
import urllib.parse
import requests

from flask import Flask, json, redirect, request, jsonify, session, url_for
from flask_cors import CORS

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = os.urandom(64)

###################### spotify #################################

CLIENT_ID  = "1f117b3fc0d34eabbf29b976c4725b4b"
CLIENT_SECRET = "6e673f232a3c42dcb2f6b916e341bccc"
REDIRECT_URI = "http://localhost:5000/callback"

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

@app.route('/authorize-spotify')
def authorize_spotify():
    scope = 'user-read-private user-read-email playlist-read-private'

    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    return jsonify({"auth_url": auth_url})

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

        token_info_str = json.dumps(session['access_token'])
        origin = request.headers.get('Origin', '*')
        close_window_script = f"""
        <script>
        window.opener.postMessage({token_info_str}, "{origin}");
        window.close();
        </script>
        """

        return close_window_script
    
@app.route('/get-spotify-playlists')
def get_playlists():
    token = request.args.get('token')
    # if datetime.now().timestamp() > session['expires_at']:
    #     return redirect('/refresh-token')    
    headers = {
        'Authorization': f"Bearer {token}"
    }
    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
    playlists = response.json()   
    return jsonify(playlists)

@app.route("/get-playlist-tracks")
def get_playlist_tracks():
    # Retrieve tracks from the playlist
    playlist_id = request.args.get('pid')
    # playlist_id = '2eZLIe7z4r2DkfzltYiK1n'
    token = request.args.get('token')
    headers = {
        'Authorization': f"Bearer {token}"
    }
    response = requests.get(API_BASE_URL + f"playlists/{playlist_id}/tracks", headers=headers)
    tracks_data = response.json()
    #print(tracks_data)
    # Extract track information
    track_names = [track['track']['name'] for track in tracks_data['items']]
    #print("tracks....:",track_names)
        # Now, for each track, search for the corresponding video ID on YouTube
    youtube_video_ids = []
    for track_name in track_names:
        # You can customize the YouTube search query based on the track name or other criteria
        youtube_search_query = f"{track_name}"
        youtube_response = requests.get(
            f"https://www.googleapis.com/youtube/v3/search?q={youtube_search_query}&key={YOUTUBE_API_KEY}"
        )
        youtube_data = youtube_response.json()
        print(youtube_data)

        # Extract video IDs from the YouTube search results
        video_ids = [item['id']['videoId'] for item in youtube_data['items'] if item['id']['kind'] == 'youtube#video']
        if video_ids:
            # Append the first video ID to the list
            print("video id")
            print(video_ids[0])
            youtube_video_ids.append(video_ids[0])

    return jsonify(youtube_video_ids)

@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/authorize-spotify')
    
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        return redirect('get-spotify-playlists')
    
###################### youtube #################################
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube','https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  
YOUTUBE_API_KEY = 'AIzaSyDI7r5P-LVdgdVEIuYfyNsFy_nglaNC8ZE'

@app.route("/create_playlist")
def create_playlist():
    if 'credentials' not in session:
        print("no credentials")
        return redirect('authorize_utube')
    
    credentials = google.oauth2.credentials.Credentials(**Flask.session['credentials'])
    youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    # Define the parameters for the playlist resource
    request_body = {
        'snippet': {
            'title': 'Playlist Porter',
            'description': 'Your Playlist Description'
        },
        'status': {
            'privacyStatus': 'public'  # Set the privacy status of the playlist
        }
    }

    playlist = youtube.playlists().insert(
       part = 'snippet,status',
       body = request_body,
    ).execute()

    # Extract playlist ID from the response
    playlist_id = playlist['id']


    Flask.session['credentials'] = credentials_to_dict(credentials)
    #return flask.redirect(flask.url_for('insert_videos', playlist_id=playlist_id, _method='POST'), code=307)
        # Redirect to the insert_videos route with the playlist_id
    return """
    <html>
    <body onload="document.getElementById('redirectForm').submit()">
        <form id="redirectForm" action="/insert_videos/{}" method="post">
        </form>
    </body>
    </html>
    """.format(playlist_id)

    
@app.route('/authorize_utube')
def authorize_utube():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(access_type='offline',include_granted_scopes='true')

    # return Flask.redirect(authorization_url)
    return jsonify({"auth_url": authorization_url})

@app.route('/oauth2callback')
def oauth2callback():

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    # session['credentials'] = credentials_to_dict(credentials)

    origin = request.headers.get('Origin', '*')
    close_window_script = f"""
    <script>
    window.opener.postMessage("{credentials_to_dict(credentials)}", "{origin}");
    window.close();
    </script>
    """
    # return Flask.redirect(Flask.url_for('home'))
    return close_window_script

@app.route("/insert_videos/<playlist_id>", methods=['POST'])
def insert_videos(playlist_id):
    if 'credentials' not in session:
        return Flask.redirect('authorize')

    # Get the list of video IDs from the request JSON
    #video_ids = flask.request.json.get('video_ids')
    video_ids = ['j6IFiUbQLl4']

    if not video_ids:
        return "No video IDs provided."

    credentials = google.oauth2.credentials.Credentials(**Flask.session['credentials'])
    youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    
    # Insert each video into the playlist
    for video_id in video_ids:
        request_body = {
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }

        youtube.playlistItems().insert(
           part='snippet',
           body=request_body
        ).execute()

    return f"{len(video_ids)} videos inserted into playlist with ID {playlist_id}."


@app.route('/logout')
def logout():
    if 'credentials' in Flask.session:
        del session['credentials']
    return redirect(Flask.url_for('home'))


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}



if __name__ == '__main__':
    app.run(debug=True)