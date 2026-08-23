import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/staging",
  timeout: 45_000,
  fullyParallel: false,
  retries: 0,
  workers: 1,
  use: {
    baseURL: "https://staging.nexkosmo.com",
    headless: true,
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
    viewport: { width: 1440, height: 1000 },
  },
});
