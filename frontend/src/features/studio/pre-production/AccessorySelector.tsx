import {
  ChevronDown,
  CloudUpload,
  Ellipsis,
  Glasses,
  Sparkles,
} from "lucide-react";
import { AssetGrid, Tabs } from "../../../components/ui";
import { accessoryTabs, glasses } from "./data";

type AccessorySelectorProps = {
  activeTab: string;
  selectedAccessory: string;
  onTabChange: (tab: string) => void;
  onAccessoryChange: (item: string) => void;
  onPlaceholder: (message: string) => void;
};

export function AccessorySelector({
  activeTab,
  selectedAccessory,
  onTabChange,
  onAccessoryChange,
  onPlaceholder,
}: AccessorySelectorProps) {
  return (
    <section className="accessory-selector" aria-label="Character accessories">
      <div className="accessory-tabs-wrap">
        <Tabs
          className="accessory-tabs"
          items={accessoryTabs.map((tab) => ({ id: tab, label: tab }))}
          value={activeTab}
          onChange={onTabChange}
          label="Accessory categories"
        />
        <span className="accessory-dropdowns" aria-hidden="true">
          <ChevronDown />
          <ChevronDown />
        </span>
      </div>

      <AssetGrid className="glasses-row">
        {glasses.map((item, index) => {
          const Icon =
            index === 0
              ? CloudUpload
              : index === 1
                ? Sparkles
                : item === "More"
                  ? Ellipsis
                  : Glasses;
          return (
            <button
              className={`glasses-card glasses-${index + 1} ${selectedAccessory === item ? "is-selected" : ""}`}
              type="button"
              key={item}
              aria-pressed={selectedAccessory === item}
              onClick={() => {
                onAccessoryChange(item);
                if (index < 2) {
                  onPlaceholder(
                    item === "Upload"
                      ? "Accessory upload placeholder opened."
                      : "AI accessory generation is a placeholder.",
                  );
                }
              }}
            >
              <Icon aria-hidden="true" />
              <span>{item}</span>
            </button>
          );
        })}
      </AssetGrid>
    </section>
  );
}
