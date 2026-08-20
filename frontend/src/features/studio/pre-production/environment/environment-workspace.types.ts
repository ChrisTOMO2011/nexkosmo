import type {
  Environment,
  EnvironmentAsset,
  EnvironmentReadiness,
  EnvironmentType,
} from "../../../../brain/environments";
import type { ActiveProducerProfile, DeferredActionId } from "../shared";

export type EnvironmentOwnership = Readonly<{
  projectId: string;
  productionId: string;
}>;

export type EnvironmentAssetCache = Readonly<{
  environmentId: string;
  category?: string;
  filter: string;
  items: readonly EnvironmentAsset[];
}>;

export type EnvironmentWorkspaceController = Readonly<{
  ownership?: EnvironmentOwnership;
  producer?: ActiveProducerProfile;
  types: readonly EnvironmentType[];
  environments: readonly Environment[];
  selected?: Environment;
  selectedId: string;
  selectedType?: EnvironmentType;
  readiness?: EnvironmentReadiness;
  supportedTabs: readonly string[];
  category?: string;
  assets: readonly EnvironmentAsset[];
  filterItems: readonly Readonly<{ id: string; label: string }>[];
  selectedAssetIds: readonly string[];
  activeTab: string;
  activeFilter: string;
  previewSlide: number;
  propertiesOpen: boolean;
  pending: boolean;
  deferredAction: DeferredActionId | null;
  status: string;
  setStatus(message: string): void;
  setPropertiesOpen(open: boolean): void;
  setPreviewSlide(index: number): void;
  setActiveTab(tab: string): void;
  setActiveFilter(filter: string): void;
  showDeferred(action: DeferredActionId): void;
  createEnvironment(): Promise<void>;
  selectEnvironment(environmentId: string): void;
  updateIdentity(values: Readonly<{ display_name?: string; description?: string }>): Promise<void>;
  updateProperties(values: Readonly<Record<string, string | number>>): Promise<void>;
  changeType(environmentTypeId: string): Promise<void>;
  selectAsset(asset: EnvironmentAsset): Promise<void>;
  validateReadiness(): Promise<void>;
}>;
