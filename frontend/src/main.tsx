import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { AppRoutes } from "./app/App";
import "./styles/tokens.css";
import "./styles/studio.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AppRoutes />
  </StrictMode>,
);
