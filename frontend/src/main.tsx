import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { AppRoutes } from "./app/App";
import "./styles/tokens.css";
import "./styles/base.css";
import "./styles/components.css";
import "./styles/studio.css";
import "./styles/character-identity.css";
import "./styles/workflow-scaffolds.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AppRoutes />
  </StrictMode>,
);
