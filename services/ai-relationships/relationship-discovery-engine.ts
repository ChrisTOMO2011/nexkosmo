export type RelationshipType =
  | "uses"
  | "depends_on"
  | "variant_of"
  | "belongs_to"
  | "animated_by"
  | "textured_by"
  | "rigged_by"
  | "lit_by"
  | "appears_in"
  | "derived_from"
  | "references"
  | "related_to";

export interface AssetCandidate {
  canonicalAssetId: string;
  assetType: string;
  name: string;
  project?: string;
  metadata?: Record<string, unknown>;
  tags?: string[];
}

export interface RelationshipSuggestion {
  targetAssetId: string;
  relationshipType: RelationshipType;
  confidence: number;
  evidence: string[];
  source: "ai" | "rules" | "hybrid";
  requiresReview: boolean;
}

export interface RelationshipProvider {
  discover(input: {
    source: AssetCandidate;
    candidates: AssetCandidate[];
  }): Promise<RelationshipSuggestion[]>;
}

export interface RelationshipVocabulary {
  isAllowed(sourceAssetType: string, relationshipType: RelationshipType, targetAssetType: string): boolean;
}

export interface RelationshipDiscoveryOptions {
  minimumConfidence?: number;
  autoApproveThreshold?: number;
  maximumSuggestions?: number;
}

export class RelationshipDiscoveryEngine {
  private readonly minimumConfidence: number;
  private readonly autoApproveThreshold: number;
  private readonly maximumSuggestions: number;

  constructor(
    private readonly provider: RelationshipProvider,
    private readonly vocabulary: RelationshipVocabulary,
    options: RelationshipDiscoveryOptions = {},
  ) {
    this.minimumConfidence = options.minimumConfidence ?? 0.6;
    this.autoApproveThreshold = options.autoApproveThreshold ?? 0.9;
    this.maximumSuggestions = options.maximumSuggestions ?? 50;
  }

  async discover(
    source: AssetCandidate,
    candidates: AssetCandidate[],
  ): Promise<RelationshipSuggestion[]> {
    const raw = await this.provider.discover({ source, candidates });

    return raw
      .filter((suggestion) => suggestion.targetAssetId !== source.canonicalAssetId)
      .filter((suggestion) => suggestion.confidence >= this.minimumConfidence)
      .filter((suggestion) => {
        const target = candidates.find(
          (candidate) => candidate.canonicalAssetId === suggestion.targetAssetId,
        );
        return target
          ? this.vocabulary.isAllowed(
              source.assetType,
              suggestion.relationshipType,
              target.assetType,
            )
          : false;
      })
      .map((suggestion) => ({
        ...suggestion,
        requiresReview: suggestion.confidence < this.autoApproveThreshold,
      }))
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, this.maximumSuggestions);
  }

  toManifestRelationships(
    suggestions: RelationshipSuggestion[],
  ): Array<Record<string, unknown>> {
    return suggestions.map((suggestion) => ({
      target_asset_id: suggestion.targetAssetId,
      relationship_type: suggestion.relationshipType,
      confidence: suggestion.confidence,
      evidence: suggestion.evidence,
      source: suggestion.source,
      requires_review: suggestion.requiresReview,
    }));
  }
}
