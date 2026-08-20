import { afterEach, describe, expect, it, vi } from "vitest";
import { beginLogin, optionalSession, requireSession, signOut } from "./session";

const token = (claims: object) =>
  [
    "eyJhbGciOiJub25lIn0",
    btoa(JSON.stringify(claims)).replaceAll("=", ""),
    "signature",
  ].join(".");

afterEach(() => {
  sessionStorage.clear();
  vi.unstubAllEnvs();
});

describe("OIDC session", () => {
  it("does not invent a session or default authority context", () => {
    expect(optionalSession()).toBeNull();
    expect(() => requireSession()).toThrow(/authentication is required/i);
  });

  it("uses token claims only as explicit routing context", () => {
    sessionStorage.setItem(
      "nexkosmo.oidc.access_token",
      token({
        sub: "00000000-0000-4000-8000-000000000001",
        workspace_id: "00000000-0000-4000-8000-000000000002",
      }),
    );
    expect(requireSession().workspaceId).toBe(
      "00000000-0000-4000-8000-000000000002",
    );
    signOut();
    expect(optionalSession()).toBeNull();
  });

  it("fails closed when deployment OIDC endpoints are placeholders", async () => {
    vi.stubEnv(
      "VITE_OIDC_AUTHORIZATION_URL",
      "https://identity.example.invalid/authorize",
    );
    vi.stubEnv("VITE_OIDC_TOKEN_URL", "https://identity.example.invalid/token");
    vi.stubEnv("VITE_OIDC_CLIENT_ID", "nexkosmo-frontend");

    await expect(beginLogin()).rejects.toThrow(/placeholder endpoints/i);
  });
});
