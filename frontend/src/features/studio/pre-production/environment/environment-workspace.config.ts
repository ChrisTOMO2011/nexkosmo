import type { Environment } from "../../../../brain/environments";

export const environmentTabs = [
  "Identity",
  "Terrain",
  "Buildings",
  "Nature",
  "Weather",
  "Time",
  "Atmosphere",
  "Materials",
  "Details",
] as const;

export const environmentCategoryByTab: Readonly<Record<string, string | undefined>> = {
  Identity: undefined,
  Terrain: "terrain",
  Buildings: "building",
  Nature: "nature",
  Weather: "weather-profile",
  Time: undefined,
  Atmosphere: "atmosphere-profile",
  Materials: "material",
  Details: "detail",
};

export const environmentMultiCategories = new Set([
  "terrain",
  "building",
  "nature",
  "material",
  "detail",
]);

export function selectedEnvironmentAssetIds(
  environment: Environment,
  category?: string,
) {
  const values: Record<string, readonly string[]> = {
    "terrain-profile": environment.terrainProfileId ? [environment.terrainProfileId] : [],
    "weather-profile": environment.weatherProfileId ? [environment.weatherProfileId] : [],
    "atmosphere-profile": environment.atmosphereProfileId
      ? [environment.atmosphereProfileId]
      : [],
    "style-profile": environment.styleProfileId ? [environment.styleProfileId] : [],
    terrain: environment.terrainAssetIds,
    building: environment.buildingAssetIds,
    nature: environment.natureAssetIds,
    background: environment.backgroundAssetIds,
    practical: environment.practicalAssetIds,
    material: environment.materialProfileIds,
    texture: environment.textureProfileIds,
    detail: environment.detailAssetIds,
  };
  return category ? [...(values[category] ?? [])] : [];
}

export function environmentTitleCase(value: string) {
  return value.replaceAll("-", " ").replace(/\b\w/gu, (letter) => letter.toUpperCase());
}
