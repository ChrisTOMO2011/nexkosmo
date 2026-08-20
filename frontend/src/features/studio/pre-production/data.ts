import {
  characterAssetService,
  characterPipelineService,
  speciesRegistry,
  speciesSeedIds,
  type AssetId,
  type Character as CanonicalCharacter,
} from "../../../brain/characters";

export type Character = {
  id: string;
  name: string;
  role: string;
  crop: string;
};

export function toCharacterView(character: CanonicalCharacter): Character {
  return {
    id: character.characterId,
    name: character.displayName,
    role: character.role,
    crop:
      characterAssetService.resolveUiToken(character.previewAssetId) ??
      "avatar-chris",
  };
}

export function resolveCharacterFromRoute(
  characters: readonly Character[],
  routeCharacterId: string,
) {
  const normalizedRoute = routeCharacterId.trim().toLocaleLowerCase();
  return (
    characters.find((character) => character.id === routeCharacterId) ??
    characters.find(
      (character) =>
        character.name
          .trim()
          .toLocaleLowerCase()
          .replaceAll(/[^a-z0-9]+/gu, "-")
          .replaceAll(/^-|-$/gu, "") === normalizedRoute,
    ) ??
    characters[0]
  );
}

const visibleEditorTabs = new Set([
  "Identity",
  "Face",
  "Hair",
  "Skin",
  "Eyes",
  "Beard",
  "Age",
  "Expression",
]);

export const editorTabs = speciesRegistry
  .require(speciesSeedIds.human)
  .supportedTabs.filter((tab) => visibleEditorTabs.has(tab));

export const styles = characterAssetService
  .list({ category: "identity", subCategory: "visual-style" })
  .map((asset) => asset.name);

const featuredSpecies = speciesRegistry.list({
  enabledOnly: true,
  featuredOnly: true,
});

export const species = featuredSpecies.map((entry) => entry.name);

export const speciesFilters = [
  "All",
  ...featuredSpecies.slice(0, 6).map((entry) => entry.name),
  "More",
];

export const accessoryTabs = [
  "Glasses",
  "Hats",
  "Facial Hair",
  "Smoke & Pipes",
  "Pimples & Skin",
  "Scars & Marks",
  "Earrings & Jewellery",
  "Masks",
  "More",
] as const;

export const accessorySubcategories: Record<
  (typeof accessoryTabs)[number],
  string
> = {
  Glasses: "glasses",
  Hats: "hats",
  "Facial Hair": "facial-hair",
  "Smoke & Pipes": "smoke-pipes",
  "Pimples & Skin": "pimples-skin",
  "Scars & Marks": "scars-marks",
  "Earrings & Jewellery": "earrings-jewelry",
  Masks: "masks",
  More: "more",
};

export const glasses = [
  "Upload",
  "AI Generate",
  ...characterAssetService
    .list({ category: "accessory", subCategory: "glasses" })
    .map((asset) => asset.name),
];

export function getSpeciesId(name: string) {
  return speciesRegistry.findByName(name)?.id;
}

export function getSpeciesName(characterId: string) {
  const character = characterPipelineService.loadCharacter(characterId);
  return speciesRegistry.require(character.speciesId).name;
}

export async function getSpeciesNameFromSource(speciesId: string) {
  return (
    await characterPipelineService.gateway.getSpecies(speciesId)
  )?.name;
}

export function getStyleAssetId(name: string): AssetId | undefined {
  return characterAssetService
    .list({ category: "identity", subCategory: "visual-style" })
    .find((asset) => asset.name === name)?.assetId;
}

export function getStyleName(assetId?: AssetId) {
  return assetId
    ? characterAssetService
        .list({ category: "identity", subCategory: "visual-style" })
        .find((asset) => asset.assetId === assetId)?.name
    : undefined;
}

export function getAccessoryAssetId(name: string): AssetId | undefined {
  return characterAssetService
    .list({ category: "accessory", subCategory: "glasses" })
    .find((asset) => asset.name === name)?.assetId;
}

export function getAccessoryName(assetId?: AssetId) {
  return assetId
    ? characterAssetService
        .list({ category: "accessory", subCategory: "glasses" })
        .find((asset) => asset.assetId === assetId)?.name
    : undefined;
}

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
    crop: "avatar-chris",
  },
] as const;
