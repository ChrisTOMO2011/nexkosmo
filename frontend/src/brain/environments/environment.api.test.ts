import { describe, expect, it, vi } from "vitest";
import { EnvironmentApiClient } from "./environment.api";

const environment = {
  environment_id: "environment-1", workspace_id: "workspace-1",
  project_id: "project-1", production_id: "production-1",
  display_name: "City Street", description: "", environment_type_id: "type-city",
  location_type: "street", interior_exterior: "exterior", biome: "urban",
  climate_profile: "temperate", terrain_profile_id: null, weather_profile_id: null,
  time_of_day: "night", atmosphere_profile_id: null, background_asset_ids: [],
  terrain_asset_ids: [], building_asset_ids: [], nature_asset_ids: [],
  practical_asset_ids: [], material_profile_ids: [], texture_profile_ids: [],
  detail_asset_ids: [], style_profile_id: null, preview_asset_id: null, scale: 100,
  lighting_compatibility_profile_id: null, camera_compatibility_profile_id: null,
  audio_compatibility_profile_id: null, vfx_compatibility_profile_id: null,
  navigation_constraints: "Standard", camera_access_constraints: "Standard",
  package_status: "draft", readiness_status: "incomplete", validation_issues: [],
  readiness_warnings: [], missing_requirements: ["material-package"],
  invalid_asset_ids: [], required_processing_jobs: ["environment-preview"],
  readiness_validated_version: null, readiness_validated_at: null,
  version: 1, created_at: "2026-08-03T00:00:00Z", updated_at: "2026-08-03T00:00:00Z",
};

describe("EnvironmentApiClient", () => {
  it("maps canonical snake-case Environment responses", async () => {
    const fetcher = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ items: [environment] }), { status: 200 }),
    );
    const client = new EnvironmentApiClient("/api/v1", fetcher, () => undefined);
    const result = await client.listByProject("project-1");
    expect(result[0]).toMatchObject({
      environmentId: "environment-1",
      environmentTypeId: "type-city",
      timeOfDay: "night",
      version: 1,
    });
  });

  it("sends expected_version and an idempotency key for mutations", async () => {
    const listFetcher = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ items: [environment] }), { status: 200 }),
    );
    const [current] = await new EnvironmentApiClient(
      "/api/v1", listFetcher, () => undefined,
    ).listByProject("project-1");
    const fetcher = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({ environment: { ...environment, version: 2 }, change_summary: {} }),
        { status: 200 },
      ),
    );
    const client = new EnvironmentApiClient("/api/v1", fetcher, () => undefined);
    await client.updateProperties(current, { biome: "metropolitan" });
    const init = fetcher.mock.calls[0][1] as RequestInit;
    expect(JSON.parse(init.body as string)).toEqual({
      expected_version: 1,
      biome: "metropolitan",
    });
    expect(new Headers(init.headers).get("Idempotency-Key")).toBeTruthy();
  });

  it("uses category and filter cache dimensions in compatible-asset queries", async () => {
    const fetcher = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ items: [] }), { status: 200 }),
    );
    const client = new EnvironmentApiClient("/api/v1", fetcher, () => undefined);
    await client.listCompatible("environment-1", "terrain", "forest-floor");
    expect(fetcher.mock.calls[0][0]).toBe(
      "/api/v1/environments/environment-1/compatible-assets?category=terrain&subcategory=forest-floor",
    );
  });

  it("maps structured readiness without inventing completed processing", async () => {
    const fetcher = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          readiness_status: "processing_required",
          blocking_issues: [],
          warnings: [],
          missing_requirements: [],
          invalid_asset_ids: [],
          required_processing_jobs: ["environment-preview"],
          validated_version: 3,
          validated_at: "2026-08-07T00:00:00Z",
        }),
        { status: 200 },
      ),
    );
    const result = await new EnvironmentApiClient(
      "/api/v1",
      fetcher,
      () => undefined,
    ).getReadiness("environment-1");
    expect(result).toMatchObject({
      readinessStatus: "processing_required",
      requiredProcessingJobs: ["environment-preview"],
      validatedVersion: 3,
    });
  });
});
