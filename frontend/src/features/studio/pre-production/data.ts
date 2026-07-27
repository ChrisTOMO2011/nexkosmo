import {
  AudioLines,
  Box,
  Camera,
  Car,
  Clapperboard,
  Cuboid,
  Lightbulb,
  Music2,
  Sparkles,
  Users,
  WandSparkles,
  type LucideIcon,
} from "lucide-react";

export type NavItem = {
  label: string;
  icon: LucideIcon;
};

export const workflowStages = [
  "PRE-PRODUCTION",
  "SET",
  "STUDIO",
  "REVIEW",
  "RENDER",
] as const;

export const productionNav: NavItem[] = [
  { label: "Characters", icon: Users },
  { label: "Environment", icon: Clapperboard },
  { label: "Camera Gear", icon: Camera },
  { label: "Lighting", icon: Lightbulb },
  { label: "Audio", icon: Music2 },
  { label: "VFX", icon: Sparkles },
  { label: "Props", icon: Box },
  { label: "Vehicles", icon: Car },
];

export const aiTools: NavItem[] = [
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

export type Character = {
  id: string;
  name: string;
  role: string;
  crop: string;
};

export const initialCharacters: Character[] = [
  { id: "christopher", name: "Christopher", role: "Lead", crop: "avatar-chris" },
  { id: "sarah", name: "Sarah", role: "Co-Lead", crop: "avatar-sarah" },
  {
    id: "detective-miller",
    name: "Detective Miller",
    role: "Supporting",
    crop: "avatar-miller",
  },
  { id: "dr-lee", name: "Dr. Lee", role: "Supporting", crop: "avatar-lee" },
];

export const editorTabs = [
  "Identity",
  "Face",
  "Hair",
  "Skin",
  "Eyes",
  "Beard",
  "Age",
  "Expression",
] as const;

export const styles = [
  "Realistic",
  "Cartoon",
  "Anime",
  "Game",
  "Comic",
  "Stylized",
] as const;

export const speciesFilters = [
  "All",
  "Human",
  "Elf",
  "Orc",
  "Robot",
  "Dragon",
  "Alien",
  "More",
] as const;

export const species = [
  "Human",
  "Elf",
  "Orc",
  "Robot",
  "Dragon",
  "Alien",
  "Monkey",
  "Demon",
] as const;

export const accessoryTabs = [
  "Glasses",
  "Hats",
  "Facial Hair",
  "Smoke & Pipes",
  "Pimples & Skin",
  "Scars & Marks",
  "Earrings & Jewelry",
  "Masks",
] as const;

export const glasses = [
  "Upload",
  "AI Generate",
  "Aviator",
  "Wayfarer",
  "Round",
  "Rectangle",
  "Vintage",
  "Clear Frame",
  "Sunglasses",
  "More",
] as const;

export const suggestions = [
  {
    id: "detective",
    title: "Detective Look",
    body: "Glasses and light stubble suit this noir scene.",
    crop: "avatar-miller",
  },
  {
    id: "rugged",
    title: "Rugged Style",
    body: "Adds grit and realism to close-up shots.",
    crop: "avatar-chris",
  },
  {
    id: "villain",
    title: "Villain Vibe",
    body: "Dark glasses and scars for a more intense look.",
    crop: "avatar-sarah",
  },
] as const;
