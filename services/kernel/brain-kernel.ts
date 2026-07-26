export type BrainCommandType =
  | "asset.ingest"
  | "asset.classify"
  | "asset.register"
  | "asset.resolve_dependencies"
  | "production.start"
  | "production.advance"
  | "workflow.start"
  | "workflow.cancel"
  | "agent.dispatch"
  | "reasoning.query";

export interface BrainCommand<TPayload = Record<string, unknown>> {
  id: string;
  type: BrainCommandType;
  payload: TPayload;
  actorId: string;
  correlationId?: string;
  causationId?: string;
  issuedAt: string;
  metadata?: Record<string, unknown>;
}

export interface BrainCommandResult<TData = unknown> {
  commandId: string;
  type: BrainCommandType;
  status: "accepted" | "completed" | "rejected" | "failed";
  data?: TData;
  error?: string;
  startedAt: string;
  completedAt: string;
}

export interface BrainContext {
  commandId: string;
  actorId: string;
  correlationId: string;
  causationId?: string;
  issuedAt: string;
  metadata: Record<string, unknown>;
}

export interface BrainCommandHandler<TPayload = unknown, TResult = unknown> {
  readonly commandType: BrainCommandType;
  execute(payload: TPayload, context: BrainContext): Promise<TResult>;
}

export interface BrainPolicyDecision {
  allowed: boolean;
  reason?: string;
}

export interface BrainPolicyEngine {
  authorise(command: BrainCommand): Promise<BrainPolicyDecision>;
}

export interface BrainAuditLog {
  record(entry: {
    event: string;
    command: BrainCommand;
    result?: BrainCommandResult;
    timestamp: string;
  }): Promise<void>;
}

export interface BrainEventBus {
  publish(event: string, payload: Record<string, unknown>): Promise<void>;
}

export interface BrainIdempotencyStore {
  get(commandId: string): Promise<BrainCommandResult | null>;
  put(commandId: string, result: BrainCommandResult): Promise<void>;
}

export interface BrainHealthIndicator {
  name: string;
  check(): Promise<{
    healthy: boolean;
    details?: Record<string, unknown>;
  }>;
}

export interface BrainKernelOptions {
  failOnUnknownCommand?: boolean;
}

export interface BrainHealthReport {
  status: "healthy" | "degraded" | "unhealthy";
  checkedAt: string;
  indicators: Array<{
    name: string;
    healthy: boolean;
    details?: Record<string, unknown>;
  }>;
}

export class UnknownBrainCommandError extends Error {
  constructor(type: string) {
    super(`No Brain command handler is registered for ${type}`);
    this.name = "UnknownBrainCommandError";
  }
}

export class DuplicateBrainHandlerError extends Error {
  constructor(type: BrainCommandType) {
    super(`A Brain command handler is already registered for ${type}`);
    this.name = "DuplicateBrainHandlerError";
  }
}

export class BrainKernel {
  private readonly handlers = new Map<
    BrainCommandType,
    BrainCommandHandler<unknown, unknown>
  >();

  private readonly healthIndicators: BrainHealthIndicator[] = [];
  private readonly failOnUnknownCommand: boolean;

  constructor(
    private readonly policies: BrainPolicyEngine,
    private readonly audit: BrainAuditLog,
    private readonly events: BrainEventBus,
    private readonly idempotency: BrainIdempotencyStore,
    options: BrainKernelOptions = {},
  ) {
    this.failOnUnknownCommand = options.failOnUnknownCommand ?? true;
  }

  registerHandler<TPayload, TResult>(
    handler: BrainCommandHandler<TPayload, TResult>,
  ): void {
    if (this.handlers.has(handler.commandType)) {
      throw new DuplicateBrainHandlerError(handler.commandType);
    }

    this.handlers.set(
      handler.commandType,
      handler as BrainCommandHandler<unknown, unknown>,
    );
  }

  registerHealthIndicator(indicator: BrainHealthIndicator): void {
    if (this.healthIndicators.some((item) => item.name === indicator.name)) {
      throw new Error(`Health indicator ${indicator.name} is already registered`);
    }
    this.healthIndicators.push(indicator);
  }

  async execute<TPayload, TResult>(
    command: BrainCommand<TPayload>,
  ): Promise<BrainCommandResult<TResult>> {
    this.validateCommand(command);

    const existing = await this.idempotency.get(command.id);
    if (existing) return existing as BrainCommandResult<TResult>;

    const startedAt = new Date().toISOString();
    await this.audit.record({
      event: "brain.command.received",
      command: command as BrainCommand,
      timestamp: startedAt,
    });

    const policyDecision = await this.policies.authorise(
      command as BrainCommand,
    );

    if (!policyDecision.allowed) {
      const rejected: BrainCommandResult<TResult> = {
        commandId: command.id,
        type: command.type,
        status: "rejected",
        error: policyDecision.reason ?? "Command rejected by Brain policy",
        startedAt,
        completedAt: new Date().toISOString(),
      };
      await this.finalise(command as BrainCommand, rejected);
      return rejected;
    }

    const handler = this.handlers.get(command.type);
    if (!handler) {
      if (this.failOnUnknownCommand) {
        throw new UnknownBrainCommandError(command.type);
      }

      const rejected: BrainCommandResult<TResult> = {
        commandId: command.id,
        type: command.type,
        status: "rejected",
        error: `No handler registered for ${command.type}`,
        startedAt,
        completedAt: new Date().toISOString(),
      };
      await this.finalise(command as BrainCommand, rejected);
      return rejected;
    }

    const context: BrainContext = {
      commandId: command.id,
      actorId: command.actorId,
      correlationId: command.correlationId ?? command.id,
      causationId: command.causationId,
      issuedAt: command.issuedAt,
      metadata: command.metadata ?? {},
    };

    await this.events.publish("brain.command.accepted", {
      commandId: command.id,
      type: command.type,
      actorId: command.actorId,
      correlationId: context.correlationId,
    });

    try {
      const data = await handler.execute(command.payload, context);
      const completed: BrainCommandResult<TResult> = {
        commandId: command.id,
        type: command.type,
        status: "completed",
        data: data as TResult,
        startedAt,
        completedAt: new Date().toISOString(),
      };
      await this.finalise(command as BrainCommand, completed);
      return completed;
    } catch (error) {
      const failed: BrainCommandResult<TResult> = {
        commandId: command.id,
        type: command.type,
        status: "failed",
        error: error instanceof Error ? error.message : "Unknown Brain failure",
        startedAt,
        completedAt: new Date().toISOString(),
      };
      await this.finalise(command as BrainCommand, failed);
      return failed;
    }
  }

  async health(): Promise<BrainHealthReport> {
    const indicators = await Promise.all(
      this.healthIndicators.map(async (indicator) => {
        try {
          const result = await indicator.check();
          return {
            name: indicator.name,
            healthy: result.healthy,
            details: result.details,
          };
        } catch (error) {
          return {
            name: indicator.name,
            healthy: false,
            details: {
              error: error instanceof Error ? error.message : "Unknown error",
            },
          };
        }
      }),
    );

    const unhealthyCount = indicators.filter((item) => !item.healthy).length;
    const status: BrainHealthReport["status"] =
      unhealthyCount === 0
        ? "healthy"
        : unhealthyCount === indicators.length
          ? "unhealthy"
          : "degraded";

    return {
      status,
      checkedAt: new Date().toISOString(),
      indicators,
    };
  }

  listRegisteredCommands(): BrainCommandType[] {
    return [...this.handlers.keys()].sort();
  }

  private async finalise<TResult>(
    command: BrainCommand,
    result: BrainCommandResult<TResult>,
  ): Promise<void> {
    await this.idempotency.put(command.id, result);
    await this.audit.record({
      event: `brain.command.${result.status}`,
      command,
      result,
      timestamp: result.completedAt,
    });
    await this.events.publish(`brain.command.${result.status}`, {
      commandId: result.commandId,
      type: result.type,
      status: result.status,
      correlationId: command.correlationId ?? command.id,
      error: result.error,
    });
  }

  private validateCommand(command: BrainCommand): void {
    if (!command.id.trim()) throw new Error("Brain command id is required");
    if (!command.actorId.trim()) throw new Error("Brain command actorId is required");
    if (!command.type) throw new Error("Brain command type is required");
    if (!command.issuedAt || Number.isNaN(Date.parse(command.issuedAt))) {
      throw new Error("Brain command issuedAt must be a valid ISO date");
    }
    if (command.payload === undefined || command.payload === null) {
      throw new Error("Brain command payload is required");
    }
  }
}
