import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { IdeaPage } from "./IdeaPage";

describe("IdeaPage", () => {
  it("captures an idea and enables its connected discovery action", async () => {
    const user = userEvent.setup();
    render(<IdeaPage projectId="the-last-dawn" />);

    const brief = screen.getByRole("textbox", { name: "Add anything..." });
    const explore = screen.getByRole("button", { name: /Explore this idea/i });

    expect(explore).toBeDisabled();
    await user.type(brief, "A city wakes beneath a frozen sky.");

    expect(screen.getByText("34 / 2000")).toBeInTheDocument();
    expect(explore).toBeEnabled();
    expect(
      screen.getByText("Your idea is ready to explore with Sophia."),
    ).toBeInTheDocument();
  });

  it("honestly reports deferred input methods", async () => {
    const user = userEvent.setup();
    render(<IdeaPage projectId="the-last-dawn" />);

    await user.click(screen.getByRole("button", { name: "Import Script" }));

    expect(
      screen.getByText("Script import will be connected in a later phase."),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Import Script" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
  });
});
