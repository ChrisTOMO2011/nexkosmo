import { Sparkles } from "lucide-react";
import { Button, Card } from "../../../components/ui";
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
            <Card className="suggestion-card" key={suggestion.id}>
              <span
                className={`suggestion-avatar ${suggestion.crop}`}
                aria-hidden="true"
              />
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
        onClick={() => onPlaceholder("AI suggestion generation is a placeholder.")}
      >
        Generate More with AI
      </Button>
    </section>
  );
}
