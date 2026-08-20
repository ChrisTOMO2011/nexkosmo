import {
  Bot,
  ChevronDown,
  ChevronRight,
  CloudUpload,
  Sparkles,
} from "lucide-react";
import type { ApiSpecies } from "../../../brain/characters";
import { AssetGrid } from "../../../components/ui";
import {
  ActionCards,
  FilterPills,
  type DeferredActionId,
} from "./shared";

export const ALL_SPECIES_FILTER_ID = "all";
export const MORE_SPECIES_FILTER_ID = "more";

const featuredSpeciesKeys = [
  "human",
  "elf",
  "orc",
  "robot",
  "dragon",
  "alien",
] as const;

const speciesVisualOrder = [
  ...featuredSpeciesKeys,
  "monkey",
  "demon",
  "goblin",
] as const;

export type SpeciesFilterId =
  | typeof ALL_SPECIES_FILTER_ID
  | typeof MORE_SPECIES_FILTER_ID
  | string;

type SpeciesSelectorProps = {
  activeFilterId: SpeciesFilterId;
  selectedSpeciesId?: string;
  species: readonly ApiSpecies[];
  focusedSpeciesId?: string;
  pendingSpeciesId?: string;
  selectionDisabled?: boolean;
  loading?: boolean;
  error?: string;
  onFilterChange: (filterId: SpeciesFilterId) => void;
  onSpeciesChange: (species: ApiSpecies) => void;
  onSpeciesFocus?: (speciesId?: string) => void;
  onPlaceholder: (message: string) => void;
  onDeferredAction: (action: DeferredActionId) => void;
};

export function SpeciesSelector({
  activeFilterId,
  selectedSpeciesId,
  species,
  focusedSpeciesId,
  pendingSpeciesId,
  selectionDisabled = false,
  loading = false,
  error,
  onFilterChange,
  onSpeciesChange,
  onSpeciesFocus,
  onPlaceholder,
  onDeferredAction,
}: SpeciesSelectorProps) {
  const enabledSpecies = [...species]
    .filter((item) => item.enabled)
    .sort((left, right) => {
      const leftIndex = speciesVisualOrder.indexOf(
        left.key as (typeof speciesVisualOrder)[number],
      );
      const rightIndex = speciesVisualOrder.indexOf(
        right.key as (typeof speciesVisualOrder)[number],
      );
      return (
        (leftIndex === -1 ? speciesVisualOrder.length : leftIndex) -
          (rightIndex === -1 ? speciesVisualOrder.length : rightIndex) ||
        left.name.localeCompare(right.name)
      );
    });
  const featuredSpecies = featuredSpeciesKeys
    .map((key) => enabledSpecies.find((item) => item.key === key))
    .filter((item): item is ApiSpecies => Boolean(item));
  const featuredIds = new Set(featuredSpecies.map((item) => item.speciesId));
  const additionalSpecies = enabledSpecies.filter(
    (item) => !featuredIds.has(item.speciesId),
  );
  const visibleSpecies =
    activeFilterId === ALL_SPECIES_FILTER_ID
      ? enabledSpecies
      : activeFilterId === MORE_SPECIES_FILTER_ID
        ? additionalSpecies
        : enabledSpecies.filter((item) => item.speciesId === activeFilterId);
  const filters = [
    { id: ALL_SPECIES_FILTER_ID, label: "All" },
    ...featuredSpecies.map((item) => ({
      id: item.speciesId,
      label: item.name,
    })),
    {
      id: MORE_SPECIES_FILTER_ID,
      label: "More",
      trailingIcon: <ChevronDown aria-hidden="true" />,
    },
  ];
  const actions = [
    {
      id: "upload",
      label: "Upload",
      description: "Upload Your Own",
      icon: <CloudUpload aria-hidden="true" />,
      status: "deferred" as const,
    },
    {
      id: "generate",
      label: "AI Generate",
      description: "Generate with AI",
      icon: <Sparkles aria-hidden="true" />,
      status: "deferred" as const,
    },
  ];

  return (
    <section
      className="selector-section species-selector"
      aria-labelledby="species-title"
      aria-busy={loading || Boolean(pendingSpeciesId)}
    >
      <h3 id="species-title">SPECIES / TYPE</h3>
      <ActionCards
        className="species-actions"
        actions={actions}
        onActivate={(action) =>
          onDeferredAction(
            action.id === "upload" ? "asset-upload" : "character-generation",
          )
        }
      />

      <FilterPills
        items={filters}
        value={activeFilterId}
        label="Species filters"
        onChange={onFilterChange}
      />

      {loading && (
        <p className="visually-hidden" role="status">
          Loading species.
        </p>
      )}
      {error && (
        <p className="visually-hidden" role="alert">
          {error}
        </p>
      )}

      <AssetGrid className="species-row">
        {visibleSpecies.map((item) => {
          const visualIndex = speciesVisualOrder.indexOf(
            item.key as (typeof speciesVisualOrder)[number],
          );
          const selected = selectedSpeciesId === item.speciesId;
          const focused = focusedSpeciesId === item.speciesId;
          const pending = pendingSpeciesId === item.speciesId;
          return (
            <button
              className={`species-card species-${(visualIndex === -1 ? enabledSpecies.indexOf(item) : visualIndex) + 1} ${selected ? "is-selected" : ""}`}
              type="button"
              key={item.speciesId}
              data-species-id={item.speciesId}
              data-species-key={item.key}
              data-focused={focused}
              data-pending={pending}
              aria-pressed={selected}
              aria-busy={pending}
              disabled={selectionDisabled}
              onFocus={() => onSpeciesFocus?.(item.speciesId)}
              onBlur={() => onSpeciesFocus?.(undefined)}
              onClick={() => onSpeciesChange(item)}
            >
              <span className="species-portrait" aria-hidden="true">
                {item.key === "robot" && <Bot />}
              </span>
              <strong>{item.name}</strong>
            </button>
          );
        })}
        <button
          className="species-next"
          type="button"
          aria-label="Show more species"
          onClick={() => onPlaceholder("More species placeholder opened.")}
        >
          <ChevronRight aria-hidden="true" />
        </button>
      </AssetGrid>
    </section>
  );
}
