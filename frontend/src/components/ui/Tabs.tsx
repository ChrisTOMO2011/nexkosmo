import type { ReactNode } from "react";

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
  return (
    <div
      className={`ui-tabs ${className}`.trim()}
      role="tablist"
      aria-label={label}
    >
      {items.map((item) => (
        <button
          className={value === item.id ? "is-active" : ""}
          type="button"
          role="tab"
          aria-selected={value === item.id}
          disabled={item.disabled}
          key={item.id}
          onClick={() => onChange(item.id)}
        >
          {item.icon}
          <span>{item.label}</span>
        </button>
      ))}
    </div>
  );
}
