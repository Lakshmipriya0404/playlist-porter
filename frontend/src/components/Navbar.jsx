import { AppBar, Toolbar, styled, Typography } from "@mui/material";
import { LibraryMusic } from "@mui/icons-material";
import React from "react";

const StyledToolbar = styled(Toolbar)({
  display: "flex",
  justifyContent: "space-between",
});

const Navbar = () => {
  return (
    <AppBar position="static" sx={{ bgcolor: "primary.light", p: 0.25 }}>
      <StyledToolbar>
        <Typography variant="h6" sx={{ display: { xs: "none", sm: "block" } }}>
          Playlist Porter
        </Typography>
        <LibraryMusic sx={{ display: { xs: "block", sm: "none" } }} />
      </StyledToolbar>
    </AppBar>
  );
};

export default Navbar;
