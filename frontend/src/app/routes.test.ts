import { describe, expect, it } from "vitest";
import { resolveAppRoute } from "./routes";
import { WORKFLOW_STAGES, workflowHref } from "./workflow";

describe("canonical shell routes", () => {
  it.each(WORKFLOW_STAGES)("resolves the %s stage", (stage) => {
    const path = workflowHref("project_42", stage);
    expect(resolveAppRoute(path)).toEqual({
      kind: "stage",
      projectId: "project_42",
      stage,
    });
  });

  it("requires project context instead of inventing an identity", () => {
    expect(resolveAppRoute("/studio")).toEqual({
      kind: "project-required",
    });
  });

  it("resolves the OIDC callback without inventing a user", () => {
    expect(resolveAppRoute("/auth/callback")).toEqual({ kind: "auth-callback" });
  });

  it("rejects unsafe project identifiers", () => {
    expect(resolveAppRoute("/studio/projects/%2E%2E/build")).toEqual({
      kind: "invalid-context",
    });
  });

  it("does not treat contextual workspaces as top-level stages", () => {
    expect(resolveAppRoute("/studio/projects/project_42/studio")).toEqual({
      kind: "not-found",
    });
    expect(resolveAppRoute("/studio/projects/project_42/render")).toEqual({
      kind: "not-found",
    });
  });
});
