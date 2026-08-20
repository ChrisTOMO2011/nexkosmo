import {
  CircleDot,
  Eye,
  Fingerprint,
  ScanFace,
  Smile,
  Sparkles,
  UserRound,
} from "lucide-react";
import { DomainEditorTabs } from "./shared";
import { editorTabs } from "./data";

type CharacterEditorTabsProps = {
  activeTab: string;
  onChange: (tab: string) => void;
  tabs?: readonly string[];
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
  tabs = editorTabs,
}: CharacterEditorTabsProps) {
  return (
    <DomainEditorTabs
      activeTab={activeTab}
      onChange={onChange}
      label="Character editor"
      tabs={tabs.map((tab, index) => {
        const Icon = tabIcons[index];
        return { id: tab, label: tab, icon: <Icon aria-hidden="true" /> };
      })}
    />
  );
}
