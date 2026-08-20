import type { ReactNode } from "react";
import { InspectorPanel } from "../../../../components/studio";
import type { TabItem } from "../../../../components/ui";

type DomainInspectorPanelProps = {
  tabs: readonly TabItem[];
  activeTab: string;
  onTabChange: (tab: string) => void;
  children: ReactNode;
  className?: string;
};

export function DomainInspectorPanel({
  tabs,
  activeTab,
  onTabChange,
  children,
  className = "properties-card",
}: DomainInspectorPanelProps) {
  return (
    <InspectorPanel
      className={className}
      tabs={tabs}
      activeTab={activeTab}
      onTabChange={onTabChange}
    >
      {children}
    </InspectorPanel>
  );
}
