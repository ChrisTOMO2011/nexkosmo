import { useEffect, useMemo, useRef, useState } from "react";
import {
  environmentApi,
  EnvironmentApiError,
  type Environment,
  type EnvironmentAsset,
  type EnvironmentReadiness,
  type EnvironmentType,
} from "../../../../brain/environments";
import { canonicalEntityId } from "../../../../brain/characters";
import {
  projectDataGateway,
  type AssignedCreativeProfile,
} from "../../../../brain/projects";
import type { ActiveProducerProfile, DeferredActionId } from "../shared";
import {
  environmentCategoryByTab,
  environmentMultiCategories,
  environmentTabs,
  environmentTitleCase,
  selectedEnvironmentAssetIds,
} from "./environment-workspace.config";
import type {
  EnvironmentAssetCache,
  EnvironmentOwnership,
  EnvironmentWorkspaceController,
} from "./environment-workspace.types";

type ControllerInput = Readonly<{
  projectId: string;
  environmentId?: string;
}>;

export function useEnvironmentWorkspaceController({
  projectId,
  environmentId,
}: ControllerInput): EnvironmentWorkspaceController {
  const [ownership, setOwnership] = useState<EnvironmentOwnership>();
  const [producer, setProducer] = useState<ActiveProducerProfile>();
  const [types, setTypes] = useState<readonly EnvironmentType[]>([]);
  const [environments, setEnvironments] = useState<readonly Environment[]>([]);
  const [selectedId, setSelectedId] = useState(environmentId ?? "");
  const [readinessLoad, setReadinessLoad] = useState<{
    environmentId: string;
    value: EnvironmentReadiness;
  }>();
  const [assetLoad, setAssetLoad] = useState<EnvironmentAssetCache>({
    environmentId: "",
    filter: "all",
    items: [],
  });
  const [filterItemsByCategory, setFilterItemsByCategory] = useState<
    Readonly<Record<string, readonly Readonly<{ id: string; label: string }>[]>>
  >({});
  const [activeTab, setActiveTabState] = useState("Identity");
  const [activeFilter, setActiveFilter] = useState("all");
  const [previewSlide, setPreviewSlide] = useState(0);
  const [propertiesOpen, setPropertiesOpen] = useState(false);
  const [pending, setPending] = useState(false);
  const [deferredAction, setDeferredAction] = useState<DeferredActionId | null>(null);
  const [status, setStatus] = useState("Loading Environment packages from the Nexkosmo Brain…");
  const loadGeneration = useRef(0);
  const assetGeneration = useRef(0);
  const readinessGeneration = useRef(0);

  const selected = environments.find((item) => item.environmentId === selectedId);
  const selectedType = types.find(
    (item) => item.environmentTypeId === selected?.environmentTypeId,
  );
  const supportedTabs = selectedType?.supportedTabs ?? environmentTabs;
  const category = environmentCategoryByTab[activeTab];

  useEffect(() => {
    const generation = ++loadGeneration.current;
    const canonicalProjectId = canonicalEntityId(projectId);
    void Promise.all([
      projectDataGateway.getProject(canonicalProjectId),
      projectDataGateway.listProductions(canonicalProjectId),
      environmentApi.listTypes(),
      environmentApi.listByProject(canonicalProjectId),
    ])
      .then(([project, productions, loadedTypes, loadedEnvironments]) => {
        if (generation !== loadGeneration.current) return;
        const production = productions[0];
        if (!production) throw new Error("Create a production before adding environments.");
        setOwnership({ projectId: project.projectId, productionId: production.productionId });
        setProducer(toProducerProfile(project.producerProfile));
        setTypes(loadedTypes);
        setEnvironments(loadedEnvironments);
        const requested = environmentId
          ? loadedEnvironments.find(
              (item) => item.environmentId === canonicalEntityId(environmentId),
            )
          : undefined;
        setSelectedId(requested?.environmentId ?? loadedEnvironments[0]?.environmentId ?? "");
        setStatus(
          loadedEnvironments.length
            ? "Environment packages loaded."
            : "No Environment package exists yet. Create the first package to begin.",
        );
      })
      .catch((error: unknown) => {
        if (generation === loadGeneration.current) setStatus(formatEnvironmentError(error));
      });
    return () => {
      loadGeneration.current += 1;
    };
  }, [environmentId, projectId]);

  useEffect(() => {
    const generation = ++assetGeneration.current;
    if (!selected || !category) {
      return;
    }
    const subcategory = activeFilter === "all" ? undefined : activeFilter;
    void environmentApi
      .listCompatible(selected.environmentId, category, subcategory)
      .then((items) => {
        if (generation !== assetGeneration.current) return;
        setAssetLoad({
          environmentId: selected.environmentId,
          category,
          filter: activeFilter,
          items,
        });
        if (activeFilter === "all") {
          setFilterItemsByCategory((current) => ({
            ...current,
            [category]: [
              { id: "all", label: "All" },
              ...Array.from(new Set(items.map((asset) => asset.subcategory))).map((value) => ({
                id: value,
                label: environmentTitleCase(value),
              })),
            ],
          }));
        }
      })
      .catch((error: unknown) => {
        if (generation === assetGeneration.current) setStatus(formatEnvironmentError(error));
      });
    return () => {
      assetGeneration.current += 1;
    };
  }, [activeFilter, category, selected]);

  useEffect(() => {
    const generation = ++readinessGeneration.current;
    if (!selected) {
      return;
    }
    void environmentApi
      .getReadiness(selected.environmentId)
      .then((value) =>
        generation === readinessGeneration.current &&
        setReadinessLoad({ environmentId: selected.environmentId, value }),
      )
      .catch((error: unknown) => {
        if (generation === readinessGeneration.current) setStatus(formatEnvironmentError(error));
      });
  }, [selected]);

  const assets = useMemo(
    () =>
      selected &&
      assetLoad.environmentId === selected.environmentId &&
      assetLoad.category === category &&
      assetLoad.filter === activeFilter
        ? assetLoad.items
        : [],
    [activeFilter, assetLoad, category, selected],
  );
  const filterItems = category
    ? filterItemsByCategory[category] ?? [{ id: "all", label: "All" }]
    : [{ id: "all", label: "All" }];
  const selectedAssetIds = selected ? selectedEnvironmentAssetIds(selected, category) : [];
  const readiness =
    selected && readinessLoad?.environmentId === selected.environmentId
      ? readinessLoad.value
      : undefined;

  function replaceEnvironment(next: Environment) {
    setEnvironments((current) =>
      current.map((item) => (item.environmentId === next.environmentId ? next : item)),
    );
  }

  function showDeferred(action: DeferredActionId) {
    setDeferredAction(null);
    setStatus(
      action === "asset-upload"
        ? "Environment upload is deferred; no file was stored."
        : action === "producer-conversation"
          ? "Producer conversation is deferred; no AI session was started."
          : "Environment AI generation is deferred; no asset was fabricated.",
    );
  }

  async function createEnvironment() {
    const firstType = types[0];
    if (!ownership || !firstType || pending) return;
    setPending(true);
    try {
      const result = await environmentApi.createForProduction({
        productionId: ownership.productionId,
        displayName: `Environment ${environments.length + 1}`,
        environmentTypeId: firstType.environmentTypeId,
      });
      setEnvironments((current) => [...current, result.environment]);
      selectEnvironment(result.environment.environmentId);
      setStatus("Environment package created and saved.");
    } catch (error) {
      setStatus(formatEnvironmentError(error));
    } finally {
      setPending(false);
    }
  }

  function selectEnvironment(nextId: string) {
    setSelectedId(nextId);
    window.history.replaceState(
      {},
      "",
      `/studio/projects/${projectId}/pre-production/environments/${nextId}`,
    );
  }

  async function mutate(
    operation: (current: Environment) => Promise<{ environment: Environment }>,
    message: string,
  ) {
    if (!selected || pending) return;
    const before = selected;
    setPending(true);
    try {
      const result = await operation(before);
      replaceEnvironment(result.environment);
      setStatus(message);
    } catch (error) {
      replaceEnvironment(before);
      setStatus(formatEnvironmentError(error));
      if (error instanceof EnvironmentApiError && error.conflict) {
        try {
          replaceEnvironment(await environmentApi.get(before.environmentId));
        } catch {
          // Preserve the canonical snapshot and the original conflict message.
        }
      }
    } finally {
      setPending(false);
    }
  }

  async function updateIdentity(values: Readonly<{ display_name?: string; description?: string }>) {
    await mutate(
      (current) => environmentApi.updateIdentity(current, values),
      "Environment identity saved.",
    );
  }

  async function updateProperties(values: Readonly<Record<string, string | number>>) {
    await mutate(
      (current) => environmentApi.updateProperties(current, values),
      "Environment properties saved.",
    );
  }

  async function changeType(environmentTypeId: string) {
    await mutate(
      (current) => environmentApi.changeType(current, environmentTypeId),
      "Environment type and compatible selections saved.",
    );
  }

  async function selectAsset(asset: EnvironmentAsset) {
    if (!category || !selected) return;
    if (environmentMultiCategories.has(category)) {
      const nextIds = selectedAssetIds.includes(asset.assetId)
        ? selectedAssetIds.filter((id) => id !== asset.assetId)
        : [...selectedAssetIds, asset.assetId];
      await mutate(
        (current) => environmentApi.replace(current, category, nextIds),
        `${asset.name} selection saved.`,
      );
      return;
    }
    if (selectedAssetIds[0] === asset.assetId) {
      await mutate(
        (current) => environmentApi.remove(current, category, asset.assetId),
        `${asset.name} selection removed.`,
      );
      return;
    }
    await mutate(
      (current) => environmentApi.select(current, category, asset.assetId),
      `${asset.name} selected.`,
    );
  }

  async function validateReadiness() {
    await mutate(async (current) => {
      const result = await environmentApi.validate(current);
      setReadinessLoad({
        environmentId: result.environment.environmentId,
        value: await environmentApi.getReadiness(result.environment.environmentId),
      });
      return result;
    }, "Environment readiness recalculated.");
  }

  function setActiveTab(tab: string) {
    setActiveTabState(tab);
    setActiveFilter("all");
  }

  return {
    ownership,
    producer,
    types,
    environments,
    selected,
    selectedId,
    selectedType,
    readiness,
    supportedTabs,
    category,
    assets,
    filterItems,
    selectedAssetIds,
    activeTab,
    activeFilter,
    previewSlide,
    propertiesOpen,
    pending,
    deferredAction,
    status,
    setStatus,
    setPropertiesOpen,
    setPreviewSlide,
    setActiveTab,
    setActiveFilter,
    showDeferred,
    createEnvironment,
    selectEnvironment,
    updateIdentity,
    updateProperties,
    changeType,
    selectAsset,
    validateReadiness,
  };
}

function toProducerProfile(
  profile: AssignedCreativeProfile | undefined,
): ActiveProducerProfile | undefined {
  return profile
    ? {
        producerProfileId: profile.profileId,
        displayName: profile.displayName,
        roleLabel: profile.roleLabel,
        avatarReference: profile.avatarReference,
        status: profile.status,
        shortPrompt: profile.shortPrompt,
        availability: profile.availability,
        providerStatus: profile.providerStatus,
      }
    : undefined;
}

export function formatEnvironmentError(error: unknown) {
  if (error instanceof EnvironmentApiError) {
    return error.conflict
      ? "This Environment changed elsewhere. Canonical state has been reloaded."
      : error.message;
  }
  return error instanceof Error
    ? error.message
    : "The Environment operation could not be completed.";
}
