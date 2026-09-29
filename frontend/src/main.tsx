import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import App from "./App";
import "./styles.css";

const theme = createTheme({
  palette: {
    mode: "dark",
    background: { default: "#07070b", paper: "#11111a" },
    primary: { main: "#9b7cff" },
    secondary: { main: "#58d6c4" },
    success: { main: "#54d38a" },
    warning: { main: "#f2b85b" },
    error: { main: "#ff6b86" },
    text: { primary: "#f5f3ff", secondary: "#a7a4b8" }
  },
  typography: {
    fontFamily: '"Inter", "Segoe UI", Arial, sans-serif',
    h4: { fontWeight: 800, letterSpacing: "-0.04em" },
    h5: { fontWeight: 750, letterSpacing: "-0.03em" },
    button: { textTransform: "none", fontWeight: 700 }
  },
  shape: { borderRadius: 16 },
  components: {
    MuiButton: { defaultProps: { disableElevation: true } },
    MuiCard: { styleOverrides: { root: { backgroundImage: "none" } } },
    MuiTextField: { defaultProps: { variant: "outlined", size: "small" } }
  }
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <App />
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
);
