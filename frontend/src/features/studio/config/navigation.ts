import {
  AudioLines,
  Box,
  Camera,
  Car,
  Clapperboard,
  Cuboid,
  LayoutDashboard,
  Lightbulb,
  Music2,
  PlaySquare,
  SlidersHorizontal,
  Sparkles,
  Users,
  WandSparkles,
  type LucideIcon,
} from "lucide-react";

export type WorkflowStageId =
  | "idea"
  | "discover"
  | "shape"
  | "build"
  | "ready"
  | "production";

export type ProductionWorkspaceId = "set" | "studio" | "render";

export type WorkflowStage = {
  id: WorkflowStageId;
  label: string;
};

export type StudioNavItem = {
  label: string;
  icon: LucideIcon;
};

export const workflowStages: readonly WorkflowStage[] = [
  { id: "idea", label: "IDEA" },
  { id: "discover", label: "DISCOVER" },
  { id: "shape", label: "SHAPE" },
  { id: "build", label: "BUILD" },
  { id: "ready", label: "READY" },
  { id: "production", label: "PRODUCTION" },
];

export const preProductionNavigation: readonly StudioNavItem[] = [
  { label: "Characters", icon: Users },
  { label: "Environment", icon: Clapperboard },
  { label: "Camera Gear", icon: Camera },
  { label: "Lighting", icon: Lightbulb },
  { label: "Audio", icon: Music2 },
  { label: "VFX", icon: Sparkles },
  { label: "Props", icon: Box },
  { label: "Vehicles", icon: Car },
];

export const workflowScaffoldNavigation: Record<
  ProductionWorkspaceId,
  readonly StudioNavItem[]
> = {
  set: [{ label: "Set Overview", icon: LayoutDashboard }],
  studio: [{ label: "Studio Overview", icon: PlaySquare }],
  render: [{ label: "Render Overview", icon: SlidersHorizontal }],
};

export const aiTools: readonly StudioNavItem[] = [
  { label: "AI Director", icon: WandSparkles },
  { label: "AI Copilot", icon: AudioLines },
];

export const advancedStudios = [
  {
    label: "CGI Studio",
    detail: "Character & Creature",
    icon: Cuboid,
    tone: "green",
  },
  {
    label: "VFX Studio",
    detail: "Particles & Effects",
    icon: Sparkles,
    tone: "blue",
  },
  {
    label: "Colour Studio",
    detail: "Grading & Looks",
    icon: Lightbulb,
    tone: "orange",
  },
  {
    label: "Audio Studio",
    detail: "Mixing & Mastering",
    icon: AudioLines,
    tone: "purple",
  },
] as const;

export function workflowHref(
  projectId: string,
  stage: WorkflowStageId,
  characterId = "christopher",
) {
  const safeProjectId = encodeURIComponent(projectId);
  const safeCharacterId = encodeURIComponent(characterId);
  if (stage === "idea") {
    return `/studio/projects/${safeProjectId}/idea`;
  }
  if (stage === "discover") {
    return `/discovery?projectId=${safeProjectId}&characterId=${safeCharacterId}`;
  }
  if (stage === "shape") {
    return `/studio/projects/${safeProjectId}/script`;
  }
  if (stage === "build") {
    return `/studio/projects/${safeProjectId}/pre-production/characters/${safeCharacterId}`;
  }
  if (stage === "ready") {
    return `/studio/projects/${safeProjectId}/ready`;
  }
  return `/studio/projects/${safeProjectId}/studio`;
}

export function productionWorkspaceHref(
  projectId: string,
  workspace: ProductionWorkspaceId,
) {
  return `/studio/projects/${encodeURIComponent(projectId)}/${workspace}`;
}
