import {
  AudioLines,
  Box,
  Camera,
  Car,
  Clapperboard,
  Cuboid,
  LayoutDashboard,
  Lightbulb,
  MessageSquare,
  Music2,
  PlaySquare,
  SlidersHorizontal,
  Sparkles,
  Users,
  WandSparkles,
  type LucideIcon,
} from "lucide-react";

export type WorkflowStageId =
  | "pre-production"
  | "set"
  | "studio"
  | "review"
  | "render";

export type WorkflowStage = {
  id: WorkflowStageId;
  label: string;
};

export type StudioNavItem = {
  label: string;
  icon: LucideIcon;
};

export const workflowStages: readonly WorkflowStage[] = [
  { id: "pre-production", label: "PRE-PRODUCTION" },
  { id: "set", label: "SET" },
  { id: "studio", label: "STUDIO" },
  { id: "review", label: "REVIEW" },
  { id: "render", label: "RENDER" },
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
  Exclude<WorkflowStageId, "pre-production">,
  readonly StudioNavItem[]
> = {
  set: [{ label: "Set Overview", icon: LayoutDashboard }],
  studio: [{ label: "Studio Overview", icon: PlaySquare }],
  review: [{ label: "Review Overview", icon: MessageSquare }],
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
  if (stage === "pre-production") {
    return `/studio/projects/${projectId}/pre-production/characters/${characterId}`;
  }
  return `/studio/projects/${projectId}/${stage}`;
}
