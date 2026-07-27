import {
  CircleDot,
  Eye,
  Fingerprint,
  ScanFace,
  Smile,
  Sparkles,
  UserRound,
} from "lucide-react";
import { editorTabs } from "./data";

type CharacterEditorTabsProps = {
  activeTab: string;
  onChange: (tab: string) => void;
};

const tabIcons = [
  UserRound,
  ScanFace,
  Sparkles,
  Fingerprint,
  Eye,
  Smile,
  CircleDot,
  Smile,
];

export function CharacterEditorTabs({
  activeTab,
  onChange,
}: CharacterEditorTabsProps) {
  return (
    <div className="editor-tabs" role="tablist" aria-label="Character editor">
      {editorTabs.map((tab, index) => {
        const Icon = tabIcons[index];
        return (
          <button
            className={activeTab === tab ? "is-active" : ""}
            type="button"
            role="tab"
            aria-selected={activeTab === tab}
            key={tab}
            onClick={() => onChange(tab)}
          >
            <Icon aria-hidden="true" />
            <span>{tab}</span>
          </button>
        );
      })}
    </div>
  );
}
