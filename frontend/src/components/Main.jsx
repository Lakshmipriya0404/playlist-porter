import React, { useState } from "react";
import { Box, Button, Card, CardActions } from "@mui/material";

const Main = () => {
  const [playlists, setPlaylists] = useState([]);

  const handleGetPlaylistsClick = async () => {
    try {
      const response = await fetch("http://localhost:5000/authorize_spotify");
      const data = await response.json();
      window.location.href = data.auth_url;
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
      bgcolor="primary.main"
    >
      <Card sx={{ width: 400, bgcolor: "primary.light" }}>
        <CardActions sx={{ justifyContent: "center" }}>
          <Button
            variant="contained"
            size="large"
            sx={{ color: "white", bgcolor: "secondary.main" }}
            onClick={handleGetPlaylistsClick} // Event handler for fetching playlists button
          >
            Get Playlists
          </Button>
        </CardActions>
      </Card>
    </Box>
  );
};

export default Main;
