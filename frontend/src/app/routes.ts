import type { WorkflowStageId } from "../features/studio/config/navigation";

export type StudioRoute =
  | {
      kind: "character";
      projectId: string;
      characterId: string;
      stage: "pre-production";
    }
  | {
      kind: "workflow";
      projectId: string;
      stage: Exclude<WorkflowStageId, "pre-production">;
    }
  | { kind: "not-found" };

const characterRoute =
  /^\/studio\/projects\/([^/]+)\/pre-production\/characters\/([^/]+)\/?$/;
const workflowRoute =
  /^\/studio\/projects\/([^/]+)\/(set|studio|review|render)\/?$/;

export function resolveStudioRoute(pathname: string): StudioRoute {
  const characterMatch = pathname.match(characterRoute);
  if (characterMatch) {
    return {
      kind: "character",
      projectId: decodeURIComponent(characterMatch[1]),
      characterId: decodeURIComponent(characterMatch[2]),
      stage: "pre-production",
    };
  }

  const workflowMatch = pathname.match(workflowRoute);
  if (workflowMatch) {
    return {
      kind: "workflow",
      projectId: decodeURIComponent(workflowMatch[1]),
      stage: workflowMatch[2] as Exclude<
        WorkflowStageId,
        "pre-production"
      >,
    };
  }

  return { kind: "not-found" };
}
