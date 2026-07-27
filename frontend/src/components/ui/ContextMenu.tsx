import type { ReactNode } from "react";

export type ContextMenuItem = {
  id: string;
  label: string;
  icon?: ReactNode;
  disabled?: boolean;
};

type ContextMenuProps = {
  open: boolean;
  label: string;
  items: readonly ContextMenuItem[];
  onSelect: (id: string) => void;
  className?: string;
};

export function ContextMenu({
  open,
  label,
  items,
  onSelect,
  className = "",
}: ContextMenuProps) {
  if (!open) return null;

  return (
    <div
      className={`ui-context-menu ${className}`.trim()}
      role="menu"
      aria-label={label}
    >
      {items.map((item) => (
        <button
          type="button"
          role="menuitem"
          disabled={item.disabled}
          key={item.id}
          onClick={() => onSelect(item.id)}
        >
          {item.icon}
          {item.label}
        </button>
      ))}
    </div>
  );
}
