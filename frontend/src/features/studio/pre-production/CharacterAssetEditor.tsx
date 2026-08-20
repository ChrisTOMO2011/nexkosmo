import { Image } from "lucide-react";
import type { ApiCharacterAsset } from "../../../brain/characters";
import {
  DomainAssetGrid,
  type DomainAssetStatus,
} from "./shared";

type CharacterAssetEditorProps = {
  tab: string;
  assets: readonly ApiCharacterAsset[];
  selectedAssetId?: string;
  onSelect: (asset: ApiCharacterAsset) => void;
};

export function CharacterAssetEditor({
  tab,
  assets,
  selectedAssetId,
  onSelect,
}: CharacterAssetEditorProps) {
  return (
    <DomainAssetGrid
      title={`${tab.toLocaleUpperCase()} PRESETS`}
      titleId="asset-editor-title"
      items={assets}
      selectedId={selectedAssetId}
      getId={(asset) => asset.assetId}
      getItemClassName={(_, index) =>
        `species-card species-${(index % 9) + 1}`
      }
      getLabel={(asset) => asset.name}
      renderMedia={() => (
        <span className="species-portrait" aria-hidden="true">
          <Image />
        </span>
      )}
      getStatus={(asset) => toPresentationStatus(asset.status)}
      getUnavailableReason={(asset) =>
        toPresentationStatus(asset.status) === "unsupported"
          ? `${asset.name} is not compatible with the selected Character.`
          : undefined
      }
      onSelect={onSelect}
      emptyMessage={`No compatible ${tab.toLocaleLowerCase()} presets are available.`}
      sectionClassName="character-asset-editor"
      gridClassName="species-row character-asset-grid"
    />
  );
}

function toPresentationStatus(status: string): DomainAssetStatus {
  return [
    "available",
    "unsupported",
    "deferred",
    "uploading",
    "generating",
    "processing",
    "failed",
  ].includes(status)
    ? (status as DomainAssetStatus)
    : "available";
}
