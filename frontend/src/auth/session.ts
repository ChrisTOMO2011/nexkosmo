const TOKEN_KEY = "nexkosmo.oidc.access_token";
const STATE_KEY = "nexkosmo.oidc.state";
const VERIFIER_KEY = "nexkosmo.oidc.verifier";

export type AuthSession = {
  accessToken: string;
  workspaceId: string;
  principalId: string;
};

type OidcConfig = {
  authorizationUrl: string;
  tokenUrl: string;
  clientId: string;
  scope: string;
  redirectUri: string;
};

function oidcConfig(): OidcConfig {
  const authorizationUrl = import.meta.env.VITE_OIDC_AUTHORIZATION_URL;
  const tokenUrl = import.meta.env.VITE_OIDC_TOKEN_URL;
  const clientId = import.meta.env.VITE_OIDC_CLIENT_ID;
  if (!authorizationUrl || !tokenUrl || !clientId) {
    throw new Error("OIDC login is not configured for this deployment.");
  }
  for (const value of [authorizationUrl, tokenUrl]) {
    const endpoint = new URL(value);
    if (endpoint.protocol !== "https:") {
      throw new Error("OIDC endpoints must use HTTPS.");
    }
    if (endpoint.hostname.endsWith(".invalid")) {
      throw new Error("OIDC placeholder endpoints are not valid deployment configuration.");
    }
  }
  return {
    authorizationUrl,
    tokenUrl,
    clientId,
    scope: import.meta.env.VITE_OIDC_SCOPE || "openid profile",
    redirectUri: `${window.location.origin}/auth/callback`,
  };
}

function randomUrlSafe(bytes = 32): string {
  const value = crypto.getRandomValues(new Uint8Array(bytes));
  return btoa(String.fromCharCode(...value))
    .replaceAll("+", "-")
    .replaceAll("/", "_")
    .replaceAll("=", "");
}

async function challenge(verifier: string): Promise<string> {
  const digest = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(verifier),
  );
  return btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replaceAll("+", "-")
    .replaceAll("/", "_")
    .replaceAll("=", "");
}

export async function beginLogin(): Promise<void> {
  const config = oidcConfig();
  const state = randomUrlSafe();
  const verifier = randomUrlSafe(64);
  sessionStorage.setItem(STATE_KEY, state);
  sessionStorage.setItem(VERIFIER_KEY, verifier);
  const url = new URL(config.authorizationUrl);
  url.search = new URLSearchParams({
    response_type: "code",
    client_id: config.clientId,
    redirect_uri: config.redirectUri,
    scope: config.scope,
    state,
    code_challenge: await challenge(verifier),
    code_challenge_method: "S256",
  }).toString();
  window.location.assign(url);
}

export async function completeLogin(search: string): Promise<AuthSession> {
  const config = oidcConfig();
  const query = new URLSearchParams(search);
  const code = query.get("code");
  const state = query.get("state");
  const expectedState = sessionStorage.getItem(STATE_KEY);
  const verifier = sessionStorage.getItem(VERIFIER_KEY);
  if (!code || !state || !expectedState || state !== expectedState || !verifier) {
    throw new Error("OIDC callback state validation failed.");
  }
  const response = await fetch(config.tokenUrl, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      client_id: config.clientId,
      redirect_uri: config.redirectUri,
      code,
      code_verifier: verifier,
    }),
  });
  if (!response.ok) throw new Error("OIDC token exchange failed.");
  const payload = (await response.json()) as {
    access_token?: unknown;
    token_type?: unknown;
  };
  if (typeof payload.access_token !== "string" || payload.token_type !== "Bearer") {
    throw new Error("OIDC token response is invalid.");
  }
  sessionStorage.removeItem(STATE_KEY);
  sessionStorage.removeItem(VERIFIER_KEY);
  sessionStorage.setItem(TOKEN_KEY, payload.access_token);
  return requireSession();
}

export function requireSession(): AuthSession {
  const accessToken = sessionStorage.getItem(TOKEN_KEY);
  if (!accessToken) throw new Error("Authentication is required.");
  const parts = accessToken.split(".");
  if (parts.length !== 3) throw new Error("Access token is malformed.");
  const encoded = parts[1].replaceAll("-", "+").replaceAll("_", "/");
  const padded = encoded.padEnd(encoded.length + ((4 - (encoded.length % 4)) % 4), "=");
  const claims = JSON.parse(atob(padded)) as Record<string, unknown>;
  if (typeof claims.workspace_id !== "string" || typeof claims.sub !== "string") {
    throw new Error("Access token is missing the required authority context.");
  }
  // These unverified values are routing hints only. The API verifies the token and
  // enforces Workspace/Project authority on every request.
  return {
    accessToken,
    workspaceId: claims.workspace_id,
    principalId: claims.sub,
  };
}

export function optionalSession(): AuthSession | null {
  try {
    return requireSession();
  } catch {
    return null;
  }
}

export function signOut(): void {
  sessionStorage.removeItem(TOKEN_KEY);
}
