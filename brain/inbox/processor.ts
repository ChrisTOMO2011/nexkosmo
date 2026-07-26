export type ProcessStatus =
  | "not_started"
  | "queued"
  | "running"
  | "passed"
  | "failed"
  | "skipped";

export type InboxStatus =
  | "received"
  | "queued"
  | "processing"
  | "needs_review"
  | "approved"
  | "registered"
  | "rejected"
  | "quarantined"
  | "failed";

export interface ProcessState {
  status: ProcessStatus;
  started_at?: string;
  completed_at?: string;
  message?: string;
}

export interface InboxManifest {
  inbox_item_id: string;
  source: string;
  source_reference?: string;
  original_filename: string;
  media_type: string;
  mime_type?: string;
  file_size_bytes?: number;
  checksum_sha256?: string;
  status: InboxStatus;
  received_at: string;
  storage_path: string;
  project_hint?: string;
  asset_type_hint?: string;
  processing: Record<string, ProcessState>;
  extracted_metadata?: Record<string, unknown>;
  ai_analysis?: {
    summary?: string;
    tags?: string[];
    confidence?: number;
    model?: string;
    analysed_at?: string;
  };
  duplicate_matches?: Array<Record<string, unknown>>;
  suggested_relationships?: Array<Record<string, unknown>>;
  review?: {
    required?: boolean;
    assigned_to?: string;
    decision?: "pending" | "approved" | "rejected" | "quarantined";
    comments?: string;
    reviewed_at?: string;
  };
  canonical_asset_id?: string;
  errors?: Array<{
    code: string;
    message: string;
    occurred_at: string;
  }>;
}

export interface InboxAsset {
  path: string;
  bytes?: Uint8Array;
}

export interface PipelineContext {
  asset: InboxAsset;
  manifest: InboxManifest;
}

export interface PipelineServices {
  saveManifest(manifest: InboxManifest): Promise<void>;
  verifyChecksum(context: PipelineContext): Promise<void>;
  scanMalware(context: PipelineContext): Promise<void>;
  extractMetadata(context: PipelineContext): Promise<Record<string, unknown>>;
  generatePreview(context: PipelineContext): Promise<void>;
  analyseWithAI(context: PipelineContext): Promise<InboxManifest["ai_analysis"]>;
  detectDuplicates(context: PipelineContext): Promise<Array<Record<string, unknown>>>;
  discoverRelationships(context: PipelineContext): Promise<Array<Record<string, unknown>>>;
  validate(context: PipelineContext): Promise<void>;
  registerAsset(context: PipelineContext): Promise<string>;
  linkAssetGraph(context: PipelineContext, canonicalAssetId: string): Promise<void>;
  archiveInboxItem(context: PipelineContext): Promise<void>;
}

export interface InboxProcessorOptions {
  requireHumanReview?: boolean;
  stopOnDuplicate?: boolean;
}

class PipelineStepError extends Error {
  constructor(
    readonly code: string,
    message: string,
    readonly cause?: unknown,
  ) {
    super(message);
    this.name = "PipelineStepError";
  }
}

function now(): string {
  return new Date().toISOString();
}

function setStep(
  manifest: InboxManifest,
  step: string,
  patch: Partial<ProcessState>,
): void {
  const current = manifest.processing[step] ?? { status: "not_started" };
  manifest.processing[step] = { ...current, ...patch };
}

export class InboxProcessor {
  constructor(
    private readonly services: PipelineServices,
    private readonly options: InboxProcessorOptions = {},
  ) {}

  async process(asset: InboxAsset, manifest: InboxManifest): Promise<InboxManifest> {
    const context: PipelineContext = { asset, manifest };

    if (manifest.status === "registered") {
      return manifest;
    }

    manifest.status = "processing";
    await this.services.saveManifest(manifest);

    try {
      await this.runStep(context, "checksum_verification", () =>
        this.services.verifyChecksum(context),
      );

      await this.runStep(context, "malware_scan", () =>
        this.services.scanMalware(context),
      );

      manifest.extracted_metadata = await this.runStep(
        context,
        "metadata_extraction",
        () => this.services.extractMetadata(context),
      );

      await this.runStep(context, "thumbnail_generation", () =>
        this.services.generatePreview(context),
      );

      manifest.ai_analysis = await this.runStep(context, "ai_tagging", () =>
        this.services.analyseWithAI(context),
      );

      manifest.duplicate_matches = await this.runStep(
        context,
        "duplicate_detection",
        () => this.services.detectDuplicates(context),
      );

      if (
        this.options.stopOnDuplicate &&
        (manifest.duplicate_matches?.length ?? 0) > 0
      ) {
        manifest.status = "needs_review";
        manifest.review = {
          required: true,
          decision: "pending",
          comments: "Potential duplicate asset detected.",
        };
        await this.services.saveManifest(manifest);
        return manifest;
      }

      manifest.suggested_relationships = await this.runStep(
        context,
        "relationship_discovery",
        () => this.services.discoverRelationships(context),
      );

      await this.runStep(context, "validation", () =>
        this.services.validate(context),
      );

      if (this.options.requireHumanReview && manifest.review?.decision !== "approved") {
        manifest.status = "needs_review";
        manifest.review = {
          ...manifest.review,
          required: true,
          decision: manifest.review?.decision ?? "pending",
        };
        await this.services.saveManifest(manifest);
        return manifest;
      }

      const canonicalAssetId = await this.runStep(
        context,
        "asset_registration",
        () => this.services.registerAsset(context),
      );

      manifest.canonical_asset_id = canonicalAssetId;

      await this.runStep(context, "asset_graph_linking", () =>
        this.services.linkAssetGraph(context, canonicalAssetId),
      );

      await this.runStep(context, "inbox_archival", () =>
        this.services.archiveInboxItem(context),
      );

      manifest.status = "registered";
      await this.services.saveManifest(manifest);
      return manifest;
    } catch (error) {
      const pipelineError =
        error instanceof PipelineStepError
          ? error
          : new PipelineStepError("INBOX_PROCESSING_FAILED", String(error), error);

      manifest.status =
        pipelineError.code === "MALWARE_DETECTED" ? "quarantined" : "failed";
      manifest.errors = [
        ...(manifest.errors ?? []),
        {
          code: pipelineError.code,
          message: pipelineError.message,
          occurred_at: now(),
        },
      ];

      await this.services.saveManifest(manifest);
      throw pipelineError;
    }
  }

  private async runStep<T>(
    context: PipelineContext,
    step: string,
    operation: () => Promise<T>,
  ): Promise<T> {
    setStep(context.manifest, step, {
      status: "running",
      started_at: now(),
      completed_at: undefined,
      message: undefined,
    });
    await this.services.saveManifest(context.manifest);

    try {
      const result = await operation();
      setStep(context.manifest, step, {
        status: "passed",
        completed_at: now(),
      });
      await this.services.saveManifest(context.manifest);
      return result;
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setStep(context.manifest, step, {
        status: "failed",
        completed_at: now(),
        message,
      });
      await this.services.saveManifest(context.manifest);

      throw error instanceof PipelineStepError
        ? error
        : new PipelineStepError(
            `STEP_${step.toUpperCase()}_FAILED`,
            message,
            error,
          );
    }
  }
}
