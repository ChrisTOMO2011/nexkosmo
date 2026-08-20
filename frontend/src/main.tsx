import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { AppRoutes } from "./app/App";
import "./styles/tokens.css";
import "./styles/base.css";
import "./styles/components.css";
import "./styles/landing.css";
import "./styles/discovery.css";
import "./styles/build-moment.css";
import "./styles/studio.css";
import "./styles/character-identity.css";
import "./styles/character-identity-studio-v1.css";
import "./styles/workflow-scaffolds.css";
import "./styles/creator-workflow.css";
import "./styles/script-workspace.css";
import "./styles/build-workspace-density.css";
import "./styles/idea-workspace.css";
import "./styles/ready-workspace.css";
import "./styles/production-workspace.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AppRoutes />
  </StrictMode>,
);
