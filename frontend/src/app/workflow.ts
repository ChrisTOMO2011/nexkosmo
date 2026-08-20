export const WORKFLOW_STAGES = [
  "idea",
  "discover",
  "shape",
  "build",
  "ready",
  "production",
] as const;

export type WorkflowStage = (typeof WORKFLOW_STAGES)[number];

export type WorkflowStageDefinition = {
  id: WorkflowStage;
  label: string;
  description: string;
};

export const WORKFLOW_STAGE_DEFINITIONS: readonly WorkflowStageDefinition[] = [
  {
    id: "idea",
    label: "IDEA",
    description: "Starting point for a Director's creative intent.",
  },
  {
    id: "discover",
    label: "DISCOVER",
    description: "Story discovery and visual mapping workspace.",
  },
  {
    id: "shape",
    label: "SHAPE",
    description: "Connected screenplay and story-shaping workspace.",
  },
  {
    id: "build",
    label: "BUILD",
    description: "Pre-Production planning and asset definition workspace.",
  },
  {
    id: "ready",
    label: "READY",
    description: "Production-readiness review and validation workspace.",
  },
  {
    id: "production",
    label: "PRODUCTION",
    description: "Production control room and contextual editor entry point.",
  },
] as const;

export function workflowHref(projectId: string, stage: WorkflowStage) {
  return `/studio/projects/${encodeURIComponent(projectId)}/${stage}`;
}

