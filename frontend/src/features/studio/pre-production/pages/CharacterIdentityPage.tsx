import { useMemo, useState } from "react";
import {
  BottomActionBar,
  LeftSidebar,
  RightSidebar,
} from "../../../../components/studio";
import { CharacterEditorTabs } from "../CharacterEditorTabs";
import { CharacterIdentitySource } from "../CharacterIdentitySource";
import { CharacterPreview } from "../CharacterPreview";
import { CharacterPropertiesPanel } from "../CharacterPropertiesPanel";
import { CharacterRoster } from "../CharacterRoster";
import { IdentityEditor } from "../IdentityEditor";
import {
  initialCharacters,
  type Character,
} from "../data";
import { preProductionNavigation } from "../../config/navigation";
import { StudioLayout } from "../../../../layouts/StudioLayout";

type CharacterIdentityPageProps = {
  projectId: string;
  characterId: string;
};

export function CharacterIdentityPage({
  projectId,
  characterId,
}: CharacterIdentityPageProps) {
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
    <StudioLayout
      activeStage="pre-production"
      projectId={projectId}
      characterId={characterId}
      leftSidebar={
        <LeftSidebar
          items={preProductionNavigation}
          activeItem={activeNav}
          sectionLabel="Pre-production sections"
          onNavigate={(label) => {
            setActiveNav(label);
            if (label !== "Characters") {
              showStatus(`${label} workspace placeholder selected.`);
            }
          }}
          onPlaceholder={showStatus}
        />
      }
      rightSidebar={
        <RightSidebar
          open={propertiesOpen}
          title="Character properties"
          onClose={() => setPropertiesOpen(false)}
        >
          <CharacterPropertiesPanel
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
        </RightSidebar>
      }
      bottomActionBar={
        <BottomActionBar
          primaryLabel="Next: Set"
          onSecondary={() => showStatus("Scene preview placeholder started.")}
          onPrimary={() =>
            window.location.assign(`/studio/projects/${projectId}/set`)
          }
        />
      }
      rightSidebarLabel="Open character properties"
      onOpenRightSidebar={() => setPropertiesOpen(true)}
      onPlaceholder={showStatus}
      statusMessage={statusMessage}
    >
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
    </StudioLayout>
  );
}
