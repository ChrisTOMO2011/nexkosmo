import type {
  ProductionWorkspaceId,
  WorkflowStageId,
} from "../features/studio/config/navigation";

export type StudioRoute =
  | { kind: "home" }
  | { kind: "discovery" }
  | { kind: "discovery-moment"; momentId: string }
  | {
      kind: "character";
      projectId: string;
      characterId: string;
      stage: "build";
    }
  | {
      kind: "environment";
      projectId: string;
      environmentId?: string;
      stage: "build";
    }
  | {
      kind: "workflow";
      projectId: string;
      stage: Extract<
        WorkflowStageId,
        "idea" | "shape" | "ready" | "production"
      >;
      workspace?: ProductionWorkspaceId;
    }
  | { kind: "invalid-context"; detail: string }
  | { kind: "not-found" };

export type StudioEntryContext = {
  projectId: string;
  characterId: string;
};

export const STUDIO_CONTEXT_STORAGE_KEY = "nexkosmo.lastStudioContext";

const defaultStudioContext: StudioEntryContext = {
  projectId: "the-last-dawn",
  characterId: "christopher",
};

const characterRoute =
  /^\/studio\/projects\/([^/]+)\/pre-production\/characters\/([^/]+)\/?$/;
const environmentRoute =
  /^\/studio\/projects\/([^/]+)\/pre-production\/environments(?:\/([^/]+))?\/?$/;
const workflowRoute =
  /^\/studio\/projects\/([^/]+)\/(idea|script|set|studio|render|ready|production)\/?$/;
const discoveryMomentRoute = /^\/discovery\/moments\/([^/]+)\/?$/;

function entryValue(value: string | null | undefined) {
  const normalized = value?.trim();
  return normalized && /^[a-z0-9][a-z0-9_-]{0,127}$/iu.test(normalized)
    ? normalized
    : undefined;
}

function hasInvalidExplicitContext(params: URLSearchParams) {
  return ["projectId", "characterId"].some(
    (key) => params.has(key) && entryValue(params.get(key)) === undefined,
  );
}

export function resolveStudioEntryContext(
  search = "",
  remembered?: Partial<StudioEntryContext> | null,
): StudioEntryContext {
  const params = new URLSearchParams(search);

  return {
    projectId:
      entryValue(params.get("projectId")) ??
      entryValue(remembered?.projectId) ??
      defaultStudioContext.projectId,
    characterId:
      entryValue(params.get("characterId")) ??
      entryValue(remembered?.characterId) ??
      defaultStudioContext.characterId,
  };
}

export function readStudioEntryContext(
  storage: Pick<Storage, "getItem">,
): Partial<StudioEntryContext> | null {
  try {
    const value = storage.getItem(STUDIO_CONTEXT_STORAGE_KEY);
    if (!value) return null;
    const parsed = JSON.parse(value) as Partial<StudioEntryContext>;
    return {
      projectId: entryValue(parsed.projectId),
      characterId: entryValue(parsed.characterId),
    };
  } catch {
    return null;
  }
}

export function rememberStudioEntryContext(
  storage: Pick<Storage, "setItem">,
  context: StudioEntryContext,
) {
  try {
    storage.setItem(STUDIO_CONTEXT_STORAGE_KEY, JSON.stringify(context));
  } catch {
    // Navigation remains usable when browser storage is unavailable.
  }
}

export function resolveStudioRoute(
  pathname: string,
  search = "",
  remembered?: Partial<StudioEntryContext> | null,
): StudioRoute {
  if (pathname === "/" || pathname === "/index.html") {
    return { kind: "home" };
  }

  if (pathname === "/discovery" || pathname === "/discovery/") {
    return { kind: "discovery" };
  }

  const discoveryMomentMatch = pathname.match(discoveryMomentRoute);
  if (discoveryMomentMatch) {
    const momentId = entryValue(decodeURIComponent(discoveryMomentMatch[1]));
    if (!momentId) {
      return { kind: "invalid-context", detail: "Discovery moment is invalid." };
    }
    return { kind: "discovery-moment", momentId };
  }

  if (pathname === "/studio" || pathname === "/studio/") {
    const params = new URLSearchParams(search);
    if (hasInvalidExplicitContext(params)) {
      return { kind: "invalid-context", detail: "Studio context is invalid." };
    }
    const context = resolveStudioEntryContext(search, remembered);
    return {
      kind: "workflow",
      projectId: context.projectId,
      stage: "idea",
    };
  }

  const characterMatch = pathname.match(characterRoute);
  if (characterMatch) {
    const params = new URLSearchParams(search);
    const pathProjectId = entryValue(decodeURIComponent(characterMatch[1]));
    const pathCharacterId = entryValue(decodeURIComponent(characterMatch[2]));
    if (!pathProjectId || !pathCharacterId || hasInvalidExplicitContext(params)) {
      return { kind: "invalid-context", detail: "Character route context is invalid." };
    }
    const isProductionSetup = params.get("source") === "production-setup";
    const setupProjectId = entryValue(params.get("projectId"));
    if (isProductionSetup && setupProjectId) {
      return { kind: "workflow", projectId: setupProjectId, stage: "idea" };
    }
    return {
      kind: "character",
      projectId: pathProjectId,
      characterId:
        (isProductionSetup && entryValue(params.get("characterId"))) ||
        pathCharacterId,
      stage: "build",
    };
  }

  const environmentMatch = pathname.match(environmentRoute);
  if (environmentMatch) {
    const projectId = entryValue(decodeURIComponent(environmentMatch[1]));
    const environmentId = environmentMatch[2]
      ? entryValue(decodeURIComponent(environmentMatch[2]))
      : undefined;
    if (!projectId || (environmentMatch[2] && !environmentId)) {
      return { kind: "invalid-context", detail: "Environment route context is invalid." };
    }
    return { kind: "environment", projectId, environmentId, stage: "build" };
  }

  const workflowMatch = pathname.match(workflowRoute);
  if (workflowMatch) {
    const projectId = entryValue(decodeURIComponent(workflowMatch[1]));
    if (!projectId) {
      return { kind: "invalid-context", detail: "Workflow project context is invalid." };
    }
    const requestedWorkspace = workflowMatch[2];
    if (requestedWorkspace === "idea") {
      return { kind: "workflow", projectId, stage: "idea" };
    }
    if (requestedWorkspace === "script") {
      return { kind: "workflow", projectId, stage: "shape" };
    }
    if (requestedWorkspace === "ready") {
      return { kind: "workflow", projectId, stage: "ready" };
    }
    return {
      kind: "workflow",
      projectId,
      stage: "production",
      workspace:
        requestedWorkspace === "production"
          ? "studio"
          : (requestedWorkspace as ProductionWorkspaceId),
    };
  }

  return { kind: "not-found" };
}
