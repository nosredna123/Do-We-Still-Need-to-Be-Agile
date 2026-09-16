import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    background: {
      default: "#f8fafc",
    },
    primary: {
      main: "#9cbde8",
    },
    secondary: {
      main: "#a7e5cb",
    },
    success: {
      main: "#2d5c48",
    },
  },
  shape: {
    borderRadius: 16,
  },
  typography: {
    fontFamily: `"Roboto", "Helvetica", "Arial", sans-serif`,
  },
});