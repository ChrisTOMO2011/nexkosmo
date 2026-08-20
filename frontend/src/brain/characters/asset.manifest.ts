import type { AssetId, SpeciesId } from "./character.schema";
import { isUuid } from "./character.schema";

export type CharacterAssetCategory =
  | "identity"
  | "face"
  | "hair"
  | "skin"
  | "eyes"
  | "beard"
  | "body"
  | "age-preset"
  | "expression"
  | "wardrobe"
  | "accessory"
  | "rig"
  | "skeleton"
  | "material"
  | "texture"
  | "animation"
  | "voice"
  | "preview"
  | "uploaded-source"
  | "generated-output";

export type CharacterAssetStatus =
  | "development-placeholder"
  | "draft"
  | "available"
  | "needs-review"
  | "approved"
  | "blocked"
  | "archived";

export type AssetCompatibility = Readonly<{
  requiredCapabilities?: readonly string[];
  excludedCapabilities?: readonly string[];
  rigIds?: readonly AssetId[];
  skeletonIds?: readonly AssetId[];
  compatibilityProfileIds?: readonly string[];
}>;

export type CharacterAssetManifest = Readonly<{
  assetId: AssetId;
  name: string;
  speciesIds: readonly SpeciesId[];
  category: CharacterAssetCategory;
  subCategory: string;
  thumbnail: string;
  preview: string;
  tags: readonly string[];
  compatibility: AssetCompatibility;
  dependencies: readonly AssetId[];
  version: number;
  status: CharacterAssetStatus;
  uploaded: boolean;
  generated: boolean;
  createdAt: string;
  updatedAt: string;
}>;

export type SpeciesDevelopmentAssetIds = Readonly<{
  identity: AssetId;
  preview: AssetId;
  rig: AssetId;
  skeleton: AssetId;
  material: AssetId;
  texture: AssetId;
}>;

export function createAssetManifest(
  input: CharacterAssetManifest,
): CharacterAssetManifest {
  if (!isUuid(input.assetId)) throw new Error("Asset IDs must be UUIDs.");
  if (!input.name.trim()) throw new Error("Assets require a name.");
  if (input.version < 1) throw new Error("Asset versions begin at one.");

  return Object.freeze({
    ...input,
    speciesIds: Object.freeze([...input.speciesIds]),
    tags: Object.freeze([...input.tags]),
    dependencies: Object.freeze([...input.dependencies]),
    compatibility: Object.freeze({
      ...input.compatibility,
      requiredCapabilities: Object.freeze([
        ...(input.compatibility.requiredCapabilities ?? []),
      ]),
      excludedCapabilities: Object.freeze([
        ...(input.compatibility.excludedCapabilities ?? []),
      ]),
      rigIds: Object.freeze([...(input.compatibility.rigIds ?? [])]),
      skeletonIds: Object.freeze([
        ...(input.compatibility.skeletonIds ?? []),
      ]),
      compatibilityProfileIds: Object.freeze([
        ...(input.compatibility.compatibilityProfileIds ?? []),
      ]),
    }),
  });
}

function seedUuid(namespace: number, sequence: number): string {
  return `${namespace.toString(16).padStart(8, "0")}-0000-4000-8000-${sequence
    .toString(16)
    .padStart(12, "0")}`;
}

export const speciesSeedIds = {
  human: seedUuid(0x20000001, 1),
  elf: seedUuid(0x20000002, 2),
  goblin: seedUuid(0x20000003, 3),
  orc: seedUuid(0x20000004, 4),
  robot: seedUuid(0x20000005, 5),
  dragon: seedUuid(0x20000006, 6),
  alien: seedUuid(0x20000007, 7),
  monkey: seedUuid(0x20000008, 8),
  demon: seedUuid(0x20000009, 9),
} as const satisfies Record<string, SpeciesId>;

const speciesSeedEntries = Object.entries(speciesSeedIds);

export const developmentAssetIds = Object.fromEntries(
  speciesSeedEntries.map(([key], index) => {
    const base = index * 10;
    return [
      key,
      {
        identity: seedUuid(0x30000001, base + 1),
        preview: seedUuid(0x30000002, base + 2),
        rig: seedUuid(0x30000003, base + 3),
        skeleton: seedUuid(0x30000004, base + 4),
        material: seedUuid(0x30000005, base + 5),
        texture: seedUuid(0x30000006, base + 6),
      },
    ];
  }),
) as Record<keyof typeof speciesSeedIds, SpeciesDevelopmentAssetIds>;

export const characterSeedAssetIds = {
  christopherPreview: seedUuid(0x31000001, 1),
  sarahPreview: seedUuid(0x31000001, 2),
  millerPreview: seedUuid(0x31000001, 3),
  leePreview: seedUuid(0x31000001, 4),
} as const;

const styleNames = [
  "Realistic",
  "Cartoon",
  "Anime",
  "Game",
  "Comic",
  "Stylized",
] as const;

const glassesNames = [
  "Aviator",
  "Wayfarer",
  "Round",
  "Rectangle",
  "Vintage",
  "Clear Frame",
  "Sunglasses",
  "More",
] as const;

const additionalAccessoryGroups = [
  ["hats", ["Fedora", "Beanie", "Wide Brim"]],
  ["facial-hair", ["Moustache", "Goatee", "Sideburns"]],
  ["smoke-pipes", ["Classic Pipe", "Slim Cigarette", "Cigar"]],
  ["pimples-skin", ["Light Freckles", "Skin Texture", "Weathered"]],
  ["scars-marks", ["Brow Scar", "Cheek Scar", "Face Mark"]],
  ["earrings-jewelry", ["Stud", "Hoop", "Chain"]],
  ["masks", ["Half Mask", "Respirator", "Tactical Mask"]],
] as const;

export const styleAssetIds = Object.fromEntries(
  styleNames.map((name, index) => [name, seedUuid(0x32000001, index + 1)]),
) as Record<(typeof styleNames)[number], AssetId>;

export const glassesAssetIds = Object.fromEntries(
  glassesNames.map((name, index) => [name, seedUuid(0x32000002, index + 1)]),
) as Record<(typeof glassesNames)[number], AssetId>;

export const additionalAccessoryAssetIds = Object.fromEntries(
  additionalAccessoryGroups.flatMap(([, names], groupIndex) =>
    names.map((name, nameIndex) => [
      name,
      seedUuid(0x43000001 + groupIndex, nameIndex + 1),
    ]),
  ),
) as Record<string, AssetId>;

const seededAt = "2026-07-28T00:00:00.000Z";

function seedAsset(
  input: Omit<
    CharacterAssetManifest,
    "version" | "status" | "uploaded" | "generated" | "createdAt" | "updatedAt"
  >,
): CharacterAssetManifest {
  return createAssetManifest({
    ...input,
    version: 1,
    status: "development-placeholder",
    uploaded: false,
    generated: false,
    createdAt: seededAt,
    updatedAt: seededAt,
  });
}

const speciesPackageAssets = speciesSeedEntries.flatMap(
  ([speciesKey, speciesId]) => {
    const ids =
      developmentAssetIds[speciesKey as keyof typeof developmentAssetIds];
    const compatibilityProfileId = `character.${speciesKey}.v1`;
    const title = `${speciesKey[0].toUpperCase()}${speciesKey.slice(1)}`;
    const common = {
      speciesIds: [speciesId],
      tags: ["development-seed", speciesKey],
      compatibility: { compatibilityProfileIds: [compatibilityProfileId] },
    };

    return [
      seedAsset({
        ...common,
        assetId: ids.identity,
        name: `${title} Identity Foundation`,
        category: "identity",
        subCategory: "species-default",
        thumbnail: `brain://assets/${ids.identity}/thumbnail`,
        preview: `brain://assets/${ids.identity}/preview`,
        dependencies: [ids.rig, ids.skeleton, ids.material, ids.texture],
      }),
      seedAsset({
        ...common,
        assetId: ids.preview,
        name: `${title} Preview Placeholder`,
        category: "preview",
        subCategory: "character-preview",
        thumbnail: `brain://assets/${ids.preview}/thumbnail`,
        preview: `brain://assets/${ids.preview}/preview`,
        dependencies: [ids.identity],
      }),
      seedAsset({
        ...common,
        assetId: ids.rig,
        name: `${title} Default Rig`,
        category: "rig",
        subCategory: "species-default",
        thumbnail: `brain://assets/${ids.rig}/thumbnail`,
        preview: `brain://assets/${ids.rig}/preview`,
        dependencies: [ids.skeleton],
      }),
      seedAsset({
        ...common,
        assetId: ids.skeleton,
        name: `${title} Default Skeleton`,
        category: "skeleton",
        subCategory: "species-default",
        thumbnail: `brain://assets/${ids.skeleton}/thumbnail`,
        preview: `brain://assets/${ids.skeleton}/preview`,
        dependencies: [],
      }),
      seedAsset({
        ...common,
        assetId: ids.material,
        name: `${title} Base Material`,
        category: "material",
        subCategory: "species-default",
        thumbnail: `brain://assets/${ids.material}/thumbnail`,
        preview: `brain://assets/${ids.material}/preview`,
        dependencies: [ids.texture],
      }),
      seedAsset({
        ...common,
        assetId: ids.texture,
        name: `${title} Base Texture`,
        category: "texture",
        subCategory: "species-default",
        thumbnail: `brain://assets/${ids.texture}/thumbnail`,
        preview: `brain://assets/${ids.texture}/preview`,
        dependencies: [],
      }),
    ];
  },
);

const rosterPreviewAssets = [
  [characterSeedAssetIds.christopherPreview, "Christopher Preview", "avatar-chris"],
  [characterSeedAssetIds.sarahPreview, "Sarah Preview", "avatar-sarah"],
  [characterSeedAssetIds.millerPreview, "Detective Miller Preview", "avatar-miller"],
  [characterSeedAssetIds.leePreview, "Dr. Lee Preview", "avatar-lee"],
] as const;

export const developmentCharacterAssetManifest: readonly CharacterAssetManifest[] =
  Object.freeze([
    ...speciesPackageAssets,
    ...rosterPreviewAssets.map(([assetId, name, visualToken]) =>
      seedAsset({
        assetId,
        name,
        speciesIds: [speciesSeedIds.human],
        category: "preview",
        subCategory: "roster",
        thumbnail: `ui-token://${visualToken}`,
        preview: `brain://assets/${assetId}/preview`,
        tags: ["development-seed", "roster"],
        compatibility: {
          compatibilityProfileIds: ["character.human.v1"],
        },
        dependencies: [],
      }),
    ),
    ...styleNames.map((name) =>
      seedAsset({
        assetId: styleAssetIds[name],
        name,
        speciesIds: Object.values(speciesSeedIds),
        category: "identity",
        subCategory: "visual-style",
        thumbnail: `brain://assets/${styleAssetIds[name]}/thumbnail`,
        preview: `brain://assets/${styleAssetIds[name]}/preview`,
        tags: ["development-seed", "style"],
        compatibility: {},
        dependencies: [],
      }),
    ),
    ...glassesNames.map((name) =>
      seedAsset({
        assetId: glassesAssetIds[name],
        name,
        speciesIds: [
          speciesSeedIds.human,
          speciesSeedIds.elf,
          speciesSeedIds.goblin,
          speciesSeedIds.orc,
          speciesSeedIds.monkey,
          speciesSeedIds.demon,
        ],
        category: "accessory",
        subCategory: name === "More" ? "more" : "glasses",
        thumbnail: `brain://assets/${glassesAssetIds[name]}/thumbnail`,
        preview: `brain://assets/${glassesAssetIds[name]}/preview`,
        tags: [
          "development-seed",
          "accessory",
          name === "More" ? "more" : "glasses",
        ],
        compatibility: { requiredCapabilities: ["wears-accessories"] },
        dependencies: [],
      }),
    ),
    ...additionalAccessoryGroups.flatMap(([subCategory, names]) =>
      names.map((name) =>
        seedAsset({
          assetId: additionalAccessoryAssetIds[name],
          name,
          speciesIds: [
            speciesSeedIds.human,
            speciesSeedIds.elf,
            speciesSeedIds.goblin,
            speciesSeedIds.orc,
            speciesSeedIds.monkey,
            speciesSeedIds.demon,
          ],
          category: "accessory",
          subCategory,
          thumbnail: `brain://assets/${additionalAccessoryAssetIds[name]}/thumbnail`,
          preview: `brain://assets/${additionalAccessoryAssetIds[name]}/preview`,
          tags: ["development-seed", "accessory", subCategory],
          compatibility: { requiredCapabilities: ["wears-accessories"] },
          dependencies: [],
        }),
      ),
    ),
  ]);
