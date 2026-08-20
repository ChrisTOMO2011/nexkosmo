import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { StudioPage } from "./StudioPage";

describe("Production page", () => {
  it("shows the production pipeline and blocking validation honestly", () => {
    render(<StudioPage projectId="the-last-dawn" />);

    expect(screen.getByRole("heading", { name: "We're making your movie." })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "PRODUCTION" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByText("1 blocking issue")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /APPROVE SHOT/i })).toBeDisabled();
  });

  it("keeps exactly one shot selected", async () => {
    const user = userEvent.setup();
    render(<StudioPage projectId="the-last-dawn" />);

    const strip = screen.getByRole("region", { name: /SHOTS IN SCENE 20/i });
    const buttons = within(strip).getAllByRole("button").filter((button) => button.hasAttribute("aria-pressed"));
    await user.click(buttons[3]);

    expect(buttons.filter((button) => button.getAttribute("aria-pressed") === "true")).toHaveLength(1);
    expect(screen.getByText("Shot 04 selected.")).toBeInTheDocument();
  });
});
