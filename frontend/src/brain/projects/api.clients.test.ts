import { describe, expect, it, vi } from "vitest";
import { canonicalEntityId } from "../characters";
import { HttpProjectDataGateway } from "./api.clients";

const projectResponse = {
  project_id: canonicalEntityId("the-last-dawn"),
  workspace_id: canonicalEntityId("workspace"),
  name: "The Last Dawn",
  description: "Feature production",
  status: "active",
  owner_id: canonicalEntityId("owner"),
  member_ids: [canonicalEntityId("owner")],
  created_at: "2026-07-28T00:00:00Z",
  updated_at: "2026-07-28T00:00:00Z",
  version: 1,
} as const;

const productionResponse = {
  production_id: canonicalEntityId("production"),
  project_id: projectResponse.project_id,
  workspace_id: projectResponse.workspace_id,
  name: "The Last Dawn",
  production_type: "Feature Film",
  status: "pre-production",
  owner_id: projectResponse.owner_id,
  created_at: projectResponse.created_at,
  updated_at: projectResponse.updated_at,
  version: 2,
} as const;

describe("project and production API adapter", () => {
  it("maps project and production contracts", async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce(Response.json(projectResponse))
      .mockResolvedValueOnce(
        Response.json({ items: [productionResponse], limit: 200, offset: 0 }),
      );
    const gateway = new HttpProjectDataGateway(
      "https://api.example.test/api/v1",
      fetcher as typeof fetch,
    );

    await expect(gateway.getProject("the-last-dawn")).resolves.toMatchObject({
      projectId: projectResponse.project_id,
      name: "The Last Dawn",
      version: 1,
    });
    await expect(
      gateway.listProductions("the-last-dawn"),
    ).resolves.toEqual([
      expect.objectContaining({
        productionId: productionResponse.production_id,
        productionType: "Feature Film",
      }),
    ]);
  });

  it("maps an optional assigned producer profile without inventing one", async () => {
    const fetcher = vi.fn(async () =>
      Response.json({
        ...projectResponse,
        producer_profile: {
          profile_id: "custom-producer-1",
          display_name: "Custom Producer",
          role_label: "Executive Producer",
          status: "active",
          provider_status: "deferred",
        },
      }),
    );
    const gateway = new HttpProjectDataGateway(
      "https://api.example.test/api/v1",
      fetcher as typeof fetch,
    );

    await expect(gateway.getProject("the-last-dawn")).resolves.toMatchObject({
      producerProfile: {
        profileId: "custom-producer-1",
        displayName: "Custom Producer",
        roleLabel: "Executive Producer",
        status: "active",
        providerStatus: "deferred",
      },
    });
  });

  it("sends expected versions and idempotency keys", async () => {
    const fetcher = vi.fn(async () =>
      Response.json({
        project: { ...projectResponse, name: "Last Dawn", version: 2 },
        change_summary: {},
      }),
    );
    const gateway = new HttpProjectDataGateway(
      "https://api.example.test/api/v1",
      fetcher as typeof fetch,
    );
    await gateway.updateProject(
      "the-last-dawn",
      { name: "Last Dawn" },
      1,
      "project-update-1",
    );

    const [, init] = fetcher.mock.calls[0] as unknown as [
      string,
      RequestInit,
    ];
    expect(init.headers).toMatchObject({
      "Idempotency-Key": "project-update-1",
    });
    expect(JSON.parse(init.body as string)).toEqual({
      name: "Last Dawn",
      expected_version: 1,
    });
  });

  it("preserves HTTP conflicts for optimistic concurrency handling", async () => {
    const fetcher = vi.fn(async () =>
      Response.json(
        { detail: "Project version conflict.", code: "version_conflict" },
        { status: 409 },
      ),
    );
    const gateway = new HttpProjectDataGateway(
      "https://api.example.test/api/v1",
      fetcher as typeof fetch,
    );
    await expect(gateway.getProject("the-last-dawn")).rejects.toMatchObject({
      status: 409,
      code: "version_conflict",
    });
  });
});
