import {
  createUuid,
  type AssetId,
  type CharacterId,
  type EntityId,
  type SpeciesId,
} from "./character.schema";

export type CharacterGenerationRequest = Readonly<{
  projectId: EntityId;
  productionId: EntityId;
  characterId: CharacterId;
  speciesId: SpeciesId;
  category: string;
  prompt: string;
  referenceAssets: readonly AssetId[];
}>;

export type CharacterGenerationResult = Readonly<{
  jobId: string;
  status: "queued" | "running" | "completed" | "failed" | "unavailable";
  generatedAssets: readonly AssetId[];
  warnings: readonly string[];
  errors: readonly string[];
  previewAssets: readonly AssetId[];
}>;

export interface CharacterGenerationProvider {
  generate(
    request: CharacterGenerationRequest,
  ): Promise<CharacterGenerationResult>;
}

export class CharacterGenerationService {
  constructor(private readonly provider?: CharacterGenerationProvider) {}

  generate(request: CharacterGenerationRequest) {
    if (!request.prompt.trim()) {
      return Promise.resolve<CharacterGenerationResult>({
        jobId: createUuid(),
        status: "failed",
        generatedAssets: [],
        warnings: [],
        errors: ["A generation prompt is required."],
        previewAssets: [],
      });
    }
    if (!this.provider) {
      return Promise.resolve<CharacterGenerationResult>({
        jobId: createUuid(),
        status: "unavailable",
        generatedAssets: [],
        warnings: ["No character generation provider is configured."],
        errors: [],
        previewAssets: [],
      });
    }
    return this.provider.generate(request);
  }
}

export const characterGenerationService = new CharacterGenerationService();
