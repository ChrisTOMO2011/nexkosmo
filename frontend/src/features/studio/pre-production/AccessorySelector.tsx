import {
  Check,
  ChevronDown,
  CloudUpload,
  Ellipsis,
  Glasses,
  Sparkles,
} from "lucide-react";
import { AssetGrid } from "../../../components/ui";
import type { ApiCharacterAsset } from "../../../brain/characters/api.clients";
import { accessoryTabs } from "./data";
import {
  CategorisedAssetSection,
  type DeferredActionId,
} from "./shared";

export type AccessoryAssetItem = Pick<
  ApiCharacterAsset,
  "assetId" | "name" | "status" | "profileMetadata"
>;

type AccessorySelectorProps = {
  activeTab: string;
  selectedAccessoryIds: readonly string[];
  focusedAssetId?: string;
  pendingAssetId?: string;
  selectionDisabled?: boolean;
  loading?: boolean;
  error?: string;
  onTabChange: (tab: string) => void;
  onAccessoryChange: (item: AccessoryAssetItem) => void;
  onAssetFocus?: (assetId?: string) => void;
  onPlaceholder: (message: string) => void;
  onDeferredAction: (action: DeferredActionId) => void;
  items: readonly AccessoryAssetItem[];
};

export function AccessorySelector({
  activeTab,
  selectedAccessoryIds,
  focusedAssetId,
  pendingAssetId,
  selectionDisabled = false,
  loading = false,
  error,
  onTabChange,
  onAccessoryChange,
  onAssetFocus,
  onPlaceholder,
  onDeferredAction,
  items,
}: AccessorySelectorProps) {
  const visibleItems = [
    { assetId: `deferred:upload:${activeTab}`, name: "Upload", status: "deferred", profileMetadata: {} },
    { assetId: `deferred:generate:${activeTab}`, name: "AI Generate", status: "deferred", profileMetadata: {} },
    ...items,
  ] satisfies readonly AccessoryAssetItem[];
  return (
    <CategorisedAssetSection
      className="accessory-selector"
      label="Character accessories"
      tabsLabel="Accessory categories"
      tabsClassName="accessory-tabs"
      tabs={accessoryTabs.map((tab) => ({ id: tab, label: tab }))}
      activeTab={activeTab}
      onTabChange={onTabChange}
      headerAdornment={
        <span className="accessory-dropdowns" aria-hidden="true">
          <ChevronDown />
          <ChevronDown />
        </span>
      }
    >
      <AssetGrid className="glasses-row" aria-busy={loading}>
        {visibleItems.map((item, index) => {
          const deferred = index < 2;
          const selected = !deferred && selectedAccessoryIds.includes(item.assetId);
          const unsupported = item.status === "unsupported";
          const pending = item.assetId === pendingAssetId;
          const Icon =
            index === 0
              ? CloudUpload
              : index === 1
                ? Sparkles
                : item.name === "More"
                  ? Ellipsis
                  : Glasses;
          const unavailableReason =
            typeof item.profileMetadata.unavailable_reason === "string"
              ? item.profileMetadata.unavailable_reason
              : "This accessory is not compatible with the selected character.";
          return (
            <button
              className={`glasses-card glasses-${index + 1} ${selected ? "is-included" : ""} ${focusedAssetId === item.assetId ? "is-focused" : ""}`.trim()}
              type="button"
              key={item.assetId}
              aria-pressed={selected}
              aria-disabled={unsupported || (!deferred && selectionDisabled)}
              aria-busy={pending}
              data-selection-mode="multiple"
              data-asset-id={item.assetId}
              data-status={deferred ? "deferred" : unsupported ? "unsupported" : "available"}
              data-focused={focusedAssetId === item.assetId || undefined}
              disabled={unsupported || (!deferred && selectionDisabled)}
              title={unsupported ? unavailableReason : undefined}
              onFocus={() => onAssetFocus?.(item.assetId)}
              onBlur={() => onAssetFocus?.(undefined)}
              onClick={() => {
                if (deferred) {
                  onDeferredAction(
                    item.name === "Upload" ? "asset-upload" : "character-generation",
                  );
                  return;
                }
                if (item.name === "More") {
                  onPlaceholder(
                    "Additional accessory catalogue items are not available in this phase.",
                  );
                  return;
                }
                onAccessoryChange(item);
              }}
            >
              <Icon aria-hidden="true" />
              <span>{pending ? `Saving ${item.name}` : item.name}</span>
              {selected && (
                <span className="selection-check" aria-hidden="true">
                  <Check />
                </span>
              )}
            </button>
          );
        })}
      </AssetGrid>
      {loading && <p className="sr-only" role="status">Loading accessory assets.</p>}
      {error && <p className="sr-only" role="alert">{error}</p>}
    </CategorisedAssetSection>
  );
}
