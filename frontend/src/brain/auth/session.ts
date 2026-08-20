export type AccessTokenProvider = () => string | undefined;

let accessToken: string | undefined;

export function setAccessToken(token: string) {
  const normalized = token.trim();
  if (!normalized) throw new Error("Access token cannot be empty.");
  accessToken = normalized;
}

export function getAccessToken() {
  return accessToken;
}

export function clearSession() {
  accessToken = undefined;
}

export function authenticatedJsonHeaders(
  provider: AccessTokenProvider,
  headers: HeadersInit | undefined,
): HeadersInit {
  const token = provider();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...headers,
  };
}
