import { Plus } from "lucide-react";
import { Button } from "../../../components/ui";
import type { Character } from "./data";

type CharacterRosterProps = {
  characters: Character[];
  selectedId: string;
  onSelect: (id: string) => void;
  onAdd: () => void;
};

export function CharacterRoster({
  characters,
  selectedId,
  onSelect,
  onAdd,
}: CharacterRosterProps) {
  return (
    <aside className="character-roster" aria-label="Characters">
      <div className="roster-list">
        {characters.map((character) => (
          <Button
            className={`roster-card ${selectedId === character.id ? "is-selected" : ""}`}
            key={character.id}
            aria-label={`${character.name}, ${character.role}`}
            aria-pressed={selectedId === character.id}
            onClick={() => onSelect(character.id)}
          >
            <span
              className={`roster-avatar ${character.crop}`}
              aria-hidden="true"
            />
            <span className="roster-copy">
              <strong>{character.name}</strong>
              <small>{character.role}</small>
            </span>
            {selectedId === character.id && <i className="roster-status" />}
          </Button>
        ))}
      </div>
      <Button
        className="add-character"
        leadingIcon={<Plus aria-hidden="true" />}
        onClick={onAdd}
      >
        Add Character
      </Button>
    </aside>
  );
}
