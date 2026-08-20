import type { ReactNode } from "react";

export type PreProductionDomainId =
  | "characters"
  | "environment"
  | "camera-gear"
  | "lighting"
  | "audio"
  | "vfx"
  | "props"
  | "vehicles";

export type DomainAssetStatus =
  | "available"
  | "unsupported"
  | "deferred"
  | "uploading"
  | "generating"
  | "processing"
  | "failed";

export type DomainAssetCard = Readonly<{
  id: string;
  name: string;
  category: string;
  thumbnailReference?: string;
  selected: boolean;
  compatible: boolean;
  status: DomainAssetStatus;
}>;

export type DomainTab = Readonly<{
  id: string;
  label: string;
  icon?: ReactNode;
  disabled?: boolean;
}>;

export type ProducerProfileStatus = "active" | "unavailable" | "deferred";

export type ActiveProducerProfile = Readonly<{
  producerProfileId: string;
  displayName: string;
  roleLabel: string;
  avatarReference?: string;
  status: ProducerProfileStatus;
  shortPrompt?: string;
  availability?: string;
  providerStatus?: string;
}>;

export type ProducerContextMetadata = Readonly<{
  domain: PreProductionDomainId;
  projectId: string;
  productionId?: string;
  entityId?: string;
  activeTab?: string;
  readinessStatus?: string;
  details?: Readonly<Record<string, string>>;
}>;
