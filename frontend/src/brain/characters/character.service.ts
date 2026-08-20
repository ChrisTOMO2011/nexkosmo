import { characterSeedAssetIds, speciesSeedIds } from "./asset.manifest";
import {
  createCharacter,
  createUuid,
  updateCharacter,
  type Character,
  type CharacterId,
  type CharacterSelectionPatch,
  type EntityId,
} from "./character.schema";
import { resolveDefaultAssets } from "./compatibility.engine";

export interface CharacterRepository {
  list(projectId: EntityId, productionId: EntityId): readonly Character[];
  get(characterId: CharacterId): Character | undefined;
  save(character: Character): Character;
}

export class InMemoryCharacterRepository implements CharacterRepository {
  readonly #characters = new Map<CharacterId, Character>();

  list(projectId: EntityId, productionId: EntityId) {
    return [...this.#characters.values()].filter(
      (character) =>
        character.projectId === projectId &&
        character.productionId === productionId,
    );
  }

  get(characterId: CharacterId) {
    return this.#characters.get(characterId);
  }

  save(character: Character) {
    this.#characters.set(character.characterId, character);
    return character;
  }
}

const seedRoster = [
  ["Christopher", "Lead", characterSeedAssetIds.christopherPreview],
  ["Sarah", "Co-Lead", characterSeedAssetIds.sarahPreview],
  ["Detective Miller", "Supporting", characterSeedAssetIds.millerPreview],
  ["Dr. Lee", "Supporting", characterSeedAssetIds.leePreview],
] as const;

export class CharacterService {
  readonly #seededScopes = new Set<string>();

  constructor(
    private readonly repository: CharacterRepository = new InMemoryCharacterRepository(),
  ) {}

  list(projectId: EntityId, productionId: EntityId) {
    this.#ensureDevelopmentSeeds(projectId, productionId);
    return this.repository.list(projectId, productionId);
  }

  get(characterId: CharacterId) {
    return this.repository.get(characterId);
  }

  require(characterId: CharacterId) {
    const character = this.get(characterId);
    if (!character) throw new Error(`Unknown character ID: ${characterId}`);
    return character;
  }

  save(character: Character) {
    return this.repository.save(character);
  }

  updateSelections(
    characterId: CharacterId,
    selections: CharacterSelectionPatch,
  ) {
    return this.save(updateCharacter(this.require(characterId), selections));
  }

  create(input: {
    projectId: EntityId;
    productionId: EntityId;
    displayName: string;
    role?: Character["role"];
    speciesId?: Character["speciesId"];
    previewAssetId?: Character["previewAssetId"];
  }) {
    const speciesId = input.speciesId ?? speciesSeedIds.human;
    const defaults = resolveDefaultAssets(speciesId);
    return this.save(
      createCharacter({
        characterId: createUuid(),
        projectId: input.projectId,
        productionId: input.productionId,
        displayName: input.displayName,
        role: input.role ?? "Supporting",
        speciesId,
        typeId: defaults.identityId,
        identityId: defaults.identityId,
        wardrobeIds: [],
        accessoryIds: [],
        rigId: defaults.rigId,
        skeletonId: defaults.skeletonId,
        materialIds: defaults.materialIds,
        textureIds: defaults.textureIds,
        animationIds: [],
        uploadedAssets: [],
        generatedAssets: [],
        previewAssetId: input.previewAssetId ?? defaults.previewAssetId,
        compatibilityProfileId: defaults.compatibilityProfileId,
        pipelineStatus: "draft",
      }),
    );
  }

  #ensureDevelopmentSeeds(projectId: EntityId, productionId: EntityId) {
    const scope = `${projectId}:${productionId}`;
    if (this.#seededScopes.has(scope)) return;
    seedRoster.forEach(([displayName, role, previewAssetId]) =>
      this.create({
        projectId,
        productionId,
        displayName,
        role,
        previewAssetId,
      }),
    );
    this.#seededScopes.add(scope);
  }
}

export const characterService = new CharacterService();
