import { WORKFLOW_STAGES, type WorkflowStage } from "./workflow";

export type AppRoute =
  | { kind: "stage"; projectId: string; stage: WorkflowStage }
  | { kind: "auth-callback" }
  | { kind: "project-required" }
  | { kind: "invalid-context" }
  | { kind: "not-found" };

const stageRoute =
  /^\/studio\/projects\/([^/]+)\/(idea|discover|shape|build|ready|production)\/?$/;
const validIdentifier = /^[a-z0-9][a-z0-9_-]{0,127}$/iu;

export function resolveAppRoute(pathname: string): AppRoute {
  if (pathname === "/auth/callback") return { kind: "auth-callback" };
  if (
    pathname === "/" ||
    pathname === "/index.html" ||
    pathname === "/studio" ||
    pathname === "/studio/"
  ) {
    return { kind: "project-required" };
  }

  const match = pathname.match(stageRoute);
  if (!match) {
    return { kind: "not-found" };
  }

  let projectId: string;
  try {
    projectId = decodeURIComponent(match[1]);
  } catch {
    return { kind: "invalid-context" };
  }

  if (!validIdentifier.test(projectId)) {
    return { kind: "invalid-context" };
  }

  const stage = match[2] as WorkflowStage;
  if (!WORKFLOW_STAGES.includes(stage)) {
    return { kind: "not-found" };
  }

  return { kind: "stage", projectId, stage };
}
