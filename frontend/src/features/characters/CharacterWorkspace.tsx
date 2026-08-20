import { type FormEvent, useEffect, useState } from "react";
import { api, type Character } from "../../api/client";
import type { AuthSession } from "../../auth/session";
import { Button, Panel } from "../../components/ui";

type Props = { session: AuthSession; projectId: string };

export function CharacterWorkspace({ session, projectId }: Props) {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selected, setSelected] = useState<Character | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [roleLabel, setRoleLabel] = useState("");
  const [status, setStatus] = useState("Loading Characters…");

  const reload = async () => {
    try {
      const result = await api.listCharacters(session, projectId);
      setCharacters(result);
      setStatus(result.length ? "" : "No Characters have been created.");
    } catch (reason) {
      setStatus((reason as Error).message);
    }
  };

  useEffect(() => {
    let active = true;
    void api
      .listCharacters(session, projectId)
      .then((result) => {
        if (!active) return;
        setCharacters(result);
        setStatus(result.length ? "" : "No Characters have been created.");
      })
      .catch((reason: Error) => {
        if (active) setStatus(reason.message);
      });
    return () => {
      active = false;
    };
  }, [projectId, session]);

  const choose = async (characterId: string) => {
    try {
      const character = await api.getCharacter(session, projectId, characterId);
      setSelected(character);
      setDisplayName(character.display_name);
      setRoleLabel(character.role_label || "");
    } catch (reason) {
      setStatus((reason as Error).message);
    }
  };

  const save = async (event: FormEvent) => {
    event.preventDefault();
    try {
      if (selected) {
        const updated = await api.updateCharacter(
          session,
          projectId,
          selected,
          displayName.trim(),
          roleLabel.trim(),
        );
        setSelected(updated);
      } else {
        await api.createCharacter(
          session,
          projectId,
          displayName.trim(),
          roleLabel.trim(),
        );
        setDisplayName("");
        setRoleLabel("");
      }
      await reload();
      setStatus("Character saved.");
    } catch (reason) {
      setStatus((reason as Error).message);
    }
  };

  return (
    <Panel className="character-workspace" aria-labelledby="character-title">
      <header>
        <div>
          <span className="stage-placeholder__eyebrow">BUILD · Character foundation</span>
          <h1 id="character-title">Characters</h1>
        </div>
        <a href="/studio">Change Project</a>
      </header>
      <div className="character-workspace__grid">
        <section aria-label="Character list">
          <h2>Project Characters</h2>
          {status && <p role="status">{status}</p>}
          <ul>
            {characters.map((character) => (
              <li key={character.character_id}>
                <button type="button" onClick={() => void choose(character.character_id)}>
                  <strong>{character.display_name}</strong>
                  <span>{character.role_label || "No role"}</span>
                </button>
              </li>
            ))}
          </ul>
        </section>
        <form onSubmit={(event) => void save(event)}>
          <h2>{selected ? "Edit Character" : "Create Character"}</h2>
          <label htmlFor="character-name">Display name</label>
          <input
            id="character-name"
            required
            maxLength={160}
            value={displayName}
            onChange={(event) => setDisplayName(event.target.value)}
          />
          <label htmlFor="character-role">Role</label>
          <input
            id="character-role"
            maxLength={160}
            value={roleLabel}
            onChange={(event) => setRoleLabel(event.target.value)}
          />
          <div>
            <Button type="submit" variant="outlined">
              {selected ? "Save Character" : "Create Character"}
            </Button>
            {selected && (
              <Button
                onClick={() => {
                  setSelected(null);
                  setDisplayName("");
                  setRoleLabel("");
                }}
              >
                New Character
              </Button>
            )}
          </div>
        </form>
      </div>
    </Panel>
  );
}
