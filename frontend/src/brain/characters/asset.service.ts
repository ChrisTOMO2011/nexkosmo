import {
  developmentCharacterAssetManifest,
  type CharacterAssetCategory,
  type CharacterAssetManifest,
} from "./asset.manifest";
import type { AssetId, SpeciesId } from "./character.schema";

export interface CharacterAssetManifestRepository {
  list(): Promise<readonly CharacterAssetManifest[]>;
  get(assetId: AssetId): Promise<CharacterAssetManifest | undefined>;
}

export class CharacterAssetService {
  readonly #manifests = new Map<AssetId, CharacterAssetManifest>();

  constructor(manifests: readonly CharacterAssetManifest[] = []) {
    this.registerMany(manifests);
  }

  register(manifest: CharacterAssetManifest) {
    this.#manifests.set(manifest.assetId, manifest);
    return manifest;
  }

  registerMany(manifests: readonly CharacterAssetManifest[]) {
    manifests.forEach((manifest) => this.register(manifest));
  }

  list(options: {
    category?: CharacterAssetCategory;
    subCategory?: string;
    speciesId?: SpeciesId;
  } = {}) {
    return [...this.#manifests.values()].filter(
      (manifest) =>
        (!options.category || manifest.category === options.category) &&
        (!options.subCategory ||
          manifest.subCategory === options.subCategory) &&
        (!options.speciesId ||
          manifest.speciesIds.length === 0 ||
          manifest.speciesIds.includes(options.speciesId)),
    );
  }

  get(assetId: AssetId | undefined) {
    return assetId ? this.#manifests.get(assetId) : undefined;
  }

  require(assetId: AssetId) {
    const manifest = this.get(assetId);
    if (!manifest) throw new Error(`Unknown character asset ID: ${assetId}`);
    return manifest;
  }

  resolveUiToken(assetId: AssetId | undefined) {
    const thumbnail = this.get(assetId)?.thumbnail;
    return thumbnail?.startsWith("ui-token://")
      ? thumbnail.slice("ui-token://".length)
      : undefined;
  }
}

export const characterAssetService = new CharacterAssetService(
  developmentCharacterAssetManifest,
);
