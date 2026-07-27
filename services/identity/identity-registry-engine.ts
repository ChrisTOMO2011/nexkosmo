export type IdentityKind =
  | "person"
  | "organisation"
  | "agent"
  | "production"
  | "project"
  | "scene"
  | "asset"
  | "character"
  | "rig"
  | "workflow"
  | "service"
  | "location"
  | "external-system"
  | "custom";

export type IdentityStatus =
  | "pending"
  | "active"
  | "suspended"
  | "archived"
  | "revoked";

export interface RegistryIdentity {
  identityId: string;
  kind: IdentityKind;
  canonicalName: string;
  status: IdentityStatus;
  ownerIdentityId?: string;
  parentIdentityId?: string;
  aliases: string[];
  externalReferences: ExternalIdentityReference[];
  roles: string[];
  permissions: string[];
  lineage: IdentityLineageEntry[];
  version: number;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  metadata?: Record<string, unknown>;
}

export interface ExternalIdentityReference {
  provider: string;
  externalId: string;
  namespace?: string;
  uri?: string;
  verified: boolean;
  linkedAt: string;
  linkedBy: string;
  metadata?: Record<string, unknown>;
}

export interface IdentityLineageEntry {
  lineageId: string;
  relationship:
    | "created-from"
    | "derived-from"
    | "copied-from"
    | "supersedes"
    | "owned-by"
    | "member-of"
    | "related-to";
  sourceIdentityId: string;
  targetIdentityId: string;
  createdAt: string;
  createdBy: string;
  metadata?: Record<string, unknown>;
}

export interface IdentityHistoryEntry {
  historyId: string;
  identityId: string;
  operation:
    | "created"
    | "updated"
    | "status-changed"
    | "alias-added"
    | "alias-removed"
    | "external-reference-linked"
    | "external-reference-unlinked"
    | "lineage-linked"
    | "ownership-transferred";
  before?: Record<string, unknown>;
  after?: Record<string, unknown>;
  actorId: string;
  reason: string;
  occurredAt: string;
}

export interface IdentityLookupQuery {
  identityId?: string;
  kinds?: IdentityKind[];
  statuses?: IdentityStatus[];
  canonicalName?: string;
  alias?: string;
  ownerIdentityId?: string;
  parentIdentityId?: string;
  role?: string;
  permission?: string;
  externalProvider?: string;
  externalId?: string;
}

export interface DuplicateIdentityCandidate {
  identityId: string;
  score: number;
  reasons: string[];
}

export interface IdentityRegistryRepository {
  getIdentity(identityId: string): Promise<RegistryIdentity | null>;
  listIdentities(): Promise<RegistryIdentity[]>;
  saveIdentity(identity: RegistryIdentity): Promise<void>;
  updateIdentity(identity: RegistryIdentity): Promise<void>;
  appendHistory(entry: IdentityHistoryEntry): Promise<void>;
  findByAlias(alias: string): Promise<RegistryIdentity[]>;
  findByExternalReference(
    provider: string,
    externalId: string,
    namespace?: string,
  ): Promise<RegistryIdentity[]>;
}

export interface IdentityRegistryEventBus {
  publish(event: string, payload: Record<string, unknown>): Promise<void>;
}

export interface IdentityIdGenerator {
  generate(kind: IdentityKind): string;
}

export interface IdentityRegistryOptions {
  duplicateThreshold?: number;
  maximumAliases?: number;
  maximumExternalReferences?: number;
}

export class IdentityRegistryIntegrityError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "IdentityRegistryIntegrityError";
  }
}

export class IdentityRegistryEngine {
  private readonly duplicateThreshold: number;
  private readonly maximumAliases: number;
  private readonly maximumExternalReferences: number;

  constructor(
    private readonly repository: IdentityRegistryRepository,
    private readonly events: IdentityRegistryEventBus,
    private readonly ids: IdentityIdGenerator,
    options: IdentityRegistryOptions = {},
  ) {
    this.duplicateThreshold = options.duplicateThreshold ?? 0.82;
    this.maximumAliases = options.maximumAliases ?? 100;
    this.maximumExternalReferences = options.maximumExternalReferences ?? 100;
  }

  async registerIdentity(input: {
    kind: IdentityKind;
    canonicalName: string;
    createdBy: string;
    ownerIdentityId?: string;
    parentIdentityId?: string;
    aliases?: string[];
    roles?: string[];
    permissions?: string[];
    metadata?: Record<string, unknown>;
    identityId?: string;
  }): Promise<RegistryIdentity> {
    this.requireText(input.canonicalName, "Canonical name");
    this.requireText(input.createdBy, "Creator identity");

    const identityId = input.identityId ?? this.ids.generate(input.kind);
    const existing = await this.repository.getIdentity(identityId);
    if (existing) {
      throw new IdentityRegistryIntegrityError(
        `Identity ${identityId} already exists`,
      );
    }

    await this.validateReferences(
      input.ownerIdentityId,
      input.parentIdentityId,
      identityId,
    );

    const duplicateCandidates = await this.detectDuplicates({
      kind: input.kind,
      canonicalName: input.canonicalName,
      aliases: input.aliases ?? [],
    });
    const likelyDuplicate = duplicateCandidates.find(
      (candidate) => candidate.score >= this.duplicateThreshold,
    );
    if (likelyDuplicate) {
      throw new IdentityRegistryIntegrityError(
        `Likely duplicate of ${likelyDuplicate.identityId} (${likelyDuplicate.score.toFixed(3)})`,
      );
    }

    const now = new Date().toISOString();
    const identity: RegistryIdentity = {
      identityId,
      kind: input.kind,
      canonicalName: input.canonicalName.trim(),
      status: "active",
      ownerIdentityId: input.ownerIdentityId,
      parentIdentityId: input.parentIdentityId,
      aliases: this.normaliseAliases(input.aliases ?? []),
      externalReferences: [],
      roles: this.normaliseStrings(input.roles ?? []),
      permissions: this.normaliseStrings(input.permissions ?? []),
      lineage: [],
      version: 1,
      createdAt: now,
      updatedAt: now,
      createdBy: input.createdBy,
      metadata: input.metadata,
    };

    await this.repository.saveIdentity(identity);
    await this.recordHistory(identity, {
      operation: "created",
      after: this.asRecord(identity),
      actorId: input.createdBy,
      reason: "Identity registered",
    });

    await this.events.publish("identity.registered", {
      identityId,
      kind: identity.kind,
      canonicalName: identity.canonicalName,
      ownerIdentityId: identity.ownerIdentityId,
      parentIdentityId: identity.parentIdentityId,
    });

    return identity;
  }

  async updateIdentity(
    identityId: string,
    changes: Partial<
      Pick<
        RegistryIdentity,
        | "canonicalName"
        | "ownerIdentityId"
        | "parentIdentityId"
        | "roles"
        | "permissions"
        | "metadata"
      >
    >,
    actorId: string,
    reason: string,
  ): Promise<RegistryIdentity> {
    this.requireText(actorId, "Actor identity");
    this.requireText(reason, "Update reason");

    const current = await this.requireIdentity(identityId);
    if (current.status === "revoked") {
      throw new IdentityRegistryIntegrityError(
        "Revoked identities cannot be modified",
      );
    }

    if (changes.canonicalName !== undefined) {
      this.requireText(changes.canonicalName, "Canonical name");
    }
    await this.validateReferences(
      changes.ownerIdentityId,
      changes.parentIdentityId,
      identityId,
    );

    const updated: RegistryIdentity = {
      ...current,
      ...changes,
      canonicalName:
        changes.canonicalName?.trim() ?? current.canonicalName,
      roles:
        changes.roles === undefined
          ? current.roles
          : this.normaliseStrings(changes.roles),
      permissions:
        changes.permissions === undefined
          ? current.permissions
          : this.normaliseStrings(changes.permissions),
      metadata:
        changes.metadata === undefined
          ? current.metadata
          : { ...(current.metadata ?? {}), ...changes.metadata },
      version: current.version + 1,
      updatedAt: new Date().toISOString(),
    };

    await this.repository.updateIdentity(updated);
    await this.recordHistory(updated, {
      operation:
        current.ownerIdentityId !== updated.ownerIdentityId
          ? "ownership-transferred"
          : "updated",
      before: this.asRecord(current),
      after: this.asRecord(updated),
      actorId,
      reason,
    });

    await this.events.publish("identity.updated", {
      identityId,
      version: updated.version,
      actorId,
    });

    return updated;
  }

  async changeStatus(
    identityId: string,
    status: IdentityStatus,
    actorId: string,
    reason: string,
  ): Promise<RegistryIdentity> {
    this.requireText(actorId, "Actor identity");
    this.requireText(reason, "Status reason");

    const current = await this.requireIdentity(identityId);
    this.validateStatusTransition(current.status, status);

    const updated: RegistryIdentity = {
      ...current,
      status,
      version: current.version + 1,
      updatedAt: new Date().toISOString(),
    };

    await this.repository.updateIdentity(updated);
    await this.recordHistory(updated, {
      operation: "status-changed",
      before: this.asRecord(current),
      after: this.asRecord(updated),
      actorId,
      reason,
    });

    await this.events.publish("identity.status.changed", {
      identityId,
      previousStatus: current.status,
      status,
      actorId,
      reason,
    });

    return updated;
  }

  async addAlias(
    identityId: string,
    alias: string,
    actorId: string,
    reason: string,
  ): Promise<RegistryIdentity> {
    this.requireText(alias, "Alias");
    const current = await this.requireIdentity(identityId);
    const aliases = this.normaliseAliases([...current.aliases, alias]);
    if (aliases.length > this.maximumAliases) {
      throw new IdentityRegistryIntegrityError(
        `Identity exceeds the maximum of ${this.maximumAliases} aliases`,
      );
    }

    const collisions = (await this.repository.findByAlias(alias)).filter(
      (identity) => identity.identityId !== identityId,
    );
    if (collisions.length > 0) {
      throw new IdentityRegistryIntegrityError(
        `Alias is already assigned to ${collisions[0].identityId}`,
      );
    }

    const updated = await this.persistSimpleUpdate(current, { aliases }, actorId);
    await this.recordHistory(updated, {
      operation: "alias-added",
      before: this.asRecord(current),
      after: this.asRecord(updated),
      actorId,
      reason,
    });
    await this.events.publish("identity.alias.added", {
      identityId,
      alias: alias.trim(),
    });
    return updated;
  }

  async removeAlias(
    identityId: string,
    alias: string,
    actorId: string,
    reason: string,
  ): Promise<RegistryIdentity> {
    const current = await this.requireIdentity(identityId);
    const key = this.normaliseKey(alias);
    const aliases = current.aliases.filter(
      (candidate) => this.normaliseKey(candidate) !== key,
    );
    const updated = await this.persistSimpleUpdate(current, { aliases }, actorId);
    await this.recordHistory(updated, {
      operation: "alias-removed",
      before: this.asRecord(current),
      after: this.asRecord(updated),
      actorId,
      reason,
    });
    await this.events.publish("identity.alias.removed", { identityId, alias });
    return updated;
  }

  async linkExternalReference(
    identityId: string,
    reference: ExternalIdentityReference,
    actorId: string,
    reason: string,
  ): Promise<RegistryIdentity> {
    this.requireText(reference.provider, "External provider");
    this.requireText(reference.externalId, "External identity id");

    const current = await this.requireIdentity(identityId);
    const matches = await this.repository.findByExternalReference(
      reference.provider,
      reference.externalId,
      reference.namespace,
    );
    const collision = matches.find(
      (identity) => identity.identityId !== identityId,
    );
    if (collision) {
      throw new IdentityRegistryIntegrityError(
        `External identity is already linked to ${collision.identityId}`,
      );
    }

    const externalReferences = [
      ...current.externalReferences.filter(
        (candidate) => !this.sameExternalReference(candidate, reference),
      ),
      { ...reference, linkedBy: actorId },
    ];
    if (externalReferences.length > this.maximumExternalReferences) {
      throw new IdentityRegistryIntegrityError(
        `Identity exceeds the maximum of ${this.maximumExternalReferences} external references`,
      );
    }

    const updated = await this.persistSimpleUpdate(
      current,
      { externalReferences },
      actorId,
    );
    await this.recordHistory(updated, {
      operation: "external-reference-linked",
      before: this.asRecord(current),
      after: this.asRecord(updated),
      actorId,
      reason,
    });
    await this.events.publish("identity.external-reference.linked", {
      identityId,
      provider: reference.provider,
      externalId: reference.externalId,
      namespace: reference.namespace,
    });
    return updated;
  }

  async linkLineage(
    lineage: IdentityLineageEntry,
    actorId: string,
    reason: string,
  ): Promise<RegistryIdentity> {
    if (lineage.sourceIdentityId === lineage.targetIdentityId) {
      throw new IdentityRegistryIntegrityError(
        "Identity lineage cannot reference itself",
      );
    }
    const [source, target] = await Promise.all([
      this.requireIdentity(lineage.sourceIdentityId),
      this.requireIdentity(lineage.targetIdentityId),
    ]);

    const entry: IdentityLineageEntry = {
      ...lineage,
      createdBy: actorId,
      createdAt: lineage.createdAt || new Date().toISOString(),
    };
    const updated = await this.persistSimpleUpdate(
      target,
      {
        lineage: [
          ...target.lineage.filter(
            (candidate) => candidate.lineageId !== entry.lineageId,
          ),
          entry,
        ],
      },
      actorId,
    );

    await this.recordHistory(updated, {
      operation: "lineage-linked",
      before: this.asRecord(target),
      after: this.asRecord(updated),
      actorId,
      reason,
    });
    await this.events.publish("identity.lineage.linked", {
      lineageId: entry.lineageId,
      sourceIdentityId: source.identityId,
      targetIdentityId: target.identityId,
      relationship: entry.relationship,
    });
    return updated;
  }

  async resolve(identifier: string): Promise<RegistryIdentity | null> {
    this.requireText(identifier, "Identity identifier");
    const direct = await this.repository.getIdentity(identifier);
    if (direct) return direct;

    const aliases = await this.repository.findByAlias(identifier);
    if (aliases.length === 1) return aliases[0];
    if (aliases.length > 1) {
      throw new IdentityRegistryIntegrityError(
        `Alias ${identifier} resolves to multiple identities`,
      );
    }
    return null;
  }

  async lookup(query: IdentityLookupQuery): Promise<RegistryIdentity[]> {
    if (query.identityId) {
      const identity = await this.repository.getIdentity(query.identityId);
      return identity && this.matches(identity, query) ? [identity] : [];
    }
    const identities = await this.repository.listIdentities();
    return identities.filter((identity) => this.matches(identity, query));
  }

  async detectDuplicates(input: {
    kind: IdentityKind;
    canonicalName: string;
    aliases: string[];
  }): Promise<DuplicateIdentityCandidate[]> {
    const identities = await this.repository.listIdentities();
    const incomingNames = [input.canonicalName, ...input.aliases].map((value) =>
      this.normaliseKey(value),
    );

    return identities
      .filter((identity) => identity.kind === input.kind)
      .map((identity) => {
        const candidateNames = [
          identity.canonicalName,
          ...identity.aliases,
        ].map((value) => this.normaliseKey(value));
        let score = 0;
        const reasons: string[] = [];

        for (const incoming of incomingNames) {
          for (const candidate of candidateNames) {
            if (incoming === candidate) {
              score = Math.max(score, 1);
              reasons.push("Exact canonical name or alias match");
            } else {
              const similarity = this.stringSimilarity(incoming, candidate);
              if (similarity > score) score = similarity;
            }
          }
        }

        if (score >= 0.7 && reasons.length === 0) {
          reasons.push("Strong name similarity");
        }
        return { identityId: identity.identityId, score, reasons };
      })
      .filter((candidate) => candidate.score >= 0.7)
      .sort((left, right) => right.score - left.score);
  }

  private async persistSimpleUpdate(
    current: RegistryIdentity,
    changes: Partial<RegistryIdentity>,
    actorId: string,
  ): Promise<RegistryIdentity> {
    this.requireText(actorId, "Actor identity");
    const updated: RegistryIdentity = {
      ...current,
      ...changes,
      version: current.version + 1,
      updatedAt: new Date().toISOString(),
    };
    await this.repository.updateIdentity(updated);
    return updated;
  }

  private async validateReferences(
    ownerIdentityId: string | undefined,
    parentIdentityId: string | undefined,
    identityId: string,
  ): Promise<void> {
    for (const [label, referenceId] of [
      ["Owner", ownerIdentityId],
      ["Parent", parentIdentityId],
    ] as const) {
      if (!referenceId) continue;
      if (referenceId === identityId) {
        throw new IdentityRegistryIntegrityError(
          `${label} identity cannot reference itself`,
        );
      }
      if (!(await this.repository.getIdentity(referenceId))) {
        throw new IdentityRegistryIntegrityError(
          `${label} identity ${referenceId} was not found`,
        );
      }
    }
  }

  private validateStatusTransition(
    current: IdentityStatus,
    next: IdentityStatus,
  ): void {
    const allowed: Record<IdentityStatus, IdentityStatus[]> = {
      pending: ["active", "revoked"],
      active: ["suspended", "archived", "revoked"],
      suspended: ["active", "archived", "revoked"],
      archived: ["active", "revoked"],
      revoked: [],
    };
    if (current === next) return;
    if (!allowed[current].includes(next)) {
      throw new IdentityRegistryIntegrityError(
        `Identity status cannot transition from ${current} to ${next}`,
      );
    }
  }

  private matches(
    identity: RegistryIdentity,
    query: IdentityLookupQuery,
  ): boolean {
    if (query.kinds && !query.kinds.includes(identity.kind)) return false;
    if (query.statuses && !query.statuses.includes(identity.status)) return false;
    if (
      query.canonicalName &&
      this.normaliseKey(identity.canonicalName) !==
        this.normaliseKey(query.canonicalName)
    ) return false;
    if (
      query.alias &&
      !identity.aliases.some(
        (alias) => this.normaliseKey(alias) === this.normaliseKey(query.alias!),
      )
    ) return false;
    if (query.ownerIdentityId !== undefined && identity.ownerIdentityId !== query.ownerIdentityId) {
      return false;
    }
    if (query.parentIdentityId !== undefined && identity.parentIdentityId !== query.parentIdentityId) {
      return false;
    }
    if (query.role && !identity.roles.includes(query.role)) return false;
    if (query.permission && !identity.permissions.includes(query.permission)) return false;
    if (query.externalProvider || query.externalId) {
      const found = identity.externalReferences.some(
        (reference) =>
          (!query.externalProvider || reference.provider === query.externalProvider) &&
          (!query.externalId || reference.externalId === query.externalId),
      );
      if (!found) return false;
    }
    return true;
  }

  private async requireIdentity(identityId: string): Promise<RegistryIdentity> {
    this.requireText(identityId, "Identity id");
    const identity = await this.repository.getIdentity(identityId);
    if (!identity) {
      throw new IdentityRegistryIntegrityError(
        `Identity ${identityId} was not found`,
      );
    }
    return identity;
  }

  private async recordHistory(
    identity: RegistryIdentity,
    input: Omit<IdentityHistoryEntry, "historyId" | "identityId" | "occurredAt">,
  ): Promise<void> {
    await this.repository.appendHistory({
      ...input,
      historyId: `identity-history:${identity.identityId}:${Date.now()}`,
      identityId: identity.identityId,
      occurredAt: new Date().toISOString(),
    });
  }

  private normaliseAliases(values: string[]): string[] {
    const aliases = new Map<string, string>();
    for (const value of values) {
      const trimmed = value.trim();
      if (trimmed) aliases.set(this.normaliseKey(trimmed), trimmed);
    }
    return [...aliases.values()];
  }

  private normaliseStrings(values: string[]): string[] {
    return [...new Set(values.map((value) => value.trim()).filter(Boolean))];
  }

  private sameExternalReference(
    left: ExternalIdentityReference,
    right: ExternalIdentityReference,
  ): boolean {
    return (
      left.provider === right.provider &&
      left.externalId === right.externalId &&
      left.namespace === right.namespace
    );
  }

  private stringSimilarity(left: string, right: string): number {
    if (left === right) return 1;
    if (!left.length || !right.length) return 0;
    const leftTokens = new Set(left.split(/\s+/));
    const rightTokens = new Set(right.split(/\s+/));
    const intersection = [...leftTokens].filter((token) =>
      rightTokens.has(token),
    ).length;
    const union = new Set([...leftTokens, ...rightTokens]).size;
    const tokenScore = union === 0 ? 0 : intersection / union;
    const prefixLength = [...left].findIndex(
      (character, index) => character !== right[index],
    );
    const prefixScore =
      prefixLength === -1
        ? Math.min(left.length, right.length) / Math.max(left.length, right.length)
        : Math.max(0, prefixLength) / Math.max(left.length, right.length);
    return Math.max(tokenScore, prefixScore);
  }

  private normaliseKey(value: string): string {
    return value.trim().toLocaleLowerCase().replace(/\s+/g, " ");
  }

  private requireText(value: string, label: string): void {
    if (!value || !value.trim()) throw new Error(`${label} is required`);
  }

  private asRecord(value: object): Record<string, unknown> {
    return { ...value };
  }
}
