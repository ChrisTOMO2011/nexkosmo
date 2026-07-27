export type WorkStatus =
  | "queued"
  | "running"
  | "paused"
  | "blocked"
  | "completed"
  | "failed"
  | "cancelled";

export interface ExecutiveObjective {
  objectiveId: string;
  title: string;
  strategicValue: number;
  urgency: number;
  confidence: number;
  deadline?: string;
  status: "planned" | "active" | "completed" | "cancelled";
  metadata?: Record<string, unknown>;
}

export interface ExecutiveWorkItem {
  workItemId: string;
  objectiveId: string;
  title: string;
  status: WorkStatus;
  priority: number;
  progress: number;
  estimatedRemainingMs: number;
  requiredResources: Record<string, number>;
  assignedResources: Record<string, number>;
  dependencies: string[];
  interruptible: boolean;
  startedAt?: string;
  deadline?: string;
  metadata?: Record<string, unknown>;
}

export interface ResourcePool {
  resource: string;
  capacity: number;
  allocated: number;
  reserved: number;
  healthy: boolean;
}

export interface SystemHealthSnapshot {
  capturedAt: string;
  overallHealth: number;
  services: Record<
    string,
    {
      healthy: boolean;
      latencyMs?: number;
      errorRate?: number;
      saturation?: number;
    }
  >;
}

export type ExecutiveDirectiveType =
  | "start"
  | "pause"
  | "resume"
  | "cancel"
  | "reprioritize"
  | "reallocate"
  | "escalate"
  | "defer";

export interface ExecutiveDirective {
  directiveId: string;
  type: ExecutiveDirectiveType;
  workItemId: string;
  objectiveId: string;
  reason: string;
  priority?: number;
  resourceChanges?: Record<string, number>;
  createdAt: string;
}

export interface ExecutiveControlState {
  objectives: ExecutiveObjective[];
  workItems: ExecutiveWorkItem[];
  resources: ResourcePool[];
  health: SystemHealthSnapshot;
}

export interface ExecutiveControlReport {
  cycleId: string;
  directives: ExecutiveDirective[];
  rankedObjectiveIds: string[];
  risks: string[];
  generatedAt: string;
}

export interface ExecutiveStateProvider {
  loadState(): Promise<ExecutiveControlState>;
}

export interface ExecutiveDirectiveDispatcher {
  dispatch(directive: ExecutiveDirective): Promise<void>;
}

export interface ExecutiveControlRepository {
  saveReport(report: ExecutiveControlReport): Promise<void>;
}

export interface ExecutiveEventBus {
  publish(event: string, payload: Record<string, unknown>): Promise<void>;
}

export interface ExecutiveControlOptions {
  healthInterventionThreshold?: number;
  deadlineRiskWindowMs?: number;
  resourceSafetyMargin?: number;
  maxDirectivesPerCycle?: number;
}

interface RankedObjective {
  objective: ExecutiveObjective;
  score: number;
}

export class ExecutiveControlEngine {
  private readonly healthInterventionThreshold: number;
  private readonly deadlineRiskWindowMs: number;
  private readonly resourceSafetyMargin: number;
  private readonly maxDirectivesPerCycle: number;

  constructor(
    private readonly stateProvider: ExecutiveStateProvider,
    private readonly dispatcher: ExecutiveDirectiveDispatcher,
    private readonly repository: ExecutiveControlRepository,
    private readonly events: ExecutiveEventBus,
    options: ExecutiveControlOptions = {},
  ) {
    this.healthInterventionThreshold = options.healthInterventionThreshold ?? 0.65;
    this.deadlineRiskWindowMs = options.deadlineRiskWindowMs ?? 24 * 60 * 60 * 1000;
    this.resourceSafetyMargin = options.resourceSafetyMargin ?? 0.1;
    this.maxDirectivesPerCycle = options.maxDirectivesPerCycle ?? 100;
  }

  async runCycle(cycleId: string): Promise<ExecutiveControlReport> {
    if (!cycleId.trim()) throw new Error("Cycle id is required");

    const state = await this.stateProvider.loadState();
    this.validateState(state);

    const rankedObjectives = this.rankObjectives(state.objectives);
    const objectiveRank = new Map(
      rankedObjectives.map((entry, index) => [entry.objective.objectiveId, index]),
    );

    const directives: ExecutiveDirective[] = [];
    const risks = this.detectRisks(state);

    directives.push(...this.healthDirectives(state));
    directives.push(...this.deadlineDirectives(state, objectiveRank));
    directives.push(...this.resourceDirectives(state, objectiveRank));
    directives.push(...this.schedulingDirectives(state, objectiveRank));

    const deduplicated = this.deduplicateDirectives(directives)
      .sort((left, right) => this.directiveWeight(right) - this.directiveWeight(left))
      .slice(0, this.maxDirectivesPerCycle);

    for (const directive of deduplicated) {
      await this.dispatcher.dispatch(directive);
    }

    const report: ExecutiveControlReport = {
      cycleId,
      directives: deduplicated,
      rankedObjectiveIds: rankedObjectives.map((entry) => entry.objective.objectiveId),
      risks,
      generatedAt: new Date().toISOString(),
    };

    await this.repository.saveReport(report);
    await this.events.publish("executive.control-cycle.completed", {
      cycleId,
      directiveCount: report.directives.length,
      riskCount: report.risks.length,
      rankedObjectiveIds: report.rankedObjectiveIds,
      overallHealth: state.health.overallHealth,
    });

    return report;
  }

  private rankObjectives(objectives: ExecutiveObjective[]): RankedObjective[] {
    const now = Date.now();

    return objectives
      .filter((objective) => objective.status === "active" || objective.status === "planned")
      .map((objective) => {
        const deadlinePressure = objective.deadline
          ? this.deadlinePressure(Date.parse(objective.deadline) - now)
          : 0;
        const score =
          this.normalise(objective.strategicValue) * 0.45 +
          this.normalise(objective.urgency) * 0.3 +
          this.clamp(objective.confidence) * 0.1 +
          deadlinePressure * 0.15;

        return { objective, score };
      })
      .sort((left, right) => right.score - left.score);
  }

  private healthDirectives(state: ExecutiveControlState): ExecutiveDirective[] {
    if (state.health.overallHealth >= this.healthInterventionThreshold) return [];

    return state.workItems
      .filter((item) => item.status === "running" && item.interruptible)
      .sort((left, right) => left.priority - right.priority)
      .slice(0, Math.max(1, Math.ceil(state.workItems.length * 0.1)))
      .map((item) =>
        this.directive(
          "pause",
          item,
          `System health ${state.health.overallHealth.toFixed(2)} is below the intervention threshold`,
        ),
      );
  }

  private deadlineDirectives(
    state: ExecutiveControlState,
    objectiveRank: Map<string, number>,
  ): ExecutiveDirective[] {
    const now = Date.now();
    const directives: ExecutiveDirective[] = [];

    for (const item of state.workItems) {
      if (!item.deadline || ["completed", "cancelled", "failed"].includes(item.status)) {
        continue;
      }

      const remaining = Date.parse(item.deadline) - now;
      if (remaining < 0) {
        directives.push(
          this.directive("escalate", item, "Work item deadline has passed"),
        );
        continue;
      }

      if (remaining <= this.deadlineRiskWindowMs && item.estimatedRemainingMs > remaining) {
        const rank = objectiveRank.get(item.objectiveId) ?? Number.MAX_SAFE_INTEGER;
        directives.push({
          ...this.directive(
            item.status === "paused" ? "resume" : "reprioritize",
            item,
            "Estimated remaining duration exceeds the available deadline window",
          ),
          priority: Math.max(item.priority, 1000 - rank),
        });
      }
    }

    return directives;
  }

  private resourceDirectives(
    state: ExecutiveControlState,
    objectiveRank: Map<string, number>,
  ): ExecutiveDirective[] {
    const available = new Map<string, number>();
    for (const pool of state.resources) {
      const usableCapacity = pool.healthy
        ? pool.capacity * (1 - this.resourceSafetyMargin)
        : 0;
      available.set(
        pool.resource,
        Math.max(0, usableCapacity - pool.allocated - pool.reserved),
      );
    }

    const running = state.workItems
      .filter((item) => item.status === "running")
      .sort(
        (left, right) =>
          (objectiveRank.get(left.objectiveId) ?? Number.MAX_SAFE_INTEGER) -
          (objectiveRank.get(right.objectiveId) ?? Number.MAX_SAFE_INTEGER),
      );

    const directives: ExecutiveDirective[] = [];
    for (const item of running) {
      const changes: Record<string, number> = {};

      for (const [resource, required] of Object.entries(item.requiredResources)) {
        const assigned = item.assignedResources[resource] ?? 0;
        const deficit = Math.max(0, required - assigned);
        const grant = Math.min(deficit, available.get(resource) ?? 0);

        if (grant > 0) {
          changes[resource] = grant;
          available.set(resource, (available.get(resource) ?? 0) - grant);
        }
      }

      if (Object.keys(changes).length > 0) {
        directives.push({
          ...this.directive(
            "reallocate",
            item,
            "Additional resources are available for a strategically ranked work item",
          ),
          resourceChanges: changes,
        });
      }
    }

    return directives;
  }

  private schedulingDirectives(
    state: ExecutiveControlState,
    objectiveRank: Map<string, number>,
  ): ExecutiveDirective[] {
    const completed = new Set(
      state.workItems
        .filter((item) => item.status === "completed")
        .map((item) => item.workItemId),
    );

    return state.workItems
      .filter((item) => item.status === "queued" || item.status === "paused")
      .filter((item) => item.dependencies.every((dependency) => completed.has(dependency)))
      .sort(
        (left, right) =>
          (objectiveRank.get(left.objectiveId) ?? Number.MAX_SAFE_INTEGER) -
            (objectiveRank.get(right.objectiveId) ?? Number.MAX_SAFE_INTEGER) ||
          right.priority - left.priority,
      )
      .map((item) =>
        this.directive(
          item.status === "paused" ? "resume" : "start",
          item,
          "Dependencies are complete and the work item is eligible for execution",
        ),
      );
  }

  private detectRisks(state: ExecutiveControlState): string[] {
    const risks: string[] = [];

    if (state.health.overallHealth < this.healthInterventionThreshold) {
      risks.push(
        `Overall system health is ${state.health.overallHealth.toFixed(2)}, below ${this.healthInterventionThreshold.toFixed(2)}`,
      );
    }

    for (const pool of state.resources) {
      if (!pool.healthy) risks.push(`Resource pool ${pool.resource} is unhealthy`);
      if (pool.allocated + pool.reserved > pool.capacity) {
        risks.push(`Resource pool ${pool.resource} is over capacity`);
      }
    }

    for (const item of state.workItems) {
      if (item.status === "blocked") risks.push(`Work item ${item.workItemId} is blocked`);
      if (item.progress < 0 || item.progress > 1) {
        risks.push(`Work item ${item.workItemId} has invalid progress`);
      }
    }

    return risks;
  }

  private directive(
    type: ExecutiveDirectiveType,
    item: ExecutiveWorkItem,
    reason: string,
  ): ExecutiveDirective {
    return {
      directiveId: `${type}:${item.workItemId}:${Date.now()}`,
      type,
      workItemId: item.workItemId,
      objectiveId: item.objectiveId,
      reason,
      createdAt: new Date().toISOString(),
    };
  }

  private deduplicateDirectives(
    directives: ExecutiveDirective[],
  ): ExecutiveDirective[] {
    const byKey = new Map<string, ExecutiveDirective>();

    for (const directive of directives) {
      const key = `${directive.type}:${directive.workItemId}`;
      if (!byKey.has(key)) byKey.set(key, directive);
    }

    return [...byKey.values()];
  }

  private directiveWeight(directive: ExecutiveDirective): number {
    const base: Record<ExecutiveDirectiveType, number> = {
      escalate: 100,
      pause: 90,
      cancel: 85,
      reallocate: 75,
      reprioritize: 70,
      resume: 60,
      start: 50,
      defer: 40,
    };

    return base[directive.type] + (directive.priority ?? 0) / 1000;
  }

  private deadlinePressure(remainingMs: number): number {
    if (remainingMs <= 0) return 1;
    return this.clamp(1 - remainingMs / Math.max(this.deadlineRiskWindowMs, 1));
  }

  private normalise(value: number): number {
    if (!Number.isFinite(value)) return 0;
    return this.clamp(value > 1 ? value / 100 : value);
  }

  private validateState(state: ExecutiveControlState): void {
    if (!state.health || !Number.isFinite(state.health.overallHealth)) {
      throw new Error("A valid system health snapshot is required");
    }

    const objectiveIds = new Set<string>();
    for (const objective of state.objectives) {
      if (!objective.objectiveId.trim()) throw new Error("Objective id is required");
      if (objectiveIds.has(objective.objectiveId)) {
        throw new Error(`Duplicate objective id: ${objective.objectiveId}`);
      }
      objectiveIds.add(objective.objectiveId);
    }

    const workItemIds = new Set<string>();
    for (const item of state.workItems) {
      if (!objectiveIds.has(item.objectiveId)) {
        throw new Error(
          `Work item ${item.workItemId} references unknown objective ${item.objectiveId}`,
        );
      }
      if (workItemIds.has(item.workItemId)) {
        throw new Error(`Duplicate work item id: ${item.workItemId}`);
      }
      workItemIds.add(item.workItemId);
    }
  }

  private clamp(value: number): number {
    return Math.max(0, Math.min(1, value));
  }
}
