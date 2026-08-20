import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { StudioHeaderUtilities } from "./StudioHeaderUtilities";

describe("StudioHeaderUtilities", () => {
  it("provides the same interactive utility panels as Studio", async () => {
    const user = userEvent.setup();
    const onAction = vi.fn();
    render(<StudioHeaderUtilities onAction={onAction} />);

    await user.click(screen.getByRole("button", { name: "Search" }));
    expect(screen.getByRole("dialog", { name: "Search" })).toBeInTheDocument();
    await user.type(
      screen.getByRole("searchbox", { name: "Search Nexkosmo Studio" }),
      "Christopher",
    );
    fireEvent.submit(
      screen
        .getByRole("searchbox", { name: "Search Nexkosmo Studio" })
        .closest("form")!,
    );
    expect(
      screen.getByText("Searching Studio for “Christopher”."),
    ).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", {
        name: "Collaborate — 2 creators online",
      }),
    );
    expect(
      screen.getByRole("dialog", { name: "Collaboration" }),
    ).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", { name: "Notifications, 31 unread" }),
    );
    await user.click(screen.getByRole("button", { name: "Mark all as read" }));
    expect(
      screen.getByRole("button", { name: "Notifications" }),
    ).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Mail, 2 unread" }));
    await user.click(screen.getByRole("button", { name: "Open inbox" }));
    expect(screen.getByRole("button", { name: "Mail" })).toBeInTheDocument();
    expect(onAction).toHaveBeenCalledWith("Studio inbox opened.");

    await user.click(screen.getByRole("button", { name: "Membership" }));
    expect(
      screen.getByRole("dialog", { name: "Membership" }),
    ).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Achieve Rewards" }));
    expect(
      screen.getByRole("dialog", { name: "Achieve Rewards™" }),
    ).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", { name: "Christopher profile" }),
    );
    expect(screen.getByRole("dialog", { name: "Profile" })).toBeInTheDocument();
  });
});
