export type ExplanationNodeType =
  | "decision"
  | "assertion"
  | "evidence"
  | "policy"
  | "world-state"
  | "plan"
  | "action"
  | "confidence"
  | "counterfactual"
  | "outcome";

export interface ExplanationNode {
  nodeId: string;
  nodeType: ExplanationNodeType;
  label: string;
  summary: string;
  confidence?: number;
  sourceIds?: string[];
  metadata?: Record<string, unknown>;
}

export interface ExplanationEdge {
  edgeId: string;
  fromNodeId: string;
  toNodeId: string;
  relationship:
    | "supports"
    | "contradicts"
    | "governs"
    | "derived-from"
    | "caused"
    | "depends-on"
    | "selected-over"
    | "changed-by";
  weight?: number;
  metadata?: Record<string, unknown>;
}

export interface ReasoningTrace {
  traceId: string;
  subjectId: string;
  decisionId?: string;
  nodes: ExplanationNode[];
  edges: ExplanationEdge[];
  createdAt: string;
  createdBy: string;
  version: number;
  metadata?: Record<string, unknown>;
}

export interface ExplanationRequest {
  subjectId: string;
  decisionId?: string;
  audience: "human" | "operator" | "auditor" | "machine";
  includeCounterfactuals?: boolean;
  includeWorldState?: boolean;
  includeRawEvidence?: boolean;
  requestedBy: string;
}

export interface HumanReadableExplanation {
  title: string;
  summary: string;
  rationale: string[];
  evidence: string[];
  policies: string[];
  uncertainties: string[];
  counterfactuals: string[];
  confidence: number;
}

export interface ExplanationReport {
  reportId: string;
  traceId: string;
  request: ExplanationRequest;
  human: HumanReadableExplanation;
  machine: ReasoningTrace;
  generatedAt: string;
}

export interface CounterfactualScenario {
  scenarioId: string;
  description: string;
  changedInputs: Record<string, unknown>;
  predictedOutcome: unknown;
  confidence: number;
  explanation: string;
}

export interface ExplainabilityRepository {
  saveTrace(trace: ReasoningTrace): Promise<void>;
  getTrace(traceId: string): Promise<ReasoningTrace | null>;
  findTraceByDecision(decisionId: string): Promise<ReasoningTrace | null>;
  saveReport(report: ExplanationReport): Promise<void>;
}

export interface ExplainabilityEventBus {
  publish(event: string, payload: Record<string, unknown>): Promise<void>;
}

export interface EvidenceTracePort {
  getEvidenceTrace(subjectId: string): Promise<Array<{
    evidenceId: string;
    summary: string;
    supports: boolean;
    confidence: number;
    sourceIds: string[];
  }>>;
}

export interface PolicyTracePort {
  getPolicyTrace(subjectId: string): Promise<Array<{
    decisionId: string;
    ruleId?: string;
    allowed: boolean;
    explanation: string;
  }>>;
}

export interface AssertionTracePort {
  getAssertionTrace(subjectId: string): Promise<Array<{
    assertionId: string;
    predicate: string;
    value: unknown;
    truthState: string;
    confidence: number;
    explanation?: string;
  }>>;
}

export interface WorldStateTracePort {
  getWorldStateTrace(subjectId: string): Promise<{
    snapshotId?: string;
    summary: string;
    state: Record<string, unknown>;
  } | null>;
}

export interface DecisionTracePort {
  getDecisionTrace(decisionId: string): Promise<{
    decisionId: string;
    summary: string;
    outcome: unknown;
    confidence: number;
    alternatives?: Array<{ label: string; outcome: unknown; confidence: number }>;
    metadata?: Record<string, unknown>;
  }>;
}

export interface CounterfactualPort {
  evaluate(input: {
    subjectId: string;
    decisionId?: string;
    changedInputs: Record<string, unknown>;
  }): Promise<CounterfactualScenario>;
}

export interface ExplainabilityEngineOptions {
  maximumNodes?: number;
  minimumConfidence?: number;
}

export class ExplainabilityIntegrityError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ExplainabilityIntegrityError";
  }
}

export class ExplainabilityEngine {
  private readonly maximumNodes: number;
  private readonly minimumConfidence: number;

  constructor(
    private readonly repository: ExplainabilityRepository,
    private readonly evidence: EvidenceTracePort,
    private readonly policies: PolicyTracePort,
    private readonly assertions: AssertionTracePort,
    private readonly worldState: WorldStateTracePort,
    private readonly decisions: DecisionTracePort,
    private readonly counterfactuals: CounterfactualPort,
    private readonly events: ExplainabilityEventBus,
    options: ExplainabilityEngineOptions = {},
  ) {
    this.maximumNodes = options.maximumNodes ?? 1000;
    this.minimumConfidence = options.minimumConfidence ?? 0;
  }

  async explain(request: ExplanationRequest): Promise<ExplanationReport> {
    this.validateRequest(request);

    const [evidenceTrace, policyTrace, assertionTrace, worldStateTrace, decisionTrace] =
      await Promise.all([
        this.evidence.getEvidenceTrace(request.subjectId),
        this.policies.getPolicyTrace(request.subjectId),
        this.assertions.getAssertionTrace(request.subjectId),
        request.includeWorldState
          ? this.worldState.getWorldStateTrace(request.subjectId)
          : Promise.resolve(null),
        request.decisionId
          ? this.decisions.getDecisionTrace(request.decisionId)
          : Promise.resolve(null),
      ]);

    const trace = this.buildTrace({
      request,
      evidenceTrace,
      policyTrace,
      assertionTrace,
      worldStateTrace,
      decisionTrace,
    });

    const scenarios = request.includeCounterfactuals
      ? await this.generateCounterfactuals(request, decisionTrace)
      : [];

    for (const scenario of scenarios) {
      this.addNode(trace, {
        nodeId: `counterfactual:${scenario.scenarioId}`,
        nodeType: "counterfactual",
        label: scenario.description,
        summary: scenario.explanation,
        confidence: scenario.confidence,
        metadata: { changedInputs: scenario.changedInputs, predictedOutcome: scenario.predictedOutcome },
      });
      if (request.decisionId) {
        this.addEdge(trace, {
          edgeId: `edge:counterfactual:${scenario.scenarioId}`,
          fromNodeId: `counterfactual:${scenario.scenarioId}`,
          toNodeId: `decision:${request.decisionId}`,
          relationship: "changed-by",
        });
      }
    }

    this.validateTrace(trace);
    await this.repository.saveTrace(trace);

    const human = this.renderHumanExplanation({
      request,
      evidenceTrace,
      policyTrace,
      assertionTrace,
      decisionTrace,
      scenarios,
    });

    const report: ExplanationReport = {
      reportId: `explanation-report:${trace.traceId}`,
      traceId: trace.traceId,
      request,
      human,
      machine: trace,
      generatedAt: new Date().toISOString(),
    };

    await this.repository.saveReport(report);
    await this.events.publish("explainability.report.generated", {
      reportId: report.reportId,
      traceId: trace.traceId,
      subjectId: request.subjectId,
      decisionId: request.decisionId,
      audience: request.audience,
      nodeCount: trace.nodes.length,
      edgeCount: trace.edges.length,
    });

    return report;
  }

  async getDecisionExplanation(decisionId: string): Promise<ReasoningTrace | null> {
    if (!decisionId.trim()) throw new Error("Decision id is required");
    return this.repository.findTraceByDecision(decisionId);
  }

  async rootCause(traceId: string, targetNodeId: string): Promise<ExplanationNode[]> {
    const trace = await this.repository.getTrace(traceId);
    if (!trace) throw new ExplainabilityIntegrityError(`Trace ${traceId} was not found`);
    if (!trace.nodes.some((node) => node.nodeId === targetNodeId)) {
      throw new ExplainabilityIntegrityError(`Node ${targetNodeId} was not found in trace ${traceId}`);
    }

    const incoming = new Map<string, string[]>();
    for (const edge of trace.edges) {
      const list = incoming.get(edge.toNodeId) ?? [];
      list.push(edge.fromNodeId);
      incoming.set(edge.toNodeId, list);
    }

    const visited = new Set<string>();
    const queue = [targetNodeId];
    const causes: ExplanationNode[] = [];

    while (queue.length > 0) {
      const nodeId = queue.shift()!;
      for (const parentId of incoming.get(nodeId) ?? []) {
        if (visited.has(parentId)) continue;
        visited.add(parentId);
        const node = trace.nodes.find((candidate) => candidate.nodeId === parentId);
        if (node) {
          causes.push(node);
          queue.push(parentId);
        }
      }
    }

    return causes;
  }

  private buildTrace(input: {
    request: ExplanationRequest;
    evidenceTrace: Awaited<ReturnType<EvidenceTracePort["getEvidenceTrace"]>>;
    policyTrace: Awaited<ReturnType<PolicyTracePort["getPolicyTrace"]>>;
    assertionTrace: Awaited<ReturnType<AssertionTracePort["getAssertionTrace"]>>;
    worldStateTrace: Awaited<ReturnType<WorldStateTracePort["getWorldStateTrace"]>>;
    decisionTrace: Awaited<ReturnType<DecisionTracePort["getDecisionTrace"]>> | null;
  }): ReasoningTrace {
    const trace: ReasoningTrace = {
      traceId: `reasoning-trace:${input.request.subjectId}:${Date.now()}`,
      subjectId: input.request.subjectId,
      decisionId: input.request.decisionId,
      nodes: [],
      edges: [],
      createdAt: new Date().toISOString(),
      createdBy: input.request.requestedBy,
      version: 1,
    };

    for (const item of input.assertionTrace) {
      this.addNode(trace, {
        nodeId: `assertion:${item.assertionId}`,
        nodeType: "assertion",
        label: item.predicate,
        summary: item.explanation ?? `${item.predicate} = ${JSON.stringify(item.value)}`,
        confidence: item.confidence,
        metadata: { truthState: item.truthState, value: item.value },
      });
    }

    for (const item of input.evidenceTrace) {
      this.addNode(trace, {
        nodeId: `evidence:${item.evidenceId}`,
        nodeType: "evidence",
        label: item.evidenceId,
        summary: item.summary,
        confidence: item.confidence,
        sourceIds: item.sourceIds,
        metadata: { supports: item.supports },
      });
      for (const assertion of input.assertionTrace) {
        this.addEdge(trace, {
          edgeId: `edge:evidence:${item.evidenceId}:${assertion.assertionId}`,
          fromNodeId: `evidence:${item.evidenceId}`,
          toNodeId: `assertion:${assertion.assertionId}`,
          relationship: item.supports ? "supports" : "contradicts",
          weight: item.confidence,
        });
      }
    }

    for (const item of input.policyTrace) {
      this.addNode(trace, {
        nodeId: `policy:${item.decisionId}`,
        nodeType: "policy",
        label: item.ruleId ?? item.decisionId,
        summary: item.explanation,
        metadata: { allowed: item.allowed },
      });
    }

    if (input.worldStateTrace) {
      this.addNode(trace, {
        nodeId: `world-state:${input.worldStateTrace.snapshotId ?? input.request.subjectId}`,
        nodeType: "world-state",
        label: "World state",
        summary: input.worldStateTrace.summary,
        metadata: { state: input.worldStateTrace.state },
      });
    }

    if (input.decisionTrace) {
      this.addNode(trace, {
        nodeId: `decision:${input.decisionTrace.decisionId}`,
        nodeType: "decision",
        label: input.decisionTrace.decisionId,
        summary: input.decisionTrace.summary,
        confidence: input.decisionTrace.confidence,
        metadata: { outcome: input.decisionTrace.outcome, ...input.decisionTrace.metadata },
      });

      for (const assertion of input.assertionTrace) {
        this.addEdge(trace, {
          edgeId: `edge:assertion:${assertion.assertionId}:decision`,
          fromNodeId: `assertion:${assertion.assertionId}`,
          toNodeId: `decision:${input.decisionTrace.decisionId}`,
          relationship: "derived-from",
          weight: assertion.confidence,
        });
      }
      for (const policy of input.policyTrace) {
        this.addEdge(trace, {
          edgeId: `edge:policy:${policy.decisionId}:decision`,
          fromNodeId: `policy:${policy.decisionId}`,
          toNodeId: `decision:${input.decisionTrace.decisionId}`,
          relationship: "governs",
        });
      }
      if (input.worldStateTrace) {
        this.addEdge(trace, {
          edgeId: `edge:world-state:decision:${input.decisionTrace.decisionId}`,
          fromNodeId: `world-state:${input.worldStateTrace.snapshotId ?? input.request.subjectId}`,
          toNodeId: `decision:${input.decisionTrace.decisionId}`,
          relationship: "depends-on",
        });
      }
    }

    return trace;
  }

  private async generateCounterfactuals(
    request: ExplanationRequest,
    decisionTrace: Awaited<ReturnType<DecisionTracePort["getDecisionTrace"]>> | null,
  ): Promise<CounterfactualScenario[]> {
    if (!decisionTrace?.alternatives?.length) return [];
    const alternatives = decisionTrace.alternatives.slice(0, 3);
    return Promise.all(
      alternatives.map((alternative) =>
        this.counterfactuals.evaluate({
          subjectId: request.subjectId,
          decisionId: request.decisionId,
          changedInputs: { selectedAlternative: alternative.label },
        }),
      ),
    );
  }

  private renderHumanExplanation(input: {
    request: ExplanationRequest;
    evidenceTrace: Awaited<ReturnType<EvidenceTracePort["getEvidenceTrace"]>>;
    policyTrace: Awaited<ReturnType<PolicyTracePort["getPolicyTrace"]>>;
    assertionTrace: Awaited<ReturnType<AssertionTracePort["getAssertionTrace"]>>;
    decisionTrace: Awaited<ReturnType<DecisionTracePort["getDecisionTrace"]>> | null;
    scenarios: CounterfactualScenario[];
  }): HumanReadableExplanation {
    const confidence = input.decisionTrace?.confidence ?? this.average(
      input.assertionTrace.map((item) => item.confidence),
    );
    return {
      title: input.decisionTrace
        ? `Explanation for decision ${input.decisionTrace.decisionId}`
        : `Explanation for ${input.request.subjectId}`,
      summary: input.decisionTrace?.summary ?? "Explanation generated from available assertions, evidence, policies, and world state.",
      rationale: input.assertionTrace.map(
        (item) => `${item.predicate}: ${item.truthState} (${item.confidence.toFixed(3)})`,
      ),
      evidence: input.evidenceTrace.map(
        (item) => `${item.supports ? "Supporting" : "Contradicting"} evidence ${item.evidenceId}: ${item.summary}`,
      ),
      policies: input.policyTrace.map(
        (item) => `${item.allowed ? "Allowed" : "Restricted"}: ${item.explanation}`,
      ),
      uncertainties: [
        ...input.assertionTrace
          .filter((item) => item.confidence < 0.7 || item.truthState === "uncertain" || item.truthState === "contested")
          .map((item) => `${item.predicate} remains ${item.truthState} at confidence ${item.confidence.toFixed(3)}.`),
        ...input.evidenceTrace
          .filter((item) => item.confidence < 0.7)
          .map((item) => `Evidence ${item.evidenceId} has confidence ${item.confidence.toFixed(3)}.`),
      ],
      counterfactuals: input.scenarios.map((scenario) => scenario.explanation),
      confidence: this.clamp(confidence),
    };
  }

  private addNode(trace: ReasoningTrace, node: ExplanationNode): void {
    if (trace.nodes.some((candidate) => candidate.nodeId === node.nodeId)) return;
    if (trace.nodes.length >= this.maximumNodes) {
      throw new ExplainabilityIntegrityError(`Trace exceeds maximum node count of ${this.maximumNodes}`);
    }
    if (node.confidence !== undefined && node.confidence < this.minimumConfidence) return;
    trace.nodes.push({ ...node, confidence: node.confidence === undefined ? undefined : this.clamp(node.confidence) });
  }

  private addEdge(trace: ReasoningTrace, edge: ExplanationEdge): void {
    if (trace.edges.some((candidate) => candidate.edgeId === edge.edgeId)) return;
    trace.edges.push({ ...edge, weight: edge.weight === undefined ? undefined : this.clamp(edge.weight) });
  }

  private validateTrace(trace: ReasoningTrace): void {
    const nodeIds = new Set(trace.nodes.map((node) => node.nodeId));
    for (const edge of trace.edges) {
      if (!nodeIds.has(edge.fromNodeId) || !nodeIds.has(edge.toNodeId)) {
        throw new ExplainabilityIntegrityError(`Edge ${edge.edgeId} references a missing node`);
      }
    }
  }

  private validateRequest(request: ExplanationRequest): void {
    if (!request.subjectId.trim()) throw new Error("Subject id is required");
    if (!request.requestedBy.trim()) throw new Error("Requester identity is required");
  }

  private average(values: number[]): number {
    return values.length === 0 ? 0 : values.reduce((sum, value) => sum + value, 0) / values.length;
  }

  private clamp(value: number): number {
    return Math.max(0, Math.min(1, value));
  }
}
