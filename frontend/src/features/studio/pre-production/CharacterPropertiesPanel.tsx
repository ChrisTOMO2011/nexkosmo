import { ChevronDown, Settings2, X } from "lucide-react";
import { AISuggestionsPanel } from "./AISuggestionsPanel";

type CharacterPropertiesPanelProps = {
  isOpen: boolean;
  onClose: () => void;
  age: number;
  height: number;
  bodyType: string;
  skinTone: number;
  appliedSuggestions: string[];
  onAgeChange: (value: number) => void;
  onHeightChange: (value: number) => void;
  onBodyTypeChange: (value: string) => void;
  onSkinToneChange: (value: number) => void;
  onApplySuggestion: (id: string) => void;
  onPlaceholder: (message: string) => void;
};

export function CharacterPropertiesPanel({
  isOpen,
  onClose,
  age,
  height,
  bodyType,
  skinTone,
  appliedSuggestions,
  onAgeChange,
  onHeightChange,
  onBodyTypeChange,
  onSkinToneChange,
  onApplySuggestion,
  onPlaceholder,
}: CharacterPropertiesPanelProps) {
  return (
    <aside
      className={`properties-sidebar ${isOpen ? "is-open" : ""}`}
      aria-label="Character properties"
    >
      <button
        className="properties-close"
        type="button"
        aria-label="Close properties"
        onClick={onClose}
      >
        <X aria-hidden="true" />
      </button>
      <div className="properties-card">
        <div className="properties-tabs" role="tablist" aria-label="Property panels">
          <button className="is-active" type="button" role="tab" aria-selected="true">
            PROPERTIES
          </button>
          <button
            type="button"
            role="tab"
            aria-selected="false"
            onClick={() => onPlaceholder("Transform panel placeholder opened.")}
          >
            TRANSFORM
          </button>
        </div>

        <div className="property-form">
          <label>
            <span>Identity Name</span>
            <input defaultValue="Christopher" aria-label="Identity Name" />
          </label>

          <label>
            <span>Identity Type</span>
            <span className="select-wrap">
              <select defaultValue="Human Male" aria-label="Identity Type">
                <option>Human Male</option>
                <option>Human Female</option>
                <option>Creature</option>
              </select>
              <ChevronDown aria-hidden="true" />
            </span>
          </label>

          <label className="slider-field">
            <span>
              Age <output>{age}</output>
            </span>
            <input
              type="range"
              min="18"
              max="80"
              value={age}
              aria-label="Age"
              onChange={(event) => onAgeChange(Number(event.target.value))}
            />
          </label>

          <label className="slider-field">
            <span>
              Height <output>{height} cm</output>
            </span>
            <input
              type="range"
              min="140"
              max="220"
              value={height}
              aria-label="Height in centimetres"
              onChange={(event) => onHeightChange(Number(event.target.value))}
            />
          </label>

          <label>
            <span>Body Type</span>
            <span className="select-wrap">
              <select
                value={bodyType}
                aria-label="Body Type"
                onChange={(event) => onBodyTypeChange(event.target.value)}
              >
                <option>Athletic</option>
                <option>Average</option>
                <option>Muscular</option>
                <option>Lean</option>
              </select>
              <ChevronDown aria-hidden="true" />
            </span>
          </label>

          <label className="slider-field skin-tone-field">
            <span>Skin Tone</span>
            <input
              type="range"
              min="0"
              max="100"
              value={skinTone}
              aria-label="Skin Tone"
              onChange={(event) => onSkinToneChange(Number(event.target.value))}
            />
          </label>

          <button
            className="advanced-settings-button"
            type="button"
            onClick={() => onPlaceholder("Advanced settings placeholder opened.")}
          >
            <Settings2 aria-hidden="true" />
            Advanced Settings
          </button>
        </div>
      </div>

      <AISuggestionsPanel
        applied={appliedSuggestions}
        onApply={onApplySuggestion}
        onPlaceholder={onPlaceholder}
      />
    </aside>
  );
}
