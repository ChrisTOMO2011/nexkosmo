import { Tabs, type TabItem } from "../../../../components/ui";

type DomainEditorTabsProps = {
  activeTab: string;
  tabs: readonly TabItem[];
  label: string;
  onChange: (tab: string) => void;
  className?: string;
};

export function DomainEditorTabs({
  activeTab,
  tabs,
  label,
  onChange,
  className = "editor-tabs",
}: DomainEditorTabsProps) {
  return (
    <Tabs
      className={className}
      label={label}
      value={activeTab}
      onChange={onChange}
      items={tabs}
    />
  );
}
