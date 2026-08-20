export type EntityId = string;
export type CharacterId = string;
export type AssetId = string;
export type SpeciesId = string;
export type CompatibilityProfileId = string;

export type CharacterPipelineStatus =
  | "draft"
  | "validating"
  | "preview-pending"
  | "ready"
  | "blocked"
  | "archived";

export type CharacterRole =
  | "Lead"
  | "Co-Lead"
  | "Supporting"
  | "Background"
  | "Creature"
  | "Custom";

export type CharacterEditorTab =
  | "Identity"
  | "Face"
  | "Hair"
  | "Skin"
  | "Eyes"
  | "Beard"
  | "Body"
  | "Age"
  | "Expression"
  | "Wardrobe"
  | "Accessories"
  | "Rig"
  | "Animation"
  | "Voice";

export type UploadedAssetReference = Readonly<{
  assetId: AssetId;
  sourceAssetId?: AssetId;
  mimeType?: string;
  checksumSha256?: string;
  uploadedAt: string;
}>;

export type GeneratedAssetReference = Readonly<{
  assetId: AssetId;
  jobId: string;
  generatedAt: string;
}>;

export type Character = Readonly<{
  characterId: CharacterId;
  projectId: EntityId;
  productionId: EntityId;
  displayName: string;
  role: CharacterRole;
  identityType: string;
  age: number;
  apparentAge: number;
  heightCm: number;
  bodyType: string;
  skinTone: number;
  genderPresentation?: string;
  physicalProfileVersion: number;
  speciesId: SpeciesId;
  typeId?: AssetId;
  styleProfileId?: AssetId;
  identityId?: AssetId;
  faceId?: AssetId;
  hairId?: AssetId;
  skinId?: AssetId;
  eyesId?: AssetId;
  beardId?: AssetId;
  bodyId?: AssetId;
  agePresetId?: AssetId;
  expressionId?: AssetId;
  wardrobeIds: readonly AssetId[];
  accessoryIds: readonly AssetId[];
  rigId?: AssetId;
  skeletonId?: AssetId;
  materialIds: readonly AssetId[];
  textureIds: readonly AssetId[];
  animationIds: readonly AssetId[];
  voiceId?: AssetId;
  uploadedAssets: readonly UploadedAssetReference[];
  generatedAssets: readonly GeneratedAssetReference[];
  previewAssetId?: AssetId;
  compatibilityProfileId: CompatibilityProfileId;
  pipelineStatus: CharacterPipelineStatus;
  readinessStatus:
    | "incomplete"
    | "invalid"
    | "processing-required"
    | "ready-for-set";
  validationIssues: readonly Readonly<Record<string, unknown>>[];
  validatedVersion?: number;
  validatedAt?: string;
  version: number;
  createdAt: string;
  updatedAt: string;
}>;

export type CharacterSelectionPatch = Partial<
  Pick<
    Character,
    | "speciesId"
    | "typeId"
    | "styleProfileId"
    | "identityId"
    | "faceId"
    | "hairId"
    | "skinId"
    | "eyesId"
    | "beardId"
    | "bodyId"
    | "agePresetId"
    | "expressionId"
    | "wardrobeIds"
    | "accessoryIds"
    | "rigId"
    | "skeletonId"
    | "materialIds"
    | "textureIds"
    | "animationIds"
    | "voiceId"
  >
>;

const uuidPattern =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/iu;

export function isUuid(value: string): boolean {
  return uuidPattern.test(value);
}

export function createUuid(): string {
  return crypto.randomUUID();
}

export function createCharacter(
  input: Omit<
    Character,
    | "version"
    | "createdAt"
    | "updatedAt"
    | "identityType"
    | "age"
    | "apparentAge"
    | "heightCm"
    | "bodyType"
    | "skinTone"
    | "physicalProfileVersion"
    | "readinessStatus"
    | "validationIssues"
  > &
    Partial<
      Pick<
        Character,
        | "version"
        | "createdAt"
        | "updatedAt"
        | "identityType"
        | "age"
        | "apparentAge"
        | "heightCm"
        | "bodyType"
        | "skinTone"
        | "physicalProfileVersion"
        | "readinessStatus"
        | "validationIssues"
      >
    >,
): Character {
  if (!isUuid(input.characterId)) {
    throw new Error("Character IDs must be UUIDs.");
  }
  if (!input.projectId.trim() || !input.productionId.trim()) {
    throw new Error("Characters require project and production IDs.");
  }
  if (!input.displayName.trim()) {
    throw new Error("Characters require a display name.");
  }

  const now = new Date().toISOString();
  return Object.freeze({
    identityType: "Human Male",
    age: 35,
    apparentAge: 35,
    heightCm: 180,
    bodyType: "Athletic",
    skinTone: 89,
    genderPresentation: undefined,
    physicalProfileVersion: 1,
    typeId: undefined,
    identityId: undefined,
    faceId: undefined,
    hairId: undefined,
    skinId: undefined,
    eyesId: undefined,
    beardId: undefined,
    bodyId: undefined,
    agePresetId: undefined,
    expressionId: undefined,
    rigId: undefined,
    skeletonId: undefined,
    voiceId: undefined,
    previewAssetId: undefined,
    styleProfileId: undefined,
    readinessStatus: "incomplete",
    validationIssues: Object.freeze([]),
    validatedVersion: undefined,
    validatedAt: undefined,
    ...input,
    displayName: input.displayName.trim(),
    wardrobeIds: Object.freeze([...(input.wardrobeIds ?? [])]),
    accessoryIds: Object.freeze([...(input.accessoryIds ?? [])]),
    materialIds: Object.freeze([...(input.materialIds ?? [])]),
    textureIds: Object.freeze([...(input.textureIds ?? [])]),
    animationIds: Object.freeze([...(input.animationIds ?? [])]),
    uploadedAssets: Object.freeze([...(input.uploadedAssets ?? [])]),
    generatedAssets: Object.freeze([...(input.generatedAssets ?? [])]),
    version: input.version ?? 1,
    createdAt: input.createdAt ?? now,
    updatedAt: input.updatedAt ?? now,
  });
}

export function updateCharacter(
  character: Character,
  updates: Partial<Omit<Character, "characterId" | "createdAt" | "version">>,
): Character {
  return createCharacter({
    ...character,
    ...updates,
    characterId: character.characterId,
    createdAt: character.createdAt,
    version: character.version + 1,
    updatedAt: new Date().toISOString(),
  });
}
