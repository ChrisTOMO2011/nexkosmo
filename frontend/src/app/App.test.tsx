import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { AppRoutes } from "./App";

describe("Nexkosmo landing route", () => {
  it("reconnects the cinematic home at the root route", () => {
    window.history.replaceState({}, "", "/");

    render(<AppRoutes />);

    expect(
      screen.getByTitle("Nexkosmo cinematic home"),
    ).toHaveAttribute("src", "/landing/index.html");
    expect(
      screen.getByRole("link", { name: "Open Nexkosmo Studio" }),
    ).toHaveAttribute(
      "href",
      "/studio/projects/the-last-dawn/pre-production/characters/christopher",
    );
  });
});

function renderCharacterRoute() {
  window.history.replaceState(
    {},
    "",
    "/studio/projects/the-last-dawn/pre-production/characters/christopher",
  );
  return render(<AppRoutes />);
}

describe("Nexkosmo character identity route", () => {
  it("renders the complete character identity workspace", () => {
    renderCharacterRoute();

    expect(
      screen.getByRole("heading", { name: "Christopher", level: 1 }),
    ).toBeInTheDocument();
    expect(screen.getByText("Camera Gear")).toBeInTheDocument();
    expect(screen.getByText("CGI Studio")).toBeInTheDocument();
    expect(
      screen.getByRole("tab", { name: "Identity" }),
    ).toHaveAttribute("aria-selected", "true");
    expect(screen.getAllByText("Upload").length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("AI Generate").length).toBeGreaterThanOrEqual(2);
    expect(screen.queryByText("None")).not.toBeInTheDocument();
  });

  it("supports character, style, slider and suggestion interactions", async () => {
    const user = userEvent.setup();
    renderCharacterRoute();

    await user.click(screen.getByRole("button", { name: "Sarah, Co-Lead" }));
    expect(
      screen.getByRole("button", { name: "Sarah, Co-Lead" }),
    ).toHaveAttribute("aria-pressed", "true");

    await user.click(screen.getByRole("button", { name: "Cartoon" }));
    expect(screen.getByRole("button", { name: "Cartoon" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );

    const age = screen.getByRole("slider", { name: "Age" });
    fireEvent.change(age, { target: { value: "42" } });
    expect(age).toHaveValue("42");

    await user.click(screen.getAllByRole("button", { name: "Apply" })[0]);
    expect(screen.getByRole("button", { name: "Applied" })).toBeInTheDocument();
  });
});

describe("Nexkosmo workflow foundations", () => {
  it.each([
    ["set", "SET"],
    ["studio", "STUDIO"],
    ["review", "REVIEW"],
    ["render", "RENDER"],
  ])("renders the shared shell for the %s route", (route, label) => {
    window.history.replaceState(
      {},
      "",
      `/studio/projects/the-last-dawn/${route}`,
    );

    render(<AppRoutes />);

    expect(
      screen.getByRole("heading", { name: label, level: 1 }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: new RegExp(label) }),
    ).toHaveAttribute("aria-current", "step");
    expect(screen.getByText("Primary workspace")).toBeInTheDocument();
    expect(screen.getByText("Inspector")).toBeInTheDocument();
  });
});
