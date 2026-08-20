import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  environmentApi,
  EnvironmentApiError,
  type Environment,
} from "../../../../brain/environments";
import { projectDataGateway } from "../../../../brain/projects";
import { useEnvironmentWorkspaceController } from "./useEnvironmentWorkspaceController";

const environment: Environment = {
  environmentId: "52000000-0000-4000-8000-000000000001",
  workspaceId: "52000000-0000-4000-8000-000000000002",
  projectId: "52000000-0000-4000-8000-000000000003",
  productionId: "52000000-0000-4000-8000-000000000004",
  displayName: "City Street",
  description: "",
  environmentTypeId: "22000000-0000-4000-8000-000000000001",
  locationType: "street",
  interiorExterior: "exterior",
  biome: "urban",
  climateProfile: "temperate",
  timeOfDay: "night",
  backgroundAssetIds: [],
  terrainAssetIds: [],
  buildingAssetIds: [],
  natureAssetIds: [],
  practicalAssetIds: [],
  materialProfileIds: [],
  textureProfileIds: [],
  detailAssetIds: [],
  scale: 100,
  navigationConstraints: "Standard",
  cameraAccessConstraints: "Standard",
  packageStatus: "draft",
  readinessStatus: "incomplete",
  validationIssues: [],
  readinessWarnings: [],
  missingRequirements: ["material-package"],
  invalidAssetIds: [],
  requiredProcessingJobs: ["environment-preview"],
  version: 1,
  createdAt: "2026-08-07T00:00:00Z",
  updatedAt: "2026-08-07T00:00:00Z",
};

const environmentType = {
  environmentTypeId: environment.environmentTypeId,
  key: "city",
  name: "City",
  enabled: true,
  capabilities: ["terrain"],
  supportedTabs: ["Identity", "Terrain"],
  version: 1,
} as const;

function arrangeController() {
  vi.spyOn(projectDataGateway, "getProject").mockResolvedValue({
    projectId: environment.projectId,
    workspaceId: environment.workspaceId,
    name: "Project",
    description: "",
    status: "active",
    ownerId: "owner",
    memberIds: [],
    createdAt: environment.createdAt,
    updatedAt: environment.updatedAt,
    version: 1,
  });
  vi.spyOn(projectDataGateway, "listProductions").mockResolvedValue([
    {
      productionId: environment.productionId,
      projectId: environment.projectId,
      workspaceId: environment.workspaceId,
      name: "Production",
      productionType: "Feature Film",
      status: "pre-production",
      ownerId: "owner",
      createdAt: environment.createdAt,
      updatedAt: environment.updatedAt,
      version: 1,
    },
  ]);
  vi.spyOn(environmentApi, "listTypes").mockResolvedValue([environmentType]);
  vi.spyOn(environmentApi, "listByProject").mockResolvedValue([environment]);
  vi.spyOn(environmentApi, "getReadiness").mockResolvedValue({
    readinessStatus: "incomplete",
    blockingIssues: [],
    warnings: [],
    missingRequirements: ["material-package"],
    invalidAssetIds: [],
    requiredProcessingJobs: ["environment-preview"],
  });
  vi.spyOn(environmentApi, "listCompatible").mockResolvedValue([
    {
      assetId: "asset-1",
      name: "Street",
      category: "terrain",
      subcategory: "street",
      thumbnailReference: "thumbnail",
      previewReference: "preview",
      status: "available",
      visibility: "global",
      uploaded: false,
      generated: false,
      placeholder: false,
      version: 1,
    },
  ]);
  return renderHook(() =>
    useEnvironmentWorkspaceController({ projectId: environment.projectId }),
  );
}

afterEach(() => vi.restoreAllMocks());

describe("useEnvironmentWorkspaceController", () => {
  it("keeps filters as navigation state and includes category and filter in requests", async () => {
    const hook = arrangeController();
    await waitFor(() => expect(hook.result.current.selected?.environmentId).toBe(environment.environmentId));
    act(() => hook.result.current.setActiveTab("Terrain"));
    await waitFor(() => expect(hook.result.current.assets).toHaveLength(1));
    const version = hook.result.current.selected?.version;
    act(() => hook.result.current.setActiveFilter("street"));
    await waitFor(() =>
      expect(environmentApi.listCompatible).toHaveBeenLastCalledWith(
        environment.environmentId,
        "terrain",
        "street",
      ),
    );
    expect(hook.result.current.selected?.version).toBe(version);
  });

  it("retains the canonical snapshot when a mutation fails", async () => {
    const hook = arrangeController();
    vi.spyOn(environmentApi, "updateProperties").mockRejectedValue(
      new EnvironmentApiError("Rejected", 422, "invariant_violation"),
    );
    await waitFor(() => expect(hook.result.current.selected).toBeDefined());
    await act(() => hook.result.current.updateProperties({ biome: "forest" }));
    expect(hook.result.current.selected).toEqual(environment);
    expect(hook.result.current.status).toBe("Rejected");
  });

  it("reloads canonical state after an optimistic concurrency conflict", async () => {
    const hook = arrangeController();
    vi.spyOn(environmentApi, "updateProperties").mockRejectedValue(
      new EnvironmentApiError("Conflict", 409, "concurrency_conflict"),
    );
    vi.spyOn(environmentApi, "get").mockResolvedValue({ ...environment, version: 2 });
    await waitFor(() => expect(hook.result.current.selected).toBeDefined());
    await act(() => hook.result.current.updateProperties({ biome: "forest" }));
    await waitFor(() => expect(hook.result.current.selected?.version).toBe(2));
    expect(hook.result.current.status).toContain("changed elsewhere");
  });

  it("exposes honest deferred controls and producer fallback", async () => {
    const hook = arrangeController();
    await waitFor(() => expect(hook.result.current.selected).toBeDefined());
    act(() => hook.result.current.showDeferred("asset-upload"));
    expect(hook.result.current.status).toContain("no file was stored");
    act(() => hook.result.current.showDeferred("character-generation"));
    expect(hook.result.current.status).toContain("no asset was fabricated");
    act(() => hook.result.current.showDeferred("producer-conversation"));
    expect(hook.result.current.status).toContain("no AI session was started");
    expect(hook.result.current.producer).toBeUndefined();
  });
});
