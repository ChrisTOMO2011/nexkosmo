import { AccessorySelector } from "./AccessorySelector";
import type { AccessoryAssetItem } from "./AccessorySelector";
import type { ApiSpecies } from "../../../brain/characters";
import {
  SpeciesSelector,
  type SpeciesFilterId,
} from "./SpeciesSelector";
import { StyleSelector } from "./StyleSelector";
import type { DeferredActionId } from "./shared";

type IdentityEditorProps = {
  selectedStyle: string;
  activeSpeciesFilterId: SpeciesFilterId;
  selectedSpeciesId?: string;
  species: readonly ApiSpecies[];
  focusedSpeciesId?: string;
  pendingSpeciesId?: string;
  speciesSelectionDisabled?: boolean;
  speciesLoading?: boolean;
  speciesError?: string;
  activeAccessoryTab: string;
  selectedAccessoryIds: readonly string[];
  accessoryItems: readonly AccessoryAssetItem[];
  focusedAccessoryId?: string;
  pendingAccessoryId?: string;
  accessorySelectionDisabled?: boolean;
  accessoryLoading?: boolean;
  accessoryError?: string;
  onStyleChange: (style: string) => void;
  onSpeciesFilterChange: (filterId: SpeciesFilterId) => void;
  onSpeciesChange: (species: ApiSpecies) => void;
  onSpeciesFocus?: (speciesId?: string) => void;
  onAccessoryTabChange: (tab: string) => void;
  onAccessoryChange: (item: AccessoryAssetItem) => void;
  onAccessoryFocus?: (assetId?: string) => void;
  onPlaceholder: (message: string) => void;
  onDeferredAction: (action: DeferredActionId) => void;
};

export function IdentityEditor({
  selectedStyle,
  activeSpeciesFilterId,
  selectedSpeciesId,
  species,
  focusedSpeciesId,
  pendingSpeciesId,
  speciesSelectionDisabled,
  speciesLoading,
  speciesError,
  activeAccessoryTab,
  selectedAccessoryIds,
  accessoryItems,
  focusedAccessoryId,
  pendingAccessoryId,
  accessorySelectionDisabled,
  accessoryLoading,
  accessoryError,
  onStyleChange,
  onSpeciesFilterChange,
  onSpeciesChange,
  onSpeciesFocus,
  onAccessoryTabChange,
  onAccessoryChange,
  onAccessoryFocus,
  onPlaceholder,
  onDeferredAction,
}: IdentityEditorProps) {
  return (
    <>
      <div className="identity-editor-grid">
        <StyleSelector selected={selectedStyle} onChange={onStyleChange} />
        <SpeciesSelector
          activeFilterId={activeSpeciesFilterId}
          selectedSpeciesId={selectedSpeciesId}
          species={species}
          focusedSpeciesId={focusedSpeciesId}
          pendingSpeciesId={pendingSpeciesId}
          selectionDisabled={speciesSelectionDisabled}
          loading={speciesLoading}
          error={speciesError}
          onFilterChange={onSpeciesFilterChange}
          onSpeciesChange={onSpeciesChange}
          onSpeciesFocus={onSpeciesFocus}
          onPlaceholder={onPlaceholder}
          onDeferredAction={onDeferredAction}
        />
      </div>
      <AccessorySelector
        activeTab={activeAccessoryTab}
        selectedAccessoryIds={selectedAccessoryIds}
        focusedAssetId={focusedAccessoryId}
        pendingAssetId={pendingAccessoryId}
        selectionDisabled={accessorySelectionDisabled}
        loading={accessoryLoading}
        error={accessoryError}
        onTabChange={onAccessoryTabChange}
        onAccessoryChange={onAccessoryChange}
        onAssetFocus={onAccessoryFocus}
        onPlaceholder={onPlaceholder}
        onDeferredAction={onDeferredAction}
        items={accessoryItems}
      />
    </>
  );
}
