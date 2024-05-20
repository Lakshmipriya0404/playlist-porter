import React, { useState } from "react";
import { Box, Button, Card, CardContent, Typography } from "@mui/material";
import Loading from "./Loading";

const Main = () => {
  const [playlists, setPlaylists] = useState([]);
  const [authorizedSpotify, setAuthorizedSpotify] = useState(false);
  const [selectedPlaylistId, setSelectedPlaylistId] = useState(null);
  const [authorizedUTube, setAuthorizedUTube] = useState(false);
  const [loading, setLoading] = useState(false);
  const [youtubePlaylistLink, setYoutubePlaylistLink] = useState(null);
  const [tracksData, setTracksData] = useState([]);

  const handleGetPlaylistsTracks = async (playlistId) => {
    try {
      setSelectedPlaylistId(playlistId);
      const token = localStorage.getItem("spotifyAuthToken");
      const tracksResponse = await fetch(
        `https://playlist-porter.onrender.com/get-playlist-tracks?token=${token}&pid=${playlistId}`
      );
      const data = await tracksResponse.json();
      setTracksData(data);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const handleSpotifyAuthClick = async () => {
    try {
      const response = await fetch(
        "https://playlist-porter.onrender.com/authorize-spotify"
      );
      const data = await response.json();
      window.open(data.auth_url, "", "width=450,height=300");
      window.addEventListener("message", async (event) => {
        const token = event.data;
        localStorage.setItem("spotifyAuthToken", token);
        setAuthorizedSpotify(true);
        const playlist_response = await fetch(
          `https://playlist-porter.onrender.com/get-spotify-playlists?token=${token}`
        );
        const playlist_data = await playlist_response.json();
        setPlaylists(playlist_data.items);
      });
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const handleUTubeAuth = async () => {
    try {
      const response = await fetch(
        "https://playlist-porter.onrender.com/authorize_utube"
      );
      const data = await response.json();
      window.open(data.auth_url, "", "width=450,height=300");
      window.addEventListener("message", (event) => {
        const credentials = event.data;
        localStorage.setItem("utubeCredentials", JSON.stringify(credentials));
        setAuthorizedUTube(true);
      });
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const handleTransferToUTube = async () => {
    try {
      setLoading(true);
      const credentialsString = localStorage.getItem("utubeCredentials");
      const credentials = JSON.parse(credentialsString);
      const response = await fetch(
        "https://playlist-porter.onrender.com/create_playlist",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ credentials, tracksData }),
        }
      );
      const link = await response.json();
      setYoutubePlaylistLink(link);
      setLoading(false);
    } catch (error) {
      console.error("Error:", error);
      setLoading(false);
    }
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      height="100vh"
    >
      <Box>
        {!authorizedSpotify && (
          <Button
            variant="contained"
            size="large"
            sx={{ color: "white", bgcolor: "secondary.main", m: 2 }}
            onClick={handleSpotifyAuthClick}
          >
            1. Authenticate with Spotify
          </Button>
        )}
        {playlists && playlists.length > 0 && !selectedPlaylistId && (
          <Box display="flex" flexWrap="wrap">
            {playlists.map((playlist) => (
              <Card
                key={playlist.id}
                variant="outlined"
                sx={{ maxWidth: 300, m: 2 }}
              >
                <CardContent>
                  <Typography variant="h5" component="div">
                    {playlist.name}
                  </Typography>
                  <Typography sx={{ mb: 1.5 }} color="text.secondary">
                    Owner: {playlist.owner.display_name}
                  </Typography>
                  <Button
                    variant="contained"
                    onClick={() => handleGetPlaylistsTracks(playlist.id)}
                  >
                    Select Playlist
                  </Button>
                </CardContent>
              </Card>
            ))}
          </Box>
        )}
        {authorizedSpotify && !authorizedUTube && selectedPlaylistId && (
          <Button
            variant="contained"
            size="large"
            sx={{ color: "white", bgcolor: "secondary.main", m: 2 }}
            onClick={handleUTubeAuth}
          >
            2. Authenticate with YouTube
          </Button>
        )}
        {authorizedSpotify && authorizedUTube && (
          <Button
            variant="contained"
            size="large"
            sx={{ color: "white", bgcolor: "secondary.main", m: 2 }}
            onClick={handleTransferToUTube}
          >
            3. Transfer Playlist to YouTube
          </Button>
        )}
        {loading && <Loading />}
        {youtubePlaylistLink && (
          <Typography variant="h6" color="primary.light">
            YouTube Playlist Link:{" "}
            <a
              href={youtubePlaylistLink}
              target="_blank"
              rel="noopener noreferrer"
            >
              {youtubePlaylistLink}
            </a>
          </Typography>
        )}
      </Box>
    </Box>
  );
};

export default Main;
