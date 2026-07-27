import {
  ChevronDown,
  CloudUpload,
  Ellipsis,
  Glasses,
  Sparkles,
} from "lucide-react";
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
      <div className="accessory-tabs" role="tablist" aria-label="Accessory categories">
        {accessoryTabs.map((tab) => (
          <button
            className={activeTab === tab ? "is-active" : ""}
            type="button"
            role="tab"
            aria-selected={activeTab === tab}
            key={tab}
            onClick={() => onTabChange(tab)}
          >
            {tab}
          </button>
        ))}
        <span className="accessory-dropdowns" aria-hidden="true">
          <ChevronDown />
          <ChevronDown />
        </span>
      </div>

      <div className="glasses-row">
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
      </div>
    </section>
  );
}
