import { AccessorySelector } from "./AccessorySelector";
import { SpeciesSelector } from "./SpeciesSelector";
import { StyleSelector } from "./StyleSelector";

type IdentityEditorProps = {
  selectedStyle: string;
  activeSpeciesFilter: string;
  selectedSpecies: string;
  activeAccessoryTab: string;
  selectedAccessory: string;
  onStyleChange: (style: string) => void;
  onSpeciesFilterChange: (filter: string) => void;
  onSpeciesChange: (species: string) => void;
  onAccessoryTabChange: (tab: string) => void;
  onAccessoryChange: (item: string) => void;
  onPlaceholder: (message: string) => void;
};

export function IdentityEditor({
  selectedStyle,
  activeSpeciesFilter,
  selectedSpecies,
  activeAccessoryTab,
  selectedAccessory,
  onStyleChange,
  onSpeciesFilterChange,
  onSpeciesChange,
  onAccessoryTabChange,
  onAccessoryChange,
  onPlaceholder,
}: IdentityEditorProps) {
  return (
    <>
      <div className="identity-editor-grid">
        <StyleSelector selected={selectedStyle} onChange={onStyleChange} />
        <SpeciesSelector
          activeFilter={activeSpeciesFilter}
          selectedSpecies={selectedSpecies}
          onFilterChange={onSpeciesFilterChange}
          onSpeciesChange={onSpeciesChange}
          onPlaceholder={onPlaceholder}
        />
      </div>
      <AccessorySelector
        activeTab={activeAccessoryTab}
        selectedAccessory={selectedAccessory}
        onTabChange={onAccessoryTabChange}
        onAccessoryChange={onAccessoryChange}
        onPlaceholder={onPlaceholder}
      />
    </>
  );
}
