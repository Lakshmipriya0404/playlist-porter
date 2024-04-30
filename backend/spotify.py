from datetime import datetime
import os
import urllib.parse
import requests

from flask import Flask, json, redirect, request, jsonify, session
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = os.urandom(64)

CLIENT_ID  = "1f117b3fc0d34eabbf29b976c4725b4b"
CLIENT_SECRET = "6e673f232a3c42dcb2f6b916e341bccc"
REDIRECT_URI = "http://localhost:5000/callback"

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

@app.route('/authorize')
def authorize():
    scope = 'user-read-private user-read-email'

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
    
@app.route('/playlists')
def get_playlists():
    
    token = request.args.get('token')
    # if datetime.now().timestamp() > session['expires_at']:
    #     return redirect('/refresh-token')    
    headers = {
        'Authorization': f"Bearer {token}"
    }
    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
    playlists = response.json()
    print(playlists)
    
    return jsonify(playlists)

@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/authorize')
    
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

        return redirect('playlists')
    
if __name__ == '__main__':
    app.run(debug=True)