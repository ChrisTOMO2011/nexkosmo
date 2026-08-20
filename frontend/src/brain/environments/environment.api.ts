import {
  authenticatedJsonHeaders,
  getAccessToken,
  type AccessTokenProvider,
} from "../auth/session";
import type {
  Environment,
  EnvironmentAsset,
  EnvironmentMutation,
  EnvironmentReadiness,
  EnvironmentType,
} from "./environment.types";

export class EnvironmentApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code: string,
  ) {
    super(message);
    this.name = "EnvironmentApiError";
  }

  get conflict() {
    return this.status === 409;
  }
}

type Fetcher = typeof fetch;

const arrays = [
  "background_asset_ids",
  "terrain_asset_ids",
  "building_asset_ids",
  "nature_asset_ids",
  "practical_asset_ids",
  "material_profile_ids",
  "texture_profile_ids",
  "detail_asset_ids",
] as const;

function mapEnvironment(item: Record<string, unknown>): Environment {
  return {
    environmentId: item.environment_id as string,
    workspaceId: item.workspace_id as string,
    projectId: item.project_id as string,
    productionId: item.production_id as string,
    displayName: item.display_name as string,
    description: item.description as string,
    environmentTypeId: item.environment_type_id as string,
    locationType: item.location_type as string,
    interiorExterior: item.interior_exterior as string,
    biome: item.biome as string,
    climateProfile: item.climate_profile as string,
    terrainProfileId: item.terrain_profile_id as string | undefined,
    weatherProfileId: item.weather_profile_id as string | undefined,
    timeOfDay: item.time_of_day as string,
    atmosphereProfileId: item.atmosphere_profile_id as string | undefined,
    backgroundAssetIds: item[arrays[0]] as string[],
    terrainAssetIds: item[arrays[1]] as string[],
    buildingAssetIds: item[arrays[2]] as string[],
    natureAssetIds: item[arrays[3]] as string[],
    practicalAssetIds: item[arrays[4]] as string[],
    materialProfileIds: item[arrays[5]] as string[],
    textureProfileIds: item[arrays[6]] as string[],
    detailAssetIds: item[arrays[7]] as string[],
    styleProfileId: item.style_profile_id as string | undefined,
    lightingCompatibilityProfileId: item.lighting_compatibility_profile_id as string | undefined,
    cameraCompatibilityProfileId: item.camera_compatibility_profile_id as string | undefined,
    audioCompatibilityProfileId: item.audio_compatibility_profile_id as string | undefined,
    vfxCompatibilityProfileId: item.vfx_compatibility_profile_id as string | undefined,
    previewAssetId: item.preview_asset_id as string | undefined,
    scale: item.scale as number,
    navigationConstraints: item.navigation_constraints as string,
    cameraAccessConstraints: item.camera_access_constraints as string,
    packageStatus: item.package_status as string,
    readinessStatus: item.readiness_status as string,
    validationIssues: item.validation_issues as Record<string, unknown>[],
    readinessWarnings: item.readiness_warnings as Record<string, unknown>[],
    missingRequirements: item.missing_requirements as string[],
    invalidAssetIds: item.invalid_asset_ids as string[],
    requiredProcessingJobs: item.required_processing_jobs as string[],
    readinessValidatedVersion: item.readiness_validated_version as number | undefined,
    readinessValidatedAt: item.readiness_validated_at as string | undefined,
    version: item.version as number,
    createdAt: item.created_at as string,
    updatedAt: item.updated_at as string,
  };
}

function mapType(item: Record<string, unknown>): EnvironmentType {
  return {
    environmentTypeId: item.environment_type_id as string,
    key: item.key as string,
    name: item.name as string,
    enabled: item.enabled as boolean,
    capabilities: item.capabilities as string[],
    supportedTabs: item.supported_tabs as string[],
    version: item.version as number,
  };
}

function mapAsset(item: Record<string, unknown>): EnvironmentAsset {
  return {
    assetId: item.asset_id as string,
    name: item.name as string,
    category: item.category as string,
    subcategory: item.subcategory as string,
    thumbnailReference: item.thumbnail_reference as string,
    previewReference: item.preview_reference as string,
    status: item.status as string,
    visibility: item.visibility as string,
    uploaded: item.uploaded as boolean,
    generated: item.generated as boolean,
    placeholder: item.placeholder as boolean,
    version: item.version as number,
  };
}

export class EnvironmentApiClient {
  constructor(
    private readonly baseUrl = import.meta.env.VITE_NEXKOSMO_API_BASE_URL ?? "/api/v1",
    private readonly fetcher: Fetcher = fetch.bind(globalThis),
    private readonly accessToken: AccessTokenProvider = getAccessToken,
  ) {}

  async listTypes() {
    return (await this.request<Record<string, unknown>[]>("/environment-types")).map(mapType);
  }

  async listByProject(projectId: string) {
    const response = await this.request<{ items: Record<string, unknown>[] }>(
      `/projects/${projectId}/environments`,
    );
    return response.items.map(mapEnvironment);
  }

  async get(environmentId: string) {
    return mapEnvironment(
      await this.request<Record<string, unknown>>(`/environments/${environmentId}`),
    );
  }

  async create(input: {
    projectId: string;
    productionId: string;
    displayName: string;
    environmentTypeId: string;
    description?: string;
  }) {
    return this.mutation(`/projects/${input.projectId}/environments`, {
      method: "POST",
      body: JSON.stringify({
        production_id: input.productionId,
        display_name: input.displayName,
        environment_type_id: input.environmentTypeId,
        description: input.description ?? "",
      }),
    });
  }

  async createForProduction(input: {
    productionId: string;
    displayName: string;
    environmentTypeId: string;
    description?: string;
  }) {
    return this.mutation(`/productions/${input.productionId}/environments`, {
      method: "POST",
      body: JSON.stringify({
        display_name: input.displayName,
        environment_type_id: input.environmentTypeId,
        description: input.description ?? "",
      }),
    });
  }

  async updateIdentity(
    environment: Environment,
    values: Readonly<{ display_name?: string; description?: string }>,
  ) {
    return this.mutation(`/environments/${environment.environmentId}/identity`, {
      method: "PATCH",
      body: JSON.stringify({ expected_version: environment.version, ...values }),
    });
  }

  async updateProperties(
    environment: Environment,
    values: Readonly<Record<string, string | number>>,
  ) {
    return this.mutation(`/environments/${environment.environmentId}/properties`, {
      method: "PATCH",
      body: JSON.stringify({ expected_version: environment.version, ...values }),
    });
  }

  async changeType(environment: Environment, environmentTypeId: string) {
    return this.mutation(`/environments/${environment.environmentId}/change-type`, {
      method: "POST",
      body: JSON.stringify({
        expected_version: environment.version,
        environment_type_id: environmentTypeId,
      }),
    });
  }

  async listCompatible(environmentId: string, category?: string, subcategory?: string) {
    const parameters = new URLSearchParams();
    if (category) parameters.set("category", category);
    if (subcategory) parameters.set("subcategory", subcategory);
    const query = parameters.size ? `?${parameters.toString()}` : "";
    const response = await this.request<{ items: Record<string, unknown>[] }>(
      `/environments/${environmentId}/compatible-assets${query}`,
    );
    return response.items.map(mapAsset);
  }

  async select(environment: Environment, category: string, assetId: string) {
    return this.mutation(
      `/environments/${environment.environmentId}/selections/${category}`,
      {
        method: "PUT",
        body: JSON.stringify({ asset_id: assetId, expected_version: environment.version }),
      },
    );
  }

  async replace(
    environment: Environment,
    category: string,
    assetIds: readonly string[],
  ) {
    return this.mutation(
      `/environments/${environment.environmentId}/collections/${category}`,
      {
        method: "PUT",
        body: JSON.stringify({
          asset_ids: assetIds,
          expected_version: environment.version,
        }),
      },
    );
  }

  async remove(environment: Environment, category: string, assetId?: string) {
    return this.mutation(
      `/environments/${environment.environmentId}/selections/${category}`,
      {
        method: "DELETE",
        body: JSON.stringify({
          expected_version: environment.version,
          asset_id: assetId,
        }),
      },
    );
  }

  async validate(environment: Environment) {
    return this.mutation(`/environments/${environment.environmentId}/validate`, {
      method: "POST",
      body: JSON.stringify({ expected_version: environment.version }),
    });
  }

  async getReadiness(environmentId: string): Promise<EnvironmentReadiness> {
    const item = await this.request<Record<string, unknown>>(
      `/environments/${environmentId}/readiness`,
    );
    return {
      readinessStatus: item.readiness_status as string,
      blockingIssues: item.blocking_issues as Record<string, unknown>[],
      warnings: item.warnings as Record<string, unknown>[],
      missingRequirements: item.missing_requirements as string[],
      invalidAssetIds: item.invalid_asset_ids as string[],
      requiredProcessingJobs: item.required_processing_jobs as string[],
      validatedVersion: item.validated_version as number | undefined,
      validatedAt: item.validated_at as string | undefined,
    };
  }

  private async mutation(path: string, init: RequestInit): Promise<EnvironmentMutation> {
    const response = await this.request<{
      environment: Record<string, unknown>;
      change_summary: Record<string, unknown>;
    }>(path, {
      ...init,
      headers: { "Idempotency-Key": crypto.randomUUID(), ...init.headers },
    });
    return {
      environment: mapEnvironment(response.environment),
      changeSummary: response.change_summary,
    };
  }

  private async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    let response: Response;
    try {
      response = await this.fetcher(`${this.baseUrl}${path}`, {
        ...init,
        headers: authenticatedJsonHeaders(this.accessToken, init.headers),
      });
    } catch {
      throw new EnvironmentApiError("The Environment service is unavailable.", 0, "network_error");
    }
    if (!response.ok) {
      const problem = (await response.json().catch(() => ({}))) as {
        detail?: string;
        code?: string;
      };
      throw new EnvironmentApiError(
        problem.detail ?? `Environment API request failed (${response.status}).`,
        response.status,
        problem.code ?? "api_error",
      );
    }
    return (await response.json()) as T;
  }
}

export const environmentApi = new EnvironmentApiClient();
