export interface HistoricalExecution {
  executionId: string;
  type: string;
  features: Record<string, number>;
  durationMs: number;
  cost: number;
  resourceUsage: Record<string, number>;
  succeeded: boolean;
  bottlenecks?: string[];
  completedAt: string;
}

export interface PredictionRequest {
  predictionId: string;
  objectiveId: string;
  type: string;
  features: Record<string, number>;
  requestedResources?: Record<string, number>;
  deadline?: string;
  budget?: number;
  metadata?: Record<string, unknown>;
}

export interface PredictionRange {
  low: number;
  expected: number;
  high: number;
}

export interface BottleneckPrediction {
  name: string;
  probability: number;
  evidenceCount: number;
}

export interface ProductionPrediction {
  predictionId: string;
  objectiveId: string;
  estimatedDurationMs: PredictionRange;
  estimatedCost: PredictionRange;
  expectedResourceUsage: Record<string, PredictionRange>;
  successProbability: number;
  deadlineProbability?: number;
  budgetProbability?: number;
  predictedBottlenecks: BottleneckPrediction[];
  confidence: number;
  evidenceIds: string[];
  generatedAt: string;
}

export interface PredictionHistoryRepository {
  findComparable(input: {
    type: string;
    features: Record<string, number>;
    limit: number;
  }): Promise<HistoricalExecution[]>;
}

export interface PredictionRepository {
  save(prediction: ProductionPrediction): Promise<void>;
  get(predictionId: string): Promise<ProductionPrediction | null>;
}

export interface PredictionEventBus {
  publish(event: string, payload: Record<string, unknown>): Promise<void>;
}

export interface PredictionEngineOptions {
  evidenceLimit?: number;
  minimumEvidence?: number;
  similarityFloor?: number;
}

interface WeightedExecution {
  execution: HistoricalExecution;
  similarity: number;
  weight: number;
}

export class InsufficientPredictionEvidenceError extends Error {
  constructor(readonly available: number, readonly required: number) {
    super(`Prediction requires at least ${required} comparable executions; found ${available}`);
    this.name = "InsufficientPredictionEvidenceError";
  }
}

export class ProductionPredictionEngine {
  private readonly evidenceLimit: number;
  private readonly minimumEvidence: number;
  private readonly similarityFloor: number;

  constructor(
    private readonly history: PredictionHistoryRepository,
    private readonly predictions: PredictionRepository,
    private readonly events: PredictionEventBus,
    options: PredictionEngineOptions = {},
  ) {
    this.evidenceLimit = options.evidenceLimit ?? 50;
    this.minimumEvidence = options.minimumEvidence ?? 3;
    this.similarityFloor = options.similarityFloor ?? 0.1;
  }

  async predict(request: PredictionRequest): Promise<ProductionPrediction> {
    this.validateRequest(request);

    const comparable = await this.history.findComparable({
      type: request.type,
      features: request.features,
      limit: this.evidenceLimit,
    });

    const weighted = comparable
      .map((execution) => {
        const similarity = this.cosineSimilarity(request.features, execution.features);
        return {
          execution,
          similarity,
          weight: Math.max(similarity, 0),
        };
      })
      .filter((item) => item.similarity >= this.similarityFloor)
      .sort((left, right) => right.similarity - left.similarity);

    if (weighted.length < this.minimumEvidence) {
      throw new InsufficientPredictionEvidenceError(
        weighted.length,
        this.minimumEvidence,
      );
    }

    const durationValues = weighted.map((item) => ({
      value: item.execution.durationMs,
      weight: item.weight,
    }));
    const costValues = weighted.map((item) => ({
      value: item.execution.cost,
      weight: item.weight,
    }));

    const duration = this.range(durationValues);
    const cost = this.range(costValues);
    const resources = this.predictResources(weighted);
    const successProbability = this.weightedMean(
      weighted.map((item) => ({
        value: item.execution.succeeded ? 1 : 0,
        weight: item.weight,
      })),
    );

    const confidence = this.calculateConfidence(weighted);
    const prediction: ProductionPrediction = {
      predictionId: request.predictionId,
      objectiveId: request.objectiveId,
      estimatedDurationMs: duration,
      estimatedCost: cost,
      expectedResourceUsage: resources,
      successProbability: this.clamp(successProbability),
      deadlineProbability: request.deadline
        ? this.probabilityAtOrBelow(
            durationValues,
            Math.max(Date.parse(request.deadline) - Date.now(), 0),
          )
        : undefined,
      budgetProbability:
        typeof request.budget === "number"
          ? this.probabilityAtOrBelow(costValues, request.budget)
          : undefined,
      predictedBottlenecks: this.predictBottlenecks(weighted),
      confidence,
      evidenceIds: weighted.map((item) => item.execution.executionId),
      generatedAt: new Date().toISOString(),
    };

    await this.predictions.save(prediction);
    await this.events.publish("prediction.generated", {
      predictionId: prediction.predictionId,
      objectiveId: prediction.objectiveId,
      confidence: prediction.confidence,
      evidenceCount: prediction.evidenceIds.length,
      successProbability: prediction.successProbability,
    });

    return prediction;
  }

  private predictResources(
    weighted: WeightedExecution[],
  ): Record<string, PredictionRange> {
    const resourceNames = new Set<string>();
    for (const item of weighted) {
      Object.keys(item.execution.resourceUsage).forEach((name) =>
        resourceNames.add(name),
      );
    }

    const result: Record<string, PredictionRange> = {};
    for (const name of resourceNames) {
      result[name] = this.range(
        weighted.map((item) => ({
          value: item.execution.resourceUsage[name] ?? 0,
          weight: item.weight,
        })),
      );
    }
    return result;
  }

  private predictBottlenecks(
    weighted: WeightedExecution[],
  ): BottleneckPrediction[] {
    const totals = new Map<string, { weightedHits: number; evidenceCount: number }>();
    const totalWeight = weighted.reduce((sum, item) => sum + item.weight, 0);

    for (const item of weighted) {
      for (const bottleneck of item.execution.bottlenecks ?? []) {
        const current = totals.get(bottleneck) ?? {
          weightedHits: 0,
          evidenceCount: 0,
        };
        current.weightedHits += item.weight;
        current.evidenceCount += 1;
        totals.set(bottleneck, current);
      }
    }

    return [...totals.entries()]
      .map(([name, value]) => ({
        name,
        probability: totalWeight > 0 ? value.weightedHits / totalWeight : 0,
        evidenceCount: value.evidenceCount,
      }))
      .sort((left, right) => right.probability - left.probability)
      .slice(0, 10);
  }

  private range(values: Array<{ value: number; weight: number }>): PredictionRange {
    const expected = this.weightedMean(values);
    const variance = this.weightedMean(
      values.map((item) => ({
        value: Math.pow(item.value - expected, 2),
        weight: item.weight,
      })),
    );
    const deviation = Math.sqrt(Math.max(variance, 0));

    return {
      low: Math.max(0, expected - deviation),
      expected: Math.max(0, expected),
      high: Math.max(0, expected + deviation),
    };
  }

  private probabilityAtOrBelow(
    values: Array<{ value: number; weight: number }>,
    threshold: number,
  ): number {
    const totalWeight = values.reduce((sum, item) => sum + item.weight, 0);
    if (totalWeight === 0) return 0;

    const matchingWeight = values
      .filter((item) => item.value <= threshold)
      .reduce((sum, item) => sum + item.weight, 0);

    return this.clamp(matchingWeight / totalWeight);
  }

  private calculateConfidence(weighted: WeightedExecution[]): number {
    const evidenceFactor = Math.min(weighted.length / this.evidenceLimit, 1);
    const similarityFactor = this.weightedMean(
      weighted.map((item) => ({
        value: item.similarity,
        weight: item.weight,
      })),
    );
    const outcomeConsistency = 1 - this.binaryVariance(
      weighted.map((item) => ({
        value: item.execution.succeeded ? 1 : 0,
        weight: item.weight,
      })),
    );

    return this.clamp(
      evidenceFactor * 0.35 + similarityFactor * 0.45 + outcomeConsistency * 0.2,
    );
  }

  private binaryVariance(
    values: Array<{ value: number; weight: number }>,
  ): number {
    const mean = this.weightedMean(values);
    return this.clamp(mean * (1 - mean) * 4);
  }

  private weightedMean(values: Array<{ value: number; weight: number }>): number {
    const totalWeight = values.reduce((sum, item) => sum + item.weight, 0);
    if (totalWeight === 0) return 0;
    return (
      values.reduce((sum, item) => sum + item.value * item.weight, 0) /
      totalWeight
    );
  }

  private cosineSimilarity(
    left: Record<string, number>,
    right: Record<string, number>,
  ): number {
    const keys = new Set([...Object.keys(left), ...Object.keys(right)]);
    let dot = 0;
    let leftMagnitude = 0;
    let rightMagnitude = 0;

    for (const key of keys) {
      const leftValue = left[key] ?? 0;
      const rightValue = right[key] ?? 0;
      dot += leftValue * rightValue;
      leftMagnitude += leftValue * leftValue;
      rightMagnitude += rightValue * rightValue;
    }

    if (leftMagnitude === 0 || rightMagnitude === 0) return 0;
    return dot / (Math.sqrt(leftMagnitude) * Math.sqrt(rightMagnitude));
  }

  private validateRequest(request: PredictionRequest): void {
    if (!request.predictionId.trim()) throw new Error("Prediction id is required");
    if (!request.objectiveId.trim()) throw new Error("Objective id is required");
    if (!request.type.trim()) throw new Error("Prediction type is required");
    if (Object.keys(request.features).length === 0) {
      throw new Error("At least one prediction feature is required");
    }
    if (request.deadline && Number.isNaN(Date.parse(request.deadline))) {
      throw new Error("Deadline must be a valid ISO date");
    }
    if (typeof request.budget === "number" && request.budget < 0) {
      throw new Error("Budget cannot be negative");
    }
  }

  private clamp(value: number): number {
    return Math.max(0, Math.min(1, value));
  }
}
