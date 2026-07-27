export type EvidenceType =
  | "document"
  | "observation"
  | "system-event"
  | "human-input"
  | "model-output"
  | "sensor"
  | "derived";

export type EvidenceStatus = "active" | "superseded" | "revoked" | "expired";

export interface EvidenceSource {
  sourceId: string;
  sourceType: EvidenceType;
  uri?: string;
  ownerId?: string;
  capturedAt: string;
  receivedAt: string;
  metadata?: Record<string, unknown>;
}

export interface EvidenceRecord {
  evidenceId: string;
  subjectId: string;
  claim: string;
  source: EvidenceSource;
  contentHash: string;
  confidence: number;
  relevance: number;
  freshness: number;
  status: EvidenceStatus;
  supersedesEvidenceId?: string;
  expiresAt?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
}

export interface ProvenanceEdge {
  edgeId: string;
  fromEvidenceId: string;
  toEvidenceId: string;
  relationship:
    | "derived-from"
    | "supports"
    | "contradicts"
    | "supersedes"
    | "transformed-from"
    | "verified-by";
  createdAt: string;
  actorId: string;
  metadata?: Record<string, unknown>;
}

export interface AssertionEvidenceLink {
  assertionId: string;
  evidenceId: string;
  weight: number;
  role: "supporting" | "contradicting" | "contextual";
}

export interface EvidenceAssessment {
  assertionId: string;
  supportScore: number;
  contradictionScore: number;
  netConfidence: number;
  supportingEvidenceIds: string[];
  contradictingEvidenceIds: string[];
  staleEvidenceIds: string[];
  revokedEvidenceIds: string[];
  explanation: string;
  assessedAt: string;
}

export interface ProvenanceTrace {
  rootEvidenceId: string;
  evidence: EvidenceRecord[];
  edges: ProvenanceEdge[];
  complete: boolean;
  missingEvidenceIds: string[];
}

export interface EvidenceRepository {
  saveEvidence(record: EvidenceRecord): Promise<void>;
  getEvidence(evidenceId: string): Promise<EvidenceRecord | null>;
  listEvidence(evidenceIds: string[]): Promise<EvidenceRecord[]>;
  updateEvidence(record: EvidenceRecord): Promise<void>;
  saveProvenanceEdge(edge: ProvenanceEdge): Promise<void>;
  listIncomingEdges(evidenceId: string): Promise<ProvenanceEdge[]>;
  listOutgoingEdges(evidenceId: string): Promise<ProvenanceEdge[]>;
  saveAssertionLink(link: AssertionEvidenceLink): Promise<void>;
  listAssertionLinks(assertionId: string): Promise<AssertionEvidenceLink[]>;
}

export interface EvidenceEventBus {
  publish(event: string, payload: Record<string, unknown>): Promise<void>;
}

export interface EvidenceEngineOptions {
  staleAfterMs?: number;
  maximumTraceDepth?: number;
  minimumConfidence?: number;
}

export class EvidenceIntegrityError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "EvidenceIntegrityError";
  }
}

export class EvidenceProvenanceEngine {
  private readonly staleAfterMs: number;
  private readonly maximumTraceDepth: number;
  private readonly minimumConfidence: number;

  constructor(
    private readonly repository: EvidenceRepository,
    private readonly events: EvidenceEventBus,
    options: EvidenceEngineOptions = {},
  ) {
    this.staleAfterMs = options.staleAfterMs ?? 90 * 24 * 60 * 60 * 1000;
    this.maximumTraceDepth = options.maximumTraceDepth ?? 25;
    this.minimumConfidence = options.minimumConfidence ?? 0.05;
  }

  async registerEvidence(record: EvidenceRecord): Promise<EvidenceRecord> {
    this.validateEvidence(record);

    const existing = await this.repository.getEvidence(record.evidenceId);
    if (existing) {
      throw new EvidenceIntegrityError(
        `Evidence ${record.evidenceId} already exists`,
      );
    }

    if (record.supersedesEvidenceId) {
      const superseded = await this.repository.getEvidence(
        record.supersedesEvidenceId,
      );
      if (!superseded) {
        throw new EvidenceIntegrityError(
          `Superseded evidence ${record.supersedesEvidenceId} was not found`,
        );
      }

      superseded.status = "superseded";
      await this.repository.updateEvidence(superseded);

      await this.linkProvenance({
        edgeId: `supersedes:${record.evidenceId}:${record.supersedesEvidenceId}`,
        fromEvidenceId: record.evidenceId,
        toEvidenceId: record.supersedesEvidenceId,
        relationship: "supersedes",
        createdAt: new Date().toISOString(),
        actorId: record.source.ownerId ?? "system",
      });
    }

    await this.repository.saveEvidence(record);
    await this.events.publish("evidence.registered", {
      evidenceId: record.evidenceId,
      subjectId: record.subjectId,
      sourceType: record.source.sourceType,
      confidence: record.confidence,
      contentHash: record.contentHash,
    });

    return record;
  }

  async linkProvenance(edge: ProvenanceEdge): Promise<ProvenanceEdge> {
    this.validateProvenanceEdge(edge);

    const [from, to] = await Promise.all([
      this.repository.getEvidence(edge.fromEvidenceId),
      this.repository.getEvidence(edge.toEvidenceId),
    ]);

    if (!from || !to) {
      throw new EvidenceIntegrityError(
        "Both provenance edge endpoints must exist",
      );
    }

    if (edge.fromEvidenceId === edge.toEvidenceId) {
      throw new EvidenceIntegrityError("Evidence cannot reference itself");
    }

    if (await this.wouldCreateCycle(edge.fromEvidenceId, edge.toEvidenceId)) {
      throw new EvidenceIntegrityError("Provenance edge would create a cycle");
    }

    await this.repository.saveProvenanceEdge(edge);
    await this.events.publish("evidence.provenance-linked", {
      edgeId: edge.edgeId,
      fromEvidenceId: edge.fromEvidenceId,
      toEvidenceId: edge.toEvidenceId,
      relationship: edge.relationship,
    });

    return edge;
  }

  async attachEvidenceToAssertion(
    link: AssertionEvidenceLink,
  ): Promise<AssertionEvidenceLink> {
    if (!link.assertionId.trim()) throw new Error("Assertion id is required");
    if (!link.evidenceId.trim()) throw new Error("Evidence id is required");
    if (!Number.isFinite(link.weight) || link.weight <= 0) {
      throw new Error("Evidence weight must be greater than zero");
    }

    const evidence = await this.repository.getEvidence(link.evidenceId);
    if (!evidence) {
      throw new EvidenceIntegrityError(
        `Evidence ${link.evidenceId} was not found`,
      );
    }

    await this.repository.saveAssertionLink(link);
    await this.events.publish("evidence.assertion-linked", {
      assertionId: link.assertionId,
      evidenceId: link.evidenceId,
      role: link.role,
      weight: link.weight,
    });

    return link;
  }

  async assessAssertion(assertionId: string): Promise<EvidenceAssessment> {
    if (!assertionId.trim()) throw new Error("Assertion id is required");

    const links = await this.repository.listAssertionLinks(assertionId);
    const evidence = await this.repository.listEvidence(
      links.map((link) => link.evidenceId),
    );
    const byId = new Map(evidence.map((record) => [record.evidenceId, record]));

    let support = 0;
    let contradiction = 0;
    let totalWeight = 0;
    const supportingEvidenceIds: string[] = [];
    const contradictingEvidenceIds: string[] = [];
    const staleEvidenceIds: string[] = [];
    const revokedEvidenceIds: string[] = [];

    for (const link of links) {
      const record = byId.get(link.evidenceId);
      if (!record) continue;

      if (record.status === "revoked") {
        revokedEvidenceIds.push(record.evidenceId);
        continue;
      }

      const freshness = this.effectiveFreshness(record);
      if (freshness < 0.5) staleEvidenceIds.push(record.evidenceId);

      if (record.status !== "active") continue;

      const contribution =
        link.weight *
        record.confidence *
        record.relevance *
        freshness;
      totalWeight += link.weight;

      if (link.role === "supporting") {
        support += contribution;
        supportingEvidenceIds.push(record.evidenceId);
      } else if (link.role === "contradicting") {
        contradiction += contribution;
        contradictingEvidenceIds.push(record.evidenceId);
      }
    }

    const denominator = Math.max(totalWeight, 1);
    const supportScore = this.clamp(support / denominator);
    const contradictionScore = this.clamp(contradiction / denominator);
    const netConfidence = this.clamp(
      supportScore * (1 - contradictionScore),
    );

    const assessment: EvidenceAssessment = {
      assertionId,
      supportScore,
      contradictionScore,
      netConfidence,
      supportingEvidenceIds,
      contradictingEvidenceIds,
      staleEvidenceIds,
      revokedEvidenceIds,
      explanation: this.buildExplanation(
        supportScore,
        contradictionScore,
        supportingEvidenceIds.length,
        contradictingEvidenceIds.length,
      ),
      assessedAt: new Date().toISOString(),
    };

    await this.events.publish("evidence.assertion-assessed", {
      assertionId,
      supportScore,
      contradictionScore,
      netConfidence,
      supportingEvidenceCount: supportingEvidenceIds.length,
      contradictingEvidenceCount: contradictingEvidenceIds.length,
    });

    return assessment;
  }

  async traceProvenance(rootEvidenceId: string): Promise<ProvenanceTrace> {
    if (!rootEvidenceId.trim()) throw new Error("Root evidence id is required");

    const visited = new Set<string>();
    const records = new Map<string, EvidenceRecord>();
    const edges = new Map<string, ProvenanceEdge>();
    const missing = new Set<string>();
    const queue: Array<{ evidenceId: string; depth: number }> = [
      { evidenceId: rootEvidenceId, depth: 0 },
    ];

    while (queue.length > 0) {
      const current = queue.shift()!;
      if (visited.has(current.evidenceId)) continue;
      visited.add(current.evidenceId);

      const record = await this.repository.getEvidence(current.evidenceId);
      if (!record) {
        missing.add(current.evidenceId);
        continue;
      }
      records.set(record.evidenceId, record);

      if (current.depth >= this.maximumTraceDepth) continue;

      const incoming = await this.repository.listIncomingEdges(
        current.evidenceId,
      );
      for (const edge of incoming) {
        edges.set(edge.edgeId, edge);
        queue.push({
          evidenceId: edge.fromEvidenceId,
          depth: current.depth + 1,
        });
      }
    }

    return {
      rootEvidenceId,
      evidence: [...records.values()],
      edges: [...edges.values()],
      complete: missing.size === 0,
      missingEvidenceIds: [...missing],
    };
  }

  async revokeEvidence(
    evidenceId: string,
    actorId: string,
    reason: string,
  ): Promise<EvidenceRecord> {
    if (!actorId.trim()) throw new Error("Actor id is required");
    if (!reason.trim()) throw new Error("Revocation reason is required");

    const record = await this.repository.getEvidence(evidenceId);
    if (!record) {
      throw new EvidenceIntegrityError(`Evidence ${evidenceId} was not found`);
    }

    record.status = "revoked";
    record.metadata = {
      ...(record.metadata ?? {}),
      revokedBy: actorId,
      revokedAt: new Date().toISOString(),
      revocationReason: reason,
    };

    await this.repository.updateEvidence(record);
    await this.events.publish("evidence.revoked", {
      evidenceId,
      actorId,
      reason,
    });

    return record;
  }

  private async wouldCreateCycle(
    fromEvidenceId: string,
    toEvidenceId: string,
  ): Promise<boolean> {
    const visited = new Set<string>();
    const queue = [toEvidenceId];

    while (queue.length > 0) {
      const current = queue.shift()!;
      if (current === fromEvidenceId) return true;
      if (visited.has(current)) continue;
      visited.add(current);

      const edges = await this.repository.listOutgoingEdges(current);
      for (const edge of edges) queue.push(edge.toEvidenceId);
    }

    return false;
  }

  private effectiveFreshness(record: EvidenceRecord): number {
    if (record.expiresAt && Date.parse(record.expiresAt) <= Date.now()) return 0;

    const capturedAt = Date.parse(record.source.capturedAt);
    if (Number.isNaN(capturedAt)) return record.freshness;

    const age = Math.max(0, Date.now() - capturedAt);
    const ageFactor = this.clamp(1 - age / Math.max(this.staleAfterMs, 1));
    return this.clamp(record.freshness * ageFactor);
  }

  private buildExplanation(
    support: number,
    contradiction: number,
    supportCount: number,
    contradictionCount: number,
  ): string {
    if (supportCount === 0 && contradictionCount === 0) {
      return "No active evidence is attached to this assertion.";
    }
    if (contradiction > support) {
      return `The assertion is more strongly contradicted than supported (${contradictionCount} contradicting, ${supportCount} supporting).`;
    }
    if (support < this.minimumConfidence) {
      return "The assertion has evidence, but the weighted support is too weak for a reliable conclusion.";
    }
    return `The assertion is supported by ${supportCount} active evidence item(s), with ${contradictionCount} contradicting item(s).`;
  }

  private validateEvidence(record: EvidenceRecord): void {
    if (!record.evidenceId.trim()) throw new Error("Evidence id is required");
    if (!record.subjectId.trim()) throw new Error("Subject id is required");
    if (!record.claim.trim()) throw new Error("Evidence claim is required");
    if (!record.contentHash.trim()) throw new Error("Content hash is required");
    if (!record.source.sourceId.trim()) throw new Error("Source id is required");
    if (Number.isNaN(Date.parse(record.source.capturedAt))) {
      throw new Error("Captured date must be valid");
    }
    if (Number.isNaN(Date.parse(record.source.receivedAt))) {
      throw new Error("Received date must be valid");
    }
    if (record.expiresAt && Number.isNaN(Date.parse(record.expiresAt))) {
      throw new Error("Expiry date must be valid");
    }

    for (const [name, value] of [
      ["confidence", record.confidence],
      ["relevance", record.relevance],
      ["freshness", record.freshness],
    ] as const) {
      if (!Number.isFinite(value) || value < 0 || value > 1) {
        throw new Error(`${name} must be between 0 and 1`);
      }
    }
  }

  private validateProvenanceEdge(edge: ProvenanceEdge): void {
    if (!edge.edgeId.trim()) throw new Error("Provenance edge id is required");
    if (!edge.fromEvidenceId.trim()) {
      throw new Error("From evidence id is required");
    }
    if (!edge.toEvidenceId.trim()) throw new Error("To evidence id is required");
    if (!edge.actorId.trim()) throw new Error("Actor id is required");
    if (Number.isNaN(Date.parse(edge.createdAt))) {
      throw new Error("Provenance edge date must be valid");
    }
  }

  private clamp(value: number): number {
    return Math.max(0, Math.min(1, value));
  }
}
