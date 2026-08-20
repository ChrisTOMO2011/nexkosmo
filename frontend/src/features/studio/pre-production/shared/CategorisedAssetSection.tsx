import type { ReactNode } from "react";
import { Tabs } from "../../../../components/ui";
import type { DomainTab } from "./domain-workspace.types";

type CategorisedAssetSectionProps = {
  label: string;
  tabsLabel?: string;
  tabs: readonly DomainTab[];
  activeTab: string;
  className: string;
  tabsClassName: string;
  headerAdornment?: ReactNode;
  children: ReactNode;
  onTabChange: (id: string) => void;
};

export function CategorisedAssetSection({
  label,
  tabsLabel,
  tabs,
  activeTab,
  className,
  tabsClassName,
  headerAdornment,
  children,
  onTabChange,
}: CategorisedAssetSectionProps) {
  return (
    <section className={className} aria-label={label}>
      <div className="accessory-tabs-wrap">
        <Tabs
          className={tabsClassName}
          items={tabs}
          value={activeTab}
          onChange={onTabChange}
          label={tabsLabel ?? `${label} categories`}
        />
        {headerAdornment}
      </div>
      {children}
    </section>
  );
}
