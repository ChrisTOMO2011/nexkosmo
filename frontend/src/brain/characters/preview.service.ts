import type { AssetId, Character, CharacterId } from "./character.schema";
import {
  updateCharacter,
  type CharacterPipelineStatus,
} from "./character.schema";
import {
  characterService,
  type CharacterService,
} from "./character.service";
import { validateSelection } from "./compatibility.engine";

export type CharacterPreviewRequest = Readonly<{
  character: Character;
  reason: "selection-change" | "manual-refresh" | "generation-complete";
}>;

export type CharacterPreviewResult = Readonly<{
  status: "rendered" | "unavailable" | "blocked" | "failed";
  previewAssetId?: AssetId;
  message: string;
}>;

export interface CharacterPreviewRenderer {
  render(request: CharacterPreviewRequest): Promise<CharacterPreviewResult>;
}

export type PreviewUpdate = Readonly<{
  characterId: CharacterId;
  status: CharacterPreviewResult["status"];
  previewAssetId?: AssetId;
  message: string;
}>;

export class CharacterPreviewService {
  readonly #listeners = new Set<(update: PreviewUpdate) => void>();

  constructor(
    private readonly characters: CharacterService = characterService,
    private readonly renderer?: CharacterPreviewRenderer,
  ) {}

  subscribe(listener: (update: PreviewUpdate) => void) {
    this.#listeners.add(listener);
    return () => this.#listeners.delete(listener);
  }

  async refresh(
    characterId: CharacterId,
    reason: CharacterPreviewRequest["reason"] = "manual-refresh",
  ) {
    const character = this.characters.require(characterId);
    const validation = validateSelection(character);
    if (!validation.valid) {
      return this.#complete(character, {
        status: "blocked",
        previewAssetId: character.previewAssetId,
        message: "Preview blocked by incompatible character assets.",
      });
    }
    if (!this.renderer) {
      return this.#complete(character, {
        status: "unavailable",
        previewAssetId: character.previewAssetId,
        message: "No character preview renderer is configured.",
      });
    }

    try {
      return this.#complete(
        character,
        await this.renderer.render({ character, reason }),
      );
    } catch {
      return this.#complete(character, {
        status: "failed",
        previewAssetId: character.previewAssetId,
        message: "Character preview rendering failed.",
      });
    }
  }

  #complete(character: Character, result: CharacterPreviewResult) {
    const pipelineStatus: CharacterPipelineStatus =
      result.status === "rendered"
        ? "ready"
        : result.status === "blocked"
          ? "blocked"
          : character.pipelineStatus;
    const saved = this.characters.save(
      updateCharacter(character, {
        previewAssetId: result.previewAssetId ?? character.previewAssetId,
        pipelineStatus,
      }),
    );
    const update = Object.freeze({
      characterId: saved.characterId,
      status: result.status,
      previewAssetId: saved.previewAssetId,
      message: result.message,
    });
    this.#listeners.forEach((listener) => listener(update));
    return update;
  }
}

export const characterPreviewService = new CharacterPreviewService();
