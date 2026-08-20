export type EnvironmentType = Readonly<{
  environmentTypeId: string;
  key: string;
  name: string;
  enabled: boolean;
  capabilities: readonly string[];
  supportedTabs: readonly string[];
  version: number;
}>;

export type EnvironmentAsset = Readonly<{
  assetId: string;
  name: string;
  category: string;
  subcategory: string;
  thumbnailReference: string;
  previewReference: string;
  status: string;
  visibility: string;
  uploaded: boolean;
  generated: boolean;
  placeholder: boolean;
  version: number;
}>;

export type Environment = Readonly<{
  environmentId: string;
  workspaceId: string;
  projectId: string;
  productionId: string;
  displayName: string;
  description: string;
  environmentTypeId: string;
  locationType: string;
  interiorExterior: string;
  biome: string;
  climateProfile: string;
  terrainProfileId?: string;
  weatherProfileId?: string;
  timeOfDay: string;
  atmosphereProfileId?: string;
  backgroundAssetIds: readonly string[];
  terrainAssetIds: readonly string[];
  buildingAssetIds: readonly string[];
  natureAssetIds: readonly string[];
  practicalAssetIds: readonly string[];
  materialProfileIds: readonly string[];
  textureProfileIds: readonly string[];
  detailAssetIds: readonly string[];
  styleProfileId?: string;
  lightingCompatibilityProfileId?: string;
  cameraCompatibilityProfileId?: string;
  audioCompatibilityProfileId?: string;
  vfxCompatibilityProfileId?: string;
  previewAssetId?: string;
  scale: number;
  navigationConstraints: string;
  cameraAccessConstraints: string;
  packageStatus: string;
  readinessStatus: string;
  validationIssues: readonly Readonly<Record<string, unknown>>[];
  readinessWarnings: readonly Readonly<Record<string, unknown>>[];
  missingRequirements: readonly string[];
  invalidAssetIds: readonly string[];
  requiredProcessingJobs: readonly string[];
  readinessValidatedVersion?: number;
  readinessValidatedAt?: string;
  version: number;
  createdAt: string;
  updatedAt: string;
}>;

export type EnvironmentReadiness = Readonly<{
  readinessStatus: string;
  blockingIssues: readonly Readonly<Record<string, unknown>>[];
  warnings: readonly Readonly<Record<string, unknown>>[];
  missingRequirements: readonly string[];
  invalidAssetIds: readonly string[];
  requiredProcessingJobs: readonly string[];
  validatedVersion?: number;
  validatedAt?: string;
}>;

export type EnvironmentMutation = Readonly<{
  environment: Environment;
  changeSummary: Readonly<Record<string, unknown>>;
}>;
