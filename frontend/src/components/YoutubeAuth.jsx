import React, { useState } from "react";
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Typography,
} from "@mui/material";

const YoutubeAuth = () => {
  const [authorized, setAuthorized] = useState(false);
  const handleUTubeAuth = async () => {
    try {
      const response = await fetch("http://localhost:5000/authorize_utube");
      const data = await response.json();
      const authWindow = window.open(data.auth_url, "", "width=450,height=300");
      window.addEventListener("message", (event) => {
        const credentials = event.data;
        console.log(credentials);
        localStorage.setItem("utubeCredentials", credentials);
        setAuthorized(true);
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
      <Button
        variant="contained"
        size="large"
        sx={{ color: "white", bgcolor: "secondary.main", m: 2 }}
        onClick={handleUTubeAuth}
      >
        1. Authenticate with YouTube
      </Button>
    </Box>
  );
};

export default YoutubeAuth;
