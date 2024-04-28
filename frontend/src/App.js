import Navbar from "./components/Navbar";
import Main from "./components/Main";
import { Box, Stack, ThemeProvider } from "@mui/material";
import { theme } from "./theme";

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Box bgcolor="primary.main">
        <Stack direction="column" justifyContent="center">
          <Navbar />
          <Main />
        </Stack>
      </Box>
    </ThemeProvider>
  );
}

export default App;
