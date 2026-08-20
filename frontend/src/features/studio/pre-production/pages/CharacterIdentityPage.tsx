import { useEffect, useMemo, useRef, useState } from "react";
import {
  type ApiCharacterAsset,
  type ApiSpecies,
  type CharacterSelectionPatch,
  CharacterApiError,
  canonicalEntityId,
  characterPipelineService,
  type Character as BrainCharacter,
} from "../../../../brain/characters";
import {
  ProjectApiError,
  projectDataGateway,
} from "../../../../brain/projects";
import { navigateInApp } from "../../../../app/navigation";
import {
  BottomActionBar,
  LeftSidebar,
  RightSidebar,
} from "../../../../components/studio";
import { CharacterEditorTabs } from "../CharacterEditorTabs";
import { CharacterAssetEditor } from "../CharacterAssetEditor";
import type { AccessoryAssetItem } from "../AccessorySelector";
import { CharacterIdentitySource } from "../CharacterIdentitySource";
import { CharacterPreview } from "../CharacterPreview";
import { CharacterPropertiesPanel } from "../CharacterPropertiesPanel";
import { CharacterRoster } from "../CharacterRoster";
import { IdentityEditor } from "../IdentityEditor";
import {
  ALL_SPECIES_FILTER_ID,
  type SpeciesFilterId,
} from "../SpeciesSelector";
import {
  ActiveProducerPanel,
  DeferredActionNotice,
  DomainStatusNotice,
  getDeferredActionMessage,
  PreProductionWorkspace,
  type ActiveProducerProfile,
  type DeferredActionId,
} from "../shared";
import {
  accessorySubcategories,
  getStyleAssetId,
  getStyleName,
  resolveCharacterFromRoute,
  toCharacterView,
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
  const requestedProductionId =
    new URLSearchParams(window.location.search).get("productionId") ??
    projectId;
  const [ownership, setOwnership] = useState<{
    projectId: string;
    productionId: string;
  } | null>(null);
  const [activeProducer, setActiveProducer] = useState<
    ActiveProducerProfile | undefined
  >();
  const [activeNav, setActiveNav] = useState("Characters");
  const [selectedCharacter, setSelectedCharacter] = useState("");
  const [characters, setCharacters] = useState<Character[]>([]);
  const [brainCharacters, setBrainCharacters] = useState<
    Record<string, BrainCharacter>
  >({});
  const [speciesLoadResult, setSpeciesLoadResult] = useState<{
    projectId: string;
    items: readonly ApiSpecies[];
    error?: string;
  }>({ projectId: "", items: [] });
  const [supportedTabs, setSupportedTabs] = useState<readonly string[]>([
    "Identity",
    "Face",
    "Hair",
    "Skin",
    "Eyes",
    "Beard",
    "Age",
    "Expression",
  ]);
  const [editorAssetLoadResult, setEditorAssetLoadResult] = useState<{
    characterId: string;
    speciesId?: string;
    category: string;
    items: readonly ApiCharacterAsset[];
    error?: string;
  }>({ characterId: "", category: "", items: [] });
  const [accessoryLoadResult, setAccessoryLoadResult] = useState<{
    characterId: string;
    speciesId?: string;
    items: readonly ApiCharacterAsset[];
    error?: string;
  }>({ characterId: "", items: [] });
  const [compatibleAssetLoadResult, setCompatibleAssetLoadResult] = useState<{
    characterId: string;
    speciesId?: string;
    ids: ReadonlySet<string>;
  }>({ characterId: "", ids: new Set() });
  const [selectionsByCharacter, setSelectionsByCharacter] = useState<
    Record<string, { style: string }>
  >({});
  const [mutationPending, setMutationPending] = useState(false);
  const [activeSpeciesFilterId, setActiveSpeciesFilterId] =
    useState<SpeciesFilterId>(ALL_SPECIES_FILTER_ID);
  const [focusedSpeciesId, setFocusedSpeciesId] = useState<string>();
  const [pendingSpeciesId, setPendingSpeciesId] = useState<string>();
  const [optimisticSpeciesId, setOptimisticSpeciesId] = useState<string>();
  const [speciesMutationError, setSpeciesMutationError] = useState<string>();
  const [pendingAccessoryId, setPendingAccessoryId] = useState<string>();
  const [focusedAccessoryId, setFocusedAccessoryId] = useState<string>();
  const [accessoryMutationError, setAccessoryMutationError] = useState<string>();
  const [selectedFace, setSelectedFace] = useState(3);
  const [previewSlide, setPreviewSlide] = useState(0);
  const [editorTab, setEditorTab] = useState("Identity");
  const [selectedStyle, setSelectedStyle] = useState("Realistic");
  const [accessoryTab, setAccessoryTab] = useState("Glasses");
  const [age, setAge] = useState(35);
  const [height, setHeight] = useState(180);
  const [bodyType, setBodyType] = useState("Athletic");
  const [skinTone, setSkinTone] = useState(89);
  const [propertiesOpen, setPropertiesOpen] = useState(false);
  const [deferredAction, setDeferredAction] = useState<DeferredActionId | null>(
    null,
  );
  const [statusMessage, setStatusMessage] = useState(
    "Loading characters from the Nexkosmo Brain…",
  );
  const selectedCharacterRef = useRef("");
  const physicalSaveTimers = useRef(new Map<string, number>());
  const pendingPhysicalByCharacter = useRef(
    new Map<string, Partial<BrainCharacter>>(),
  );
  const speciesRegistry =
    speciesLoadResult.projectId === projectId ? speciesLoadResult.items : [];
  const speciesLoading = speciesLoadResult.projectId !== projectId;
  const speciesError =
    speciesLoadResult.projectId === projectId
      ? speciesLoadResult.error
      : undefined;
  const selectedCharacterSpeciesId =
    brainCharacters[selectedCharacter]?.speciesId;

  useEffect(() => {
    selectedCharacterRef.current = selectedCharacter;
  }, [selectedCharacter]);

  useEffect(
    () => () => {
      physicalSaveTimers.current.forEach((timer) =>
        window.clearTimeout(timer),
      );
      physicalSaveTimers.current.clear();
      pendingPhysicalByCharacter.current.clear();
    },
    [],
  );

  useEffect(() => {
    let active = true;
    const canonicalProjectId = canonicalEntityId(projectId);
    void Promise.all([
      projectDataGateway.getProject(canonicalProjectId),
      projectDataGateway.listProductions(canonicalProjectId),
    ])
      .then(([project, productions]) => {
        if (!active) return;
        const requestedId = canonicalEntityId(requestedProductionId);
        const production =
          productions.find((item) => item.productionId === requestedId) ??
          productions[0];
        if (!production) {
          throw new ProjectApiError(
            "Create a production before adding characters.",
            409,
            "production_required",
          );
        }
        setOwnership({
          projectId: project.projectId,
          productionId: production.productionId,
        });
        setActiveProducer(
          project.producerProfile
            ? {
                producerProfileId: project.producerProfile.profileId,
                displayName: project.producerProfile.displayName,
                roleLabel: project.producerProfile.roleLabel,
                avatarReference: project.producerProfile.avatarReference,
                status: project.producerProfile.status,
                shortPrompt: project.producerProfile.shortPrompt,
                availability: project.producerProfile.availability,
                providerStatus: project.producerProfile.providerStatus,
              }
            : undefined,
        );
      })
      .catch((error: unknown) => {
        if (active) setStatusMessage(formatApiError(error));
      });
    return () => {
      active = false;
    };
  }, [projectId, requestedProductionId]);

  useEffect(() => {
    let active = true;
    void characterPipelineService
      .loadCharactersFromSource(projectId)
      .then(async (loaded) => {
        if (!active) return;
        const roster = loaded.map(toCharacterView);
        const routeCharacter = resolveCharacterFromRoute(roster, characterId);
        const registry = await characterPipelineService.loadSpeciesFromSource();
        const selectionNames = Object.fromEntries(
          loaded.map((character) => [
            character.characterId,
            {
              style:
                getStyleName(character.styleProfileId ?? character.typeId) ?? "Realistic",
            },
          ]),
        );
        if (!active) return;
        setCharacters(roster);
        setBrainCharacters(
          Object.fromEntries(loaded.map((character) => [character.characterId, character])),
        );
        setSpeciesLoadResult({ projectId, items: registry });
        setSelectionsByCharacter(selectionNames);
        const routeCharacterId = routeCharacter?.id ?? "";
        selectedCharacterRef.current = routeCharacterId;
        setSelectedCharacter(routeCharacterId);
        const routeBrainCharacter = routeCharacter
          ? loaded.find((item) => item.characterId === routeCharacter.id)
          : undefined;
        setActiveSpeciesFilterId(
          routeBrainCharacter?.speciesId ?? ALL_SPECIES_FILTER_ID,
        );
        setSelectedStyle(
          routeCharacter
            ? selectionNames[routeCharacter.id]?.style ?? "Realistic"
            : "Realistic",
        );
        if (routeCharacter) {
          const brainCharacter = loaded.find(
            (item) => item.characterId === routeCharacter.id,
          );
          if (brainCharacter) syncPhysicalState(brainCharacter);
        }
        setStatusMessage(
          roster.length
            ? ""
            : "No characters have been created for this project yet.",
        );
      })
      .catch((error: unknown) => {
        if (active) {
          const message = formatApiError(error);
          setSpeciesLoadResult({ projectId, items: [], error: message });
          setStatusMessage(message);
        }
      });
    return () => {
      active = false;
    };
  }, [characterId, projectId]);

  useEffect(() => {
    let active = true;
    if (!selectedCharacter) return;
    void characterPipelineService.gateway
      .getSupportedTabs(selectedCharacter)
      .then((items) => {
        if (!active) return;
        const visible = items.filter((item) =>
          ["Identity", "Face", "Hair", "Skin", "Eyes", "Beard", "Age", "Expression"].includes(item),
        );
        setSupportedTabs(visible);
        setEditorTab((current) =>
          visible.includes(current) ? current : "Identity",
        );
      })
      .catch((error: unknown) => {
        if (active) setStatusMessage(formatApiError(error));
      });
    return () => {
      active = false;
    };
  }, [selectedCharacter, selectedCharacterSpeciesId]);

  useEffect(() => {
    let active = true;
    if (!selectedCharacter || editorTab === "Identity") {
      return;
    }
    const category = editorTab === "Age" ? "age-preset" : editorTab.toLocaleLowerCase();
    const speciesId = selectedCharacterSpeciesId;
    void characterPipelineService
      .loadCompatibleAssetsFromSource(selectedCharacter, category)
      .then((items) => {
        if (active) {
          setEditorAssetLoadResult({
            characterId: selectedCharacter,
            speciesId,
            category,
            items,
          });
        }
      })
      .catch((error: unknown) => {
        if (active) {
          const message = formatApiError(error);
          setEditorAssetLoadResult({
            characterId: selectedCharacter,
            speciesId,
            category,
            items: [],
            error: message,
          });
          setStatusMessage(message);
        }
      });
    return () => {
      active = false;
    };
  }, [editorTab, selectedCharacter, selectedCharacterSpeciesId]);

  useEffect(() => {
    let active = true;
    if (!selectedCharacter) return;
    const speciesId = selectedCharacterSpeciesId;
    void characterPipelineService
      .loadCompatibleAssetsFromSource(selectedCharacter, "accessory")
      .then((items) => {
        if (active) {
          setAccessoryLoadResult({
            characterId: selectedCharacter,
            speciesId,
            items,
          });
          setAccessoryMutationError(undefined);
        }
      })
      .catch((error: unknown) => {
        if (active) {
          const message = formatApiError(error);
          setAccessoryLoadResult({
            characterId: selectedCharacter,
            speciesId,
            items: [],
            error: message,
          });
          setStatusMessage(message);
        }
      });
    return () => {
      active = false;
    };
  }, [selectedCharacter, selectedCharacterSpeciesId]);

  useEffect(() => {
    let active = true;
    if (!selectedCharacter) {
      return;
    }
    const speciesId = selectedCharacterSpeciesId;
    void characterPipelineService
      .loadCompatibleAssetsFromSource(selectedCharacter)
      .then((assets) => {
        if (active) {
          setCompatibleAssetLoadResult({
            characterId: selectedCharacter,
            speciesId,
            ids: new Set(assets.map((asset) => asset.assetId)),
          });
        }
      })
      .catch((error: unknown) => {
        if (active) setStatusMessage(formatApiError(error));
      });
    return () => {
      active = false;
    };
  }, [selectedCharacter, selectedCharacterSpeciesId]);

  const activeEditorName = useMemo(
    () => (editorTab === "Identity" ? "Identity" : `${editorTab} editor`),
    [editorTab],
  );

  function showStatus(message: string) {
    setDeferredAction(null);
    setStatusMessage(message);
  }

  function showDeferredAction(action: DeferredActionId) {
    setDeferredAction(action);
    setStatusMessage(getDeferredActionMessage(action));
  }

  function acceptPersisted(
    character: BrainCharacter,
    options: { reconcileSpeciesFilter?: boolean } = {},
  ) {
    setBrainCharacters((current) => ({ ...current, [character.characterId]: character }));
    setCharacters((current) =>
      current.map((item) =>
        item.id === character.characterId ? toCharacterView(character) : item,
      ),
    );
    if (character.characterId === selectedCharacterRef.current) {
      syncPhysicalState(character);
      const styleName =
        getStyleName(character.styleProfileId ?? character.typeId) ??
        "Realistic";
      setSelectedStyle(styleName);
      if (options.reconcileSpeciesFilter) {
        setActiveSpeciesFilterId(character.speciesId);
      }
      setSelectionsByCharacter((current) => ({
        ...current,
        [character.characterId]: { style: styleName },
      }));
    }
  }

  async function handleMutationFailure(
    error: unknown,
    rollback?: () => void,
    reconcileSpeciesFilter = false,
  ) {
    rollback?.();
    if (
      error instanceof CharacterApiError &&
      error.conflict &&
      selectedCharacter
    ) {
      try {
        const authoritative =
          await characterPipelineService.gateway.getCharacter(selectedCharacter);
        acceptPersisted(authoritative, { reconcileSpeciesFilter });
        showStatus(
          "This character changed elsewhere. The authoritative Character state has been reloaded.",
        );
        return;
      } catch (reloadError) {
        showStatus(formatApiError(reloadError));
        return;
      }
    }
    showStatus(formatApiError(error));
  }

  function syncPhysicalState(character: BrainCharacter) {
    setAge(character.age);
    setHeight(character.heightCm);
    setBodyType(character.bodyType);
    setSkinTone(character.skinTone);
  }

  function schedulePhysicalSave(values: Partial<BrainCharacter>) {
    const characterId = selectedCharacterRef.current;
    if (!characterId) return;
    const pending = pendingPhysicalByCharacter.current.get(characterId) ?? {};
    pendingPhysicalByCharacter.current.set(characterId, {
      ...pending,
      ...values,
    });
    const existingTimer = physicalSaveTimers.current.get(characterId);
    if (existingTimer) window.clearTimeout(existingTimer);
    const timer = window.setTimeout(() => {
      const update = pendingPhysicalByCharacter.current.get(characterId) ?? {};
      pendingPhysicalByCharacter.current.delete(characterId);
      physicalSaveTimers.current.delete(characterId);
      void characterPipelineService
        .updatePhysicalPropertiesInSource(characterId, update)
        .then((character) => {
          acceptPersisted(character);
          showStatus("Character physical profile saved.");
        })
        .catch((error: unknown) => void handleMutationFailure(error));
    }, 350);
    physicalSaveTimers.current.set(characterId, timer);
  }

  async function addCharacter() {
    if (mutationPending) return;
    if (!ownership) {
      showStatus("A persisted project and production are required.");
      return;
    }
    const index = characters.length + 1;
    const speciesId = speciesRegistry.find((item) => item.key === "human")
      ?.speciesId;
    if (!speciesId) return;
    setMutationPending(true);
    try {
      const created = await characterPipelineService.createCharacterInSource({
        projectId: ownership.projectId,
        productionId: ownership.productionId,
        displayName: `Character ${index}`,
        role: "Supporting",
        speciesId,
      });
      const newCharacter = toCharacterView(created);
      setCharacters((current) => [...current, newCharacter]);
      setSelectionsByCharacter((current) => ({
        ...current,
        [newCharacter.id]: { style: "Realistic" },
      }));
      selectedCharacterRef.current = newCharacter.id;
      setSelectedCharacter(newCharacter.id);
      setActiveSpeciesFilterId(speciesId);
      setSelectedStyle("Realistic");
      setBrainCharacters((current) => ({
        ...current,
        [created.characterId]: created,
      }));
      syncPhysicalState(created);
      showStatus(`${newCharacter.name} saved to the Nexkosmo Brain.`);
    } catch (error) {
      showStatus(formatApiError(error));
    } finally {
      setMutationPending(false);
    }
  }

  function selectCharacter(id: string) {
    selectedCharacterRef.current = id;
    setSelectedCharacter(id);
    setSelectedStyle(selectionsByCharacter[id]?.style ?? "Realistic");
    const character = brainCharacters[id];
    if (character) {
      setActiveSpeciesFilterId(character.speciesId);
      syncPhysicalState(character);
    }
  }

  async function selectSpecies(species: ApiSpecies) {
    if (!selectedCharacter || mutationPending || !species.enabled) return;
    const currentCharacter = brainCharacters[selectedCharacter];
    if (!currentCharacter) return;
    if (currentCharacter.speciesId === species.speciesId) {
      setActiveSpeciesFilterId(species.speciesId);
      return;
    }
    setOptimisticSpeciesId(species.speciesId);
    setPendingSpeciesId(species.speciesId);
    setSpeciesMutationError(undefined);
    setMutationPending(true);
    try {
      const mutation = await characterPipelineService.changeSpeciesInSource(
        selectedCharacter,
        species.speciesId,
      );
      acceptPersisted(mutation.character, { reconcileSpeciesFilter: true });
      setOptimisticSpeciesId(undefined);
      showStatus(formatSpeciesChangeSummary(species.name, mutation.changeSummary));
    } catch (error) {
      const message = formatApiError(error);
      setSpeciesMutationError(message);
      await handleMutationFailure(
        error,
        () => setOptimisticSpeciesId(undefined),
        true,
      );
    } finally {
      setPendingSpeciesId(undefined);
      setMutationPending(false);
    }
  }

  async function selectStyle(name: string) {
    const typeId = getStyleAssetId(name);
    if (!typeId || !selectedCharacter || mutationPending) return;
    if (compatibleAssetIds.size && !compatibleAssetIds.has(typeId)) {
      showStatus(`${name} is not compatible with the selected species.`);
      return;
    }
    const previousStyle = selectedStyle;
    setSelectedStyle(name);
    setMutationPending(true);
    try {
      const updated = await characterPipelineService.updateSelectionsInSource(
        selectedCharacter,
        { styleProfileId: typeId },
      );
      acceptPersisted(updated);
      setSelectionsByCharacter((current) => ({
        ...current,
        [selectedCharacter]: {
          style: name,
        },
      }));
      showStatus(`${name} style saved.`);
    } catch (error) {
      await handleMutationFailure(error, () => setSelectedStyle(previousStyle));
    } finally {
      setMutationPending(false);
    }
  }

  async function selectAccessory(asset: AccessoryAssetItem) {
    const assetId = asset.assetId;
    if (!selectedCharacter || mutationPending) return;
    if (compatibleAssetIds.size && !compatibleAssetIds.has(assetId)) {
      showStatus(`${asset.name} is not compatible with the selected species.`);
      return;
    }
    const currentCharacter = brainCharacters[selectedCharacter];
    if (!currentCharacter) return;
    const wasSelected = currentCharacter.accessoryIds.includes(assetId);
    const accessoryIds = wasSelected
      ? currentCharacter.accessoryIds.filter((item) => item !== assetId)
      : [...currentCharacter.accessoryIds, assetId];
    const characterId = selectedCharacter;
    setBrainCharacters((current) => ({
      ...current,
      [characterId]: { ...currentCharacter, accessoryIds },
    }));
    setAccessoryMutationError(undefined);
    setPendingAccessoryId(assetId);
    setMutationPending(true);
    try {
      const updated = await characterPipelineService.updateSelectionsInSource(
        characterId,
        { accessoryIds },
      );
      acceptPersisted(updated);
      showStatus(`${asset.name} accessory ${wasSelected ? "removed" : "saved"}.`);
    } catch (error) {
      setBrainCharacters((current) => ({
        ...current,
        [characterId]: currentCharacter,
      }));
      const message = formatApiError(error);
      setAccessoryMutationError(message);
      await handleMutationFailure(error);
    } finally {
      setPendingAccessoryId(undefined);
      setMutationPending(false);
    }
  }

  function applySuggestion(id: string) {
    void id;
    showDeferredAction("suggestion-application");
  }

  async function updateIdentityName(displayName: string) {
    const current = brainCharacters[selectedCharacter];
    const trimmed = displayName.trim();
    if (!current || !trimmed || trimmed === current.displayName) return;
    try {
      const updated = await characterPipelineService.updateMetadataInSource(
        selectedCharacter,
        { displayName: trimmed },
      );
      acceptPersisted(updated);
      showStatus("Character identity name saved.");
    } catch (error) {
      await handleMutationFailure(error);
    }
  }

  async function updateIdentityType(identityType: string) {
    try {
      const updated = await characterPipelineService.updateIdentityPropertiesInSource(
        selectedCharacter,
        { identityType },
      );
      acceptPersisted(updated);
      showStatus("Character identity type saved.");
    } catch (error) {
      await handleMutationFailure(error);
    }
  }

  async function selectEditorAsset(asset: ApiCharacterAsset) {
    if (!selectedCharacter || mutationPending) return;
    const selection = selectionPatchForTab(editorTab, asset.assetId);
    setMutationPending(true);
    try {
      const updated = await characterPipelineService.updateSelectionsInSource(
        selectedCharacter,
        selection,
      );
      acceptPersisted(updated);
      showStatus(`${asset.name} saved.`);
    } catch (error) {
      await handleMutationFailure(error);
    } finally {
      setMutationPending(false);
    }
  }

  const activeBrainCharacter = brainCharacters[selectedCharacter];
  const canonicalSpeciesId = activeBrainCharacter?.speciesId;
  const selectedSpeciesId = optimisticSpeciesId ?? canonicalSpeciesId;
  const selectedSpeciesName =
    speciesRegistry.find((item) => item.speciesId === selectedSpeciesId)?.name ??
    "Human";
  const editorCategory =
    editorTab === "Age" ? "age-preset" : editorTab.toLocaleLowerCase();
  const editorAssets =
    editorAssetLoadResult.characterId === selectedCharacter &&
    editorAssetLoadResult.speciesId === canonicalSpeciesId &&
    editorAssetLoadResult.category === editorCategory
      ? editorAssetLoadResult.items
      : [];
  const compatibleAssetIds =
    compatibleAssetLoadResult.characterId === selectedCharacter &&
    compatibleAssetLoadResult.speciesId === canonicalSpeciesId
      ? compatibleAssetLoadResult.ids
      : new Set<string>();
  const accessoryAssets =
    accessoryLoadResult.characterId === selectedCharacter &&
    accessoryLoadResult.speciesId === canonicalSpeciesId
      ? accessoryLoadResult.items
      : [];
  const accessoryLoading = Boolean(
    selectedCharacter &&
      (accessoryLoadResult.characterId !== selectedCharacter ||
        accessoryLoadResult.speciesId !== canonicalSpeciesId),
  );
  const accessoryError =
    accessoryMutationError ??
    (accessoryLoadResult.characterId === selectedCharacter &&
    accessoryLoadResult.speciesId === canonicalSpeciesId
      ? accessoryLoadResult.error
      : undefined);
  const activeSpecies = speciesRegistry.find(
    (item) => item.speciesId === activeBrainCharacter?.speciesId,
  );
  const accessorySubcategory =
    accessorySubcategories[
      accessoryTab as keyof typeof accessorySubcategories
    ];
  const visibleAccessories = accessoryAssets.filter(
    (asset) => asset.subcategory === accessorySubcategory,
  );
  const selectedAccessoryIds = activeBrainCharacter?.accessoryIds ?? [];

  return (
    <StudioLayout
      activeStage="build"
      projectId={projectId}
      characterId={characterId}
      variant="character-identity"
      leftSidebar={
        <LeftSidebar
          items={preProductionNavigation}
          activeItem={activeNav}
          sectionLabel="Pre-production sections"
          onNavigate={(label) => {
            setActiveNav(label);
            if (label === "Environment") {
              navigateInApp(
                `/studio/projects/${encodeURIComponent(projectId)}/pre-production/environments`,
              );
            } else if (label !== "Characters") {
              showStatus(`${label} workspace placeholder selected.`);
            }
          }}
          onOpenAdvancedStudio={(label) => {
            if (label !== "CGI Studio" && label !== "VFX Studio") return;
            const editor = label === "CGI Studio" ? "cgi" : "vfx";
            navigateInApp(
              `/studio/projects/${encodeURIComponent(projectId)}/studio?editor=${editor}`,
            );
          }}
          onPlaceholder={showStatus}
          producerPanel={
            <ActiveProducerPanel
              profile={activeProducer}
              context={{
                domain: "characters",
                projectId: ownership?.projectId ?? projectId,
                productionId: ownership?.productionId,
                entityId: selectedCharacter || characterId,
                activeTab: editorTab,
                readinessStatus: activeBrainCharacter?.readinessStatus,
                details: {
                  species: selectedSpeciesName,
                  style: selectedStyle,
                },
              }}
              onDeferredConversation={() =>
                showDeferredAction("producer-conversation")
              }
            />
          }
        />
      }
      rightSidebar={
        <RightSidebar
          open={propertiesOpen}
          title="Character properties"
          onClose={() => setPropertiesOpen(false)}
        >
          <CharacterPropertiesPanel
            identityName={activeBrainCharacter?.displayName ?? "Christopher"}
            identityType={activeBrainCharacter?.identityType ?? "Human Male"}
            age={age}
            height={height}
            bodyType={bodyType}
            skinTone={skinTone}
            appliedSuggestions={[]}
            minAge={activeSpecies?.minAge}
            maxAge={activeSpecies?.maxAge}
            minHeight={activeSpecies?.minHeightCm}
            maxHeight={activeSpecies?.maxHeightCm}
            surfaceControlLabel={activeSpecies?.surfaceControlLabel}
            onIdentityNameCommit={(value) => void updateIdentityName(value)}
            onIdentityTypeChange={(value) => void updateIdentityType(value)}
            onAgeChange={(value) => {
              setAge(value);
              schedulePhysicalSave({ age: value, apparentAge: value });
            }}
            onHeightChange={(value) => {
              setHeight(value);
              schedulePhysicalSave({ heightCm: value });
            }}
            onBodyTypeChange={(value) => {
              setBodyType(value);
              schedulePhysicalSave({ bodyType: value });
            }}
            onSkinToneChange={(value) => {
              setSkinTone(value);
              schedulePhysicalSave({ skinTone: value });
            }}
            onApplySuggestion={applySuggestion}
            onPlaceholder={showStatus}
            onDeferredAction={showDeferredAction}
          />
        </RightSidebar>
      }
      bottomActionBar={
        <BottomActionBar
          primaryLabel="Next: READY"
          onSecondary={() => showStatus("Scene preview placeholder started.")}
          onPrimary={() => navigateInApp(`/studio/projects/${projectId}/ready`)}
        />
      }
      rightSidebarLabel="Open character properties"
      onOpenRightSidebar={() => setPropertiesOpen(true)}
      onPlaceholder={showStatus}
      statusMessage={statusMessage}
      statusNotice={
        deferredAction ? (
          <DeferredActionNotice key={statusMessage} action={deferredAction} />
        ) : (
          <DomainStatusNotice key={statusMessage} message={statusMessage} />
        )
      }
    >
      <PreProductionWorkspace
        sourcePanel={
          <CharacterIdentitySource
            displayName={activeBrainCharacter?.displayName ?? "Christopher"}
            role={activeBrainCharacter?.role ?? "Lead"}
            identityType={activeBrainCharacter?.identityType ?? "Human Male"}
            selectedFace={selectedFace}
            onSelectFace={setSelectedFace}
            onDeferredAction={showDeferredAction}
          />
        }
        preview={
          <CharacterPreview
            slide={previewSlide}
            onSlideChange={setPreviewSlide}
            onPlaceholder={showStatus}
          />
        }
        selectionRail={
          <CharacterRoster
            characters={characters}
            selectedId={selectedCharacter}
            onSelect={selectCharacter}
            onAdd={() => void addCharacter()}
          />
        }
        editorTabs={
          <CharacterEditorTabs
            activeTab={editorTab}
            tabs={supportedTabs}
            onChange={(tab) => {
              setEditorTab(tab);
            }}
          />
        }
        editorLabel={activeEditorName}
        editorContent={
          editorTab === "Identity" ? (
            <IdentityEditor
              selectedStyle={selectedStyle}
              activeSpeciesFilterId={activeSpeciesFilterId}
              selectedSpeciesId={selectedSpeciesId}
              species={speciesRegistry}
              focusedSpeciesId={focusedSpeciesId}
              pendingSpeciesId={pendingSpeciesId}
              speciesSelectionDisabled={mutationPending}
              speciesLoading={speciesLoading}
              speciesError={speciesMutationError ?? speciesError}
              activeAccessoryTab={accessoryTab}
              selectedAccessoryIds={selectedAccessoryIds}
              accessoryItems={visibleAccessories}
              focusedAccessoryId={focusedAccessoryId}
              pendingAccessoryId={pendingAccessoryId}
              accessorySelectionDisabled={mutationPending}
              accessoryLoading={accessoryLoading}
              accessoryError={accessoryError}
              onStyleChange={(name) => void selectStyle(name)}
              onSpeciesFilterChange={setActiveSpeciesFilterId}
              onSpeciesChange={(species) => void selectSpecies(species)}
              onSpeciesFocus={setFocusedSpeciesId}
              onAccessoryTabChange={setAccessoryTab}
              onAccessoryChange={(asset) => void selectAccessory(asset)}
              onAccessoryFocus={setFocusedAccessoryId}
              onPlaceholder={showStatus}
              onDeferredAction={showDeferredAction}
            />
          ) : (
            <CharacterAssetEditor
              tab={editorTab}
              assets={editorAssets}
              selectedAssetId={getSelectedAssetId(activeBrainCharacter, editorTab)}
              onSelect={(asset) => void selectEditorAsset(asset)}
            />
          )
        }
      />
    </StudioLayout>
  );
}

function formatSpeciesChangeSummary(
  speciesName: string,
  summary: Readonly<Record<string, unknown>>,
) {
  const preserved = Array.isArray(summary.preserved_asset_ids)
    ? summary.preserved_asset_ids.length
    : 0;
  const cleared = Array.isArray(summary.cleared_asset_ids)
    ? summary.cleared_asset_ids.length
    : 0;
  const defaults = Array.isArray(summary.applied_default_asset_ids)
    ? summary.applied_default_asset_ids.length
    : 0;
  return `${speciesName} compatibility profile saved. Preserved ${preserved} compatible selections, cleared ${cleared} incompatible selections, and applied ${defaults} species defaults.`;
}

function formatApiError(error: unknown) {
  if (error instanceof ProjectApiError) {
    return error.status === 409
      ? `${error.message} Refresh the project before trying again.`
      : error.message;
  }
  if (error instanceof CharacterApiError) {
    if (error.conflict) {
      return "This character changed elsewhere. Reload before trying again.";
    }
    return error.retryable
      ? `${error.message} Try the action again.`
      : error.message;
  }
  return "The character operation could not be completed.";
}

function selectionPatchForTab(tab: string, assetId: string): CharacterSelectionPatch {
  const fields: Record<string, keyof CharacterSelectionPatch> = {
    Face: "faceId",
    Hair: "hairId",
    Skin: "skinId",
    Eyes: "eyesId",
    Beard: "beardId",
    Age: "agePresetId",
    Expression: "expressionId",
  };
  const field = fields[tab];
  return field ? ({ [field]: assetId } as CharacterSelectionPatch) : {};
}

function getSelectedAssetId(character: BrainCharacter | undefined, tab: string) {
  if (!character) return undefined;
  const selected: Record<string, string | undefined> = {
    Face: character.faceId,
    Hair: character.hairId,
    Skin: character.skinId,
    Eyes: character.eyesId,
    Beard: character.beardId,
    Age: character.agePresetId,
    Expression: character.expressionId,
  };
  return selected[tab];
}
