import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./index.css";
import App from "./App.jsx";

import { ScrollSmoother } from "gsap/ScrollSmoother";
import { ScrollTrigger } from "gsap/ScrollTrigger";

import { FlashcardProvider } from "./contexts/FlashcardContext";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <FlashcardProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </FlashcardProvider>
  </StrictMode>
);

