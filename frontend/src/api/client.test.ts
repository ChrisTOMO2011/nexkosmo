import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "./client";

const session = {
  accessToken: "header.payload.signature",
  workspaceId: "00000000-0000-4000-8000-000000000002",
  principalId: "00000000-0000-4000-8000-000000000001",
};

afterEach(() => vi.unstubAllGlobals());

describe("authenticated API client", () => {
  it("lists Projects with the bearer token and explicit Workspace", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [],
    });
    vi.stubGlobal("fetch", fetchMock);
    await api.listProjects(session);
    expect(fetchMock).toHaveBeenCalledWith(
      "/v1/workspaces/00000000-0000-4000-8000-000000000002/projects",
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer header.payload.signature",
        }),
      }),
    );
  });

  it("uses idempotency and expected version for Character updates", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ version: 4 }),
    });
    vi.stubGlobal("fetch", fetchMock);
    await api.updateCharacter(
      session,
      "project-id",
      {
        character_id: "character-id",
        workspace_id: session.workspaceId,
        project_id: "project-id",
        display_name: "Christopher",
        role_label: "Lead",
        version: 3,
      },
      "Christopher",
      "Lead",
    );
    const init = fetchMock.mock.calls[0][1] as RequestInit;
    expect(init.method).toBe("PATCH");
    expect(init.headers).toEqual(
      expect.objectContaining({ "Idempotency-Key": expect.any(String) }),
    );
    expect(JSON.parse(String(init.body))).toEqual(
      expect.objectContaining({ expected_version: 3 }),
    );
  });
});
