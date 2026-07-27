export type ConfidenceSubjectType =
  | "assertion"
  | "decision"
  | "prediction"
  | "plan"
  | "workflow"
  | "world-state"
  | "source";

export type ConfidenceDisposition = "accept" | "review" | "reject";

export interface ConfidenceEvidence {
  evidenceId: string;
  sourceId: string;
  supports: boolean;
  weight: number;
  reliability?: number;
  observedAt: string;
  expiresAt?: string;
  metadata?: Record<string, unknown>;
}

export interface SourceReliability {
  sourceId: string;
  reliability: number;
  observations: number;
  correctObservations: number;
  lastEvaluatedAt: string;
  metadata?: Record<string, unknown>;
}

export interface ConfidenceThresholds {
  accept: number;
  review: number;
}

export interface ConfidenceContribution {
  evidenceId: string;
  sourceId: string;
  effectiveWeight: number;
  direction: "support" | "contradict";
  contribution: number;
  decayFactor: number;
  sourceReliability: number;
}

export interface ConfidenceScore {
  scoreId: string;
  subjectId: string;
  subjectType: ConfidenceSubjectType;
  value: number;
  uncertainty: number;
  disposition: ConfidenceDisposition;
  contributors: ConfidenceContribution[];
  version: number;
  calculatedAt: string;
  previousScoreId?: string;
  explanation: string[];
  metadata?: Record<string, unknown>;
}

export interface ConfidenceHistoryEntry {
  scoreId: string;
  subjectId: string;
  value: number;
  uncertainty: number;
  disposition: ConfidenceDisposition;
  version: number;
  calculatedAt: string;
}

export interface ConfidenceCalculationRequest {
  subjectId: string;
  subjectType: ConfidenceSubjectType;
  evidence: ConfidenceEvidence[];
  prior?: number;
  now?: string;
  thresholds?: Partial<ConfidenceThresholds>;
  metadata?: Record<string, unknown>;
}

export interface ConfidencePropagationTarget {
  targetId: string;
  targetType: ConfidenceSubjectType;
  influence: number;
}

export interface ConfidenceRepository {
  saveScore(score: ConfidenceScore): Promise<void>;
  getLatestScore(subjectId: string): Promise<ConfidenceScore | null>;
  getHistory(subjectId: string): Promise<ConfidenceHistoryEntry[]>;
  saveSourceReliability(reliability: SourceReliability): Promise<void>;
  getSourceReliability(sourceId: string): Promise<SourceReliability | null>;
}

export interface ConfidenceEventBus {
  publish(event: string, payload: Record<string, unknown>): Promise<void>;
}

export interface ConfidencePropagationPort {
  applyConfidence(target: ConfidencePropagationTarget, score: ConfidenceScore): Promise<void>;
}

export interface ConfidenceEngineOptions {
  defaultPrior?: number;
  defaultSourceReliability?: number;
  halfLifeHours?: number;
  contradictionPenalty?: number;
  thresholds?: ConfidenceThresholds;
}

export class ConfidenceValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ConfidenceValidationError";
  }
}

export class CanonicalConfidenceEngine {
  private readonly defaultPrior: number;
  private readonly defaultSourceReliability: number;
  private readonly halfLifeHours: number;
  private readonly contradictionPenalty: number;
  private readonly thresholds: ConfidenceThresholds;

  constructor(
    private readonly repository: ConfidenceRepository,
    private readonly propagation: ConfidencePropagationPort,
    private readonly events: ConfidenceEventBus,
    options: ConfidenceEngineOptions = {},
  ) {
    this.defaultPrior = this.clamp(options.defaultPrior ?? 0.5);
    this.defaultSourceReliability = this.clamp(options.defaultSourceReliability ?? 0.5);
    this.halfLifeHours = Math.max(1, options.halfLifeHours ?? 720);
    this.contradictionPenalty = this.clamp(options.contradictionPenalty ?? 0.15);
    this.thresholds = this.validateThresholds(
      options.thresholds ?? { accept: 0.8, review: 0.5 },
    );
  }

  async calculate(request: ConfidenceCalculationRequest): Promise<ConfidenceScore> {
    this.validateRequest(request);

    const now = new Date(request.now ?? new Date().toISOString());
    const previous = await this.repository.getLatestScore(request.subjectId);
    const prior = this.clamp(request.prior ?? previous?.value ?? this.defaultPrior);
    const thresholds = this.validateThresholds({
      accept: request.thresholds?.accept ?? this.thresholds.accept,
      review: request.thresholds?.review ?? this.thresholds.review,
    });

    const contributions: ConfidenceContribution[] = [];
    let logOdds = this.toLogOdds(prior);
    let supportingWeight = 0;
    let contradictingWeight = 0;

    for (const item of request.evidence) {
      const reliabilityRecord = await this.repository.getSourceReliability(item.sourceId);
      const reliability = this.clamp(
        item.reliability ?? reliabilityRecord?.reliability ?? this.defaultSourceReliability,
      );
      const decayFactor = this.decayFactor(item, now);
      const effectiveWeight = this.clamp(item.weight) * reliability * decayFactor;
      const signedContribution = (item.supports ? 1 : -1) * effectiveWeight;

      logOdds += signedContribution;
      if (item.supports) supportingWeight += effectiveWeight;
      else contradictingWeight += effectiveWeight;

      contributions.push({
        evidenceId: item.evidenceId,
        sourceId: item.sourceId,
        effectiveWeight,
        direction: item.supports ? "support" : "contradict",
        contribution: signedContribution,
        decayFactor,
        sourceReliability: reliability,
      });
    }

    const contradiction = Math.min(supportingWeight, contradictingWeight);
    logOdds -= contradiction * this.contradictionPenalty;

    const value = this.clamp(this.fromLogOdds(logOdds));
    const totalEffectiveWeight = contributions.reduce(
      (sum, contribution) => sum + contribution.effectiveWeight,
      0,
    );
    const uncertainty = this.clamp(1 / (1 + totalEffectiveWeight));
    const disposition = this.disposition(value, thresholds);
    const version = (previous?.version ?? 0) + 1;

    const score: ConfidenceScore = {
      scoreId: `confidence:${request.subjectId}:v${version}`,
      subjectId: request.subjectId,
      subjectType: request.subjectType,
      value,
      uncertainty,
      disposition,
      contributors: contributions,
      version,
      calculatedAt: now.toISOString(),
      previousScoreId: previous?.scoreId,
      explanation: this.explain({
        prior,
        value,
        uncertainty,
        supportingWeight,
        contradictingWeight,
        contradiction,
        disposition,
      }),
      metadata: request.metadata,
    };

    await this.repository.saveScore(score);
    await this.events.publish("confidence.score.calculated", {
      scoreId: score.scoreId,
      subjectId: score.subjectId,
      subjectType: score.subjectType,
      value: score.value,
      uncertainty: score.uncertainty,
      disposition: score.disposition,
      version: score.version,
    });

    return score;
  }

  async updateSourceReliability(
    sourceId: string,
    wasCorrect: boolean,
  ): Promise<SourceReliability> {
    if (!sourceId.trim()) throw new ConfidenceValidationError("Source id is required");

    const current = await this.repository.getSourceReliability(sourceId);
    const observations = (current?.observations ?? 0) + 1;
    const correctObservations = (current?.correctObservations ?? 0) + (wasCorrect ? 1 : 0);

    // Beta(1,1) smoothing prevents extreme reliability after very few samples.
    const reliability = (correctObservations + 1) / (observations + 2);
    const record: SourceReliability = {
      sourceId,
      reliability: this.clamp(reliability),
      observations,
      correctObservations,
      lastEvaluatedAt: new Date().toISOString(),
      metadata: current?.metadata,
    };

    await this.repository.saveSourceReliability(record);
    await this.events.publish("confidence.source-reliability.updated", {
      sourceId,
      reliability: record.reliability,
      observations,
      correctObservations,
    });

    return record;
  }

  async propagate(
    score: ConfidenceScore,
    targets: ConfidencePropagationTarget[],
  ): Promise<void> {
    for (const target of targets) {
      if (!target.targetId.trim()) {
        throw new ConfidenceValidationError("Propagation target id is required");
      }
      const influence = this.clamp(target.influence);
      await this.propagation.applyConfidence(
        { ...target, influence },
        { ...score, value: this.clamp(score.value * influence) },
      );
    }

    await this.events.publish("confidence.score.propagated", {
      scoreId: score.scoreId,
      subjectId: score.subjectId,
      targetCount: targets.length,
    });
  }

  combine(
    subjectId: string,
    subjectType: ConfidenceSubjectType,
    scores: ConfidenceScore[],
    weights: number[] = [],
  ): ConfidenceScore {
    if (!subjectId.trim()) throw new ConfidenceValidationError("Subject id is required");
    if (scores.length === 0) {
      throw new ConfidenceValidationError("At least one confidence score is required");
    }
    if (weights.length > 0 && weights.length !== scores.length) {
      throw new ConfidenceValidationError("Weights must match the number of scores");
    }

    const effectiveWeights = scores.map((_, index) => this.clamp(weights[index] ?? 1));
    const totalWeight = effectiveWeights.reduce((sum, weight) => sum + weight, 0);
    if (totalWeight === 0) {
      throw new ConfidenceValidationError("Combined score weights cannot all be zero");
    }

    const value = this.clamp(
      scores.reduce(
        (sum, score, index) => sum + score.value * effectiveWeights[index],
        0,
      ) / totalWeight,
    );
    const uncertainty = this.clamp(
      scores.reduce(
        (sum, score, index) => sum + score.uncertainty * effectiveWeights[index],
        0,
      ) / totalWeight,
    );

    return {
      scoreId: `confidence:${subjectId}:combined:${Date.now()}`,
      subjectId,
      subjectType,
      value,
      uncertainty,
      disposition: this.disposition(value, this.thresholds),
      contributors: scores.flatMap((score) => score.contributors),
      version: 1,
      calculatedAt: new Date().toISOString(),
      explanation: [
        `Combined ${scores.length} confidence scores using weighted averaging.`,
        `Resulting confidence is ${value.toFixed(4)} with uncertainty ${uncertainty.toFixed(4)}.`,
      ],
    };
  }

  async getHistory(subjectId: string): Promise<ConfidenceHistoryEntry[]> {
    if (!subjectId.trim()) throw new ConfidenceValidationError("Subject id is required");
    return this.repository.getHistory(subjectId);
  }

  private decayFactor(item: ConfidenceEvidence, now: Date): number {
    const observedAt = new Date(item.observedAt);
    if (Number.isNaN(observedAt.getTime())) {
      throw new ConfidenceValidationError(`Invalid observedAt for ${item.evidenceId}`);
    }
    if (item.expiresAt && now >= new Date(item.expiresAt)) return 0;

    const ageHours = Math.max(0, (now.getTime() - observedAt.getTime()) / 3_600_000);
    return Math.pow(0.5, ageHours / this.halfLifeHours);
  }

  private disposition(
    value: number,
    thresholds: ConfidenceThresholds,
  ): ConfidenceDisposition {
    if (value >= thresholds.accept) return "accept";
    if (value >= thresholds.review) return "review";
    return "reject";
  }

  private explain(input: {
    prior: number;
    value: number;
    uncertainty: number;
    supportingWeight: number;
    contradictingWeight: number;
    contradiction: number;
    disposition: ConfidenceDisposition;
  }): string[] {
    const explanation = [
      `Started from prior confidence ${input.prior.toFixed(4)}.`,
      `Supporting effective weight: ${input.supportingWeight.toFixed(4)}.`,
      `Contradicting effective weight: ${input.contradictingWeight.toFixed(4)}.`,
    ];
    if (input.contradiction > 0) {
      explanation.push(
        `Applied contradiction penalty to overlapping weight ${input.contradiction.toFixed(4)}.`,
      );
    }
    explanation.push(
      `Final confidence is ${input.value.toFixed(4)} with uncertainty ${input.uncertainty.toFixed(4)}.`,
      `Threshold disposition: ${input.disposition}.`,
    );
    return explanation;
  }

  private validateRequest(request: ConfidenceCalculationRequest): void {
    if (!request.subjectId.trim()) {
      throw new ConfidenceValidationError("Subject id is required");
    }
    const evidenceIds = new Set<string>();
    for (const item of request.evidence) {
      if (!item.evidenceId.trim() || !item.sourceId.trim()) {
        throw new ConfidenceValidationError("Evidence and source ids are required");
      }
      if (evidenceIds.has(item.evidenceId)) {
        throw new ConfidenceValidationError(`Duplicate evidence id: ${item.evidenceId}`);
      }
      evidenceIds.add(item.evidenceId);
      if (!Number.isFinite(item.weight)) {
        throw new ConfidenceValidationError(`Invalid weight for ${item.evidenceId}`);
      }
    }
  }

  private validateThresholds(thresholds: ConfidenceThresholds): ConfidenceThresholds {
    const accept = this.clamp(thresholds.accept);
    const review = this.clamp(thresholds.review);
    if (review > accept) {
      throw new ConfidenceValidationError("Review threshold cannot exceed accept threshold");
    }
    return { accept, review };
  }

  private toLogOdds(probability: number): number {
    const bounded = Math.max(0.000001, Math.min(0.999999, probability));
    return Math.log(bounded / (1 - bounded));
  }

  private fromLogOdds(logOdds: number): number {
    return 1 / (1 + Math.exp(-logOdds));
  }

  private clamp(value: number): number {
    if (!Number.isFinite(value)) return 0;
    return Math.max(0, Math.min(1, value));
  }
}
