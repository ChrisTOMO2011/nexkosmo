import type { Character } from "./data";
import { DomainSelectionRail, type DomainSelectionItem } from "./shared";

type CharacterRosterProps = {
  characters: Character[];
  selectedId: string;
  onSelect: (id: string) => void;
  onAdd: () => void;
};

type CharacterSelectionItem = DomainSelectionItem & {
  character: Character;
};

export function CharacterRoster({
  characters,
  selectedId,
  onSelect,
  onAdd,
}: CharacterRosterProps) {
  const items: CharacterSelectionItem[] = characters.map((character) => ({
    id: character.id,
    primaryText: character.name,
    secondaryText: character.role,
    thumbnail: (
      <span
        className={`roster-avatar ${character.crop}`}
        aria-hidden="true"
      />
    ),
    character,
  }));

  return (
    <DomainSelectionRail
      label="Characters"
      items={items}
      selectedId={selectedId}
      addLabel="Add Character"
      onSelect={(item) => onSelect(item.character.id)}
      onAdd={onAdd}
    />
  );
}
