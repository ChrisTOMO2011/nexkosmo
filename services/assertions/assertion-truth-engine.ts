export type AssertionStatus =
  | "proposed"
  | "accepted"
  | "rejected"
  | "contested"
  | "superseded"
  | "revoked";

export type TruthState =
  | "true"
  | "false"
  | "uncertain"
  | "contested"
  | "unknown";

export interface AssertionRecord {
  assertionId: string;
  subjectId: string;
  predicate: string;
  object: unknown;
  status: AssertionStatus;
  truthState: TruthState;
  confidence: number;
  version: number;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  supersedesAssertionId?: string;
  evidenceIds: string[];
  policyDecisionIds?: string[];
  metadata?: Record<string, unknown>;
}

export interface AssertionEvaluation {
  assertionId: string;
  truthState: TruthState;
  confidence: number;
  supportScore: number;
  contradictionScore: number;
  evidenceIds: string[];
  conflictingAssertionIds: string[];
  policyAllowed: boolean;
  explanation: string;
  evaluatedAt: string;
}

export interface CanonicalTruth {
  truthId: string;
  subjectId: string;
  predicate: string;
  assertionId: string;
  value: unknown;
  truthState: TruthState;
  confidence: number;
  establishedAt: string;
  updatedAt: string;
  version: number;
  evidenceIds: string[];
  explanation: string;
}

export interface AssertionHistoryEntry {
  historyId: string;
  assertionId: string;
  previousStatus?: AssertionStatus;
  nextStatus: AssertionStatus;
  previousTruthState?: TruthState;
  nextTruthState: TruthState;
  previousConfidence?: number;
  nextConfidence: number;
  actorId: string;
  reason: string;
  occurredAt: string;
}

export interface EvidenceAssessmentPort {
  assessAssertion(assertionId: string): Promise<{
    supportScore: number;
    contradictionScore: number;
    netConfidence: number;
    supportingEvidenceIds: string[];
    contradictingEvidenceIds: string[];
    staleEvidenceIds: string[];
    revokedEvidenceIds: string[];
    explanation: string;
  }>;
}

export interface PolicyEvaluationPort {
  evaluate(context: Record<string, unknown>): Promise<{
    allowed: boolean;
    violations: string[];
    explanation: string;
    decisionId?: string;
  }>;
}

export interface AssertionRepository {
  getAssertion(assertionId: string): Promise<AssertionRecord | null>;
  listAssertionsBySubject(subjectId: string): Promise<AssertionRecord[]>;
  listAssertionsByFact(subjectId: string, predicate: string): Promise<AssertionRecord[]>;
  saveAssertion(assertion: AssertionRecord): Promise<void>;
  updateAssertion(assertion: AssertionRecord): Promise<void>;
  appendHistory(entry: AssertionHistoryEntry): Promise<void>;
  getCanonicalTruth(subjectId: string, predicate: string): Promise<CanonicalTruth | null>;
  saveCanonicalTruth(truth: CanonicalTruth): Promise<void>;
}

export interface AssertionEventBus {
  publish(event: string, payload: Record<string, unknown>): Promise<void>;
}

export interface AssertionTruthEngineOptions {
  acceptanceThreshold?: number;
  rejectionThreshold?: number;
  contestThreshold?: number;
  minimumPolicyConfidence?: number;
}

export class AssertionTruthIntegrityError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AssertionTruthIntegrityError";
  }
}

export class AssertionTruthEngine {
  private readonly acceptanceThreshold: number;
  private readonly rejectionThreshold: number;
  private readonly contestThreshold: number;
  private readonly minimumPolicyConfidence: number;

  constructor(
    private readonly repository: AssertionRepository,
    private readonly evidence: EvidenceAssessmentPort,
    private readonly policy: PolicyEvaluationPort,
    private readonly events: AssertionEventBus,
    options: AssertionTruthEngineOptions = {},
  ) {
    this.acceptanceThreshold = options.acceptanceThreshold ?? 0.72;
    this.rejectionThreshold = options.rejectionThreshold ?? 0.72;
    this.contestThreshold = options.contestThreshold ?? 0.35;
    this.minimumPolicyConfidence = options.minimumPolicyConfidence ?? 0.5;
  }

  async proposeAssertion(
    assertion: AssertionRecord,
  ): Promise<AssertionRecord> {
    this.validateAssertion(assertion);

    const existing = await this.repository.getAssertion(assertion.assertionId);
    if (existing) {
      throw new AssertionTruthIntegrityError(
        `Assertion ${assertion.assertionId} already exists`,
      );
    }

    if (assertion.supersedesAssertionId) {
      const superseded = await this.repository.getAssertion(
        assertion.supersedesAssertionId,
      );
      if (!superseded) {
        throw new AssertionTruthIntegrityError(
          `Superseded assertion ${assertion.supersedesAssertionId} was not found`,
        );
      }
      await this.transitionAssertion(
        superseded,
        "superseded",
        superseded.truthState,
        superseded.confidence,
        assertion.createdBy,
        `Superseded by assertion ${assertion.assertionId}`,
      );
    }

    const record: AssertionRecord = {
      ...assertion,
      status: "proposed",
      truthState: "unknown",
      confidence: this.clamp(assertion.confidence),
      version: Math.max(1, assertion.version),
      evidenceIds: [...new Set(assertion.evidenceIds)],
      updatedAt: assertion.updatedAt || assertion.createdAt,
    };

    await this.repository.saveAssertion(record);
    await this.repository.appendHistory({
      historyId: this.historyId(record.assertionId),
      assertionId: record.assertionId,
      nextStatus: record.status,
      nextTruthState: record.truthState,
      nextConfidence: record.confidence,
      actorId: record.createdBy,
      reason: "Assertion proposed",
      occurredAt: new Date().toISOString(),
    });

    await this.events.publish("assertion.proposed", {
      assertionId: record.assertionId,
      subjectId: record.subjectId,
      predicate: record.predicate,
      version: record.version,
    });

    return record;
  }

  async evaluateAssertion(assertionId: string): Promise<AssertionEvaluation> {
    const assertion = await this.requireAssertion(assertionId);

    if (assertion.status === "revoked" || assertion.status === "superseded") {
      return {
        assertionId,
        truthState: assertion.truthState,
        confidence: assertion.confidence,
        supportScore: 0,
        contradictionScore: 0,
        evidenceIds: assertion.evidenceIds,
        conflictingAssertionIds: [],
        policyAllowed: false,
        explanation: `Assertion is ${assertion.status} and cannot become canonical.`,
        evaluatedAt: new Date().toISOString(),
      };
    }

    const [assessment, policyDecision, factAssertions] = await Promise.all([
      this.evidence.assessAssertion(assertionId),
      this.policy.evaluate({
        action: "evaluate-assertion",
        assertionId,
        subjectId: assertion.subjectId,
        predicate: assertion.predicate,
        object: assertion.object,
        confidence: assertion.confidence,
      }),
      this.repository.listAssertionsByFact(
        assertion.subjectId,
        assertion.predicate,
      ),
    ]);

    const conflicts = factAssertions.filter(
      (candidate) =>
        candidate.assertionId !== assertion.assertionId &&
        candidate.status !== "revoked" &&
        candidate.status !== "superseded" &&
        !this.valuesEqual(candidate.object, assertion.object),
    );

    const weightedConflict = conflicts.reduce(
      (maximum, candidate) => Math.max(maximum, candidate.confidence),
      0,
    );

    const effectiveContradiction = this.clamp(
      Math.max(assessment.contradictionScore, weightedConflict),
    );
    const effectiveSupport = this.clamp(assessment.supportScore);
    const confidence = this.clamp(
      assessment.netConfidence * (1 - weightedConflict * 0.5),
    );

    let truthState: TruthState = "uncertain";
    let nextStatus: AssertionStatus = "proposed";

    if (!policyDecision.allowed || confidence < this.minimumPolicyConfidence) {
      truthState = "uncertain";
      nextStatus = "rejected";
    } else if (
      effectiveSupport >= this.acceptanceThreshold &&
      effectiveContradiction < this.contestThreshold &&
      conflicts.length === 0
    ) {
      truthState = "true";
      nextStatus = "accepted";
    } else if (
      effectiveContradiction >= this.rejectionThreshold &&
      effectiveSupport < this.contestThreshold
    ) {
      truthState = "false";
      nextStatus = "rejected";
    } else if (
      conflicts.length > 0 ||
      (effectiveSupport >= this.contestThreshold &&
        effectiveContradiction >= this.contestThreshold)
    ) {
      truthState = "contested";
      nextStatus = "contested";
    }

    const evidenceIds = [
      ...new Set([
        ...assertion.evidenceIds,
        ...assessment.supportingEvidenceIds,
        ...assessment.contradictingEvidenceIds,
      ]),
    ];

    const explanation = this.buildExplanation({
      truthState,
      confidence,
      supportScore: effectiveSupport,
      contradictionScore: effectiveContradiction,
      conflictCount: conflicts.length,
      policyAllowed: policyDecision.allowed,
      policyExplanation: policyDecision.explanation,
      evidenceExplanation: assessment.explanation,
    });

    const updated: AssertionRecord = {
      ...assertion,
      status: nextStatus,
      truthState,
      confidence,
      evidenceIds,
      policyDecisionIds: policyDecision.decisionId
        ? [
            ...new Set([
              ...(assertion.policyDecisionIds ?? []),
              policyDecision.decisionId,
            ]),
          ]
        : assertion.policyDecisionIds,
      version: assertion.version + 1,
      updatedAt: new Date().toISOString(),
    };

    await this.repository.updateAssertion(updated);
    await this.repository.appendHistory({
      historyId: this.historyId(assertionId),
      assertionId,
      previousStatus: assertion.status,
      nextStatus,
      previousTruthState: assertion.truthState,
      nextTruthState: truthState,
      previousConfidence: assertion.confidence,
      nextConfidence: confidence,
      actorId: "assertion-truth-engine",
      reason: explanation,
      occurredAt: updated.updatedAt,
    });

    if (nextStatus === "accepted" && truthState === "true") {
      await this.promoteCanonicalTruth(updated, explanation);
    }

    await this.events.publish("assertion.evaluated", {
      assertionId,
      status: nextStatus,
      truthState,
      confidence,
      supportScore: effectiveSupport,
      contradictionScore: effectiveContradiction,
      conflictingAssertionCount: conflicts.length,
      policyAllowed: policyDecision.allowed,
    });

    return {
      assertionId,
      truthState,
      confidence,
      supportScore: effectiveSupport,
      contradictionScore: effectiveContradiction,
      evidenceIds,
      conflictingAssertionIds: conflicts.map(
        (candidate) => candidate.assertionId,
      ),
      policyAllowed: policyDecision.allowed,
      explanation,
      evaluatedAt: updated.updatedAt,
    };
  }

  async resolveContest(
    subjectId: string,
    predicate: string,
    actorId: string,
    reason: string,
  ): Promise<CanonicalTruth | null> {
    if (!actorId.trim()) throw new Error("Actor id is required");
    if (!reason.trim()) throw new Error("Resolution reason is required");

    const assertions = await this.repository.listAssertionsByFact(
      subjectId,
      predicate,
    );
    const candidates = assertions
      .filter(
        (assertion) =>
          assertion.status !== "revoked" &&
          assertion.status !== "superseded",
      )
      .sort((left, right) => right.confidence - left.confidence);

    if (candidates.length === 0) return null;

    const winner = candidates[0];
    const runnerUp = candidates[1];

    if (
      winner.truthState !== "true" ||
      winner.confidence < this.acceptanceThreshold ||
      (runnerUp && winner.confidence - runnerUp.confidence < 0.1)
    ) {
      await this.events.publish("assertion.contest.unresolved", {
        subjectId,
        predicate,
        candidateCount: candidates.length,
      });
      return null;
    }

    for (const candidate of candidates.slice(1)) {
      if (candidate.status === "contested" || candidate.status === "accepted") {
        await this.transitionAssertion(
          candidate,
          "rejected",
          candidate.truthState === "true" ? "uncertain" : candidate.truthState,
          candidate.confidence,
          actorId,
          `Contest resolved in favour of ${winner.assertionId}: ${reason}`,
        );
      }
    }

    const canonical = await this.promoteCanonicalTruth(
      winner,
      `Contest resolved by ${actorId}: ${reason}`,
    );

    await this.events.publish("assertion.contest.resolved", {
      subjectId,
      predicate,
      winningAssertionId: winner.assertionId,
      canonicalTruthId: canonical.truthId,
    });

    return canonical;
  }

  async revokeAssertion(
    assertionId: string,
    actorId: string,
    reason: string,
  ): Promise<AssertionRecord> {
    if (!actorId.trim()) throw new Error("Actor id is required");
    if (!reason.trim()) throw new Error("Revocation reason is required");

    const assertion = await this.requireAssertion(assertionId);
    const revoked = await this.transitionAssertion(
      assertion,
      "revoked",
      "unknown",
      0,
      actorId,
      reason,
    );

    await this.events.publish("assertion.revoked", {
      assertionId,
      actorId,
      reason,
    });

    return revoked;
  }

  async getCanonicalTruth(
    subjectId: string,
    predicate: string,
  ): Promise<CanonicalTruth | null> {
    return this.repository.getCanonicalTruth(subjectId, predicate);
  }

  private async promoteCanonicalTruth(
    assertion: AssertionRecord,
    explanation: string,
  ): Promise<CanonicalTruth> {
    const existing = await this.repository.getCanonicalTruth(
      assertion.subjectId,
      assertion.predicate,
    );

    if (
      existing &&
      existing.assertionId !== assertion.assertionId &&
      existing.confidence > assertion.confidence
    ) {
      return existing;
    }

    const now = new Date().toISOString();
    const truth: CanonicalTruth = {
      truthId:
        existing?.truthId ??
        `canonical-truth:${assertion.subjectId}:${assertion.predicate}`,
      subjectId: assertion.subjectId,
      predicate: assertion.predicate,
      assertionId: assertion.assertionId,
      value: assertion.object,
      truthState: assertion.truthState,
      confidence: assertion.confidence,
      establishedAt: existing?.establishedAt ?? now,
      updatedAt: now,
      version: (existing?.version ?? 0) + 1,
      evidenceIds: assertion.evidenceIds,
      explanation,
    };

    await this.repository.saveCanonicalTruth(truth);
    await this.events.publish("truth.canonical.updated", {
      truthId: truth.truthId,
      subjectId: truth.subjectId,
      predicate: truth.predicate,
      assertionId: truth.assertionId,
      confidence: truth.confidence,
      version: truth.version,
    });

    return truth;
  }

  private async transitionAssertion(
    assertion: AssertionRecord,
    nextStatus: AssertionStatus,
    nextTruthState: TruthState,
    nextConfidence: number,
    actorId: string,
    reason: string,
  ): Promise<AssertionRecord> {
    const updated: AssertionRecord = {
      ...assertion,
      status: nextStatus,
      truthState: nextTruthState,
      confidence: this.clamp(nextConfidence),
      version: assertion.version + 1,
      updatedAt: new Date().toISOString(),
    };

    await this.repository.updateAssertion(updated);
    await this.repository.appendHistory({
      historyId: this.historyId(assertion.assertionId),
      assertionId: assertion.assertionId,
      previousStatus: assertion.status,
      nextStatus,
      previousTruthState: assertion.truthState,
      nextTruthState,
      previousConfidence: assertion.confidence,
      nextConfidence: updated.confidence,
      actorId,
      reason,
      occurredAt: updated.updatedAt,
    });

    return updated;
  }

  private async requireAssertion(assertionId: string): Promise<AssertionRecord> {
    if (!assertionId.trim()) throw new Error("Assertion id is required");
    const assertion = await this.repository.getAssertion(assertionId);
    if (!assertion) {
      throw new AssertionTruthIntegrityError(
        `Assertion ${assertionId} was not found`,
      );
    }
    return assertion;
  }

  private validateAssertion(assertion: AssertionRecord): void {
    if (!assertion.assertionId.trim()) throw new Error("Assertion id is required");
    if (!assertion.subjectId.trim()) throw new Error("Subject id is required");
    if (!assertion.predicate.trim()) throw new Error("Predicate is required");
    if (!assertion.createdBy.trim()) throw new Error("Creator id is required");
    if (Number.isNaN(Date.parse(assertion.createdAt))) {
      throw new Error("Created date must be valid");
    }
    if (assertion.updatedAt && Number.isNaN(Date.parse(assertion.updatedAt))) {
      throw new Error("Updated date must be valid");
    }
    if (
      !Number.isFinite(assertion.confidence) ||
      assertion.confidence < 0 ||
      assertion.confidence > 1
    ) {
      throw new Error("Confidence must be between 0 and 1");
    }
  }

  private buildExplanation(input: {
    truthState: TruthState;
    confidence: number;
    supportScore: number;
    contradictionScore: number;
    conflictCount: number;
    policyAllowed: boolean;
    policyExplanation: string;
    evidenceExplanation: string;
  }): string {
    if (!input.policyAllowed) {
      return `Assertion rejected by governance policy. ${input.policyExplanation}`;
    }
    if (input.truthState === "true") {
      return `Assertion accepted as canonical truth with confidence ${input.confidence.toFixed(3)}. Support ${input.supportScore.toFixed(3)}, contradiction ${input.contradictionScore.toFixed(3)}. ${input.evidenceExplanation}`;
    }
    if (input.truthState === "false") {
      return `Assertion rejected as false with contradiction ${input.contradictionScore.toFixed(3)} exceeding support ${input.supportScore.toFixed(3)}. ${input.evidenceExplanation}`;
    }
    if (input.truthState === "contested") {
      return `Assertion remains contested because ${input.conflictCount} conflicting assertion(s) or materially mixed evidence were detected. ${input.evidenceExplanation}`;
    }
    return `Assertion remains uncertain with confidence ${input.confidence.toFixed(3)}. ${input.evidenceExplanation}`;
  }

  private valuesEqual(left: unknown, right: unknown): boolean {
    return JSON.stringify(left) === JSON.stringify(right);
  }

  private historyId(assertionId: string): string {
    return `assertion-history:${assertionId}:${Date.now()}`;
  }

  private clamp(value: number): number {
    return Math.max(0, Math.min(1, value));
  }
}
