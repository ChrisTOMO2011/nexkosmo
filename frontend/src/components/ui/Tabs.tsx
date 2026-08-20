import type { KeyboardEvent, ReactNode } from "react";

export type TabItem = {
  id: string;
  label: string;
  icon?: ReactNode;
  disabled?: boolean;
};

type TabsProps = {
  items: readonly TabItem[];
  value: string;
  onChange: (value: string) => void;
  label: string;
  className?: string;
};

export function Tabs({
  items,
  value,
  onChange,
  label,
  className = "",
}: TabsProps) {
  function moveFocus(
    event: KeyboardEvent<HTMLButtonElement>,
    itemIndex: number,
  ) {
    const enabledItems = items
      .map((item, index) => ({ item, index }))
      .filter(({ item }) => !item.disabled);
    const enabledIndex = enabledItems.findIndex(({ index }) => index === itemIndex);
    if (enabledIndex < 0) return;

    let nextIndex: number | undefined;
    if (event.key === "ArrowRight") {
      nextIndex = (enabledIndex + 1) % enabledItems.length;
    } else if (event.key === "ArrowLeft") {
      nextIndex = (enabledIndex - 1 + enabledItems.length) % enabledItems.length;
    } else if (event.key === "Home") {
      nextIndex = 0;
    } else if (event.key === "End") {
      nextIndex = enabledItems.length - 1;
    }
    if (nextIndex === undefined) return;

    event.preventDefault();
    const next = enabledItems[nextIndex];
    onChange(next.item.id);
    const buttons = event.currentTarget.parentElement?.querySelectorAll<HTMLButtonElement>(
      '[role="tab"]:not(:disabled)',
    );
    buttons?.[nextIndex]?.focus();
  }

  return (
    <div
      className={`ui-tabs ${className}`.trim()}
      role="tablist"
      aria-label={label}
    >
      {items.map((item, index) => (
        <button
          className={value === item.id ? "is-active" : ""}
          type="button"
          role="tab"
          aria-selected={value === item.id}
          disabled={item.disabled}
          key={item.id}
          onClick={() => onChange(item.id)}
          onKeyDown={(event) => moveFocus(event, index)}
        >
          {item.icon}
          <span>{item.label}</span>
        </button>
      ))}
    </div>
  );
}
