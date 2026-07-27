import {
  CircleDot,
  Eye,
  Fingerprint,
  ScanFace,
  Smile,
  Sparkles,
  UserRound,
} from "lucide-react";
import { Tabs } from "../../../components/ui";
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
    <Tabs
      className="editor-tabs"
      label="Character editor"
      value={activeTab}
      onChange={onChange}
      items={editorTabs.map((tab, index) => {
        const Icon = tabIcons[index];
        return { id: tab, label: tab, icon: <Icon aria-hidden="true" /> };
      })}
    />
  );
}
