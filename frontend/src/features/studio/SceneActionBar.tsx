import {
  ChevronDown,
  ChevronRight,
  Cloud,
  Play,
} from "lucide-react";

type SceneActionBarProps = {
  onPreview: () => void;
  onNext: () => void;
};

export function SceneActionBar({
  onPreview,
  onNext,
}: SceneActionBarProps) {
  return (
    <footer className="scene-action-bar">
      <div className="scene-identity">
        <strong>SCENE 12</strong>
        <i aria-label="Scene online" />
        <button type="button" aria-label="Choose scene">
          EXT. CITY STREET — NIGHT
          <ChevronDown aria-hidden="true" />
        </button>
      </div>
      <div className="scene-actions">
        <span className="saved-status">
          <Cloud aria-hidden="true" />
          Saved 2 min ago
        </span>
        <button className="preview-scene-button" type="button" onClick={onPreview}>
          <Play aria-hidden="true" />
          Preview Scene
        </button>
        <button className="next-set-button" type="button" onClick={onNext}>
          Next: Set
          <ChevronRight aria-hidden="true" />
        </button>
      </div>
    </footer>
  );
}
