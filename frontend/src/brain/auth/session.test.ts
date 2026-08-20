import { afterEach, describe, expect, it } from "vitest";
import {
  authenticatedJsonHeaders,
  clearSession,
  getAccessToken,
  setAccessToken,
} from "./session";

afterEach(clearSession);

describe("frontend authentication session", () => {
  it("attaches the bearer token and clears it on logout", () => {
    setAccessToken("signed-token");
    expect(authenticatedJsonHeaders(getAccessToken, {})).toMatchObject({
      Authorization: "Bearer signed-token",
    });
    clearSession();
    expect(authenticatedJsonHeaders(getAccessToken, {})).not.toHaveProperty(
      "Authorization",
    );
  });
});
