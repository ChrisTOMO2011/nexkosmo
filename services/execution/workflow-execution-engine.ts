export type WorkflowStatus =
  | "pending"
  | "running"
  | "waiting_for_approval"
  | "blocked"
  | "completed"
  | "failed"
  | "cancelled";

export type StepStatus =
  | "pending"
  | "queued"
  | "running"
  | "waiting_for_approval"
  | "completed"
  | "failed"
  | "skipped";

export interface WorkflowStep {
  id: string;
  name: string;
  handler: string;
  dependsOn?: string[];
  requiresApproval?: boolean;
  retryLimit?: number;
  timeoutMs?: number;
  input?: Record<string, unknown>;
}

export interface WorkflowDefinition {
  id: string;
  name: string;
  version: number;
  steps: WorkflowStep[];
}

export interface StepExecution {
  stepId: string;
  status: StepStatus;
  attempts: number;
  startedAt?: string;
  completedAt?: string;
  output?: Record<string, unknown>;
  error?: string;
}

export interface WorkflowRun {
  id: string;
  workflowId: string;
  workflowVersion: number;
  status: WorkflowStatus;
  context: Record<string, unknown>;
  steps: StepExecution[];
  createdAt: string;
  updatedAt: string;
}

export interface JobQueue {
  enqueue(job: {
    runId: string;
    stepId: string;
    handler: string;
    input: Record<string, unknown>;
    timeoutMs?: number;
  }): Promise<void>;
}

export interface WorkflowRepository {
  create(run: WorkflowRun): Promise<void>;
  get(runId: string): Promise<WorkflowRun | null>;
  save(run: WorkflowRun): Promise<void>;
}

export interface ApprovalGateway {
  request(input: {
    runId: string;
    stepId: string;
    workflowId: string;
    context: Record<string, unknown>;
  }): Promise<void>;
}

export interface EventBus {
  publish(event: string, payload: Record<string, unknown>): Promise<void>;
}

export interface IdGenerator {
  generate(prefix: string): string;
}

export class WorkflowExecutionEngine {
  constructor(
    private readonly repository: WorkflowRepository,
    private readonly queue: JobQueue,
    private readonly approvals: ApprovalGateway,
    private readonly events: EventBus,
    private readonly ids: IdGenerator,
  ) {}

  async start(
    definition: WorkflowDefinition,
    context: Record<string, unknown>,
  ): Promise<WorkflowRun> {
    this.validateDefinition(definition);
    const now = new Date().toISOString();
    const run: WorkflowRun = {
      id: this.ids.generate("workflow-run"),
      workflowId: definition.id,
      workflowVersion: definition.version,
      status: "pending",
      context,
      steps: definition.steps.map((step) => ({
        stepId: step.id,
        status: "pending",
        attempts: 0,
      })),
      createdAt: now,
      updatedAt: now,
    };

    await this.repository.create(run);
    await this.events.publish("workflow.started", {
      runId: run.id,
      workflowId: run.workflowId,
    });
    return this.scheduleReadySteps(definition, run);
  }

  async completeStep(
    definition: WorkflowDefinition,
    runId: string,
    stepId: string,
    output: Record<string, unknown> = {},
  ): Promise<WorkflowRun> {
    const run = await this.requireRun(runId);
    const execution = this.requireExecution(run, stepId);
    execution.status = "completed";
    execution.output = output;
    execution.completedAt = new Date().toISOString();
    run.updatedAt = execution.completedAt;

    await this.events.publish("workflow.step.completed", { runId, stepId });
    return this.scheduleReadySteps(definition, run);
  }

  async failStep(
    definition: WorkflowDefinition,
    runId: string,
    stepId: string,
    error: Error,
  ): Promise<WorkflowRun> {
    const run = await this.requireRun(runId);
    const step = this.requireStep(definition, stepId);
    const execution = this.requireExecution(run, stepId);
    execution.error = error.message;

    if (execution.attempts <= (step.retryLimit ?? 0)) {
      execution.status = "pending";
      await this.events.publish("workflow.step.retrying", {
        runId,
        stepId,
        attempt: execution.attempts,
      });
      return this.scheduleReadySteps(definition, run);
    }

    execution.status = "failed";
    run.status = "failed";
    run.updatedAt = new Date().toISOString();
    await this.repository.save(run);
    await this.events.publish("workflow.failed", {
      runId,
      stepId,
      error: error.message,
    });
    return run;
  }

  async approveStep(
    definition: WorkflowDefinition,
    runId: string,
    stepId: string,
  ): Promise<WorkflowRun> {
    const run = await this.requireRun(runId);
    const execution = this.requireExecution(run, stepId);
    if (execution.status !== "waiting_for_approval") {
      throw new Error(`Step ${stepId} is not waiting for approval`);
    }
    execution.status = "pending";
    run.status = "running";
    await this.events.publish("workflow.step.approved", { runId, stepId });
    return this.scheduleReadySteps(definition, run, new Set([stepId]));
  }

  async cancel(runId: string): Promise<WorkflowRun> {
    const run = await this.requireRun(runId);
    run.status = "cancelled";
    run.updatedAt = new Date().toISOString();
    await this.repository.save(run);
    await this.events.publish("workflow.cancelled", { runId });
    return run;
  }

  private async scheduleReadySteps(
    definition: WorkflowDefinition,
    run: WorkflowRun,
    approvedSteps: Set<string> = new Set(),
  ): Promise<WorkflowRun> {
    if (["failed", "cancelled", "completed"].includes(run.status)) return run;

    for (const step of definition.steps) {
      const execution = this.requireExecution(run, step.id);
      if (execution.status !== "pending") continue;

      const dependencies = step.dependsOn ?? [];
      const ready = dependencies.every(
        (dependencyId) =>
          this.requireExecution(run, dependencyId).status === "completed",
      );
      if (!ready) continue;

      if (step.requiresApproval && !approvedSteps.has(step.id)) {
        execution.status = "waiting_for_approval";
        run.status = "waiting_for_approval";
        await this.approvals.request({
          runId: run.id,
          stepId: step.id,
          workflowId: run.workflowId,
          context: run.context,
        });
        continue;
      }

      execution.status = "queued";
      execution.attempts += 1;
      execution.startedAt = new Date().toISOString();
      run.status = "running";
      await this.queue.enqueue({
        runId: run.id,
        stepId: step.id,
        handler: step.handler,
        input: { ...run.context, ...(step.input ?? {}) },
        timeoutMs: step.timeoutMs,
      });
      await this.events.publish("workflow.step.queued", {
        runId: run.id,
        stepId: step.id,
        handler: step.handler,
      });
    }

    const finished = run.steps.every((step) =>
      ["completed", "skipped"].includes(step.status),
    );
    if (finished) {
      run.status = "completed";
      await this.events.publish("workflow.completed", { runId: run.id });
    }

    run.updatedAt = new Date().toISOString();
    await this.repository.save(run);
    return run;
  }

  private validateDefinition(definition: WorkflowDefinition): void {
    const ids = new Set(definition.steps.map((step) => step.id));
    if (ids.size !== definition.steps.length) {
      throw new Error("Workflow step IDs must be unique");
    }
    for (const step of definition.steps) {
      for (const dependency of step.dependsOn ?? []) {
        if (!ids.has(dependency)) {
          throw new Error(`Unknown dependency ${dependency} for step ${step.id}`);
        }
      }
    }
  }

  private async requireRun(runId: string): Promise<WorkflowRun> {
    const run = await this.repository.get(runId);
    if (!run) throw new Error(`Workflow run ${runId} was not found`);
    return run;
  }

  private requireStep(
    definition: WorkflowDefinition,
    stepId: string,
  ): WorkflowStep {
    const step = definition.steps.find((candidate) => candidate.id === stepId);
    if (!step) throw new Error(`Workflow step ${stepId} was not found`);
    return step;
  }

  private requireExecution(run: WorkflowRun, stepId: string): StepExecution {
    const execution = run.steps.find((candidate) => candidate.stepId === stepId);
    if (!execution) throw new Error(`Execution for step ${stepId} was not found`);
    return execution;
  }
}
