import os

import flask

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube','https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = flask.Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(64)

@app.route("/")
def home():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    return flask.redirect('/create_playlist')    

@app.route("/create_playlist")
def create_playlist():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    
    credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
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


    flask.session['credentials'] = credentials_to_dict(credentials)
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

    
@app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(access_type='offline',include_granted_scopes='true')

    flask.session['state'] = state

    return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():

  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('home'))

@app.route("/insert_videos/<playlist_id>", methods=['POST'])
def insert_videos(playlist_id):
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    # Get the list of video IDs from the request JSON
    #video_ids = flask.request.json.get('video_ids')
    video_ids = ['j6IFiUbQLl4']

    if not video_ids:
        return "No video IDs provided."

    credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
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
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return flask.redirect(flask.url_for('home'))


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


if __name__ == '__main__':
    app.run(debug=True,port=5001)