import { Check } from "lucide-react";
import type { ReactNode } from "react";
import { AssetGrid } from "../../../../components/ui";
import type { DomainAssetStatus } from "./domain-workspace.types";

type DomainAssetGridProps<T> = {
  title: string;
  titleId: string;
  items: readonly T[];
  selectedId?: string;
  selectedIds?: readonly string[];
  getId: (item: T) => string;
  getItemClassName: (item: T, index: number) => string;
  getLabel: (item: T) => string;
  renderMedia: (item: T, index: number) => ReactNode;
  onSelect: (item: T) => void;
  emptyMessage: string;
  selectionMode?: "single" | "multiple";
  getStatus?: (item: T) => DomainAssetStatus;
  getUnavailableReason?: (item: T) => string | undefined;
  sectionClassName?: string;
  gridClassName?: string;
};

export function DomainAssetGrid<T>({
  title,
  titleId,
  items,
  selectedId,
  selectedIds,
  getId,
  getItemClassName,
  getLabel,
  renderMedia,
  onSelect,
  emptyMessage,
  selectionMode = "single",
  getStatus = () => "available",
  getUnavailableReason,
  sectionClassName = "",
  gridClassName = "",
}: DomainAssetGridProps<T>) {
  return (
    <section
      className={`selector-section ${sectionClassName}`.trim()}
      aria-labelledby={titleId}
    >
      <h3 id={titleId}>{title}</h3>
      {items.length ? (
        <AssetGrid className={gridClassName}>
          {items.map((item, index) => {
            const itemId = getId(item);
            const selected = selectedIds?.includes(itemId) ?? selectedId === itemId;
            const status = getStatus(item);
            const disabled = status === "unsupported";
            return (
              <button
                className={`${getItemClassName(item, index)} ${selected ? "is-selected" : ""}`.trim()}
                type="button"
                key={itemId}
                aria-pressed={selected}
                aria-disabled={disabled}
                data-status={status}
                disabled={disabled}
                title={disabled ? getUnavailableReason?.(item) : undefined}
                onClick={() => onSelect(item)}
              >
                {renderMedia(item, index)}
                <strong>{getLabel(item)}</strong>
                {selectionMode === "multiple" && selected && (
                  <span className="selection-check">
                    <Check aria-hidden="true" />
                  </span>
                )}
              </button>
            );
          })}
        </AssetGrid>
      ) : (
        <p role="status">{emptyMessage}</p>
      )}
    </section>
  );
}
