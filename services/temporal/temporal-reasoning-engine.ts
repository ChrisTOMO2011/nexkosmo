export type TemporalRelation =
  | "before"
  | "after"
  | "meets"
  | "overlaps"
  | "during"
  | "starts"
  | "finishes"
  | "equals";

export type TemporalEventStatus =
  | "planned"
  | "scheduled"
  | "active"
  | "completed"
  | "cancelled"
  | "failed";

export interface TemporalPoint {
  instant: string;
  timezone?: string;
}

export interface TemporalInterval {
  start: string;
  end?: string;
  timezone?: string;
}

export interface TemporalEvent {
  eventId: string;
  subjectId: string;
  eventType: string;
  interval: TemporalInterval;
  status: TemporalEventStatus;
  confidence: number;
  sourceIds: string[];
  recurrence?: TemporalRecurrence;
  parentEventId?: string;
  causes?: string[];
  causedBy?: string[];
  payload?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
  version: number;
}

export interface TemporalRecurrence {
  frequency: "hourly" | "daily" | "weekly" | "monthly" | "yearly";
  interval?: number;
  count?: number;
  until?: string;
}

export interface TemporalAssertion {
  assertionId: string;
  subjectId: string;
  predicate: string;
  value: unknown;
  validDuring: TemporalInterval;
  confidence: number;
  sourceIds: string[];
  supersedesAssertionId?: string;
  createdAt: string;
}

export interface TimelineBranch {
  branchId: string;
  parentBranchId?: string;
  divergenceAt: string;
  label: string;
  probability: number;
  eventIds: string[];
  createdAt: string;
}

export interface TemporalConflict {
  conflictId: string;
  eventIds: string[];
  assertionIds: string[];
  reason: string;
  severity: "low" | "medium" | "high" | "critical";
  detectedAt: string;
}

export interface WorldStateSnapshot<TState = Record<string, unknown>> {
  snapshotId: string;
  branchId: string;
  effectiveAt: string;
  state: TState;
  appliedEventIds: string[];
  appliedAssertionIds: string[];
  createdAt: string;
}

export interface TemporalQuery {
  subjectId?: string;
  eventType?: string;
  status?: TemporalEventStatus;
  interval?: TemporalInterval;
  branchId?: string;
}

export interface TemporalReplayResult<TState = Record<string, unknown>> {
  branchId: string;
  from: string;
  to: string;
  initialState: TState;
  finalState: TState;
  appliedEvents: TemporalEvent[];
}

export interface TemporalRepository {
  saveEvent(event: TemporalEvent): Promise<void>;
  getEvent(eventId: string): Promise<TemporalEvent | null>;
  queryEvents(query: TemporalQuery): Promise<TemporalEvent[]>;
  saveAssertion(assertion: TemporalAssertion): Promise<void>;
  queryAssertions(subjectId: string, at: string): Promise<TemporalAssertion[]>;
  saveBranch(branch: TimelineBranch): Promise<void>;
  getBranch(branchId: string): Promise<TimelineBranch | null>;
  saveSnapshot(snapshot: WorldStateSnapshot): Promise<void>;
  getLatestSnapshot(branchId: string, at: string): Promise<WorldStateSnapshot | null>;
  saveConflict(conflict: TemporalConflict): Promise<void>;
}

export interface TemporalStateReducer<TState = Record<string, unknown>> {
  apply(state: TState, event: TemporalEvent): Promise<TState>;
}

export interface TemporalEventBus {
  publish(event: string, payload: Record<string, unknown>): Promise<void>;
}

export interface TemporalClock {
  now(): Date;
}

export interface TemporalIdGenerator {
  next(prefix: string): string;
}

export interface TemporalReasoningEngineOptions {
  defaultBranchId?: string;
  maximumReplayEvents?: number;
  conflictToleranceMs?: number;
}

export class TemporalValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "TemporalValidationError";
  }
}

export class TemporalReasoningEngine<TState = Record<string, unknown>> {
  private readonly defaultBranchId: string;
  private readonly maximumReplayEvents: number;
  private readonly conflictToleranceMs: number;

  constructor(
    private readonly repository: TemporalRepository,
    private readonly reducer: TemporalStateReducer<TState>,
    private readonly events: TemporalEventBus,
    private readonly ids: TemporalIdGenerator,
    private readonly clock: TemporalClock,
    options: TemporalReasoningEngineOptions = {},
  ) {
    this.defaultBranchId = options.defaultBranchId ?? "canonical";
    this.maximumReplayEvents = options.maximumReplayEvents ?? 10000;
    this.conflictToleranceMs = options.conflictToleranceMs ?? 0;
  }

  async registerEvent(
    input: Omit<TemporalEvent, "createdAt" | "updatedAt" | "version">,
  ): Promise<TemporalEvent> {
    this.validateInterval(input.interval);
    this.validateConfidence(input.confidence);

    const existing = await this.repository.getEvent(input.eventId);
    if (existing) {
      throw new TemporalValidationError(`Event ${input.eventId} already exists`);
    }

    if (input.parentEventId) {
      const parent = await this.repository.getEvent(input.parentEventId);
      if (!parent) {
        throw new TemporalValidationError(`Parent event ${input.parentEventId} was not found`);
      }
    }

    const now = this.clock.now().toISOString();
    const event: TemporalEvent = {
      ...input,
      sourceIds: [...new Set(input.sourceIds)],
      createdAt: now,
      updatedAt: now,
      version: 1,
    };

    await this.detectAndPersistConflicts(event);
    await this.repository.saveEvent(event);
    await this.events.publish("temporal.event.registered", {
      eventId: event.eventId,
      subjectId: event.subjectId,
      eventType: event.eventType,
      status: event.status,
    });

    return event;
  }

  async updateEvent(
    eventId: string,
    patch: Partial<Pick<TemporalEvent, "interval" | "status" | "confidence" | "payload" | "causes" | "causedBy">>,
  ): Promise<TemporalEvent> {
    const current = await this.requireEvent(eventId);
    if (patch.interval) this.validateInterval(patch.interval);
    if (patch.confidence !== undefined) this.validateConfidence(patch.confidence);

    const updated: TemporalEvent = {
      ...current,
      ...patch,
      interval: patch.interval ?? current.interval,
      updatedAt: this.clock.now().toISOString(),
      version: current.version + 1,
    };

    await this.detectAndPersistConflicts(updated, eventId);
    await this.repository.saveEvent(updated);
    await this.events.publish("temporal.event.updated", {
      eventId,
      version: updated.version,
      status: updated.status,
    });

    return updated;
  }

  async assertAt(
    input: Omit<TemporalAssertion, "assertionId" | "createdAt"> & { assertionId?: string },
  ): Promise<TemporalAssertion> {
    this.validateInterval(input.validDuring);
    this.validateConfidence(input.confidence);

    const assertion: TemporalAssertion = {
      ...input,
      assertionId: input.assertionId ?? this.ids.next("temporal-assertion"),
      sourceIds: [...new Set(input.sourceIds)],
      createdAt: this.clock.now().toISOString(),
    };

    await this.repository.saveAssertion(assertion);
    await this.events.publish("temporal.assertion.recorded", {
      assertionId: assertion.assertionId,
      subjectId: assertion.subjectId,
      predicate: assertion.predicate,
    });

    return assertion;
  }

  async createBranch(input: {
    branchId?: string;
    parentBranchId?: string;
    divergenceAt: string;
    label: string;
    probability: number;
    eventIds?: string[];
  }): Promise<TimelineBranch> {
    this.requireDate(input.divergenceAt, "divergenceAt");
    this.validateConfidence(input.probability);

    if (input.parentBranchId) {
      const parent = await this.repository.getBranch(input.parentBranchId);
      if (!parent && input.parentBranchId !== this.defaultBranchId) {
        throw new TemporalValidationError(`Parent branch ${input.parentBranchId} was not found`);
      }
    }

    const branch: TimelineBranch = {
      branchId: input.branchId ?? this.ids.next("timeline-branch"),
      parentBranchId: input.parentBranchId ?? this.defaultBranchId,
      divergenceAt: new Date(input.divergenceAt).toISOString(),
      label: input.label,
      probability: input.probability,
      eventIds: [...new Set(input.eventIds ?? [])],
      createdAt: this.clock.now().toISOString(),
    };

    await this.repository.saveBranch(branch);
    await this.events.publish("temporal.branch.created", {
      branchId: branch.branchId,
      parentBranchId: branch.parentBranchId,
      divergenceAt: branch.divergenceAt,
      probability: branch.probability,
    });

    return branch;
  }

  async reconstructState(
    branchId: string,
    at: string,
    initialState: TState,
  ): Promise<WorldStateSnapshot<TState>> {
    this.requireDate(at, "at");
    const snapshot = await this.repository.getLatestSnapshot(branchId, at);
    let state = snapshot ? (snapshot.state as TState) : initialState;
    const from = snapshot?.effectiveAt ?? "1970-01-01T00:00:00.000Z";

    const replay = await this.replay(branchId, from, at, state);
    state = replay.finalState;

    const assertions = await this.repository.queryAssertions("*", at);
    const result: WorldStateSnapshot<TState> = {
      snapshotId: this.ids.next("world-state-snapshot"),
      branchId,
      effectiveAt: new Date(at).toISOString(),
      state,
      appliedEventIds: replay.appliedEvents.map((event) => event.eventId),
      appliedAssertionIds: assertions.map((assertion) => assertion.assertionId),
      createdAt: this.clock.now().toISOString(),
    };

    await this.repository.saveSnapshot(result as WorldStateSnapshot);
    await this.events.publish("temporal.state.reconstructed", {
      snapshotId: result.snapshotId,
      branchId,
      effectiveAt: result.effectiveAt,
      appliedEventCount: result.appliedEventIds.length,
    });

    return result;
  }

  async replay(
    branchId: string,
    from: string,
    to: string,
    initialState: TState,
  ): Promise<TemporalReplayResult<TState>> {
    const fromDate = this.requireDate(from, "from");
    const toDate = this.requireDate(to, "to");
    if (fromDate > toDate) {
      throw new TemporalValidationError("Replay start cannot be after replay end");
    }

    const events = await this.repository.queryEvents({
      branchId,
      interval: { start: fromDate.toISOString(), end: toDate.toISOString() },
    });

    const ordered = events
      .filter((event) => event.status !== "cancelled")
      .sort((a, b) => this.startMs(a.interval) - this.startMs(b.interval));

    if (ordered.length > this.maximumReplayEvents) {
      throw new TemporalValidationError(
        `Replay exceeds maximum event count of ${this.maximumReplayEvents}`,
      );
    }

    let state = initialState;
    for (const event of ordered) {
      state = await this.reducer.apply(state, event);
    }

    return {
      branchId,
      from: fromDate.toISOString(),
      to: toDate.toISOString(),
      initialState,
      finalState: state,
      appliedEvents: ordered,
    };
  }

  relate(left: TemporalInterval, right: TemporalInterval): TemporalRelation {
    this.validateInterval(left);
    this.validateInterval(right);

    const aStart = this.startMs(left);
    const aEnd = this.endMs(left);
    const bStart = this.startMs(right);
    const bEnd = this.endMs(right);

    if (aStart === bStart && aEnd === bEnd) return "equals";
    if (aEnd < bStart) return "before";
    if (aStart > bEnd) return "after";
    if (aEnd === bStart) return "meets";
    if (aStart === bStart && aEnd < bEnd) return "starts";
    if (aEnd === bEnd && aStart > bStart) return "finishes";
    if (aStart > bStart && aEnd < bEnd) return "during";
    return "overlaps";
  }

  expandRecurrence(event: TemporalEvent, window: TemporalInterval): TemporalEvent[] {
    if (!event.recurrence) return [event];
    this.validateInterval(window);

    const result: TemporalEvent[] = [];
    const recurrence = event.recurrence;
    const increment = Math.max(1, recurrence.interval ?? 1);
    const originalStart = this.startMs(event.interval);
    const originalEnd = this.endMs(event.interval);
    const duration = originalEnd - originalStart;
    const windowEnd = this.endMs(window);
    const until = recurrence.until ? this.requireDate(recurrence.until, "recurrence.until").getTime() : windowEnd;
    const limit = Math.min(recurrence.count ?? Number.MAX_SAFE_INTEGER, 10000);

    let cursor = new Date(originalStart);
    for (let index = 0; index < limit && cursor.getTime() <= Math.min(until, windowEnd); index += 1) {
      const start = cursor.toISOString();
      const end = new Date(cursor.getTime() + duration).toISOString();
      if (this.intersects({ start, end }, window)) {
        result.push({
          ...event,
          eventId: `${event.eventId}:occurrence:${index + 1}`,
          interval: { ...event.interval, start, end },
          parentEventId: event.eventId,
          recurrence: undefined,
        });
      }
      cursor = this.increment(cursor, recurrence.frequency, increment);
    }

    return result;
  }

  async query(query: TemporalQuery): Promise<TemporalEvent[]> {
    if (query.interval) this.validateInterval(query.interval);
    const events = await this.repository.queryEvents(query);
    return events.sort((a, b) => this.startMs(a.interval) - this.startMs(b.interval));
  }

  private async detectAndPersistConflicts(
    candidate: TemporalEvent,
    excludingEventId?: string,
  ): Promise<void> {
    const existing = await this.repository.queryEvents({
      subjectId: candidate.subjectId,
      interval: candidate.interval,
    });

    for (const other of existing) {
      if (other.eventId === excludingEventId || other.eventId === candidate.eventId) continue;
      if (!this.intersects(candidate.interval, other.interval)) continue;
      if (candidate.eventType !== other.eventType) continue;
      if (candidate.status === "cancelled" || other.status === "cancelled") continue;

      const conflict: TemporalConflict = {
        conflictId: this.ids.next("temporal-conflict"),
        eventIds: [other.eventId, candidate.eventId],
        assertionIds: [],
        reason: `Events overlap for subject ${candidate.subjectId} and type ${candidate.eventType}`,
        severity: candidate.status === "active" && other.status === "active" ? "high" : "medium",
        detectedAt: this.clock.now().toISOString(),
      };
      await this.repository.saveConflict(conflict);
      await this.events.publish("temporal.conflict.detected", {
        conflictId: conflict.conflictId,
        eventIds: conflict.eventIds,
        severity: conflict.severity,
      });
    }
  }

  private intersects(left: TemporalInterval, right: TemporalInterval): boolean {
    return (
      this.startMs(left) <= this.endMs(right) + this.conflictToleranceMs &&
      this.startMs(right) <= this.endMs(left) + this.conflictToleranceMs
    );
  }

  private increment(date: Date, frequency: TemporalRecurrence["frequency"], amount: number): Date {
    const next = new Date(date);
    if (frequency === "hourly") next.setUTCHours(next.getUTCHours() + amount);
    if (frequency === "daily") next.setUTCDate(next.getUTCDate() + amount);
    if (frequency === "weekly") next.setUTCDate(next.getUTCDate() + amount * 7);
    if (frequency === "monthly") next.setUTCMonth(next.getUTCMonth() + amount);
    if (frequency === "yearly") next.setUTCFullYear(next.getUTCFullYear() + amount);
    return next;
  }

  private async requireEvent(eventId: string): Promise<TemporalEvent> {
    if (!eventId.trim()) throw new TemporalValidationError("Event id is required");
    const event = await this.repository.getEvent(eventId);
    if (!event) throw new TemporalValidationError(`Event ${eventId} was not found`);
    return event;
  }

  private validateInterval(interval: TemporalInterval): void {
    const start = this.requireDate(interval.start, "interval.start");
    if (interval.end) {
      const end = this.requireDate(interval.end, "interval.end");
      if (end < start) {
        throw new TemporalValidationError("Interval end cannot be before interval start");
      }
    }
  }

  private validateConfidence(value: number): void {
    if (!Number.isFinite(value) || value < 0 || value > 1) {
      throw new TemporalValidationError("Confidence must be between 0 and 1");
    }
  }

  private requireDate(value: string, field: string): Date {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      throw new TemporalValidationError(`${field} must be a valid ISO date`);
    }
    return date;
  }

  private startMs(interval: TemporalInterval): number {
    return this.requireDate(interval.start, "interval.start").getTime();
  }

  private endMs(interval: TemporalInterval): number {
    return interval.end
      ? this.requireDate(interval.end, "interval.end").getTime()
      : this.startMs(interval);
  }
}
