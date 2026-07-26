export type AgentStatus =
  | "offline"
  | "idle"
  | "reserved"
  | "running"
  | "paused"
  | "failed";

export interface AgentCapability {
  name: string;
  version: string;
  assetTypes?: string[];
  departments?: string[];
  handlers: string[];
}

export interface AgentRegistration {
  agentId: string;
  displayName: string;
  agentType: string;
  capabilities: AgentCapability[];
  maxConcurrentJobs: number;
  metadata?: Record<string, unknown>;
}

export interface AgentState extends AgentRegistration {
  status: AgentStatus;
  activeJobs: number;
  lastHeartbeatAt?: string;
  registeredAt: string;
  updatedAt: string;
}

export interface AgentJob {
  jobId: string;
  runId: string;
  stepId: string;
  handler: string;
  input: Record<string, unknown>;
  requiredCapabilities?: string[];
  assetType?: string;
  department?: string;
  priority?: number;
  timeoutMs?: number;
}

export interface AgentJobResult {
  jobId: string;
  agentId: string;
  status: "completed" | "failed";
  output?: Record<string, unknown>;
  error?: string;
  producedAssetIds?: string[];
  relationshipSuggestions?: Array<Record<string, unknown>>;
  completedAt: string;
}

export interface AgentRepository {
  upsert(agent: AgentState): Promise<void>;
  get(agentId: string): Promise<AgentState | null>;
  listAvailable(): Promise<AgentState[]>;
  save(agent: AgentState): Promise<void>;
}

export interface AgentTransport {
  dispatch(agentId: string, job: AgentJob): Promise<void>;
  cancel(agentId: string, jobId: string): Promise<void>;
}

export interface AgentAssignmentRepository {
  assign(input: {
    job: AgentJob;
    agentId: string;
    assignedAt: string;
  }): Promise<void>;
  complete(result: AgentJobResult): Promise<void>;
  findAgentForJob(jobId: string): Promise<string | null>;
}

export interface AgentEventBus {
  publish(event: string, payload: Record<string, unknown>): Promise<void>;
}

export interface AgentRuntimeOptions {
  heartbeatTimeoutMs?: number;
}

export class NoCapableAgentError extends Error {
  constructor(job: AgentJob) {
    super(`No capable AI agent is available for handler ${job.handler}`);
    this.name = "NoCapableAgentError";
  }
}

export class AIAgentRuntime {
  private readonly heartbeatTimeoutMs: number;

  constructor(
    private readonly agents: AgentRepository,
    private readonly assignments: AgentAssignmentRepository,
    private readonly transport: AgentTransport,
    private readonly events: AgentEventBus,
    options: AgentRuntimeOptions = {},
  ) {
    this.heartbeatTimeoutMs = options.heartbeatTimeoutMs ?? 60_000;
  }

  async register(registration: AgentRegistration): Promise<AgentState> {
    if (registration.maxConcurrentJobs < 1) {
      throw new Error("Agent maxConcurrentJobs must be at least 1");
    }

    const now = new Date().toISOString();
    const existing = await this.agents.get(registration.agentId);
    const state: AgentState = {
      ...registration,
      status: "idle",
      activeJobs: existing?.activeJobs ?? 0,
      lastHeartbeatAt: now,
      registeredAt: existing?.registeredAt ?? now,
      updatedAt: now,
    };

    await this.agents.upsert(state);
    await this.events.publish("agent.registered", {
      agentId: state.agentId,
      agentType: state.agentType,
      capabilities: state.capabilities.map((capability) => capability.name),
    });
    return state;
  }

  async heartbeat(agentId: string): Promise<AgentState> {
    const agent = await this.requireAgent(agentId);
    const now = new Date().toISOString();
    agent.lastHeartbeatAt = now;
    agent.updatedAt = now;
    if (agent.status === "offline") {
      agent.status = agent.activeJobs > 0 ? "running" : "idle";
    }
    await this.agents.save(agent);
    return agent;
  }

  async dispatch(job: AgentJob): Promise<AgentState> {
    const candidates = (await this.agents.listAvailable())
      .filter((agent) => this.isHealthy(agent))
      .filter((agent) => agent.status === "idle" || agent.status === "running")
      .filter((agent) => agent.activeJobs < agent.maxConcurrentJobs)
      .filter((agent) => this.canHandle(agent, job))
      .sort((left, right) => this.score(right, job) - this.score(left, job));

    const agent = candidates[0];
    if (!agent) throw new NoCapableAgentError(job);

    const now = new Date().toISOString();
    agent.activeJobs += 1;
    agent.status = agent.activeJobs >= agent.maxConcurrentJobs ? "reserved" : "running";
    agent.updatedAt = now;

    await this.agents.save(agent);
    await this.assignments.assign({ job, agentId: agent.agentId, assignedAt: now });

    try {
      await this.transport.dispatch(agent.agentId, job);
      await this.events.publish("agent.job.dispatched", {
        agentId: agent.agentId,
        jobId: job.jobId,
        runId: job.runId,
        stepId: job.stepId,
      });
      return agent;
    } catch (error) {
      agent.activeJobs = Math.max(0, agent.activeJobs - 1);
      agent.status = agent.activeJobs > 0 ? "running" : "idle";
      agent.updatedAt = new Date().toISOString();
      await this.agents.save(agent);
      throw error;
    }
  }

  async reportResult(result: AgentJobResult): Promise<void> {
    const agent = await this.requireAgent(result.agentId);
    agent.activeJobs = Math.max(0, agent.activeJobs - 1);
    agent.status = result.status === "failed"
      ? "failed"
      : agent.activeJobs > 0
        ? "running"
        : "idle";
    agent.updatedAt = result.completedAt;

    await this.assignments.complete(result);
    await this.agents.save(agent);
    await this.events.publish(
      result.status === "completed" ? "agent.job.completed" : "agent.job.failed",
      {
        agentId: result.agentId,
        jobId: result.jobId,
        producedAssetIds: result.producedAssetIds ?? [],
        error: result.error,
      },
    );
  }

  async cancel(jobId: string): Promise<void> {
    const agentId = await this.assignments.findAgentForJob(jobId);
    if (!agentId) throw new Error(`No agent assignment exists for job ${jobId}`);
    await this.transport.cancel(agentId, jobId);
    await this.events.publish("agent.job.cancelled", { agentId, jobId });
  }

  async markStaleAgentsOffline(now = Date.now()): Promise<string[]> {
    const agents = await this.agents.listAvailable();
    const markedOffline: string[] = [];

    for (const agent of agents) {
      if (!agent.lastHeartbeatAt) continue;
      const age = now - Date.parse(agent.lastHeartbeatAt);
      if (age <= this.heartbeatTimeoutMs || agent.status === "offline") continue;

      agent.status = "offline";
      agent.updatedAt = new Date(now).toISOString();
      await this.agents.save(agent);
      await this.events.publish("agent.offline", { agentId: agent.agentId });
      markedOffline.push(agent.agentId);
    }

    return markedOffline;
  }

  private canHandle(agent: AgentState, job: AgentJob): boolean {
    return agent.capabilities.some((capability) => {
      if (!capability.handlers.includes(job.handler)) return false;
      if (
        job.requiredCapabilities?.length &&
        !job.requiredCapabilities.every((required) =>
          agent.capabilities.some((candidate) => candidate.name === required),
        )
      ) return false;
      if (job.assetType && capability.assetTypes?.length) {
        if (!capability.assetTypes.includes(job.assetType)) return false;
      }
      if (job.department && capability.departments?.length) {
        if (!capability.departments.includes(job.department)) return false;
      }
      return true;
    });
  }

  private score(agent: AgentState, job: AgentJob): number {
    const matchingCapabilities = agent.capabilities.filter((capability) =>
      capability.handlers.includes(job.handler),
    ).length;
    const availableCapacity = agent.maxConcurrentJobs - agent.activeJobs;
    const priority = job.priority ?? 0;
    return matchingCapabilities * 100 + availableCapacity * 10 + priority;
  }

  private isHealthy(agent: AgentState): boolean {
    if (!agent.lastHeartbeatAt) return false;
    return Date.now() - Date.parse(agent.lastHeartbeatAt) <= this.heartbeatTimeoutMs;
  }

  private async requireAgent(agentId: string): Promise<AgentState> {
    const agent = await this.agents.get(agentId);
    if (!agent) throw new Error(`AI agent ${agentId} was not found`);
    return agent;
  }
}
