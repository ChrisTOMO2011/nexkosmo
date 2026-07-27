import { SlidersHorizontal } from "lucide-react";
import { useMemo, useState } from "react";
import { ProjectSidebar } from "../features/studio/ProjectSidebar";
import { SceneActionBar } from "../features/studio/SceneActionBar";
import { StudioTopNavigation } from "../features/studio/StudioTopNavigation";
import { CharacterEditorTabs } from "../features/studio/pre-production/CharacterEditorTabs";
import { CharacterIdentitySource } from "../features/studio/pre-production/CharacterIdentitySource";
import { CharacterPreview } from "../features/studio/pre-production/CharacterPreview";
import { CharacterPropertiesPanel } from "../features/studio/pre-production/CharacterPropertiesPanel";
import { CharacterRoster } from "../features/studio/pre-production/CharacterRoster";
import { IdentityEditor } from "../features/studio/pre-production/IdentityEditor";
import {
  initialCharacters,
  type Character,
} from "../features/studio/pre-production/data";

export function CharacterIdentityPage() {
  const [activeStage, setActiveStage] = useState(0);
  const [activeNav, setActiveNav] = useState("Characters");
  const [selectedCharacter, setSelectedCharacter] = useState("christopher");
  const [characters, setCharacters] = useState<Character[]>(initialCharacters);
  const [selectedFace, setSelectedFace] = useState(3);
  const [previewSlide, setPreviewSlide] = useState(0);
  const [editorTab, setEditorTab] = useState("Identity");
  const [selectedStyle, setSelectedStyle] = useState("Realistic");
  const [speciesFilter, setSpeciesFilter] = useState("Human");
  const [selectedSpecies, setSelectedSpecies] = useState("Human");
  const [accessoryTab, setAccessoryTab] = useState("Glasses");
  const [selectedAccessory, setSelectedAccessory] = useState("");
  const [age, setAge] = useState(35);
  const [height, setHeight] = useState(180);
  const [bodyType, setBodyType] = useState("Athletic");
  const [skinTone, setSkinTone] = useState(89);
  const [appliedSuggestions, setAppliedSuggestions] = useState<string[]>([]);
  const [propertiesOpen, setPropertiesOpen] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");

  const activeEditorName = useMemo(
    () => (editorTab === "Identity" ? "Identity" : `${editorTab} editor`),
    [editorTab],
  );

  function showStatus(message: string) {
    setStatusMessage(message);
  }

  function addCharacter() {
    const index = characters.length + 1;
    const newCharacter: Character = {
      id: `character-${index}`,
      name: `Character ${index}`,
      role: "Supporting",
      crop: "avatar-lee",
    };
    setCharacters((current) => [...current, newCharacter]);
    setSelectedCharacter(newCharacter.id);
    showStatus(`${newCharacter.name} added locally.`);
  }

  function applySuggestion(id: string) {
    setAppliedSuggestions((current) =>
      current.includes(id)
        ? current.filter((item) => item !== id)
        : [...current, id],
    );
    showStatus("Character suggestion updated locally.");
  }

  return (
    <div className="nexkosmo-studio">
      <StudioTopNavigation
        activeStage={activeStage}
        onStageChange={setActiveStage}
        onPlaceholder={showStatus}
      />

      <div className="studio-shell">
        <ProjectSidebar
          activeItem={activeNav}
          onNavigate={(label) => {
            setActiveNav(label);
            if (label !== "Characters") {
              showStatus(`${label} workspace placeholder selected.`);
            }
          }}
          onPlaceholder={showStatus}
        />

        <main className="studio-workspace">
          <section className="workspace-top">
            <CharacterIdentitySource
              selectedFace={selectedFace}
              onSelectFace={setSelectedFace}
              onPlaceholder={showStatus}
            />
            <CharacterPreview
              slide={previewSlide}
              onSlideChange={setPreviewSlide}
              onPlaceholder={showStatus}
            />
            <CharacterRoster
              characters={characters}
              selectedId={selectedCharacter}
              onSelect={setSelectedCharacter}
              onAdd={addCharacter}
            />
          </section>

          <section className="lower-editor" aria-label={activeEditorName}>
            <CharacterEditorTabs
              activeTab={editorTab}
              onChange={(tab) => {
                setEditorTab(tab);
                if (tab !== "Identity") {
                  showStatus(`${tab} editor placeholder selected.`);
                }
              }}
            />
            <div className="editor-scroll">
              <IdentityEditor
                selectedStyle={selectedStyle}
                activeSpeciesFilter={speciesFilter}
                selectedSpecies={selectedSpecies}
                activeAccessoryTab={accessoryTab}
                selectedAccessory={selectedAccessory}
                onStyleChange={setSelectedStyle}
                onSpeciesFilterChange={setSpeciesFilter}
                onSpeciesChange={setSelectedSpecies}
                onAccessoryTabChange={setAccessoryTab}
                onAccessoryChange={setSelectedAccessory}
                onPlaceholder={showStatus}
              />
            </div>
          </section>
        </main>

        <button
          className="properties-toggle"
          type="button"
          aria-label="Open character properties"
          onClick={() => setPropertiesOpen(true)}
        >
          <SlidersHorizontal aria-hidden="true" />
        </button>

        <CharacterPropertiesPanel
          isOpen={propertiesOpen}
          onClose={() => setPropertiesOpen(false)}
          age={age}
          height={height}
          bodyType={bodyType}
          skinTone={skinTone}
          appliedSuggestions={appliedSuggestions}
          onAgeChange={setAge}
          onHeightChange={setHeight}
          onBodyTypeChange={setBodyType}
          onSkinToneChange={setSkinTone}
          onApplySuggestion={applySuggestion}
          onPlaceholder={showStatus}
        />
      </div>

      <SceneActionBar
        onPreview={() => showStatus("Scene preview placeholder started.")}
        onNext={() => {
          setActiveStage(1);
          showStatus("Set workflow selected.");
        }}
      />

      <div className="status-announcer" role="status" aria-live="polite">
        {statusMessage}
      </div>
    </div>
  );
}
