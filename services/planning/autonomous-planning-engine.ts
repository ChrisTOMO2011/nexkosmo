export type PlanStatus =
  | "draft"
  | "ready"
  | "running"
  | "blocked"
  | "completed"
  | "cancelled";

export type PlanNodeStatus =
  | "pending"
  | "ready"
  | "running"
  | "blocked"
  | "completed"
  | "failed"
  | "cancelled";

export type PlanNodeKind =
  | "production"
  | "sequence"
  | "scene"
  | "shot"
  | "asset"
  | "workflow"
  | "agent_task"
  | "approval"
  | "milestone";

export interface PlanningObjective {
  objectiveId: string;
  title: string;
  description: string;
  actorId: string;
  projectId?: string;
  deadline?: string;
  constraints?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface PlanNode {
  nodeId: string;
  kind: PlanNodeKind;
  title: string;
  description?: string;
  status: PlanNodeStatus;
  dependencies: string[];
  requiredCapabilities?: string[];
  estimatedDurationMs?: number;
  priority: number;
  payload: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface AutonomousPlan {
  planId: string;
  objective: PlanningObjective;
  status: PlanStatus;
  version: number;
  nodes: PlanNode[];
  createdAt: string;
  updatedAt: string;
}

export interface PlanProposal {
  nodes: Array<
    Omit<PlanNode, "status" | "createdAt" | "updatedAt"> & {
      status?: PlanNodeStatus;
    }
  >;
}

export interface PlanningModel {
  decompose(objective: PlanningObjective): Promise<PlanProposal>;
  revise(input: {
    plan: AutonomousPlan;
    reason: string;
    context?: Record<string, unknown>;
  }): Promise<PlanProposal>;
}

export interface PlanRepository {
  save(plan: AutonomousPlan): Promise<void>;
  get(planId: string): Promise<AutonomousPlan | null>;
}

export interface PlanDispatcher {
  dispatch(node: PlanNode, plan: AutonomousPlan): Promise<void>;
  cancel(node: PlanNode, plan: AutonomousPlan): Promise<void>;
}

export interface PlanningEventBus {
  publish(event: string, payload: Record<string, unknown>): Promise<void>;
}

export interface PlanningIdGenerator {
  next(prefix: string): string;
}

export interface PlanValidationIssue {
  code: string;
  message: string;
  nodeId?: string;
}

export class InvalidPlanError extends Error {
  constructor(readonly issues: PlanValidationIssue[]) {
    super(issues.map((issue) => issue.message).join("; "));
    this.name = "InvalidPlanError";
  }
}

export class AutonomousPlanningEngine {
  constructor(
    private readonly model: PlanningModel,
    private readonly plans: PlanRepository,
    private readonly dispatcher: PlanDispatcher,
    private readonly events: PlanningEventBus,
    private readonly ids: PlanningIdGenerator,
  ) {}

  async createPlan(objective: PlanningObjective): Promise<AutonomousPlan> {
    this.validateObjective(objective);
    const proposal = await this.model.decompose(objective);
    const now = new Date().toISOString();

    const plan: AutonomousPlan = {
      planId: this.ids.next("plan"),
      objective,
      status: "draft",
      version: 1,
      nodes: proposal.nodes.map((node) => ({
        ...node,
        status: node.status ?? "pending",
        dependencies: [...new Set(node.dependencies)],
        priority: Number.isFinite(node.priority) ? node.priority : 0,
        payload: node.payload ?? {},
        createdAt: now,
        updatedAt: now,
      })),
      createdAt: now,
      updatedAt: now,
    };

    const issues = this.validatePlan(plan);
    if (issues.length > 0) throw new InvalidPlanError(issues);

    this.refreshReadiness(plan);
    plan.status = "ready";
    plan.updatedAt = new Date().toISOString();

    await this.plans.save(plan);
    await this.events.publish("planning.plan.created", {
      planId: plan.planId,
      objectiveId: objective.objectiveId,
      nodeCount: plan.nodes.length,
      version: plan.version,
    });

    return plan;
  }

  async start(planId: string): Promise<AutonomousPlan> {
    const plan = await this.requirePlan(planId);
    if (plan.status === "cancelled" || plan.status === "completed") {
      throw new Error(`Plan ${planId} cannot be started from ${plan.status}`);
    }

    plan.status = "running";
    plan.updatedAt = new Date().toISOString();
    await this.dispatchReadyNodes(plan);
    await this.persistAndPublish(plan, "planning.plan.started");
    return plan;
  }

  async completeNode(
    planId: string,
    nodeId: string,
    output: Record<string, unknown> = {},
  ): Promise<AutonomousPlan> {
    const plan = await this.requirePlan(planId);
    const node = this.requireNode(plan, nodeId);

    node.status = "completed";
    node.payload = { ...node.payload, output };
    node.updatedAt = new Date().toISOString();

    this.refreshReadiness(plan);
    await this.dispatchReadyNodes(plan);
    this.refreshPlanStatus(plan);
    await this.persistAndPublish(plan, "planning.node.completed", { nodeId });
    return plan;
  }

  async failNode(
    planId: string,
    nodeId: string,
    error: string,
  ): Promise<AutonomousPlan> {
    const plan = await this.requirePlan(planId);
    const node = this.requireNode(plan, nodeId);

    node.status = "failed";
    node.payload = { ...node.payload, error };
    node.updatedAt = new Date().toISOString();
    plan.status = "blocked";
    plan.updatedAt = node.updatedAt;

    await this.persistAndPublish(plan, "planning.node.failed", {
      nodeId,
      error,
    });
    return plan;
  }

  async revisePlan(
    planId: string,
    reason: string,
    context?: Record<string, unknown>,
  ): Promise<AutonomousPlan> {
    const plan = await this.requirePlan(planId);
    if (plan.status === "cancelled" || plan.status === "completed") {
      throw new Error(`Plan ${planId} cannot be revised from ${plan.status}`);
    }

    const proposal = await this.model.revise({ plan, reason, context });
    const now = new Date().toISOString();
    const existingById = new Map(plan.nodes.map((node) => [node.nodeId, node]));

    plan.nodes = proposal.nodes.map((proposed) => {
      const existing = existingById.get(proposed.nodeId);
      return {
        ...proposed,
        status: existing?.status ?? proposed.status ?? "pending",
        dependencies: [...new Set(proposed.dependencies)],
        priority: Number.isFinite(proposed.priority) ? proposed.priority : 0,
        payload: {
          ...(existing?.payload ?? {}),
          ...(proposed.payload ?? {}),
        },
        createdAt: existing?.createdAt ?? now,
        updatedAt: now,
      };
    });

    plan.version += 1;
    plan.status = "ready";
    plan.updatedAt = now;

    const issues = this.validatePlan(plan);
    if (issues.length > 0) throw new InvalidPlanError(issues);

    this.refreshReadiness(plan);
    await this.plans.save(plan);
    await this.events.publish("planning.plan.revised", {
      planId,
      version: plan.version,
      reason,
      nodeCount: plan.nodes.length,
    });
    return plan;
  }

  async cancel(planId: string): Promise<AutonomousPlan> {
    const plan = await this.requirePlan(planId);
    if (plan.status === "completed") {
      throw new Error(`Completed plan ${planId} cannot be cancelled`);
    }

    for (const node of plan.nodes) {
      if (node.status === "running" || node.status === "ready") {
        await this.dispatcher.cancel(node, plan);
      }
      if (node.status !== "completed") {
        node.status = "cancelled";
        node.updatedAt = new Date().toISOString();
      }
    }

    plan.status = "cancelled";
    plan.updatedAt = new Date().toISOString();
    await this.persistAndPublish(plan, "planning.plan.cancelled");
    return plan;
  }

  validatePlan(plan: AutonomousPlan): PlanValidationIssue[] {
    const issues: PlanValidationIssue[] = [];
    const ids = new Set<string>();

    for (const node of plan.nodes) {
      if (!node.nodeId.trim()) {
        issues.push({ code: "NODE_ID_REQUIRED", message: "Every plan node requires an id" });
        continue;
      }
      if (ids.has(node.nodeId)) {
        issues.push({
          code: "DUPLICATE_NODE_ID",
          message: `Duplicate plan node id ${node.nodeId}`,
          nodeId: node.nodeId,
        });
      }
      ids.add(node.nodeId);
    }

    for (const node of plan.nodes) {
      for (const dependency of node.dependencies) {
        if (!ids.has(dependency)) {
          issues.push({
            code: "MISSING_DEPENDENCY",
            message: `Node ${node.nodeId} depends on missing node ${dependency}`,
            nodeId: node.nodeId,
          });
        }
        if (dependency === node.nodeId) {
          issues.push({
            code: "SELF_DEPENDENCY",
            message: `Node ${node.nodeId} cannot depend on itself`,
            nodeId: node.nodeId,
          });
        }
      }
    }

    if (this.hasCycle(plan.nodes)) {
      issues.push({
        code: "DEPENDENCY_CYCLE",
        message: "Plan contains a dependency cycle",
      });
    }

    return issues;
  }

  private async dispatchReadyNodes(plan: AutonomousPlan): Promise<void> {
    const ready = plan.nodes
      .filter((node) => node.status === "ready")
      .sort((left, right) => right.priority - left.priority);

    for (const node of ready) {
      node.status = "running";
      node.updatedAt = new Date().toISOString();
      await this.dispatcher.dispatch(node, plan);
      await this.events.publish("planning.node.dispatched", {
        planId: plan.planId,
        nodeId: node.nodeId,
        kind: node.kind,
      });
    }
  }

  private refreshReadiness(plan: AutonomousPlan): void {
    const byId = new Map(plan.nodes.map((node) => [node.nodeId, node]));

    for (const node of plan.nodes) {
      if (node.status !== "pending" && node.status !== "blocked") continue;

      const dependencies = node.dependencies
        .map((dependencyId) => byId.get(dependencyId))
        .filter((dependency): dependency is PlanNode => Boolean(dependency));

      if (dependencies.some((dependency) => dependency.status === "failed")) {
        node.status = "blocked";
      } else if (dependencies.every((dependency) => dependency.status === "completed")) {
        node.status = "ready";
      }
      node.updatedAt = new Date().toISOString();
    }
  }

  private refreshPlanStatus(plan: AutonomousPlan): void {
    if (plan.nodes.every((node) => node.status === "completed")) {
      plan.status = "completed";
    } else if (plan.nodes.some((node) => node.status === "failed" || node.status === "blocked")) {
      plan.status = "blocked";
    } else {
      plan.status = "running";
    }
    plan.updatedAt = new Date().toISOString();
  }

  private hasCycle(nodes: PlanNode[]): boolean {
    const dependencies = new Map(nodes.map((node) => [node.nodeId, node.dependencies]));
    const visiting = new Set<string>();
    const visited = new Set<string>();

    const visit = (nodeId: string): boolean => {
      if (visiting.has(nodeId)) return true;
      if (visited.has(nodeId)) return false;

      visiting.add(nodeId);
      for (const dependency of dependencies.get(nodeId) ?? []) {
        if (visit(dependency)) return true;
      }
      visiting.delete(nodeId);
      visited.add(nodeId);
      return false;
    };

    return nodes.some((node) => visit(node.nodeId));
  }

  private validateObjective(objective: PlanningObjective): void {
    if (!objective.objectiveId.trim()) throw new Error("Objective id is required");
    if (!objective.title.trim()) throw new Error("Objective title is required");
    if (!objective.description.trim()) throw new Error("Objective description is required");
    if (!objective.actorId.trim()) throw new Error("Objective actorId is required");
    if (objective.deadline && Number.isNaN(Date.parse(objective.deadline))) {
      throw new Error("Objective deadline must be a valid ISO date");
    }
  }

  private async requirePlan(planId: string): Promise<AutonomousPlan> {
    const plan = await this.plans.get(planId);
    if (!plan) throw new Error(`Plan ${planId} was not found`);
    return plan;
  }

  private requireNode(plan: AutonomousPlan, nodeId: string): PlanNode {
    const node = plan.nodes.find((candidate) => candidate.nodeId === nodeId);
    if (!node) throw new Error(`Plan node ${nodeId} was not found`);
    return node;
  }

  private async persistAndPublish(
    plan: AutonomousPlan,
    event: string,
    payload: Record<string, unknown> = {},
  ): Promise<void> {
    plan.updatedAt = new Date().toISOString();
    await this.plans.save(plan);
    await this.events.publish(event, {
      planId: plan.planId,
      status: plan.status,
      version: plan.version,
      ...payload,
    });
  }
}
