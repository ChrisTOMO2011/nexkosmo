import { canonicalEntityId } from "../characters/api.clients";
import {
  authenticatedJsonHeaders,
  getAccessToken,
  type AccessTokenProvider,
} from "../auth/session";

export type ProjectStatus = "active" | "archived";
export type ProjectMemberRole = "Owner" | "Admin" | "Editor" | "Viewer";
export type ProductionType =
  | "Feature Film"
  | "Short Film"
  | "TV"
  | "Commercial"
  | "Music Video"
  | "Social"
  | "Animation"
  | "Documentary"
  | "Custom";
export type ProductionStatus =
  | "draft"
  | "pre-production"
  | "production"
  | "post-production"
  | "completed"
  | "archived";

export type AssignedCreativeProfile = Readonly<{
  profileId: string;
  displayName: string;
  roleLabel: string;
  avatarReference?: string;
  status: "active" | "unavailable" | "deferred";
  shortPrompt?: string;
  availability?: string;
  providerStatus?: string;
}>;

export type Project = Readonly<{
  projectId: string;
  workspaceId: string;
  name: string;
  description: string;
  status: ProjectStatus;
  ownerId: string;
  memberIds: readonly string[];
  producerProfile?: AssignedCreativeProfile;
  createdAt: string;
  updatedAt: string;
  version: number;
}>;

export type Production = Readonly<{
  productionId: string;
  projectId: string;
  workspaceId: string;
  name: string;
  productionType: ProductionType;
  status: ProductionStatus;
  ownerId: string;
  createdAt: string;
  updatedAt: string;
  version: number;
}>;

export interface ProjectDataGateway {
  listProjects(): Promise<readonly Project[]>;
  getProject(projectId: string): Promise<Project>;
  createProject(input: {
    name: string;
    description?: string;
    idempotencyKey: string;
  }): Promise<Project>;
  updateProject(
    projectId: string,
    patch: Partial<Pick<Project, "name" | "description" | "status">>,
    expectedVersion: number,
    idempotencyKey: string,
  ): Promise<Project>;
  listProductions(projectId: string): Promise<readonly Production[]>;
  getProduction(productionId: string): Promise<Production>;
  createProduction(
    projectId: string,
    input: {
      name: string;
      productionType: ProductionType;
      idempotencyKey: string;
    },
  ): Promise<Production>;
  updateProduction(
    productionId: string,
    patch: Partial<Pick<Production, "name" | "status">>,
    expectedVersion: number,
    idempotencyKey: string,
  ): Promise<Production>;
}

export class ProjectApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code: string,
  ) {
    super(message);
    this.name = "ProjectApiError";
  }
}

type SnakeProject = {
  project_id: string;
  workspace_id: string;
  name: string;
  description: string;
  status: ProjectStatus;
  owner_id: string;
  member_ids: string[];
  producer_profile?: {
    profile_id: string;
    display_name: string;
    role_label: string;
    avatar_reference?: string;
    status: AssignedCreativeProfile["status"];
    short_prompt?: string;
    availability?: string;
    provider_status?: string;
  };
  created_at: string;
  updated_at: string;
  version: number;
};

type SnakeProduction = {
  production_id: string;
  project_id: string;
  workspace_id: string;
  name: string;
  production_type: ProductionType;
  status: ProductionStatus;
  owner_id: string;
  created_at: string;
  updated_at: string;
  version: number;
};

const toProject = (value: SnakeProject): Project => ({
  projectId: value.project_id,
  workspaceId: value.workspace_id,
  name: value.name,
  description: value.description,
  status: value.status,
  ownerId: value.owner_id,
  memberIds: value.member_ids,
  producerProfile: value.producer_profile
    ? {
        profileId: value.producer_profile.profile_id,
        displayName: value.producer_profile.display_name,
        roleLabel: value.producer_profile.role_label,
        avatarReference: value.producer_profile.avatar_reference,
        status: value.producer_profile.status,
        shortPrompt: value.producer_profile.short_prompt,
        availability: value.producer_profile.availability,
        providerStatus: value.producer_profile.provider_status,
      }
    : undefined,
  createdAt: value.created_at,
  updatedAt: value.updated_at,
  version: value.version,
});

const toProduction = (value: SnakeProduction): Production => ({
  productionId: value.production_id,
  projectId: value.project_id,
  workspaceId: value.workspace_id,
  name: value.name,
  productionType: value.production_type,
  status: value.status,
  ownerId: value.owner_id,
  createdAt: value.created_at,
  updatedAt: value.updated_at,
  version: value.version,
});

export class HttpProjectDataGateway implements ProjectDataGateway {
  constructor(
    private readonly baseUrl: string,
    private readonly fetcher: typeof fetch = fetch,
    private readonly accessToken: AccessTokenProvider = getAccessToken,
  ) {}

  async listProjects() {
    const response = await this.#request<{ items: SnakeProject[] }>(
      "/projects?limit=200&offset=0",
    );
    return response.items.map(toProject);
  }

  async getProject(projectId: string) {
    return toProject(
      await this.#request<SnakeProject>(
        `/projects/${canonicalEntityId(projectId)}`,
      ),
    );
  }

  async createProject(input: {
    name: string;
    description?: string;
    idempotencyKey: string;
  }) {
    const response = await this.#request<{ project: SnakeProject }>(
      "/projects",
      {
        method: "POST",
        headers: { "Idempotency-Key": input.idempotencyKey },
        body: JSON.stringify({
          name: input.name,
          description: input.description ?? "",
        }),
      },
    );
    return toProject(response.project);
  }

  async updateProject(
    projectId: string,
    patch: Partial<Pick<Project, "name" | "description" | "status">>,
    expectedVersion: number,
    idempotencyKey: string,
  ) {
    const response = await this.#request<{ project: SnakeProject }>(
      `/projects/${canonicalEntityId(projectId)}`,
      {
        method: "PATCH",
        headers: { "Idempotency-Key": idempotencyKey },
        body: JSON.stringify({
          ...patch,
          expected_version: expectedVersion,
        }),
      },
    );
    return toProject(response.project);
  }

  async listProductions(projectId: string) {
    const response = await this.#request<{ items: SnakeProduction[] }>(
      `/projects/${canonicalEntityId(projectId)}/productions?limit=200&offset=0`,
    );
    return response.items.map(toProduction);
  }

  async getProduction(productionId: string) {
    return toProduction(
      await this.#request<SnakeProduction>(
        `/productions/${canonicalEntityId(productionId)}`,
      ),
    );
  }

  async createProduction(
    projectId: string,
    input: {
      name: string;
      productionType: ProductionType;
      idempotencyKey: string;
    },
  ) {
    const response = await this.#request<{ production: SnakeProduction }>(
      `/projects/${canonicalEntityId(projectId)}/productions`,
      {
        method: "POST",
        headers: { "Idempotency-Key": input.idempotencyKey },
        body: JSON.stringify({
          name: input.name,
          production_type: input.productionType,
        }),
      },
    );
    return toProduction(response.production);
  }

  async updateProduction(
    productionId: string,
    patch: Partial<Pick<Production, "name" | "status">>,
    expectedVersion: number,
    idempotencyKey: string,
  ) {
    const response = await this.#request<{ production: SnakeProduction }>(
      `/productions/${canonicalEntityId(productionId)}`,
      {
        method: "PATCH",
        headers: { "Idempotency-Key": idempotencyKey },
        body: JSON.stringify({
          ...patch,
          expected_version: expectedVersion,
        }),
      },
    );
    return toProduction(response.production);
  }

  async #request<T>(path: string, init: RequestInit = {}): Promise<T> {
    let response: Response;
    try {
      const fetcher = this.fetcher;
      response = await fetcher(`${this.baseUrl}${path}`, {
        ...init,
        headers: authenticatedJsonHeaders(this.accessToken, init.headers),
      });
    } catch {
      throw new ProjectApiError(
        "The project service is unavailable.",
        0,
        "network_error",
      );
    }
    if (!response.ok) {
      const problem = (await response.json().catch(() => ({}))) as {
        detail?: string;
        code?: string;
      };
      throw new ProjectApiError(
        problem.detail ?? `Project API request failed (${response.status}).`,
        response.status,
        problem.code ?? "api_error",
      );
    }
    return (await response.json()) as T;
  }
}

export class InMemoryProjectDataGateway implements ProjectDataGateway {
  readonly #projects = new Map<string, Project>();
  readonly #productions = new Map<string, Production>();

  constructor(projectId = "the-last-dawn") {
    const canonicalId = canonicalEntityId(projectId);
    const timestamp = "2026-07-28T00:00:00Z";
    const workspaceId = canonicalEntityId("default-workspace");
    const ownerId = canonicalEntityId("default-owner");
    this.#projects.set(canonicalId, {
      projectId: canonicalId,
      workspaceId,
      name: "The Last Dawn",
      description: "",
      status: "active",
      ownerId,
      memberIds: [ownerId],
      createdAt: timestamp,
      updatedAt: timestamp,
      version: 1,
    });
    this.#productions.set(canonicalId, {
      productionId: canonicalId,
      projectId: canonicalId,
      workspaceId,
      name: "The Last Dawn",
      productionType: "Feature Film",
      status: "pre-production",
      ownerId,
      createdAt: timestamp,
      updatedAt: timestamp,
      version: 1,
    });
  }

  async listProjects() {
    return [...this.#projects.values()];
  }

  async getProject(projectId: string) {
    const project = this.#projects.get(canonicalEntityId(projectId));
    if (!project) {
      throw new ProjectApiError("Project not found.", 404, "not_found");
    }
    return project;
  }

  async createProject(): Promise<Project> {
    throw new ProjectApiError(
      "Not implemented in test memory mode.",
      501,
      "not_implemented",
    );
  }

  async updateProject(): Promise<Project> {
    throw new ProjectApiError(
      "Not implemented in test memory mode.",
      501,
      "not_implemented",
    );
  }

  async listProductions(projectId: string) {
    const canonicalId = canonicalEntityId(projectId);
    return [...this.#productions.values()].filter(
      (production) => production.projectId === canonicalId,
    );
  }

  async getProduction(productionId: string) {
    const production = this.#productions.get(canonicalEntityId(productionId));
    if (!production) {
      throw new ProjectApiError("Production not found.", 404, "not_found");
    }
    return production;
  }

  async createProduction(): Promise<Production> {
    throw new ProjectApiError(
      "Not implemented in test memory mode.",
      501,
      "not_implemented",
    );
  }

  async updateProduction(): Promise<Production> {
    throw new ProjectApiError(
      "Not implemented in test memory mode.",
      501,
      "not_implemented",
    );
  }
}

export function createProjectDataGateway(): ProjectDataGateway {
  const source =
    import.meta.env.VITE_CHARACTER_DATA_SOURCE ??
    (import.meta.env.MODE === "test" ? "memory" : "api");
  if (source === "memory") return new InMemoryProjectDataGateway();
  if (source !== "api") {
    throw new Error(`Unknown project data source: ${source}`);
  }
  return new HttpProjectDataGateway(
    import.meta.env.VITE_NEXKOSMO_API_BASE_URL ?? "/api/v1",
  );
}

export const projectDataGateway = createProjectDataGateway();
