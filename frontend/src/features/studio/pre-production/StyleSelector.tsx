import { Check } from "lucide-react";
import { styles } from "./data";

type StyleSelectorProps = {
  selected: string;
  onChange: (style: string) => void;
};

export function StyleSelector({ selected, onChange }: StyleSelectorProps) {
  return (
    <section className="selector-section style-selector" aria-labelledby="style-title">
      <h3 id="style-title">STYLE</h3>
      <div className="style-grid">
        {styles.map((style, index) => (
          <button
            className={`style-card style-crop-${index + 1} ${selected === style ? "is-selected" : ""}`}
            type="button"
            key={style}
            aria-pressed={selected === style}
            onClick={() => onChange(style)}
          >
            {selected === style && (
              <span className="selection-check">
                <Check aria-hidden="true" />
              </span>
            )}
            <span>{style}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
