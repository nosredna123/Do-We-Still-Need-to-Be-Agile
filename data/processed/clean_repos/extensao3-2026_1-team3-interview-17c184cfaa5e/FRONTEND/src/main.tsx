import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { ThemeModeProvider } from "./contexts/ThemeModeContext";
import { LoadingProvider } from "./contexts/LoadingContext";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ThemeModeProvider>
      <LoadingProvider>
      <App />
      </LoadingProvider>
    </ThemeModeProvider>
  </React.StrictMode>
);