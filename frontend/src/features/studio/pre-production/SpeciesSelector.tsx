import {
  Bot,
  ChevronDown,
  ChevronRight,
  CloudUpload,
  Sparkles,
} from "lucide-react";
import { species, speciesFilters } from "./data";

type SpeciesSelectorProps = {
  activeFilter: string;
  selectedSpecies: string;
  onFilterChange: (filter: string) => void;
  onSpeciesChange: (species: string) => void;
  onPlaceholder: (message: string) => void;
};

export function SpeciesSelector({
  activeFilter,
  selectedSpecies,
  onFilterChange,
  onSpeciesChange,
  onPlaceholder,
}: SpeciesSelectorProps) {
  return (
    <section
      className="selector-section species-selector"
      aria-labelledby="species-title"
    >
      <h3 id="species-title">SPECIES / TYPE</h3>
      <div className="species-actions">
        <button
          type="button"
          onClick={() => onPlaceholder("Species upload placeholder opened.")}
        >
          <CloudUpload aria-hidden="true" />
          <span>
            <strong>Upload</strong>
            <small>Upload Your Own</small>
          </span>
        </button>
        <button
          type="button"
          onClick={() => onPlaceholder("AI species generation is a placeholder.")}
        >
          <Sparkles aria-hidden="true" />
          <span>
            <strong>AI Generate</strong>
            <small>Generate with AI</small>
          </span>
        </button>
      </div>

      <div className="filter-row" aria-label="Species filters">
        {speciesFilters.map((filter) => (
          <button
            className={activeFilter === filter ? "is-active" : ""}
            type="button"
            key={filter}
            aria-pressed={activeFilter === filter}
            onClick={() => onFilterChange(filter)}
          >
            {filter}
            {filter === "More" && <ChevronDown aria-hidden="true" />}
          </button>
        ))}
      </div>

      <div className="species-row">
        {species.map((item, index) => (
          <button
            className={`species-card species-${index + 1} ${selectedSpecies === item ? "is-selected" : ""}`}
            type="button"
            key={item}
            aria-pressed={selectedSpecies === item}
            onClick={() => onSpeciesChange(item)}
          >
            <span className="species-portrait" aria-hidden="true">
              {item === "Robot" && <Bot />}
            </span>
            <strong>{item}</strong>
          </button>
        ))}
        <button
          className="species-next"
          type="button"
          aria-label="Show more species"
          onClick={() => onPlaceholder("More species placeholder opened.")}
        >
          <ChevronRight aria-hidden="true" />
        </button>
      </div>
    </section>
  );
}
