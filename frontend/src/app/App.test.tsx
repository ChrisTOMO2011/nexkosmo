import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { WORKFLOW_STAGE_DEFINITIONS } from "./workflow";

function renderAt(pathname: string) {
  window.history.replaceState({}, "", pathname);
  return render(<App />);
}

const testToken = [
  "eyJhbGciOiJub25lIn0",
  btoa(
    JSON.stringify({
      sub: "00000000-0000-4000-8000-000000000001",
      workspace_id: "00000000-0000-4000-8000-000000000002",
    }),
  ).replaceAll("=", ""),
  "signature",
].join(".");

beforeEach(() => {
  sessionStorage.setItem("nexkosmo.oidc.access_token", testToken);
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({ ok: true, json: async () => [] }),
  );
});

afterEach(() => {
  cleanup();
  sessionStorage.clear();
  vi.unstubAllGlobals();
  window.history.replaceState({}, "", "/");
});

describe("canonical Nexkosmo shell", () => {
  it("renders exactly the approved six-stage navigation", () => {
    renderAt("/studio/projects/project_42/build");
    const navigation = screen.getByRole("navigation", {
      name: "Creator workflow",
    });
    const links = within(navigation).getAllByRole("link");

    expect(links).toHaveLength(6);
    expect(links.map((link) => link.textContent?.trim())).toEqual(
      WORKFLOW_STAGE_DEFINITIONS.map(
        (stage, index) => `${index + 1}${stage.label}`,
      ),
    );
    expect(within(navigation).queryByText("STUDIO")).not.toBeInTheDocument();
  });

  it("uses the repository canonical SVG rather than a raster substitute", () => {
    renderAt("/studio/projects/project_42/idea");
    const brand = screen.getByRole("link", { name: "Nexkosmo home" });
    const logo = brand.querySelector("img");

    expect(logo).toHaveAttribute(
      "data-canonical-asset",
      "assets/brand/nexkosmo-x-star.svg",
    );
    expect(logo?.getAttribute("src")).toMatch(/^data:image\/svg\+xml,/);
    expect(logo?.getAttribute("src")).not.toMatch(/\.(jpe?g|png)(?:$|\?)/i);
  });

  it("renders an honest non-operational stage placeholder", () => {
    renderAt("/studio/projects/project_42/ready");

    expect(screen.getByRole("heading", { name: "READY" })).toBeInTheDocument();
    expect(
      screen.getByText(/no stage operations, persistence, or intelligence/i),
    ).toBeInTheDocument();
    const buttons = screen.getAllByRole("button");
    expect(buttons.every((button) => button.hasAttribute("disabled"))).toBe(
      true,
    );
  });

  it("shows a safe state when project context is missing", () => {
    renderAt("/studio");

    expect(screen.getByRole("heading", { name: "Your Projects" })).toBeInTheDocument();
    expect(screen.getByText(/only projects with an active project membership/i)).toBeInTheDocument();
  });

  it("does not render unsupported public claims", () => {
    renderAt("/studio/projects/project_42/production");
    const rendered = document.body.textContent ?? "";
    const blockedClaims = [
      "Disney",
      "Netflix",
      "Sony Pictures",
      "Universal Pictures",
      "Epic Games",
      "10K+ creators",
      "5M+ assets",
      "creator earnings",
      "99.9% uptime",
    ];

    for (const claim of blockedClaims) {
      expect(rendered).not.toContain(claim);
    }
  });
});
