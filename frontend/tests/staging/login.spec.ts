import { expect, test, type Page, type Response } from "@playwright/test";

const STAGING_ORIGIN = "https://staging.nexkosmo.com";

type Colour = [number, number, number];

function colourChannels(value: string): Colour {
  const channels = [...value.matchAll(/[\d.]+/g)]
    .slice(0, 3)
    .map((match) => Number(match[0]));
  if (channels.length !== 3) throw new Error(`Unsupported colour: ${value}`);
  return channels as Colour;
}

function channelLuminance(value: number): number {
  const channel = value / 255;
  return channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
}

function luminance(colour: Colour): number {
  return (
    0.2126 * channelLuminance(colour[0]) +
    0.7152 * channelLuminance(colour[1]) +
    0.0722 * channelLuminance(colour[2])
  );
}

function contrastRatio(foreground: string, background: string): number {
  const foregroundLuminance = luminance(colourChannels(foreground));
  const backgroundLuminance = luminance(colourChannels(background));
  return (
    (Math.max(foregroundLuminance, backgroundLuminance) + 0.05) /
    (Math.min(foregroundLuminance, backgroundLuminance) + 0.05)
  );
}

async function computedVisibility(page: Page, selector: string) {
  return page.locator(selector).evaluate((element) => {
    const style = getComputedStyle(element);
    const rectangle = element.getBoundingClientRect();
    let background = style.backgroundColor;
    let ancestor = element.parentElement;
    while (background === "rgba(0, 0, 0, 0)" && ancestor) {
      background = getComputedStyle(ancestor).backgroundColor;
      ancestor = ancestor.parentElement;
    }
    return {
      display: style.display,
      visibility: style.visibility,
      opacity: Number(style.opacity),
      foreground: style.color,
      background,
      width: rectangle.width,
      height: rectangle.height,
    };
  });
}

test("Staging login is visible, accessible, PKCE-bound, versioned and CSP-clean", async ({
  page,
}) => {
  const consoleErrors: string[] = [];
  const pageErrors: string[] = [];
  const failedRequests: string[] = [];
  const badResponses: string[] = [];
  const keycloakAssets: Response[] = [];

  page.on("console", (message) => {
    if (message.type() !== "error") return;
    const text = message.text();
    // Cloudflare injects analytics after origin delivery. Blocking that unapproved
    // third-party script is the intended Staging CSP result, not an application error.
    if (!text.includes("static.cloudflareinsights.com")) consoleErrors.push(text);
  });
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("requestfailed", (request) => {
    if (!request.url().startsWith("https://static.cloudflareinsights.com/")) {
      failedRequests.push(`${request.failure()?.errorText ?? "failed"} ${request.url()}`);
    }
  });
  page.on("response", (response) => {
    if (response.status() >= 400) badResponses.push(`${response.status()} ${response.url()}`);
    if (response.url().includes("/auth/resources/")) keycloakAssets.push(response);
  });

  await page.goto(STAGING_ORIGIN, { waitUntil: "networkidle" });
  await expect(page.getByRole("heading", { name: "Sign in to Nexkosmo" })).toBeVisible();
  await page.getByRole("button", { name: "Continue securely" }).click();
  await page.waitForURL(/\/auth\/realms\/nexkosmo\/protocol\/openid-connect\/auth/);

  const authorizationUrl = new URL(page.url());
  expect(authorizationUrl.origin).toBe(STAGING_ORIGIN);
  expect(authorizationUrl.searchParams.get("response_type")).toBe("code");
  expect(authorizationUrl.searchParams.get("client_id")).toBe("nexkosmo-staging-spa");
  expect(authorizationUrl.searchParams.get("redirect_uri")).toBe(
    `${STAGING_ORIGIN}/auth/callback`,
  );
  expect(authorizationUrl.searchParams.get("code_challenge_method")).toBe("S256");
  expect(authorizationUrl.searchParams.get("code_challenge")).toBeTruthy();
  expect(authorizationUrl.searchParams.get("state")).toBeTruthy();

  const controls = [
    ["username", "#username", "Username or email"],
    ["password", "#password", "Password"],
    ["login", "#kc-login", "Sign In"],
  ] as const;

  for (const [name, selector, accessibleName] of controls) {
    const control = page.locator(selector);
    await expect(control, `${name} is rendered`).toBeVisible();
    await expect(control, `${name} is enabled`).toBeEnabled();
    if (name === "login") {
      await expect(page.getByRole("button", { name: accessibleName })).toBeVisible();
    } else {
      await expect(page.getByLabel(accessibleName, { exact: true })).toBeVisible();
    }
    const visibility = await computedVisibility(page, selector);
    expect(visibility.display, `${name} display`).not.toBe("none");
    expect(visibility.visibility, `${name} visibility`).toBe("visible");
    expect(visibility.opacity, `${name} opacity`).toBeGreaterThan(0);
    expect(visibility.width, `${name} width`).toBeGreaterThan(0);
    expect(visibility.height, `${name} height`).toBeGreaterThan(0);
    expect(
      contrastRatio(visibility.foreground, visibility.background),
      `${name} WCAG contrast`,
    ).toBeGreaterThanOrEqual(4.5);

    await control.focus();
    await expect(control, `${name} receives keyboard focus`).toBeFocused();
    const focusIndicator = await control.evaluate((element) => {
      const style = getComputedStyle(element);
      return {
        outlineWidth: Number.parseFloat(style.outlineWidth),
        outlineStyle: style.outlineStyle,
        boxShadow: style.boxShadow,
      };
    });
    expect(
      focusIndicator.outlineWidth > 0 || focusIndicator.boxShadow !== "none",
      `${name} has a visible focus indicator`,
    ).toBe(true);
    expect(focusIndicator.outlineStyle).not.toBe("none");
  }

  const authorizationResponse = await page.request.get(page.url());
  expect(authorizationResponse.headers()["cache-control"]).toMatch(/no-store/);

  await page.locator("#kc-login").click();
  await expect(page.getByText("Invalid username or password.")).toBeVisible();

  expect(keycloakAssets.length).toBeGreaterThan(0);
  for (const response of keycloakAssets) {
    expect(response.status(), response.url()).toBe(200);
    expect(response.url(), "Keycloak asset has a version segment").toMatch(
      /\/auth\/resources\/[A-Za-z0-9_-]+\//,
    );
    expect(response.headers()["cache-control"], response.url()).toMatch(/max-age=/);
    const contentType = response.headers()["content-type"] ?? "";
    expect(contentType, response.url()).toMatch(
      /^(text\/css|text\/javascript|application\/javascript|image\/|font\/|application\/(font|octet-stream|x-font))/,
    );
  }

  expect(consoleErrors).toEqual([]);
  expect(pageErrors).toEqual([]);
  expect(failedRequests).toEqual([]);
  expect(badResponses).toEqual([]);
});
