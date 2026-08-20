import {
  characterAssetService,
  type CharacterAssetService,
} from "./asset.service";
import {
  characterDataGateway,
  type CharacterDataGateway,
} from "./api.clients";
import {
  characterService,
  type CharacterService,
} from "./character.service";
import type {
  Character,
  CharacterId,
  CharacterSelectionPatch,
  EntityId,
  SpeciesId,
} from "./character.schema";
import { updateCharacter } from "./character.schema";
import {
  clearInvalidSelections,
  resolveDefaultAssets,
  validateSelection,
} from "./compatibility.engine";
import {
  characterPreviewService,
  type CharacterPreviewService,
} from "./preview.service";
import { speciesRegistry, type SpeciesRegistry } from "./species.registry";

export type CharacterPipelineEvent = Readonly<{
  type: "character-created" | "selection-updated" | "preview-updated";
  character: Character;
  changedFields: readonly string[];
}>;

export interface CharacterDownstreamSynchronizer {
  synchronize(
    event: CharacterPipelineEvent,
  ): Promise<{ status: "synchronized" | "deferred"; message: string }>;
}

export class CharacterPipelineService {
  readonly #listeners = new Set<(event: CharacterPipelineEvent) => void>();

  constructor(
    readonly characters: CharacterService = characterService,
    readonly assets: CharacterAssetService = characterAssetService,
    readonly species: SpeciesRegistry = speciesRegistry,
    readonly previews: CharacterPreviewService = characterPreviewService,
    private readonly downstream?: CharacterDownstreamSynchronizer,
    readonly gateway: CharacterDataGateway = characterDataGateway,
  ) {}

  subscribe(listener: (event: CharacterPipelineEvent) => void) {
    this.#listeners.add(listener);
    return () => this.#listeners.delete(listener);
  }

  loadCharacters(projectId: EntityId, productionId: EntityId) {
    return this.characters.list(projectId, productionId);
  }

  loadCharactersFromSource(projectId: EntityId) {
    return this.gateway.listByProject(projectId);
  }

  loadSpeciesFromSource() {
    return this.gateway.list();
  }

  loadCompatibleAssetsFromSource(characterId: CharacterId, category?: string) {
    return this.gateway.listCompatible(characterId, category);
  }

  async createCharacterInSource(input: {
    projectId: EntityId;
    productionId: EntityId;
    displayName: string;
    role?: Character["role"];
    speciesId: SpeciesId;
  }) {
    return (
      await this.gateway.create({
        ...input,
        role: input.role ?? "Supporting",
        idempotencyKey: crypto.randomUUID(),
      })
    ).character;
  }

  async updateSelectionsInSource(
    characterId: CharacterId,
    selections: CharacterSelectionPatch,
  ) {
    return (
      await this.gateway.updateSelections(
        characterId,
        selections,
        crypto.randomUUID(),
      )
    ).character;
  }

  changeSpeciesInSource(characterId: CharacterId, speciesId: SpeciesId) {
    return this.gateway.updateSelections(
      characterId,
      { speciesId },
      crypto.randomUUID(),
    );
  }

  async updateMetadataInSource(
    characterId: CharacterId,
    values: { displayName?: string; role?: Character["role"] },
  ) {
    return (
      await this.gateway.updateMetadata(characterId, values, crypto.randomUUID())
    ).character;
  }

  async updateIdentityPropertiesInSource(
    characterId: CharacterId,
    values: { identityType?: string; genderPresentation?: string },
  ) {
    return (
      await this.gateway.updateIdentityProperties(
        characterId,
        values,
        crypto.randomUUID(),
      )
    ).character;
  }

  async updatePhysicalPropertiesInSource(
    characterId: CharacterId,
    values: Partial<
      Pick<Character, "age" | "apparentAge" | "heightCm" | "bodyType" | "skinTone">
    >,
  ) {
    return (
      await this.gateway.updatePhysicalProperties(
        characterId,
        values,
        crypto.randomUUID(),
      )
    ).character;
  }

  async validatePackageInSource(characterId: CharacterId) {
    return (
      await this.gateway.validatePackage(characterId, crypto.randomUUID())
    ).character;
  }

  loadCharacter(characterId: CharacterId) {
    return this.characters.require(characterId);
  }

  saveCharacter(character: Character) {
    return this.characters.save(character);
  }

  loadAssetManifests(characterId: CharacterId) {
    const character = this.loadCharacter(characterId);
    return this.assets.list({ speciesId: character.speciesId });
  }

  createCharacter(input: {
    projectId: EntityId;
    productionId: EntityId;
    displayName: string;
    role?: Character["role"];
    speciesId?: SpeciesId;
  }) {
    const character = this.characters.create(input);
    this.#publish({
      type: "character-created",
      character,
      changedFields: Object.freeze(["characterId"]),
    });
    return character;
  }

  updateSelections(
    characterId: CharacterId,
    selections: CharacterSelectionPatch,
  ) {
    const current = this.loadCharacter(characterId);
    const speciesChanged =
      selections.speciesId !== undefined &&
      selections.speciesId !== current.speciesId;
    const defaults = speciesChanged
      ? resolveDefaultAssets(
          selections.speciesId as SpeciesId,
          this.species,
          this.assets,
        )
      : {};
    const candidate = this.characters.updateSelections(characterId, {
      ...selections,
      ...defaults,
    });
    const cleared = clearInvalidSelections(candidate, this.assets, this.species);
    const saved = Object.keys(cleared).length
      ? this.characters.updateSelections(characterId, cleared)
      : candidate;
    const validation = validateSelection(saved, this.assets, this.species);
    const finalCharacter =
      saved.pipelineStatus === (validation.valid ? "preview-pending" : "blocked")
        ? saved
        : this.characters.save(
            updateCharacter(saved, {
              pipelineStatus: validation.valid ? "preview-pending" : "blocked",
            }),
          );

    const event = Object.freeze({
      type: "selection-updated" as const,
      character: finalCharacter,
      changedFields: Object.freeze(Object.keys(selections)),
    });
    this.#publish(event);
    void this.previews
      .refresh(characterId, "selection-change")
      .then((preview) => {
        this.#publish({
          type: "preview-updated",
          character: this.loadCharacter(preview.characterId),
          changedFields: Object.freeze(["previewAssetId", "pipelineStatus"]),
        });
      });
    void this.downstream?.synchronize(event);
    return finalCharacter;
  }

  refreshPreview(characterId: CharacterId) {
    return this.previews.refresh(characterId, "manual-refresh");
  }

  async synchronize(characterId: CharacterId) {
    const character = this.loadCharacter(characterId);
    if (!this.downstream) {
      return {
        status: "deferred" as const,
        message: "No downstream character synchronizer is configured.",
      };
    }
    return this.downstream.synchronize({
      type: "selection-updated",
      character,
      changedFields: Object.freeze([]),
    });
  }

  #publish(event: CharacterPipelineEvent) {
    this.#listeners.forEach((listener) => listener(event));
  }
}

export const characterPipelineService = new CharacterPipelineService();
