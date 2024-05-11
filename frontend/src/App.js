import Navbar from "./components/Navbar";
import Main from "./components/Main";
import { Box, Stack, ThemeProvider } from "@mui/material";
import { theme } from "./theme";
import YoutubeAuth from "./components/YoutubeAuth";
import Loading from "./components/Loading";

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Box bgcolor="primary.main">
        <Stack direction="column" justifyContent="center">
          <Navbar />
          <Main />
          {/* <YoutubeAuth /> */}
          {/* <Loading /> */}
        </Stack>
      </Box>
    </ThemeProvider>
  );
}

export default App;
