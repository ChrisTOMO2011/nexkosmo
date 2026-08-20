import { AlertCircle } from "lucide-react";
import { CanonicalLogo } from "../brand/CanonicalLogo";
import { Panel } from "../ui";

type SafeRouteStateProps = {
  kind: "project-required" | "invalid-context" | "not-found";
};

const copy = {
  "project-required": {
    title: "Project context required",
    body: "Select a project before entering the creator workflow. No project has been assumed.",
  },
  "invalid-context": {
    title: "Project context is invalid",
    body: "The project identifier in this address cannot be used. No fallback identity has been created.",
  },
  "not-found": {
    title: "Page not found",
    body: "This address is not part of the canonical Nexkosmo shell routes.",
  },
} as const;

export function SafeRouteState({ kind }: SafeRouteStateProps) {
  const message = copy[kind];
  return (
    <div className="safe-route-state">
      <CanonicalLogo />
      <main>
        <Panel className="safe-route-state__panel" role="status">
          <AlertCircle aria-hidden="true" />
          <h1>{message.title}</h1>
          <p>{message.body}</p>
        </Panel>
      </main>
    </div>
  );
}

