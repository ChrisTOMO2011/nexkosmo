import type {
  CharacterAssetCategory,
  CharacterAssetManifest,
} from "./asset.manifest";
import {
  characterAssetService,
  type CharacterAssetService,
} from "./asset.service";
import type {
  AssetId,
  Character,
  CharacterEditorTab,
  CharacterSelectionPatch,
  SpeciesId,
} from "./character.schema";
import {
  speciesRegistry,
  type SpeciesRegistry,
  type SpeciesRegistryEntry,
} from "./species.registry";

export type CompatibilityIssue = Readonly<{
  field: keyof CharacterSelectionPatch;
  assetId: AssetId;
  reason: string;
}>;

export type CompatibilityValidation = Readonly<{
  valid: boolean;
  issues: readonly CompatibilityIssue[];
}>;

const scalarSelectionFields = {
  typeId: "identity",
  identityId: "identity",
  faceId: "face",
  hairId: "hair",
  skinId: "skin",
  eyesId: "eyes",
  beardId: "beard",
  bodyId: "body",
  agePresetId: "age-preset",
  expressionId: "expression",
  rigId: "rig",
  skeletonId: "skeleton",
  voiceId: "voice",
} as const satisfies Partial<
  Record<keyof CharacterSelectionPatch, CharacterAssetCategory>
>;

const arraySelectionFields = {
  wardrobeIds: "wardrobe",
  accessoryIds: "accessory",
  materialIds: "material",
  textureIds: "texture",
  animationIds: "animation",
} as const satisfies Partial<
  Record<keyof CharacterSelectionPatch, CharacterAssetCategory>
>;

function supportsManifest(
  manifest: CharacterAssetManifest,
  species: SpeciesRegistryEntry,
  selection: Pick<Character, "rigId" | "skeletonId">,
) {
  const compatibility = manifest.compatibility;
  const speciesSupported =
    manifest.speciesIds.length === 0 ||
    manifest.speciesIds.includes(species.id);
  const capabilitiesSupported = (
    compatibility.requiredCapabilities ?? []
  ).every((capability) => species.capabilities.includes(capability));
  const capabilitiesExcluded = (
    compatibility.excludedCapabilities ?? []
  ).some((capability) => species.capabilities.includes(capability));
  const profileSupported =
    !compatibility.compatibilityProfileIds?.length ||
    compatibility.compatibilityProfileIds.includes(
      species.compatibilityProfile,
    );
  const rigSupported =
    !compatibility.rigIds?.length ||
    (selection.rigId !== undefined &&
      compatibility.rigIds.includes(selection.rigId));
  const skeletonSupported =
    !compatibility.skeletonIds?.length ||
    (selection.skeletonId !== undefined &&
      compatibility.skeletonIds.includes(selection.skeletonId));

  return (
    speciesSupported &&
    capabilitiesSupported &&
    !capabilitiesExcluded &&
    profileSupported &&
    rigSupported &&
    skeletonSupported
  );
}

export function getCompatibleAssets(
  character: Pick<Character, "speciesId" | "rigId" | "skeletonId">,
  category?: CharacterAssetCategory,
  assets: CharacterAssetService = characterAssetService,
  registry: SpeciesRegistry = speciesRegistry,
) {
  const species = registry.require(character.speciesId);
  return assets
    .list({ category, speciesId: character.speciesId })
    .filter((manifest) => supportsManifest(manifest, species, character));
}

export function validateSelection(
  character: Character,
  assets: CharacterAssetService = characterAssetService,
  registry: SpeciesRegistry = speciesRegistry,
): CompatibilityValidation {
  const compatibleIds = new Set(
    getCompatibleAssets(character, undefined, assets, registry).map(
      (asset) => asset.assetId,
    ),
  );
  const issues: CompatibilityIssue[] = [];
  const selectedIds = new Set<AssetId>();

  for (const field of Object.keys(
    scalarSelectionFields,
  ) as (keyof typeof scalarSelectionFields)[]) {
    const assetId = character[field];
    if (assetId) selectedIds.add(assetId);
  }
  for (const field of Object.keys(
    arraySelectionFields,
  ) as (keyof typeof arraySelectionFields)[]) {
    character[field].forEach((assetId) => selectedIds.add(assetId));
  }

  for (const field of Object.keys(
    scalarSelectionFields,
  ) as (keyof typeof scalarSelectionFields)[]) {
    const assetId = character[field];
    if (assetId && !compatibleIds.has(assetId)) {
      issues.push({
        field,
        assetId,
        reason: "Asset is incompatible with the active species profile.",
      });
    } else if (assetId) {
      const missingDependency = assets
        .require(assetId)
        .dependencies.find((dependency) => !selectedIds.has(dependency));
      if (missingDependency) {
        issues.push({
          field,
          assetId,
          reason: `Asset dependency is not selected: ${missingDependency}`,
        });
      }
    }
  }

  for (const field of Object.keys(
    arraySelectionFields,
  ) as (keyof typeof arraySelectionFields)[]) {
    for (const assetId of character[field]) {
      if (!compatibleIds.has(assetId)) {
        issues.push({
          field,
          assetId,
          reason: "Asset is incompatible with the active species profile.",
        });
      } else {
        const missingDependency = assets
          .require(assetId)
          .dependencies.find((dependency) => !selectedIds.has(dependency));
        if (missingDependency) {
          issues.push({
            field,
            assetId,
            reason: `Asset dependency is not selected: ${missingDependency}`,
          });
        }
      }
    }
  }

  return Object.freeze({ valid: issues.length === 0, issues });
}

export function resolveDefaultAssets(
  speciesId: SpeciesId,
  registry: SpeciesRegistry = speciesRegistry,
  assets: CharacterAssetService = characterAssetService,
) {
  const species = registry.require(speciesId);
  const manifests = species.assetManifest.map((assetId) =>
    assets.require(assetId),
  );
  const find = (category: CharacterAssetCategory) =>
    manifests.find((manifest) => manifest.category === category)?.assetId;
  return Object.freeze({
    identityId: find("identity"),
    previewAssetId: find("preview"),
    rigId: species.defaultRig,
    skeletonId: species.defaultSkeleton,
    materialIds: find("material")
      ? Object.freeze([find("material") as AssetId])
      : Object.freeze([]),
    textureIds: find("texture")
      ? Object.freeze([find("texture") as AssetId])
      : Object.freeze([]),
    compatibilityProfileId: species.compatibilityProfile,
  });
}

export function clearInvalidSelections(
  character: Character,
  assets: CharacterAssetService = characterAssetService,
  registry: SpeciesRegistry = speciesRegistry,
): CharacterSelectionPatch {
  const invalid = validateSelection(character, assets, registry).issues;
  const invalidByField = new Map<keyof CharacterSelectionPatch, Set<AssetId>>();
  invalid.forEach((issue) => {
    const ids = invalidByField.get(issue.field) ?? new Set<AssetId>();
    ids.add(issue.assetId);
    invalidByField.set(issue.field, ids);
  });

  const patch: CharacterSelectionPatch = {};
  for (const field of Object.keys(
    scalarSelectionFields,
  ) as (keyof typeof scalarSelectionFields)[]) {
    if (invalidByField.has(field)) Object.assign(patch, { [field]: undefined });
  }
  for (const field of Object.keys(
    arraySelectionFields,
  ) as (keyof typeof arraySelectionFields)[]) {
    const invalidIds = invalidByField.get(field);
    if (invalidIds) {
      Object.assign(patch, {
        [field]: character[field].filter((id) => !invalidIds.has(id)),
      });
    }
  }
  return patch;
}

export function resolveSupportedTabs(
  speciesId: SpeciesId,
  registry: SpeciesRegistry = speciesRegistry,
): readonly CharacterEditorTab[] {
  return registry.require(speciesId).supportedTabs;
}

export function resolveRig(
  speciesId: SpeciesId,
  registry: SpeciesRegistry = speciesRegistry,
): AssetId {
  return registry.require(speciesId).defaultRig;
}

export function resolveMaterials(
  speciesId: SpeciesId,
  registry: SpeciesRegistry = speciesRegistry,
): readonly AssetId[] {
  return resolveDefaultAssets(speciesId, registry).materialIds;
}
