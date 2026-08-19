import { ChevronDown, ChevronRight, Cloud, Play } from "lucide-react";
import { Button } from "../ui";

type BottomActionBarProps = {
  sceneNumber?: string;
  sceneName?: string;
  saveStatus?: string;
  primaryLabel: string;
  secondaryLabel?: string;
  onPrimary: () => void;
  onSecondary?: () => void;
};

export function BottomActionBar({
  sceneNumber = "SCENE 12",
  sceneName = "EXT. CITY STREET — NIGHT",
  saveStatus = "Saved 2 min ago",
  primaryLabel,
  secondaryLabel = "Preview Scene",
  onPrimary,
  onSecondary,
}: BottomActionBarProps) {
  return (
    <footer className="scene-action-bar">
      <div className="scene-identity">
        <strong>{sceneNumber}</strong>
        <i aria-label="Scene online" />
        <Button className="scene-selector" aria-label="Choose scene">
          {sceneName}
          <ChevronDown aria-hidden="true" />
        </Button>
      </div>
      <div className="scene-actions">
        <span className="saved-status">
          <Cloud aria-hidden="true" />
          {saveStatus}
        </span>
        {onSecondary && (
          <Button
            className="preview-scene-button"
            leadingIcon={<Play aria-hidden="true" />}
            onClick={onSecondary}
          >
            {secondaryLabel}
          </Button>
        )}
        <Button
          className="next-set-button"
          trailingIcon={<ChevronRight aria-hidden="true" />}
          onClick={onPrimary}
        >
          {primaryLabel}
        </Button>
      </div>
    </footer>
  );
}
