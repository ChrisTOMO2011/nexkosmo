import { Plus } from "lucide-react";
import type { ReactNode } from "react";
import { Button } from "../../../../components/ui";

export type DomainSelectionItem = {
  id: string;
  primaryText: string;
  secondaryText: string;
  thumbnail: ReactNode;
  ariaLabel?: string;
};

type DomainSelectionRailProps<T extends DomainSelectionItem> = {
  label: string;
  items: readonly T[];
  selectedId: string;
  addLabel: string;
  onSelect: (item: T) => void;
  onAdd: () => void;
  className?: string;
};

export function DomainSelectionRail<T extends DomainSelectionItem>({
  label,
  items,
  selectedId,
  addLabel,
  onSelect,
  onAdd,
  className = "character-roster",
}: DomainSelectionRailProps<T>) {
  return (
    <aside className={className} aria-label={label}>
      <div className="roster-list">
        {items.map((item) => {
          const selected = selectedId === item.id;
          return (
            <Button
              className={`roster-card ${selected ? "is-selected" : ""}`}
              key={item.id}
              aria-label={
                item.ariaLabel ?? `${item.primaryText}, ${item.secondaryText}`
              }
              aria-pressed={selected}
              onClick={() => onSelect(item)}
            >
              {item.thumbnail}
              <span className="roster-copy">
                <strong>{item.primaryText}</strong>
                <small>{item.secondaryText}</small>
              </span>
              {selected && <i className="roster-status" />}
            </Button>
          );
        })}
      </div>
      <Button
        className="add-character"
        leadingIcon={<Plus aria-hidden="true" />}
        onClick={onAdd}
      >
        {addLabel}
      </Button>
    </aside>
  );
}
