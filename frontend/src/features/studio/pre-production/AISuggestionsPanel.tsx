import { suggestions } from "./data";
import { SuggestionsPanel, type DeferredActionId } from "./shared";

type AISuggestionsPanelProps = {
  applied: string[];
  onApply: (id: string) => void;
  onPlaceholder: (message: string) => void;
  onDeferredAction: (action: DeferredActionId) => void;
};

export function AISuggestionsPanel({
  applied,
  onApply,
  onPlaceholder,
  onDeferredAction,
}: AISuggestionsPanelProps) {
  return (
    <SuggestionsPanel
      suggestions={suggestions}
      appliedIds={applied}
      eyebrow="CURATED"
      generateLabel="More curated presets"
      renderMedia={(suggestion) => (
        <span
          className={`suggestion-avatar ${suggestion.crop}`}
          aria-hidden="true"
        />
      )}
      onApply={onApply}
      onViewAll={() =>
        onPlaceholder("The complete curated preset catalogue is not available in this phase.")
      }
      onGenerateMore={() => onDeferredAction("suggestion-catalogue")}
    />
  );
}
