import type { KeyboardEvent, ReactNode } from "react";

type FilterPill = Readonly<{
  id: string;
  label: string;
  trailingIcon?: ReactNode;
  disabled?: boolean;
}>;

type FilterPillsProps = {
  items: readonly FilterPill[];
  value: string;
  label: string;
  className?: string;
  onChange: (id: string) => void;
};

export function FilterPills({
  items,
  value,
  label,
  className = "filter-row",
  onChange,
}: FilterPillsProps) {
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
    onChange(enabledItems[nextIndex].item.id);
    const buttons = event.currentTarget.parentElement?.querySelectorAll<HTMLButtonElement>(
      "button:not(:disabled)",
    );
    buttons?.[nextIndex]?.focus();
  }

  return (
    <div className={className} aria-label={label}>
      {items.map((item, index) => (
        <button
          className={value === item.id ? "is-active" : ""}
          type="button"
          key={item.id}
          aria-pressed={value === item.id}
          disabled={item.disabled}
          onClick={() => onChange(item.id)}
          onKeyDown={(event) => moveFocus(event, index)}
        >
          {item.label}
          {item.trailingIcon}
        </button>
      ))}
    </div>
  );
}
