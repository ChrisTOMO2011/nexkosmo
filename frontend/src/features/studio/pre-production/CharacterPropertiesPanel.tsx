import { Settings2 } from "lucide-react";
import { InspectorPanel } from "../../../components/studio";
import {
  Button,
  Dropdown,
  PropertyField,
  Slider,
} from "../../../components/ui";
import { AISuggestionsPanel } from "./AISuggestionsPanel";

type CharacterPropertiesPanelProps = {
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
    <>
      <InspectorPanel
        className="properties-card"
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
            <input defaultValue="Christopher" aria-label="Identity Name" />
          </PropertyField>

          <PropertyField label="Identity Type">
            <Dropdown
              className="select-wrap"
              label="Identity Type"
              defaultValue="Human Male"
              options={[
                { label: "Human Male", value: "Human Male" },
                { label: "Human Female", value: "Human Female" },
                { label: "Creature", value: "Creature" },
              ]}
            />
          </PropertyField>

          <Slider
            label="Age"
            min={0}
            max={73}
            value={age}
            onChange={onAgeChange}
          />

          <Slider
            label="Height"
            min={90}
            max={240}
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
            label="Skin Tone"
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
      </InspectorPanel>

      <AISuggestionsPanel
        applied={appliedSuggestions}
        onApply={onApplySuggestion}
        onPlaceholder={onPlaceholder}
      />
    </>
  );
}
