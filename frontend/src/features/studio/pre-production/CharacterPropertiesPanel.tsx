import { Settings2 } from "lucide-react";
import {
  Button,
  Dropdown,
  PropertyField,
  Slider,
} from "../../../components/ui";
import { AISuggestionsPanel } from "./AISuggestionsPanel";
import {
  DomainInspectorPanel,
  type DeferredActionId,
} from "./shared";

type CharacterPropertiesPanelProps = {
  identityName: string;
  identityType: string;
  age: number;
  height: number;
  bodyType: string;
  skinTone: number;
  appliedSuggestions: string[];
  minAge?: number;
  maxAge?: number;
  minHeight?: number;
  maxHeight?: number;
  surfaceControlLabel?: string;
  onIdentityNameCommit: (value: string) => void;
  onIdentityTypeChange: (value: string) => void;
  onAgeChange: (value: number) => void;
  onHeightChange: (value: number) => void;
  onBodyTypeChange: (value: string) => void;
  onSkinToneChange: (value: number) => void;
  onApplySuggestion: (id: string) => void;
  onPlaceholder: (message: string) => void;
  onDeferredAction: (action: DeferredActionId) => void;
};

export function CharacterPropertiesPanel({
  identityName,
  identityType,
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
  onDeferredAction,
  minAge = 0,
  maxAge = 120,
  minHeight = 90,
  maxHeight = 240,
  surfaceControlLabel = "Skin Tone",
  onIdentityNameCommit,
  onIdentityTypeChange,
}: CharacterPropertiesPanelProps) {
  return (
    <>
      <DomainInspectorPanel
        tabs={[
          { id: "properties", label: "PROPERTIES" },
          { id: "transform", label: "TRANSFORM" },
        ]}
        activeTab="properties"
        onTabChange={(tab) => {
          if (tab === "transform") {
            onPlaceholder("Transform panel placeholder opened.");
          }
        }}
      >
        <div className="property-form">
          <PropertyField label="Identity Name">
            <input
              key={identityName}
              defaultValue={identityName}
              aria-label="Identity Name"
              onBlur={(event) => onIdentityNameCommit(event.target.value)}
            />
          </PropertyField>

          <PropertyField label="Identity Type">
            <Dropdown
              className="select-wrap"
              label="Identity Type"
              value={identityType}
              options={[
                { label: "Human Male", value: "Human Male" },
                { label: "Human Female", value: "Human Female" },
                { label: "Creature", value: "Creature" },
              ]}
              onChange={(event) => onIdentityTypeChange(event.target.value)}
            />
          </PropertyField>

          <Slider
            label="Age"
            min={minAge}
            max={maxAge}
            value={age}
            onChange={onAgeChange}
          />

          <Slider
            label="Height"
            min={minHeight}
            max={maxHeight}
            value={height}
            formatValue={(value) => `${value} cm`}
            onChange={onHeightChange}
          />

          <PropertyField label="Body Type">
            <Dropdown
              className="select-wrap"
              label="Body Type"
              value={bodyType}
              options={["Athletic", "Average", "Muscular", "Lean"].map(
                (value) => ({ label: value, value }),
              )}
              onChange={(event) => onBodyTypeChange(event.target.value)}
            />
          </PropertyField>

          <Slider
            className="skin-tone-field"
            label={surfaceControlLabel}
            min={0}
            max={100}
            value={skinTone}
            showValue={false}
            onChange={onSkinToneChange}
          />

          <Button
            className="advanced-settings-button"
            leadingIcon={<Settings2 aria-hidden="true" />}
            onClick={() => onPlaceholder("Advanced settings placeholder opened.")}
          >
            Advanced Settings
          </Button>
        </div>
      </DomainInspectorPanel>

      <AISuggestionsPanel
        applied={appliedSuggestions}
        onApply={onApplySuggestion}
        onPlaceholder={onPlaceholder}
        onDeferredAction={onDeferredAction}
      />
    </>
  );
}
