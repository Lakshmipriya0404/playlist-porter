from datetime import datetime
import os
import urllib.parse
import requests
import json

from flask import Flask, json, redirect, request, jsonify, session, url_for
from flask_cors import CORS

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = os.urandom(64)

###################### spotify #################################

f = open('spotify_secret.json', 'r')
client_data = json.load(f)

CLIENT_ID  = client_data["CLIENT_ID"]
CLIENT_SECRET = client_data["CLIENT_SECRET"]
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
    headers = {
        'Authorization': f"Bearer {token}"
    }
    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
    playlists = response.json()   
    return jsonify(playlists)

@app.route("/get-playlist-tracks")
def get_playlist_tracks():

    playlist_id = request.args.get('pid')
    token = request.args.get('token')
    headers = {
        'Authorization': f"Bearer {token}"
    }
    response = requests.get(API_BASE_URL + f"playlists/{playlist_id}/tracks", headers=headers)
    tracks_data = response.json()
    track_names = [track['track']['name'] for track in tracks_data['items']]

    return jsonify(track_names)

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

@app.route("/create_playlist", methods=['POST'])
def create_playlist():
    data = request.json
    credentials_str = data.get('credentials')
    track_names = data.get('tracksData')
    credentials_str = credentials_str.replace("'", '"').replace("None","null")
    credentials_json = json.loads(credentials_str)
    credentials = google.oauth2.credentials.Credentials(**credentials_json)

    youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    request_body = {
        'snippet': {
            'title': 'Playlist Porter',
            'description': 'Your Playlist Description'
        },
        'status': {
            'privacyStatus': 'public' 
        }
    }

    playlist = youtube.playlists().insert(
       part = 'snippet,status',
       body = request_body,
    ).execute()

    playlist_id = playlist['id']

    youtube_video_ids = []
    print(track_names)
    for track_name in track_names:
        youtube_search_query = f"{track_name}"
        youtube_response = requests.get(
            f"https://www.googleapis.com/youtube/v3/search?q={youtube_search_query}&key={YOUTUBE_API_KEY}"
        )
        youtube_data = youtube_response.json()

        video_ids = [item['id']['videoId'] for item in youtube_data['items'] if item['id']['kind'] == 'youtube#video']
        if video_ids:
            youtube_video_ids.append(video_ids[0])

    link = insert_videos(playlist_id, credentials,youtube_video_ids)
    print("LINK: ")
    print(link)
    return link

    
@app.route('/authorize_utube')
def authorize_utube():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(access_type='offline',include_granted_scopes='true')

    return jsonify({"auth_url": authorization_url})

@app.route('/oauth2callback')
def oauth2callback():

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    origin = request.headers.get('Origin', '*')
    close_window_script = f"""
    <script>
    window.opener.postMessage("{credentials_to_dict(credentials)}", "{origin}");
    window.close();
    </script>
    """
    return close_window_script


def insert_videos(playlist_id, credentials, video_ids):

    if not video_ids:
        return "No video IDs provided."

    youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    
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

    return f"https://www.youtube.com/playlist?list={playlist_id}"


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