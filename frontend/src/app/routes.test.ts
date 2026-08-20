import { describe, expect, it } from "vitest";
import {
  readStudioEntryContext,
  rememberStudioEntryContext,
  resolveStudioEntryContext,
  resolveStudioRoute,
  STUDIO_CONTEXT_STORAGE_KEY,
} from "./routes";

describe("Studio entry routing", () => {
  it("resolves the Discovery experience", () => {
    expect(resolveStudioRoute("/discovery")).toEqual({ kind: "discovery" });
    expect(resolveStudioRoute("/discovery/")).toEqual({ kind: "discovery" });
  });

  it("resolves a Discovery moment workspace", () => {
    expect(resolveStudioRoute("/discovery/moments/1")).toEqual({
      kind: "discovery-moment",
      momentId: "1",
    });
  });

  it("resolves Environment list and package routes", () => {
    expect(
      resolveStudioRoute("/studio/projects/project-1/pre-production/environments"),
    ).toEqual({
      kind: "environment",
      projectId: "project-1",
      environmentId: undefined,
      stage: "build",
    });
    expect(
      resolveStudioRoute(
        "/studio/projects/project-1/pre-production/environments/environment-1",
      ),
    ).toMatchObject({
      kind: "environment",
      projectId: "project-1",
      environmentId: "environment-1",
    });
  });

  it("starts an explicitly selected Studio project in IDEA", () => {
    expect(
      resolveStudioRoute(
        "/studio",
        "?projectId=project-42&characterId=lead-actor",
      ),
    ).toEqual({
      kind: "workflow",
      projectId: "project-42",
      stage: "idea",
    });
  });

  it("uses remembered context before the development fallback", () => {
    expect(
      resolveStudioEntryContext("", {
        projectId: "remembered-project",
        characterId: "remembered-character",
      }),
    ).toEqual({
      projectId: "remembered-project",
      characterId: "remembered-character",
    });
  });

  it("starts a newly configured production in the IDEA stage", () => {
    expect(
      resolveStudioRoute(
        "/studio/projects/the-last-dawn/pre-production/characters/christopher",
        "?source=production-setup&projectId=project-1785&productionType=feature-film",
      ),
    ).toEqual({
      kind: "workflow",
      projectId: "project-1785",
      stage: "idea",
    });
  });

  it("falls back to the existing demonstration project", () => {
    expect(resolveStudioEntryContext()).toEqual({
      projectId: "the-last-dawn",
      characterId: "christopher",
    });
  });

  it("persists and restores the last Studio context", () => {
    const values = new Map<string, string>();
    const storage = {
      getItem: (key: string) => values.get(key) ?? null,
      setItem: (key: string, value: string) => values.set(key, value),
    };

    rememberStudioEntryContext(storage, {
      projectId: "project-7",
      characterId: "character-9",
    });

    expect(values.has(STUDIO_CONTEXT_STORAGE_KEY)).toBe(true);
    expect(readStudioEntryContext(storage)).toEqual({
      projectId: "project-7",
      characterId: "character-9",
    });
  });

  it("maps existing pages into the canonical creator workflow", () => {
    expect(resolveStudioRoute("/studio/projects/project-7/idea")).toEqual({
      kind: "workflow",
      projectId: "project-7",
      stage: "idea",
    });
    expect(resolveStudioRoute("/studio/projects/project-7/script")).toEqual({
      kind: "workflow",
      projectId: "project-7",
      stage: "shape",
    });
    expect(resolveStudioRoute("/studio/projects/project-7/ready")).toEqual({
      kind: "workflow",
      projectId: "project-7",
      stage: "ready",
    });
    for (const workspace of ["set", "studio", "render"]) {
      expect(
        resolveStudioRoute(`/studio/projects/project-7/${workspace}`),
      ).toEqual({
        kind: "workflow",
        projectId: "project-7",
        stage: "production",
        workspace,
      });
    }
    expect(resolveStudioRoute("/studio/projects/project-7/production")).toEqual({
      kind: "workflow",
      projectId: "project-7",
      stage: "production",
      workspace: "studio",
    });
  });

  it("fails clearly for unsafe explicit context", () => {
    expect(resolveStudioRoute("/studio", "?projectId=../unsafe")).toEqual({
      kind: "invalid-context",
      detail: "Studio context is invalid.",
    });
  });
});
