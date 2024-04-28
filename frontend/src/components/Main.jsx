import React, { useState } from "react";
import { Box, Button, Card, CardActions } from "@mui/material";

const Main = () => {
  const [playlists, setPlaylists] = useState([]);
  const [authorized, setAuthorized] = useState(false);

  const handleGetPlaylistsClick = async () => {
    try {
      const response = await fetch("http://localhost:5000/get_playlists");
      const data = await response.json();
      console.log(data); // Display playlists data in console
      setPlaylists(data.playlists);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const handleAuthClick = async () => {
    try {
      const response = await fetch("http://localhost:5000/authorize_spotify");
      const data = await response.json();
      const authWindow = window.open(data.auth_url, "", "width=450,height=300");
      window.addEventListener("message", (event) => {
        const token = event.data;
        console.log(token);
        setAuthorized(true);
        authWindow.close();
      });
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      height="100vh"
    >
      <Card sx={{ width: 400, bgcolor: "primary.light" }}>
        <CardActions
          sx={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
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
              onClick={handleGetPlaylistsClick}
            >
              2. Get Playlists
            </Button>
          )}
          {playlists.length > 0 && (
            <div>
              <h2>Your Playlists:</h2>
              <ul>
                {playlists.map((playlist, index) => (
                  <li key={index}>
                    <a href={playlist[1]}>{playlist[0]}</a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardActions>
      </Card>
    </Box>
  );
};

export default Main;
