import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { describe, expect, it, vi } from "vitest";
import { Modal, Slider, Tabs } from ".";

describe("shared Studio primitives", () => {
  it("supports accessible tab selection", async () => {
    const user = userEvent.setup();

    function TabsExample() {
      const [value, setValue] = useState("one");
      return (
        <Tabs
          label="Example tabs"
          items={[
            { id: "one", label: "One" },
            { id: "two", label: "Two" },
          ]}
          value={value}
          onChange={setValue}
        />
      );
    }

    render(<TabsExample />);
    await user.click(screen.getByRole("tab", { name: "Two" }));

    expect(screen.getByRole("tab", { name: "Two" })).toHaveAttribute(
      "aria-selected",
      "true",
    );
  });

  it("reports slider changes and closes modals with Escape", () => {
    const onChange = vi.fn();
    const onClose = vi.fn();

    render(
      <>
        <Slider
          label="Scale"
          min={0}
          max={100}
          value={50}
          onChange={onChange}
        />
        <Modal open title="Example modal" onClose={onClose}>
          Modal content
        </Modal>
      </>,
    );

    fireEvent.change(screen.getByRole("slider", { name: "Scale" }), {
      target: { value: "65" },
    });
    fireEvent.keyDown(document, { key: "Escape" });

    expect(onChange).toHaveBeenCalledWith(65);
    expect(onClose).toHaveBeenCalledOnce();
  });
});
