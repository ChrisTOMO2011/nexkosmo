import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { ReadyPage } from "./ReadyPage";

describe("ReadyPage", () => {
  it("shows the complete production-readiness result", () => {
    render(<ReadyPage projectId="the-last-dawn" />);

    expect(screen.getByRole("heading", { name: "Ready to bring it to life?" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "READY FOR PRODUCTION" })).toBeInTheDocument();
    const results = screen.getByRole("region", { name: "READY FOR PRODUCTION" });
    expect(within(results).getAllByText("READY")).toHaveLength(6);
    expect(screen.getByRole("button", { name: /START PRODUCTION/i })).toBeInTheDocument();
  });

  it("selects a scene preview without fabricating production state", async () => {
    const user = userEvent.setup();
    render(<ReadyPage projectId="the-last-dawn" />);

    const scene = screen.getByRole("button", { name: /Scene 40.*The Choice/i });
    await user.click(scene);

    expect(scene).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText("Scene 40 selected for preview.")).toBeInTheDocument();
  });
});
