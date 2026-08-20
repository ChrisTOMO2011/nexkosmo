import {
  developmentAssetIds,
  speciesSeedIds,
  type SpeciesDevelopmentAssetIds,
} from "./asset.manifest";
import type {
  AssetId,
  CharacterEditorTab,
  CompatibilityProfileId,
  SpeciesId,
} from "./character.schema";

export type SpeciesCategory =
  | "humanoid"
  | "creature"
  | "synthetic"
  | "extraterrestrial";

export type SpeciesRegistryEntry = Readonly<{
  id: SpeciesId;
  name: string;
  category: SpeciesCategory;
  thumbnail: AssetId;
  enabled: boolean;
  capabilities: readonly string[];
  defaultRig: AssetId;
  defaultSkeleton: AssetId;
  compatibilityProfile: CompatibilityProfileId;
  supportedTabs: readonly CharacterEditorTab[];
  assetManifest: readonly AssetId[];
  featured: boolean;
  displayOrder: number;
}>;

const supportedTabsBySpecies: Record<
  keyof typeof speciesSeedIds,
  readonly CharacterEditorTab[]
> = {
  human: ["Identity", "Face", "Hair", "Skin", "Eyes", "Beard", "Age", "Expression"],
  elf: ["Identity", "Face", "Hair", "Skin", "Eyes", "Age", "Expression"],
  goblin: ["Identity", "Face", "Skin", "Eyes", "Age", "Expression"],
  orc: ["Identity", "Face", "Hair", "Skin", "Eyes", "Beard", "Age", "Expression"],
  robot: ["Identity", "Face", "Skin", "Eyes", "Expression"],
  dragon: ["Identity", "Skin", "Eyes", "Age", "Expression"],
  alien: ["Identity", "Face", "Skin", "Eyes", "Age", "Expression"],
  monkey: ["Identity", "Face", "Hair", "Skin", "Eyes", "Age", "Expression"],
  demon: ["Identity", "Face", "Skin", "Eyes", "Age", "Expression"],
};

function createSpecies(
  key: keyof typeof speciesSeedIds,
  name: string,
  category: SpeciesCategory,
  capabilities: readonly string[],
  displayOrder: number,
  featured = true,
): SpeciesRegistryEntry {
  const assets: SpeciesDevelopmentAssetIds = developmentAssetIds[key];
  return Object.freeze({
    id: speciesSeedIds[key],
    name,
    category,
    thumbnail: assets.preview,
    enabled: true,
    capabilities: Object.freeze([...capabilities]),
    defaultRig: assets.rig,
    defaultSkeleton: assets.skeleton,
    compatibilityProfile: `character.${key}.v1`,
    supportedTabs: Object.freeze([...supportedTabsBySpecies[key]]),
    assetManifest: Object.freeze(Object.values(assets)),
    featured,
    displayOrder,
  });
}

export const seededSpecies: readonly SpeciesRegistryEntry[] = Object.freeze([
  createSpecies(
    "human",
    "Human",
    "humanoid",
    ["facial-animation", "hair", "beard", "wears-accessories", "voice"],
    1,
  ),
  createSpecies(
    "elf",
    "Elf",
    "humanoid",
    ["facial-animation", "hair", "wears-accessories", "voice"],
    2,
  ),
  createSpecies(
    "goblin",
    "Goblin",
    "humanoid",
    ["facial-animation", "wears-accessories", "voice"],
    9,
    false,
  ),
  createSpecies(
    "orc",
    "Orc",
    "humanoid",
    ["facial-animation", "hair", "beard", "wears-accessories", "voice"],
    3,
  ),
  createSpecies(
    "robot",
    "Robot",
    "synthetic",
    ["facial-animation", "modular-body", "voice"],
    4,
  ),
  createSpecies(
    "dragon",
    "Dragon",
    "creature",
    ["facial-animation", "creature-rig", "voice"],
    5,
  ),
  createSpecies(
    "alien",
    "Alien",
    "extraterrestrial",
    ["facial-animation", "modular-body", "voice"],
    6,
  ),
  createSpecies(
    "monkey",
    "Monkey",
    "creature",
    ["facial-animation", "hair", "wears-accessories", "voice"],
    7,
  ),
  createSpecies(
    "demon",
    "Demon",
    "creature",
    ["facial-animation", "wears-accessories", "voice"],
    8,
  ),
]);

export class SpeciesRegistry {
  readonly #entries: readonly SpeciesRegistryEntry[];
  readonly #byId: ReadonlyMap<SpeciesId, SpeciesRegistryEntry>;

  constructor(entries: readonly SpeciesRegistryEntry[]) {
    this.#entries = Object.freeze(
      [...entries].sort((left, right) => left.displayOrder - right.displayOrder),
    );
    this.#byId = new Map(this.#entries.map((entry) => [entry.id, entry]));
  }

  list(options: { enabledOnly?: boolean; featuredOnly?: boolean } = {}) {
    return this.#entries.filter(
      (entry) =>
        (!options.enabledOnly || entry.enabled) &&
        (!options.featuredOnly || entry.featured),
    );
  }

  get(id: SpeciesId) {
    return this.#byId.get(id);
  }

  require(id: SpeciesId) {
    const species = this.get(id);
    if (!species) throw new Error(`Unknown species ID: ${id}`);
    return species;
  }

  findByName(name: string) {
    const normalized = name.trim().toLocaleLowerCase();
    return this.#entries.find(
      (entry) => entry.name.toLocaleLowerCase() === normalized,
    );
  }
}

export const speciesRegistry = new SpeciesRegistry(seededSpecies);
