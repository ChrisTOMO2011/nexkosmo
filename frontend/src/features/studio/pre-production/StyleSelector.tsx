import { SelectionGrid } from "../../../components/ui";
import { styles } from "./data";
import { AssetSelectionSection } from "./shared";

type StyleSelectorProps = {
  selected: string;
  onChange: (style: string) => void;
};

export function StyleSelector({ selected, onChange }: StyleSelectorProps) {
  return (
    <AssetSelectionSection
      title="STYLE"
      titleId="style-title"
      className="style-selector"
    >
      <SelectionGrid className="style-grid">
        {styles.map((style, index) => (
          <button
            className={`style-card style-crop-${index + 1} ${selected === style ? "is-selected" : ""}`}
            type="button"
            key={style}
            aria-pressed={selected === style}
            onClick={() => onChange(style)}
          >
            <span>{style}</span>
          </button>
        ))}
      </SelectionGrid>
    </AssetSelectionSection>
  );
}
