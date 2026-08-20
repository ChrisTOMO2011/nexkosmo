import { Sparkles } from "lucide-react";
import type { ReactNode } from "react";
import { Button, Card } from "../../../../components/ui";

export type SuggestionPresentation = {
  id: string;
  title: string;
  body: string;
};

type SuggestionsPanelProps<T extends SuggestionPresentation> = {
  suggestions: readonly T[];
  appliedIds: readonly string[];
  renderMedia: (suggestion: T) => ReactNode;
  onApply: (id: string) => void;
  onViewAll: () => void;
  onGenerateMore: () => void;
  title?: string;
  eyebrow?: string;
  generateLabel?: string;
};

export function SuggestionsPanel<T extends SuggestionPresentation>({
  suggestions,
  appliedIds,
  renderMedia,
  onApply,
  onViewAll,
  onGenerateMore,
  title = "SUGGESTIONS",
  eyebrow,
  generateLabel = "More suggestions",
}: SuggestionsPanelProps<T>) {
  return (
    <section className="ai-suggestions" aria-labelledby="ai-suggestions-title">
      <div className="suggestions-heading">
        <h2 id="ai-suggestions-title">
          {eyebrow && <span>{eyebrow}</span>} {title}
        </h2>
        <button type="button" onClick={onViewAll}>
          View all
        </button>
      </div>
      <div className="suggestion-list">
        {suggestions.map((suggestion) => {
          const isApplied = appliedIds.includes(suggestion.id);
          return (
            <Card className="suggestion-card" key={suggestion.id}>
              {renderMedia(suggestion)}
              <div>
                <strong>{suggestion.title}</strong>
                <p>{suggestion.body}</p>
              </div>
              <Button
                className={isApplied ? "is-applied" : ""}
                onClick={() => onApply(suggestion.id)}
              >
                {isApplied ? "Applied" : "Apply"}
              </Button>
            </Card>
          );
        })}
      </div>
      <Button
        className="generate-more-button"
        leadingIcon={<Sparkles aria-hidden="true" />}
        onClick={onGenerateMore}
      >
        {generateLabel}
      </Button>
    </section>
  );
}
