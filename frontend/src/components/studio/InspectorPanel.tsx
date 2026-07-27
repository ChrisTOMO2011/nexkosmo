import type { ReactNode } from "react";
import { Panel, Tabs, type TabItem } from "../ui";

type InspectorPanelProps = {
  title?: string;
  tabs?: readonly TabItem[];
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  children: ReactNode;
  className?: string;
};

export function InspectorPanel({
  title,
  tabs,
  activeTab,
  onTabChange,
  children,
  className = "",
}: InspectorPanelProps) {
  return (
    <Panel className={`inspector-panel ${className}`.trim()} title={title}>
      {tabs && activeTab && onTabChange && (
        <Tabs
          className="properties-tabs"
          items={tabs}
          value={activeTab}
          onChange={onTabChange}
          label="Inspector panels"
        />
      )}
      {children}
    </Panel>
  );
}
