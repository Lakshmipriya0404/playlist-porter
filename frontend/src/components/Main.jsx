import React, { useState } from "react";
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Typography,
} from "@mui/material";

const Main = () => {
  const [playlists, setPlaylists] = useState([]);
  const [authorized, setAuthorized] = useState(false);
  const [selectedPlaylistId, setSelectedPlaylistId] = useState(null);

  const handleGetPlaylistsTracks = async () => {
    try {
      const token = localStorage.getItem("spotifyAuthToken");
      const tracksResponse = await fetch(
        `http://localhost:5000/get-playlist-tracks?token=${token}&pid=${selectedPlaylistId}`
      );
      const tracksData = await tracksResponse.json();
      console.log(tracksData); // Display playlists data in console
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const handleAuthClick = async () => {
    try {
      const response = await fetch("http://localhost:5000/authorize-spotify");
      const data = await response.json();
      window.open(data.auth_url, "", "width=450,height=300");
      window.addEventListener("message", async (event) => {
        const token = event.data;
        localStorage.setItem("spotifyAuthToken", token);
        setAuthorized(true);
        const playlist_response = await fetch(
          `http://localhost:5000/get-spotify-playlists?token=${token}`
        );
        const playlist_data = await playlist_response.json();
        console.log(playlist_data.items); // Display playlists data in console
        setPlaylists(playlist_data.items);
      });
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const handlePlaylistClick = (playlistId) => {
    setSelectedPlaylistId(playlistId);
    console.log(playlistId);
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      height="100vh"
    >
      <Box>
        {!authorized && (
          <Button
            variant="contained"
            size="large"
            sx={{ color: "white", bgcolor: "secondary.main", m: 2 }}
            onClick={handleAuthClick}
          >
            1. Authenticate with Spotify
          </Button>
        )}
        {authorized && (
          <Button
            variant="contained"
            size="large"
            sx={{ color: "white", bgcolor: "secondary.main", m: 2 }}
            onClick={handleGetPlaylistsTracks}
          >
            2. Get Playlists tracks
          </Button>
        )}
        {playlists && playlists.length > 0 && (
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
                    onClick={() => handlePlaylistClick(playlist.id)}
                  >
                    Select Playlist
                  </Button>
                </CardContent>
              </Card>
            ))}
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default Main;

/* <img src={playlist.images[0].url} alt={playlist.name} /> */

/* <a href={playlist.external_urls.spotify}>Open Playlist</a> */
