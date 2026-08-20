import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { describe, expect, it, vi } from "vitest";
import { Modal, Slider, Tabs, UploadArea } from ".";

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

  it("moves and selects tabs with arrow, Home and End keys", () => {
    function TabsExample() {
      const [value, setValue] = useState("one");
      return (
        <Tabs
          label="Keyboard tabs"
          items={[
            { id: "one", label: "One" },
            { id: "two", label: "Two" },
            { id: "three", label: "Three" },
          ]}
          value={value}
          onChange={setValue}
        />
      );
    }

    render(<TabsExample />);
    const one = screen.getByRole("tab", { name: "One" });
    one.focus();
    fireEvent.keyDown(one, { key: "ArrowRight" });
    expect(screen.getByRole("tab", { name: "Two" })).toHaveFocus();
    expect(screen.getByRole("tab", { name: "Two" })).toHaveAttribute(
      "aria-selected",
      "true",
    );
    fireEvent.keyDown(screen.getByRole("tab", { name: "Two" }), { key: "End" });
    expect(screen.getByRole("tab", { name: "Three" })).toHaveFocus();
    fireEvent.keyDown(screen.getByRole("tab", { name: "Three" }), { key: "Home" });
    expect(one).toHaveFocus();
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

  it("can intercept deferred upload activation without opening a local file flow", () => {
    const onActivate = vi.fn(() => false);
    const onFile = vi.fn();
    render(
      <UploadArea
        label="Upload face image"
        onActivate={onActivate}
        onFile={onFile}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Upload face image" }));

    expect(onActivate).toHaveBeenCalledOnce();
    expect(onFile).not.toHaveBeenCalled();
  });
});
