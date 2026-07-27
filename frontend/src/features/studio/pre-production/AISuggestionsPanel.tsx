import { Sparkles } from "lucide-react";
import { suggestions } from "./data";

type AISuggestionsPanelProps = {
  applied: string[];
  onApply: (id: string) => void;
  onPlaceholder: (message: string) => void;
};

export function AISuggestionsPanel({
  applied,
  onApply,
  onPlaceholder,
}: AISuggestionsPanelProps) {
  return (
    <section className="ai-suggestions" aria-labelledby="ai-suggestions-title">
      <div className="suggestions-heading">
        <h2 id="ai-suggestions-title">
          <span>AI</span> SUGGESTIONS
        </h2>
        <button
          type="button"
          onClick={() => onPlaceholder("All AI suggestions placeholder opened.")}
        >
          View all
        </button>
      </div>
      <div className="suggestion-list">
        {suggestions.map((suggestion) => {
          const isApplied = applied.includes(suggestion.id);
          return (
            <article className="suggestion-card" key={suggestion.id}>
              <span
                className={`suggestion-avatar ${suggestion.crop}`}
                aria-hidden="true"
              />
              <div>
                <strong>{suggestion.title}</strong>
                <p>{suggestion.body}</p>
              </div>
              <button
                className={isApplied ? "is-applied" : ""}
                type="button"
                onClick={() => onApply(suggestion.id)}
              >
                {isApplied ? "Applied" : "Apply"}
              </button>
            </article>
          );
        })}
      </div>
      <button
        className="generate-more-button"
        type="button"
        onClick={() => onPlaceholder("AI suggestion generation is a placeholder.")}
      >
        <Sparkles aria-hidden="true" />
        Generate More with AI
      </button>
    </section>
  );
}
