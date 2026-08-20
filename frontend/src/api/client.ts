import type { AuthSession } from "../auth/session";

export type Project = {
  project_id: string;
  workspace_id: string;
  name: string;
  lifecycle: "active" | "archived";
  version: number;
};

export type Character = {
  character_id: string;
  workspace_id: string;
  project_id: string;
  display_name: string;
  role_label: string | null;
  version: number;
};

const apiBase = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/u, "");

async function request<T>(
  session: AuthSession,
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${session.accessToken}`,
      "Content-Type": "application/json",
      ...init.headers,
    },
  });
  if (!response.ok) {
    const problem = (await response.json().catch(() => null)) as {
      detail?: string;
    } | null;
    throw new Error(problem?.detail || `API request failed (${response.status}).`);
  }
  return (await response.json()) as T;
}

const workspacePath = (session: AuthSession) =>
  `/v1/workspaces/${encodeURIComponent(session.workspaceId)}`;

export const api = {
  listProjects: (session: AuthSession) =>
    request<Project[]>(session, `${workspacePath(session)}/projects`),
  createProject: (session: AuthSession, name: string) =>
    request<Project>(session, `${workspacePath(session)}/projects`, {
      method: "POST",
      headers: { "Idempotency-Key": crypto.randomUUID() },
      body: JSON.stringify({ name }),
    }),
  listCharacters: (session: AuthSession, projectId: string) =>
    request<Character[]>(
      session,
      `${workspacePath(session)}/projects/${encodeURIComponent(projectId)}/characters`,
    ),
  getCharacter: (session: AuthSession, projectId: string, characterId: string) =>
    request<Character>(
      session,
      `${workspacePath(session)}/projects/${encodeURIComponent(projectId)}/characters/${encodeURIComponent(characterId)}`,
    ),
  createCharacter: (
    session: AuthSession,
    projectId: string,
    displayName: string,
    roleLabel: string,
  ) =>
    request<Character>(
      session,
      `${workspacePath(session)}/projects/${encodeURIComponent(projectId)}/characters`,
      {
        method: "POST",
        headers: { "Idempotency-Key": crypto.randomUUID() },
        body: JSON.stringify({
          display_name: displayName,
          role_label: roleLabel || null,
        }),
      },
    ),
  updateCharacter: (
    session: AuthSession,
    projectId: string,
    character: Character,
    displayName: string,
    roleLabel: string,
  ) =>
    request<Character>(
      session,
      `${workspacePath(session)}/projects/${encodeURIComponent(projectId)}/characters/${encodeURIComponent(character.character_id)}`,
      {
        method: "PATCH",
        headers: { "Idempotency-Key": crypto.randomUUID() },
        body: JSON.stringify({
          expected_version: character.version,
          display_name: displayName,
          role_label: roleLabel || null,
        }),
      },
    ),
};
