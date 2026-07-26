import type { InboxManifest, PipelineContext } from "../../brain/inbox/processor";

export interface CanonicalAssetRecord {
  canonical_asset_id: string;
  uuid: string;
  asset_type: string;
  name: string;
  project?: string;
  owner?: string;
  department?: string;
  source_inbox_item_id: string;
  source_path: string;
  checksum_sha256?: string;
  media_type: string;
  mime_type?: string;
  status: "registered";
  metadata: Record<string, unknown>;
  ai_provenance?: InboxManifest["ai_analysis"];
  relationships: Array<Record<string, unknown>>;
  created_at: string;
  updated_at: string;
}

export interface AssetRegistryRepository {
  findByInboxItemId(inboxItemId: string): Promise<CanonicalAssetRecord | null>;
  findByChecksum(checksum: string): Promise<CanonicalAssetRecord | null>;
  create(record: CanonicalAssetRecord): Promise<void>;
}

export interface AssetGraphWriter {
  upsertAssetNode(record: CanonicalAssetRecord): Promise<void>;
  createSuggestedRelationships(
    sourceAssetId: string,
    relationships: Array<Record<string, unknown>>,
  ): Promise<void>;
}

export interface SearchIndexer {
  indexAsset(record: CanonicalAssetRecord): Promise<void>;
}

export interface AuditWriter {
  append(entry: {
    event: string;
    subject_id: string;
    actor: string;
    occurred_at: string;
    details: Record<string, unknown>;
  }): Promise<void>;
}

export interface CanonicalIdGenerator {
  generate(input: {
    assetType: string;
    project?: string;
    inboxItemId: string;
  }): Promise<{ canonicalAssetId: string; uuid: string }>;
}

export interface RegistrationOptions {
  rejectChecksumDuplicates?: boolean;
  defaultOwner?: string;
  defaultDepartment?: string;
}

export class DuplicateAssetError extends Error {
  constructor(readonly existingAssetId: string) {
    super(`Asset already exists as ${existingAssetId}`);
    this.name = "DuplicateAssetError";
  }
}

export class AssetRegistrationService {
  constructor(
    private readonly repository: AssetRegistryRepository,
    private readonly graph: AssetGraphWriter,
    private readonly search: SearchIndexer,
    private readonly audit: AuditWriter,
    private readonly idGenerator: CanonicalIdGenerator,
    private readonly options: RegistrationOptions = {},
  ) {}

  async register(context: PipelineContext): Promise<string> {
    const { manifest, asset } = context;

    const existingByInbox = await this.repository.findByInboxItemId(
      manifest.inbox_item_id,
    );
    if (existingByInbox) {
      return existingByInbox.canonical_asset_id;
    }

    if (manifest.checksum_sha256) {
      const existingByChecksum = await this.repository.findByChecksum(
        manifest.checksum_sha256,
      );
      if (existingByChecksum && this.options.rejectChecksumDuplicates) {
        throw new DuplicateAssetError(existingByChecksum.canonical_asset_id);
      }
    }

    const assetType =
      manifest.asset_type_hint ?? manifest.media_type ?? "unknown";
    const identity = await this.idGenerator.generate({
      assetType,
      project: manifest.project_hint,
      inboxItemId: manifest.inbox_item_id,
    });
    const timestamp = new Date().toISOString();

    const record: CanonicalAssetRecord = {
      canonical_asset_id: identity.canonicalAssetId,
      uuid: identity.uuid,
      asset_type: assetType,
      name: manifest.original_filename,
      project: manifest.project_hint,
      owner: this.options.defaultOwner,
      department: this.options.defaultDepartment,
      source_inbox_item_id: manifest.inbox_item_id,
      source_path: asset.path,
      checksum_sha256: manifest.checksum_sha256,
      media_type: manifest.media_type,
      mime_type: manifest.mime_type,
      status: "registered",
      metadata: manifest.extracted_metadata ?? {},
      ai_provenance: manifest.ai_analysis,
      relationships: manifest.suggested_relationships ?? [],
      created_at: timestamp,
      updated_at: timestamp,
    };

    await this.repository.create(record);
    await this.graph.upsertAssetNode(record);

    if (record.relationships.length > 0) {
      await this.graph.createSuggestedRelationships(
        record.canonical_asset_id,
        record.relationships,
      );
    }

    await this.search.indexAsset(record);
    await this.audit.append({
      event: "asset.registered",
      subject_id: record.canonical_asset_id,
      actor: "nexkosmo-brain",
      occurred_at: timestamp,
      details: {
        inbox_item_id: manifest.inbox_item_id,
        source_path: asset.path,
        asset_type: assetType,
      },
    });

    return record.canonical_asset_id;
  }
}
