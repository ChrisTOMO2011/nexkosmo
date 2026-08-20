import {
  characterAssetService,
  type CharacterAssetService,
} from "./asset.service";
import type { CharacterAssetCategory } from "./asset.manifest";
import {
  clearInvalidSelections,
  getCompatibleAssets,
  resolveDefaultAssets,
} from "./compatibility.engine";
import {
  characterService,
  type CharacterService,
} from "./character.service";
import type {
  Character,
  CharacterSelectionPatch,
  EntityId,
  SpeciesId,
} from "./character.schema";
import { updateCharacter } from "./character.schema";
import { speciesRegistry, type SpeciesRegistry } from "./species.registry";
import {
  authenticatedJsonHeaders,
  getAccessToken,
  type AccessTokenProvider,
} from "../auth/session";

export type ApiSpecies = Readonly<{
  speciesId: SpeciesId;
  key: string;
  name: string;
  category: string;
  enabled: boolean;
  capabilities: readonly string[];
  supportedTabs: readonly string[];
  compatibilityProfileId: string;
  defaultRigId?: string;
  defaultSkeletonId?: string;
  defaultMaterialProfileId?: string;
  defaultBodyId?: string;
  minAge: number;
  maxAge: number;
  minHeightCm: number;
  maxHeightCm: number;
  surfaceControlLabel: string;
  version: number;
}>;

export type ApiCharacterAsset = Readonly<{
  assetId: string;
  name: string;
  speciesIds: readonly string[];
  category: string;
  subcategory: string;
  thumbnailReference?: string;
  previewReference?: string;
  status: string;
  version: number;
  profileMetadata: Readonly<Record<string, unknown>>;
}>;

export type CharacterMutation = Readonly<{
  character: Character;
  changeSummary: Readonly<Record<string, unknown>>;
}>;

export interface CharacterApiClient {
  listByProject(projectId: EntityId): Promise<readonly Character[]>;
  getCharacter(characterId: string): Promise<Character>;
  create(input: {
    projectId: EntityId;
    productionId: EntityId;
    displayName: string;
    role: Character["role"];
    speciesId: SpeciesId;
    idempotencyKey: string;
  }): Promise<CharacterMutation>;
  updateSelections(
    characterId: string,
    selections: CharacterSelectionPatch,
    idempotencyKey: string,
  ): Promise<CharacterMutation>;
  updateMetadata(
    characterId: string,
    values: { displayName?: string; role?: Character["role"] },
    idempotencyKey: string,
  ): Promise<CharacterMutation>;
  updateIdentityProperties(
    characterId: string,
    values: { identityType?: string; genderPresentation?: string },
    idempotencyKey: string,
  ): Promise<CharacterMutation>;
  updatePhysicalProperties(
    characterId: string,
    values: Partial<
      Pick<Character, "age" | "apparentAge" | "heightCm" | "bodyType" | "skinTone">
    >,
    idempotencyKey: string,
  ): Promise<CharacterMutation>;
  validatePackage(characterId: string, idempotencyKey: string): Promise<CharacterMutation>;
  getSupportedTabs(characterId: string): Promise<readonly string[]>;
}

export interface SpeciesApiClient {
  list(): Promise<readonly ApiSpecies[]>;
  getSpecies(speciesId: SpeciesId): Promise<ApiSpecies | undefined>;
}

export interface CharacterAssetApiClient {
  listCompatible(
    characterId: string,
    category?: string,
  ): Promise<readonly ApiCharacterAsset[]>;
  getAsset(assetId: string): Promise<ApiCharacterAsset>;
}

export type CharacterDataGateway = CharacterApiClient &
  SpeciesApiClient &
  CharacterAssetApiClient;

export class CharacterApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code: string,
    readonly retryable: boolean,
  ) {
    super(message);
    this.name = "CharacterApiError";
  }

  get conflict() {
    return this.status === 409;
  }
}

type SnakeCharacter = Record<string, unknown> & {
  character_id: string;
  project_id: string;
  production_id: string;
  display_name: string;
  role: Character["role"];
  identity_type: string;
  age: number;
  apparent_age: number;
  height_cm: number;
  body_type: string;
  skin_tone: number;
  gender_presentation?: string;
  physical_profile_version: number;
  species_id: string;
  compatibility_profile_id: string;
  pipeline_status: Character["pipelineStatus"];
  readiness_status: Character["readinessStatus"];
  validation_issues: Readonly<Record<string, unknown>>[];
  validated_version?: number;
  validated_at?: string;
  version: number;
  created_at: string;
  updated_at: string;
};

const scalarFields = [
  "type",
  "style_profile",
  "identity",
  "face",
  "hair",
  "skin",
  "eyes",
  "beard",
  "body",
  "age_preset",
  "expression",
  "rig",
  "skeleton",
  "voice",
  "preview_asset",
] as const;

const collectionFields = [
  "wardrobe",
  "accessory",
  "material",
  "texture",
  "animation",
  "uploaded_asset",
  "generated_asset",
] as const;

function toCharacter(value: SnakeCharacter): Character {
  const scalar = Object.fromEntries(
    scalarFields.map((field) => [
      `${field.replaceAll(/_([a-z])/gu, (_match, letter: string) =>
        letter.toUpperCase(),
      )}Id`,
      value[`${field}_id`] as string | undefined,
    ]),
  );
  const collections = Object.fromEntries(
    collectionFields.map((field) => [
      `${field.replaceAll(/_([a-z])/gu, (_match, letter: string) =>
        letter.toUpperCase(),
      )}Ids`,
      (value[`${field}_ids`] as string[] | undefined) ?? [],
    ]),
  );
  return {
    characterId: value.character_id,
    projectId: value.project_id,
    productionId: value.production_id,
    displayName: value.display_name,
    role: value.role,
    identityType: value.identity_type,
    age: value.age,
    apparentAge: value.apparent_age,
    heightCm: value.height_cm,
    bodyType: value.body_type,
    skinTone: value.skin_tone,
    genderPresentation: value.gender_presentation,
    physicalProfileVersion: value.physical_profile_version,
    speciesId: value.species_id,
    ...(scalar as Partial<Character>),
    ...(collections as Partial<Character>),
    uploadedAssets: [],
    generatedAssets: [],
    compatibilityProfileId: value.compatibility_profile_id,
    pipelineStatus: value.pipeline_status,
    readinessStatus: value.readiness_status,
    validationIssues: value.validation_issues,
    validatedVersion: value.validated_version,
    validatedAt: value.validated_at,
    version: value.version,
    createdAt: value.created_at,
    updatedAt: value.updated_at,
  } as Character;
}

function fnv1a(value: string, seed: number) {
  let hash = seed >>> 0;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }
  return hash >>> 0;
}

export function canonicalEntityId(value: EntityId): EntityId {
  if (
    /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/iu.test(
      value,
    )
  ) {
    return value;
  }
  const hex = [0x811c9dc5, 0x9e3779b9, 0x85ebca6b, 0xc2b2ae35]
    .map((seed) => fnv1a(value, seed).toString(16).padStart(8, "0"))
    .join("");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-4${hex.slice(13, 16)}-8${hex.slice(17, 20)}-${hex.slice(20, 32)}`;
}

export class HttpCharacterDataGateway implements CharacterDataGateway {
  readonly #versions = new Map<string, number>();

  constructor(
    private readonly baseUrl: string,
    private readonly fetcher: typeof fetch = fetch,
    private readonly accessToken: AccessTokenProvider = getAccessToken,
  ) {}

  async listByProject(projectId: EntityId) {
    const response = await this.#request<{
      items: SnakeCharacter[];
    }>(
      `/projects/${canonicalEntityId(projectId)}/characters?limit=200&offset=0`,
    );
    const characters = response.items.map(toCharacter);
    characters.forEach((character) =>
      this.#versions.set(character.characterId, character.version),
    );
    return characters;
  }

  async getCharacter(characterId: string) {
    const character = toCharacter(
      await this.#request<SnakeCharacter>(`/characters/${characterId}`),
    );
    this.#versions.set(characterId, character.version);
    return character;
  }

  async create(input: {
    projectId: EntityId;
    productionId: EntityId;
    displayName: string;
    role: Character["role"];
    speciesId: SpeciesId;
    idempotencyKey: string;
  }) {
    const response = await this.#request<{
      character: SnakeCharacter;
      change_summary: Record<string, unknown>;
    }>(`/projects/${canonicalEntityId(input.projectId)}/characters`, {
      method: "POST",
      headers: { "Idempotency-Key": input.idempotencyKey },
      body: JSON.stringify({
        production_id: canonicalEntityId(input.productionId),
        display_name: input.displayName,
        role: input.role,
        species_id: input.speciesId,
      }),
    });
    const character = toCharacter(response.character);
    this.#versions.set(character.characterId, character.version);
    return { character, changeSummary: response.change_summary };
  }

  async updateSelections(
    characterId: string,
    selections: CharacterSelectionPatch,
    idempotencyKey: string,
  ) {
    const expectedVersion =
      this.#versions.get(characterId) ??
      (await this.getCharacter(characterId)).version;
    let path: string;
    let method = "PUT";
    let body: Record<string, unknown>;
    if (selections.speciesId) {
      path = `/characters/${characterId}/change-species`;
      method = "POST";
      body = {
        species_id: selections.speciesId,
        expected_version: expectedVersion,
      };
    } else if (selections.styleProfileId) {
      path = `/characters/${characterId}/selections/style-profile`;
      body = {
        asset_id: selections.styleProfileId,
        expected_version: expectedVersion,
      };
    } else if (selections.typeId) {
      path = `/characters/${characterId}/selections/type`;
      body = { asset_id: selections.typeId, expected_version: expectedVersion };
    } else if (selections.accessoryIds) {
      path = `/characters/${characterId}/accessories`;
      body = {
        asset_ids: selections.accessoryIds,
        expected_version: expectedVersion,
      };
    } else {
      const scalarEntry = Object.entries(selections).find(
        ([key, value]) => key.endsWith("Id") && value,
      );
      if (!scalarEntry) {
        throw new CharacterApiError(
          "Unsupported character selection mutation.",
          422,
          "unsupported_selection",
          false,
        );
      }
      const [field, assetId] = scalarEntry;
      const category = field
        .slice(0, -"Id".length)
        .replaceAll(/[A-Z]/gu, (letter) => `-${letter.toLowerCase()}`);
      path = `/characters/${characterId}/selections/${category}`;
      body = { asset_id: assetId, expected_version: expectedVersion };
    }
    const response = await this.#request<{
      character: SnakeCharacter;
      change_summary: Record<string, unknown>;
    }>(path, {
      method,
      headers: { "Idempotency-Key": idempotencyKey },
      body: JSON.stringify(body),
    });
    const character = toCharacter(response.character);
    this.#versions.set(characterId, character.version);
    return { character, changeSummary: response.change_summary };
  }

  async updateMetadata(
    characterId: string,
    values: { displayName?: string; role?: Character["role"] },
    idempotencyKey: string,
  ) {
    return this.#mutate(characterId, `/characters/${characterId}`, "PATCH", {
      display_name: values.displayName,
      role: values.role,
    }, idempotencyKey);
  }

  async updateIdentityProperties(
    characterId: string,
    values: { identityType?: string; genderPresentation?: string },
    idempotencyKey: string,
  ) {
    return this.#mutate(
      characterId,
      `/characters/${characterId}/identity-properties`,
      "PATCH",
      {
        identity_type: values.identityType,
        gender_presentation: values.genderPresentation,
      },
      idempotencyKey,
    );
  }

  async updatePhysicalProperties(
    characterId: string,
    values: Partial<
      Pick<Character, "age" | "apparentAge" | "heightCm" | "bodyType" | "skinTone">
    >,
    idempotencyKey: string,
  ) {
    return this.#mutate(
      characterId,
      `/characters/${characterId}/physical-properties`,
      "PATCH",
      {
        age: values.age,
        apparent_age: values.apparentAge,
        height_cm: values.heightCm,
        body_type: values.bodyType,
        skin_tone: values.skinTone,
      },
      idempotencyKey,
    );
  }

  async validatePackage(characterId: string, idempotencyKey: string) {
    return this.#mutate(
      characterId,
      `/characters/${characterId}/validate-package`,
      "POST",
      {},
      idempotencyKey,
    );
  }

  async getSupportedTabs(characterId: string) {
    const response = await this.#request<{ items: string[] }>(
      `/characters/${characterId}/supported-tabs`,
    );
    return response.items;
  }

  async #mutate(
    characterId: string,
    path: string,
    method: string,
    values: Record<string, unknown>,
    idempotencyKey: string,
  ) {
    const expectedVersion =
      this.#versions.get(characterId) ?? (await this.getCharacter(characterId)).version;
    const response = await this.#request<{
      character: SnakeCharacter;
      change_summary: Record<string, unknown>;
    }>(path, {
      method,
      headers: { "Idempotency-Key": idempotencyKey },
      body: JSON.stringify({
        ...Object.fromEntries(Object.entries(values).filter(([, value]) => value !== undefined)),
        expected_version: expectedVersion,
      }),
    });
    const character = toCharacter(response.character);
    this.#versions.set(characterId, character.version);
    return { character, changeSummary: response.change_summary };
  }

  async list() {
    const species = await this.#request<Record<string, unknown>[]>("/species");
    return species.map((item) => ({
      speciesId: item.species_id as string,
      key: item.key as string,
      name: item.name as string,
      category: item.category as string,
      enabled: item.enabled as boolean,
      capabilities: item.capabilities as string[],
      supportedTabs: item.supported_tabs as string[],
      compatibilityProfileId: item.compatibility_profile_id as string,
      defaultRigId: item.default_rig_id as string | undefined,
      defaultSkeletonId: item.default_skeleton_id as string | undefined,
      defaultMaterialProfileId: item.default_material_profile_id as
        | string
        | undefined,
      defaultBodyId: item.default_body_id as string | undefined,
      minAge: item.min_age as number,
      maxAge: item.max_age as number,
      minHeightCm: item.min_height_cm as number,
      maxHeightCm: item.max_height_cm as number,
      surfaceControlLabel: item.surface_control_label as string,
      version: item.version as number,
    }));
  }

  async getSpecies(speciesId: SpeciesId) {
    return (await this.list()).find((item) => item.speciesId === speciesId);
  }

  async listCompatible(characterId: string, category?: string) {
    const query = category ? `?category=${encodeURIComponent(category)}` : "";
    const response = await this.#request<{
      items: Record<string, unknown>[];
    }>(`/characters/${characterId}/compatible-assets${query}`);
    return response.items.map(this.#mapAsset);
  }

  async getAsset(assetId: string) {
    return this.#mapAsset(
      await this.#request<Record<string, unknown>>(`/assets/${assetId}`),
    );
  }

  #mapAsset(item: Record<string, unknown>): ApiCharacterAsset {
    return {
      assetId: item.asset_id as string,
      name: item.name as string,
      speciesIds: item.species_ids as string[],
      category: item.category as string,
      subcategory: item.subcategory as string,
      thumbnailReference: item.thumbnail_reference as string | undefined,
      previewReference: item.preview_reference as string | undefined,
      status: item.status as string,
      version: item.version as number,
      profileMetadata: item.profile_metadata as Record<string, unknown>,
    };
  }

  async #request<T>(path: string, init: RequestInit = {}): Promise<T> {
    let response: Response;
    try {
      const fetcher = this.fetcher;
      response = await fetcher(`${this.baseUrl}${path}`, {
        ...init,
        headers: authenticatedJsonHeaders(this.accessToken, init.headers),
      });
    } catch {
      throw new CharacterApiError(
        "The character service is unavailable.",
        0,
        "network_error",
        true,
      );
    }
    if (!response.ok) {
      const problem = (await response.json().catch(() => ({}))) as {
        detail?: string;
        code?: string;
      };
      throw new CharacterApiError(
        problem.detail ?? `Character API request failed (${response.status}).`,
        response.status,
        problem.code ?? "api_error",
        response.status >= 500 || response.status === 429,
      );
    }
    return (await response.json()) as T;
  }
}

function selectedAssetIds(character: Character) {
  return [
    character.typeId,
    character.styleProfileId,
    character.identityId,
    character.faceId,
    character.hairId,
    character.skinId,
    character.eyesId,
    character.beardId,
    character.bodyId,
    character.agePresetId,
    character.expressionId,
    character.rigId,
    character.skeletonId,
    character.voiceId,
    ...character.wardrobeIds,
    ...character.accessoryIds,
    ...character.materialIds,
    ...character.textureIds,
    ...character.animationIds,
  ].filter((assetId): assetId is string => Boolean(assetId));
}

export class InMemoryCharacterDataGateway implements CharacterDataGateway {
  constructor(
    private readonly characters: CharacterService = characterService,
    private readonly species: SpeciesRegistry = speciesRegistry,
    private readonly assets: CharacterAssetService = characterAssetService,
  ) {}

  async listByProject(projectId: EntityId) {
    return this.characters.list(projectId, projectId);
  }

  async getCharacter(characterId: string) {
    return this.characters.require(characterId);
  }

  async create(input: {
    projectId: EntityId;
    productionId: EntityId;
    displayName: string;
    role: Character["role"];
    speciesId: SpeciesId;
  }) {
    return {
      character: this.characters.create(input),
      changeSummary: {},
    };
  }

  async updateSelections(
    characterId: string,
    selections: CharacterSelectionPatch,
  ) {
    const previous = this.characters.require(characterId);
    const speciesChanged =
      selections.speciesId !== undefined &&
      selections.speciesId !== previous.speciesId;
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
    const character = Object.keys(cleared).length
      ? this.characters.updateSelections(characterId, cleared)
      : candidate;
    if (speciesChanged) {
      const previousIds = selectedAssetIds(previous);
      const currentIds = new Set(selectedAssetIds(character));
      const previousSet = new Set(previousIds);
      return {
        character,
        changeSummary: {
          previous_species_id: previous.speciesId,
          species_id: character.speciesId,
          preserved_asset_ids: previousIds.filter((item) => currentIds.has(item)),
          cleared_asset_ids: previousIds.filter((item) => !currentIds.has(item)),
          applied_default_asset_ids: selectedAssetIds(character).filter(
            (item) => !previousSet.has(item),
          ),
        },
      };
    }
    return {
      character,
      changeSummary: {},
    };
  }

  async updateMetadata(characterId: string, values: { displayName?: string; role?: Character["role"] }) {
    return {
      character: this.characters.save(
        updateCharacter(this.characters.require(characterId), {
          ...(values.displayName ? { displayName: values.displayName } : {}),
          ...(values.role ? { role: values.role } : {}),
        }),
      ),
      changeSummary: {},
    };
  }

  async updateIdentityProperties(characterId: string, values: { identityType?: string; genderPresentation?: string }) {
    return {
      character: this.characters.save(
        updateCharacter(this.characters.require(characterId), values),
      ),
      changeSummary: {},
    };
  }

  async updatePhysicalProperties(
    characterId: string,
    values: Partial<Pick<Character, "age" | "apparentAge" | "heightCm" | "bodyType" | "skinTone">>,
  ) {
    return {
      character: this.characters.save(updateCharacter(this.characters.require(characterId), values)),
      changeSummary: {},
    };
  }

  async validatePackage(characterId: string) {
    const current = this.characters.require(characterId);
    return { character: current, changeSummary: { readinessStatus: current.readinessStatus } };
  }

  async getSupportedTabs(characterId: string) {
    const character = this.characters.require(characterId);
    return this.species.require(character.speciesId).supportedTabs;
  }

  async list() {
    return this.species.list({ enabledOnly: true }).map((item) => ({
      speciesId: item.id,
      key: item.name.toLocaleLowerCase(),
      name: item.name,
      category: item.category,
      enabled: item.enabled,
      capabilities: item.capabilities,
      supportedTabs: item.supportedTabs,
      compatibilityProfileId: item.compatibilityProfile,
      defaultRigId: item.defaultRig,
      defaultSkeletonId: item.defaultSkeleton,
      version: 1,
      minAge: 0,
      maxAge: 250,
      minHeightCm: 30,
      maxHeightCm: 400,
      surfaceControlLabel: "Skin Tone",
    }));
  }

  async getSpecies(speciesId: SpeciesId) {
    const species = this.species.require(speciesId);
    return (await this.list()).find((item) => item.speciesId === species.id);
  }

  async listCompatible(characterId: string, category?: string) {
    const character = this.characters.require(characterId);
    return getCompatibleAssets(
      character,
      category as CharacterAssetCategory | undefined,
      this.assets,
      this.species,
    ).map((item) => ({
      assetId: item.assetId,
      name: item.name,
      speciesIds: item.speciesIds,
      category: item.category,
      subcategory: item.subCategory,
      thumbnailReference: item.thumbnail,
      previewReference: item.preview,
      status: item.status,
      version: item.version,
      profileMetadata: {},
    }));
  }

  async getAsset(assetId: string) {
    const item = this.assets.require(assetId);
    return {
      assetId: item.assetId,
      name: item.name,
      speciesIds: item.speciesIds,
      category: item.category,
      subcategory: item.subCategory,
      thumbnailReference: item.thumbnail,
      previewReference: item.preview,
      status: item.status,
      version: item.version,
      profileMetadata: {},
    };
  }
}

export function createCharacterDataGateway(): CharacterDataGateway {
  const source =
    import.meta.env.VITE_CHARACTER_DATA_SOURCE ??
    (import.meta.env.MODE === "test" ? "memory" : "api");
  if (source === "memory") {
    if (import.meta.env.PROD) {
      throw new Error(
        "In-memory character persistence cannot be enabled in production.",
      );
    }
    return new InMemoryCharacterDataGateway();
  }
  if (source !== "api") {
    throw new Error(`Unknown character data source: ${source}`);
  }
  return new HttpCharacterDataGateway(
    import.meta.env.VITE_NEXKOSMO_API_BASE_URL ?? "/api/v1",
  );
}

export const characterDataGateway = createCharacterDataGateway();
