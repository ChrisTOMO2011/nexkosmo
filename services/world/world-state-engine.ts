export type WorldEntityType =
  | "production"
  | "project"
  | "scene"
  | "asset"
  | "character"
  | "location"
  | "agent"
  | "service"
  | "resource"
  | "organisation"
  | "person"
  | "external-system"
  | "custom";

export type WorldEntityStatus =
  | "active"
  | "inactive"
  | "degraded"
  | "blocked"
  | "completed"
  | "archived"
  | "unknown";

export interface WorldEntity {
  entityId: string;
  entityType: WorldEntityType;
  name: string;
  status: WorldEntityStatus;
  version: number;
  attributes: Record<string, unknown>;
  confidence: number;
  observedAt: string;
  updatedAt: string;
  sourceIds: string[];
  tags?: string[];
  metadata?: Record<string, unknown>;
}

export interface WorldRelationship {
  relationshipId: string;
  fromEntityId: string;
  toEntityId: string;
  relationshipType: string;
  directed: boolean;
  confidence: number;
  attributes?: Record<string, unknown>;
  observedAt: string;
  updatedAt: string;
  sourceIds: string[];
}

export type WorldStateOperation =
  | "create-entity"
  | "update-entity"
  | "remove-entity"
  | "create-relationship"
  | "update-relationship"
  | "remove-relationship";

export interface WorldStateChange {
  changeId: string;
  operation: WorldStateOperation;
  entityId?: string;
  relationshipId?: string;
  before?: Record<string, unknown>;
  after?: Record<string, unknown>;
  actorId: string;
  reason: string;
  occurredAt: string;
  correlationId?: string;
  sourceIds?: string[];
}

export interface WorldStateSnapshot {
  snapshotId: string;
  version: number;
  entities: WorldEntity[];
  relationships: WorldRelationship[];
  createdAt: string;
  checksum: string;
  metadata?: Record<string, unknown>;
}

export interface WorldStateConflict {
  conflictId: string;
  targetId: string;
  targetType: "entity" | "relationship";
  field: string;
  currentValue: unknown;
  incomingValue: unknown;
  currentConfidence: number;
  incomingConfidence: number;
  detectedAt: string;
  resolution: "accepted-current" | "accepted-incoming" | "merged" | "unresolved";
  reason: string;
}

export interface WorldStateQuery {
  entityTypes?: WorldEntityType[];
  statuses?: WorldEntityStatus[];
  tags?: string[];
  sourceIds?: string[];
  updatedAfter?: string;
  updatedBefore?: string;
  attributeEquals?: Record<string, unknown>;
  minimumConfidence?: number;
}

export interface WorldStateQueryResult {
  entities: WorldEntity[];
  relationships: WorldRelationship[];
  evaluatedAt: string;
  snapshotVersion: number;
}

export interface WorldStateRepository {
  getEntity(entityId: string): Promise<WorldEntity | null>;
  listEntities(): Promise<WorldEntity[]>;
  saveEntity(entity: WorldEntity): Promise<void>;
  deleteEntity(entityId: string): Promise<void>;
  getRelationship(relationshipId: string): Promise<WorldRelationship | null>;
  listRelationships(): Promise<WorldRelationship[]>;
  saveRelationship(relationship: WorldRelationship): Promise<void>;
  deleteRelationship(relationshipId: string): Promise<void>;
  appendChange(change: WorldStateChange): Promise<void>;
  listChanges(fromVersion?: number): Promise<WorldStateChange[]>;
  saveSnapshot(snapshot: WorldStateSnapshot): Promise<void>;
  getLatestSnapshot(): Promise<WorldStateSnapshot | null>;
  saveConflict(conflict: WorldStateConflict): Promise<void>;
}

export interface WorldStateEventBus {
  publish(event: string, payload: Record<string, unknown>): Promise<void>;
}

export interface WorldStateHasher {
  hash(value: unknown): Promise<string>;
}

export interface WorldStateEngineOptions {
  minimumConfidence?: number;
  staleAfterMs?: number;
  maximumSourcesPerRecord?: number;
}

export class WorldStateIntegrityError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "WorldStateIntegrityError";
  }
}

export class WorldStateEngine {
  private readonly minimumConfidence: number;
  private readonly staleAfterMs: number;
  private readonly maximumSourcesPerRecord: number;

  constructor(
    private readonly repository: WorldStateRepository,
    private readonly events: WorldStateEventBus,
    private readonly hasher: WorldStateHasher,
    options: WorldStateEngineOptions = {},
  ) {
    this.minimumConfidence = options.minimumConfidence ?? 0.05;
    this.staleAfterMs = options.staleAfterMs ?? 30 * 24 * 60 * 60 * 1000;
    this.maximumSourcesPerRecord = options.maximumSourcesPerRecord ?? 100;
  }

  async upsertEntity(
    incoming: WorldEntity,
    actorId: string,
    reason: string,
    correlationId?: string,
  ): Promise<{ entity: WorldEntity; conflicts: WorldStateConflict[] }> {
    this.validateEntity(incoming);
    this.validateMutation(actorId, reason);

    const current = await this.repository.getEntity(incoming.entityId);
    if (!current) {
      const created = this.normaliseEntity({ ...incoming, version: Math.max(1, incoming.version) });
      await this.repository.saveEntity(created);
      await this.recordChange({
        changeId: this.changeId("create-entity", incoming.entityId),
        operation: "create-entity",
        entityId: incoming.entityId,
        after: this.asRecord(created),
        actorId,
        reason,
        occurredAt: new Date().toISOString(),
        correlationId,
        sourceIds: created.sourceIds,
      });
      await this.events.publish("world.entity.created", {
        entityId: created.entityId,
        entityType: created.entityType,
        version: created.version,
      });
      return { entity: created, conflicts: [] };
    }

    const { merged, conflicts } = this.mergeEntity(current, incoming);
    await this.repository.saveEntity(merged);
    for (const conflict of conflicts) await this.repository.saveConflict(conflict);

    await this.recordChange({
      changeId: this.changeId("update-entity", incoming.entityId),
      operation: "update-entity",
      entityId: incoming.entityId,
      before: this.asRecord(current),
      after: this.asRecord(merged),
      actorId,
      reason,
      occurredAt: new Date().toISOString(),
      correlationId,
      sourceIds: merged.sourceIds,
    });

    await this.events.publish("world.entity.updated", {
      entityId: merged.entityId,
      entityType: merged.entityType,
      version: merged.version,
      conflictCount: conflicts.length,
    });

    return { entity: merged, conflicts };
  }

  async upsertRelationship(
    incoming: WorldRelationship,
    actorId: string,
    reason: string,
    correlationId?: string,
  ): Promise<{ relationship: WorldRelationship; conflicts: WorldStateConflict[] }> {
    this.validateRelationship(incoming);
    this.validateMutation(actorId, reason);

    const [from, to] = await Promise.all([
      this.repository.getEntity(incoming.fromEntityId),
      this.repository.getEntity(incoming.toEntityId),
    ]);
    if (!from || !to) {
      throw new WorldStateIntegrityError(
        "Both relationship endpoints must exist in world state",
      );
    }

    const current = await this.repository.getRelationship(incoming.relationshipId);
    if (!current) {
      const created = this.normaliseRelationship(incoming);
      await this.repository.saveRelationship(created);
      await this.recordChange({
        changeId: this.changeId("create-relationship", incoming.relationshipId),
        operation: "create-relationship",
        relationshipId: incoming.relationshipId,
        after: this.asRecord(created),
        actorId,
        reason,
        occurredAt: new Date().toISOString(),
        correlationId,
        sourceIds: created.sourceIds,
      });
      await this.events.publish("world.relationship.created", {
        relationshipId: created.relationshipId,
        fromEntityId: created.fromEntityId,
        toEntityId: created.toEntityId,
        relationshipType: created.relationshipType,
      });
      return { relationship: created, conflicts: [] };
    }

    const { merged, conflicts } = this.mergeRelationship(current, incoming);
    await this.repository.saveRelationship(merged);
    for (const conflict of conflicts) await this.repository.saveConflict(conflict);

    await this.recordChange({
      changeId: this.changeId("update-relationship", incoming.relationshipId),
      operation: "update-relationship",
      relationshipId: incoming.relationshipId,
      before: this.asRecord(current),
      after: this.asRecord(merged),
      actorId,
      reason,
      occurredAt: new Date().toISOString(),
      correlationId,
      sourceIds: merged.sourceIds,
    });

    await this.events.publish("world.relationship.updated", {
      relationshipId: merged.relationshipId,
      conflictCount: conflicts.length,
    });

    return { relationship: merged, conflicts };
  }

  async removeEntity(
    entityId: string,
    actorId: string,
    reason: string,
  ): Promise<void> {
    this.validateMutation(actorId, reason);
    const entity = await this.repository.getEntity(entityId);
    if (!entity) throw new WorldStateIntegrityError(`Entity ${entityId} was not found`);

    const relationships = await this.repository.listRelationships();
    const connected = relationships.filter(
      (relationship) =>
        relationship.fromEntityId === entityId || relationship.toEntityId === entityId,
    );

    for (const relationship of connected) {
      await this.repository.deleteRelationship(relationship.relationshipId);
      await this.recordChange({
        changeId: this.changeId("remove-relationship", relationship.relationshipId),
        operation: "remove-relationship",
        relationshipId: relationship.relationshipId,
        before: this.asRecord(relationship),
        actorId,
        reason: `Cascade removal: ${reason}`,
        occurredAt: new Date().toISOString(),
        sourceIds: relationship.sourceIds,
      });
    }

    await this.repository.deleteEntity(entityId);
    await this.recordChange({
      changeId: this.changeId("remove-entity", entityId),
      operation: "remove-entity",
      entityId,
      before: this.asRecord(entity),
      actorId,
      reason,
      occurredAt: new Date().toISOString(),
      sourceIds: entity.sourceIds,
    });

    await this.events.publish("world.entity.removed", {
      entityId,
      cascadedRelationshipCount: connected.length,
    });
  }

  async query(query: WorldStateQuery = {}): Promise<WorldStateQueryResult> {
    const [entities, relationships, snapshot] = await Promise.all([
      this.repository.listEntities(),
      this.repository.listRelationships(),
      this.repository.getLatestSnapshot(),
    ]);

    const filtered = entities.filter((entity) => this.matchesQuery(entity, query));
    const visibleIds = new Set(filtered.map((entity) => entity.entityId));

    return {
      entities: filtered,
      relationships: relationships.filter(
        (relationship) =>
          visibleIds.has(relationship.fromEntityId) &&
          visibleIds.has(relationship.toEntityId),
      ),
      evaluatedAt: new Date().toISOString(),
      snapshotVersion: snapshot?.version ?? 0,
    };
  }

  async createSnapshot(metadata?: Record<string, unknown>): Promise<WorldStateSnapshot> {
    const [entities, relationships, previous] = await Promise.all([
      this.repository.listEntities(),
      this.repository.listRelationships(),
      this.repository.getLatestSnapshot(),
    ]);

    this.validateGraph(entities, relationships);
    const createdAt = new Date().toISOString();
    const version = (previous?.version ?? 0) + 1;
    const checksum = await this.hasher.hash({ entities, relationships, version, createdAt });

    const snapshot: WorldStateSnapshot = {
      snapshotId: `world-snapshot:${version}:${Date.now()}`,
      version,
      entities,
      relationships,
      createdAt,
      checksum,
      metadata,
    };

    await this.repository.saveSnapshot(snapshot);
    await this.events.publish("world.snapshot.created", {
      snapshotId: snapshot.snapshotId,
      version,
      entityCount: entities.length,
      relationshipCount: relationships.length,
      checksum,
    });

    return snapshot;
  }

  async getEntityHistory(entityId: string): Promise<WorldStateChange[]> {
    const changes = await this.repository.listChanges();
    return changes
      .filter((change) => change.entityId === entityId)
      .sort((left, right) => Date.parse(left.occurredAt) - Date.parse(right.occurredAt));
  }

  async detectStaleEntities(referenceTime = Date.now()): Promise<WorldEntity[]> {
    const entities = await this.repository.listEntities();
    return entities.filter((entity) => {
      const observedAt = Date.parse(entity.observedAt);
      return !Number.isNaN(observedAt) && referenceTime - observedAt > this.staleAfterMs;
    });
  }

  private mergeEntity(
    current: WorldEntity,
    incoming: WorldEntity,
  ): { merged: WorldEntity; conflicts: WorldStateConflict[] } {
    const conflicts: WorldStateConflict[] = [];
    const attributes = { ...current.attributes };

    for (const [field, incomingValue] of Object.entries(incoming.attributes)) {
      const currentValue = attributes[field];
      if (
        currentValue !== undefined &&
        !this.valuesEqual(currentValue, incomingValue)
      ) {
        const acceptIncoming = incoming.confidence >= current.confidence;
        conflicts.push(
          this.conflict(
            current.entityId,
            "entity",
            `attributes.${field}`,
            currentValue,
            incomingValue,
            current.confidence,
            incoming.confidence,
            acceptIncoming ? "accepted-incoming" : "accepted-current",
            acceptIncoming
              ? "Incoming observation has equal or greater confidence"
              : "Current observation has greater confidence",
          ),
        );
        if (acceptIncoming) attributes[field] = incomingValue;
      } else {
        attributes[field] = incomingValue;
      }
    }

    const preferIncoming = incoming.confidence >= current.confidence;
    return {
      merged: this.normaliseEntity({
        ...current,
        ...(preferIncoming
          ? {
              name: incoming.name,
              status: incoming.status,
              entityType: incoming.entityType,
              confidence: incoming.confidence,
              observedAt: incoming.observedAt,
            }
          : {}),
        attributes,
        sourceIds: this.mergeSources(current.sourceIds, incoming.sourceIds),
        tags: [...new Set([...(current.tags ?? []), ...(incoming.tags ?? [])])],
        metadata: { ...(current.metadata ?? {}), ...(incoming.metadata ?? {}) },
        version: current.version + 1,
        updatedAt: new Date().toISOString(),
      }),
      conflicts,
    };
  }

  private mergeRelationship(
    current: WorldRelationship,
    incoming: WorldRelationship,
  ): { merged: WorldRelationship; conflicts: WorldStateConflict[] } {
    const conflicts: WorldStateConflict[] = [];
    const preferIncoming = incoming.confidence >= current.confidence;

    if (current.relationshipType !== incoming.relationshipType) {
      conflicts.push(
        this.conflict(
          current.relationshipId,
          "relationship",
          "relationshipType",
          current.relationshipType,
          incoming.relationshipType,
          current.confidence,
          incoming.confidence,
          preferIncoming ? "accepted-incoming" : "accepted-current",
          "Relationship types differ",
        ),
      );
    }

    return {
      merged: this.normaliseRelationship({
        ...current,
        ...(preferIncoming ? incoming : {}),
        attributes: {
          ...(current.attributes ?? {}),
          ...(preferIncoming ? incoming.attributes ?? {} : {}),
        },
        sourceIds: this.mergeSources(current.sourceIds, incoming.sourceIds),
        updatedAt: new Date().toISOString(),
      }),
      conflicts,
    };
  }

  private matchesQuery(entity: WorldEntity, query: WorldStateQuery): boolean {
    if (query.entityTypes && !query.entityTypes.includes(entity.entityType)) return false;
    if (query.statuses && !query.statuses.includes(entity.status)) return false;
    if (
      query.tags &&
      !query.tags.every((tag) => (entity.tags ?? []).includes(tag))
    ) return false;
    if (
      query.sourceIds &&
      !query.sourceIds.some((sourceId) => entity.sourceIds.includes(sourceId))
    ) return false;
    if (
      query.minimumConfidence !== undefined &&
      entity.confidence < query.minimumConfidence
    ) return false;
    if (query.updatedAfter && Date.parse(entity.updatedAt) <= Date.parse(query.updatedAfter)) {
      return false;
    }
    if (query.updatedBefore && Date.parse(entity.updatedAt) >= Date.parse(query.updatedBefore)) {
      return false;
    }
    if (query.attributeEquals) {
      for (const [key, expected] of Object.entries(query.attributeEquals)) {
        if (!this.valuesEqual(entity.attributes[key], expected)) return false;
      }
    }
    return true;
  }

  private validateGraph(
    entities: WorldEntity[],
    relationships: WorldRelationship[],
  ): void {
    const ids = new Set(entities.map((entity) => entity.entityId));
    for (const relationship of relationships) {
      if (!ids.has(relationship.fromEntityId) || !ids.has(relationship.toEntityId)) {
        throw new WorldStateIntegrityError(
          `Relationship ${relationship.relationshipId} contains a missing endpoint`,
        );
      }
    }
  }

  private validateEntity(entity: WorldEntity): void {
    if (!entity.entityId.trim()) throw new Error("Entity id is required");
    if (!entity.name.trim()) throw new Error("Entity name is required");
    this.validateConfidence(entity.confidence);
    this.validateDate(entity.observedAt, "Observed date");
    this.validateDate(entity.updatedAt, "Updated date");
    if (entity.sourceIds.length === 0) throw new Error("At least one source id is required");
  }

  private validateRelationship(relationship: WorldRelationship): void {
    if (!relationship.relationshipId.trim()) throw new Error("Relationship id is required");
    if (!relationship.fromEntityId.trim() || !relationship.toEntityId.trim()) {
      throw new Error("Relationship endpoint ids are required");
    }
    if (relationship.fromEntityId === relationship.toEntityId) {
      throw new Error("Self relationships are not permitted");
    }
    if (!relationship.relationshipType.trim()) {
      throw new Error("Relationship type is required");
    }
    this.validateConfidence(relationship.confidence);
    this.validateDate(relationship.observedAt, "Observed date");
    this.validateDate(relationship.updatedAt, "Updated date");
  }

  private validateMutation(actorId: string, reason: string): void {
    if (!actorId.trim()) throw new Error("Actor id is required");
    if (!reason.trim()) throw new Error("Mutation reason is required");
  }

  private validateConfidence(confidence: number): void {
    if (
      !Number.isFinite(confidence) ||
      confidence < this.minimumConfidence ||
      confidence > 1
    ) {
      throw new Error(
        `Confidence must be between ${this.minimumConfidence} and 1`,
      );
    }
  }

  private validateDate(value: string, label: string): void {
    if (Number.isNaN(Date.parse(value))) throw new Error(`${label} must be valid`);
  }

  private normaliseEntity(entity: WorldEntity): WorldEntity {
    return {
      ...entity,
      confidence: this.clamp(entity.confidence),
      sourceIds: this.mergeSources([], entity.sourceIds),
      attributes: { ...entity.attributes },
    };
  }

  private normaliseRelationship(
    relationship: WorldRelationship,
  ): WorldRelationship {
    return {
      ...relationship,
      confidence: this.clamp(relationship.confidence),
      sourceIds: this.mergeSources([], relationship.sourceIds),
      attributes: { ...(relationship.attributes ?? {}) },
    };
  }

  private mergeSources(left: string[], right: string[]): string[] {
    return [...new Set([...left, ...right])].slice(0, this.maximumSourcesPerRecord);
  }

  private conflict(
    targetId: string,
    targetType: "entity" | "relationship",
    field: string,
    currentValue: unknown,
    incomingValue: unknown,
    currentConfidence: number,
    incomingConfidence: number,
    resolution: WorldStateConflict["resolution"],
    reason: string,
  ): WorldStateConflict {
    return {
      conflictId: `world-conflict:${targetId}:${field}:${Date.now()}`,
      targetId,
      targetType,
      field,
      currentValue,
      incomingValue,
      currentConfidence,
      incomingConfidence,
      detectedAt: new Date().toISOString(),
      resolution,
      reason,
    };
  }

  private async recordChange(change: WorldStateChange): Promise<void> {
    await this.repository.appendChange(change);
    await this.events.publish("world.state.changed", {
      changeId: change.changeId,
      operation: change.operation,
      entityId: change.entityId,
      relationshipId: change.relationshipId,
      actorId: change.actorId,
      correlationId: change.correlationId,
    });
  }

  private changeId(operation: WorldStateOperation, targetId: string): string {
    return `world-change:${operation}:${targetId}:${Date.now()}`;
  }

  private valuesEqual(left: unknown, right: unknown): boolean {
    return JSON.stringify(left) === JSON.stringify(right);
  }

  private asRecord(value: object): Record<string, unknown> {
    return { ...value };
  }

  private clamp(value: number): number {
    return Math.max(0, Math.min(1, value));
  }
}
