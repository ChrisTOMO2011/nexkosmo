import { describe, expect, it, vi } from "vitest";
import {
  characterAssetService,
  CharacterGenerationService,
  CharacterPipelineService,
  CharacterPreviewService,
  CharacterService,
  clearInvalidSelections,
  developmentCharacterAssetManifest,
  getCompatibleAssets,
  glassesAssetIds,
  InMemoryCharacterRepository,
  isUuid,
  resolveDefaultAssets,
  resolveMaterials,
  resolveRig,
  resolveSupportedTabs,
  seededSpecies,
  speciesRegistry,
  speciesSeedIds,
  validateSelection,
} from ".";

const scope = {
  projectId: "project-character-foundation",
  productionId: "production-character-foundation",
};

describe("canonical character asset foundation", () => {
  it("seeds every required species with UUID-backed defaults", () => {
    expect(seededSpecies.map((entry) => entry.name)).toEqual([
      "Human",
      "Elf",
      "Goblin",
      "Orc",
      "Robot",
      "Dragon",
      "Alien",
      "Monkey",
      "Demon",
    ]);

    for (const species of seededSpecies) {
      expect(isUuid(species.id)).toBe(true);
      expect(isUuid(species.thumbnail)).toBe(true);
      expect(isUuid(species.defaultRig)).toBe(true);
      expect(isUuid(species.defaultSkeleton)).toBe(true);
      expect(species.assetManifest.every(isUuid)).toBe(true);
      expect(species.supportedTabs[0]).toBe("Identity");
    }
  });

  it("provides complete immutable manifests without filename identity", () => {
    expect(developmentCharacterAssetManifest.length).toBeGreaterThan(60);
    for (const asset of developmentCharacterAssetManifest) {
      expect(isUuid(asset.assetId)).toBe(true);
      expect(asset.version).toBe(1);
      expect(Object.isFrozen(asset)).toBe(true);
      expect(asset.thumbnail).not.toMatch(/\.(png|jpe?g|webp|glb|fbx)$/iu);
      expect(asset.preview).not.toMatch(/\.(png|jpe?g|webp|glb|fbx)$/iu);
    }
  });

  it("resolves compatibility, defaults, tabs, rigs, and materials from registries", () => {
    const characters = new CharacterService(new InMemoryCharacterRepository());
    const character = characters.create({
      ...scope,
      displayName: "Compatibility Test",
      speciesId: speciesSeedIds.human,
    });
    const compatibleAccessories = getCompatibleAssets(
      character,
      "accessory",
    );

    expect(
      compatibleAccessories.some(
        (asset) => asset.assetId === glassesAssetIds.Aviator,
      ),
    ).toBe(true);
    expect(validateSelection(character).valid).toBe(true);
    expect(resolveSupportedTabs(character.speciesId)[0]).toBe("Identity");
    expect(resolveRig(character.speciesId)).toBe(character.rigId);
    expect(resolveMaterials(character.speciesId)).toEqual(
      character.materialIds,
    );
  });

  it("identifies and clears incompatible selections without species conditionals", () => {
    const characters = new CharacterService(new InMemoryCharacterRepository());
    const human = characters.create({
      ...scope,
      displayName: "Selection Test",
      speciesId: speciesSeedIds.human,
    });
    const robotDefaults = resolveDefaultAssets(speciesSeedIds.robot);
    const invalidRobot = characters.save({
      ...human,
      speciesId: speciesSeedIds.robot,
      compatibilityProfileId: robotDefaults.compatibilityProfileId,
      rigId: robotDefaults.rigId,
      skeletonId: robotDefaults.skeletonId,
      materialIds: robotDefaults.materialIds,
      textureIds: robotDefaults.textureIds,
      accessoryIds: [glassesAssetIds.Aviator],
    });

    expect(validateSelection(invalidRobot).valid).toBe(false);
    expect(clearInvalidSelections(invalidRobot).accessoryIds).toEqual([]);
  });

  it("orchestrates roster loading and species selection through pipeline services", () => {
    const characters = new CharacterService(new InMemoryCharacterRepository());
    const previews = new CharacterPreviewService(characters);
    const pipeline = new CharacterPipelineService(
      characters,
      characterAssetService,
      speciesRegistry,
      previews,
    );
    const listener = vi.fn();
    pipeline.subscribe(listener);
    const roster = pipeline.loadCharacters(
      scope.projectId,
      scope.productionId,
    );
    const updated = pipeline.updateSelections(roster[0].characterId, {
      speciesId: speciesSeedIds.elf,
    });

    expect(roster).toHaveLength(4);
    expect(updated.speciesId).toBe(speciesSeedIds.elf);
    expect(updated.rigId).toBe(resolveRig(speciesSeedIds.elf));
    expect(updated.compatibilityProfileId).toBe("character.elf.v1");
    expect(updated.version).toBeGreaterThan(roster[0].version);
    expect(listener).toHaveBeenCalledWith(
      expect.objectContaining({ type: "selection-updated" }),
    );
  });

  it("reports unavailable preview and generation providers instead of faking output", async () => {
    const characters = new CharacterService(new InMemoryCharacterRepository());
    const character = characters.create({
      ...scope,
      displayName: "Provider Test",
    });
    const previews = new CharacterPreviewService(characters);
    const previewListener = vi.fn();
    previews.subscribe(previewListener);
    const preview = await previews.refresh(character.characterId);
    const generation = await new CharacterGenerationService().generate({
      ...scope,
      characterId: character.characterId,
      speciesId: character.speciesId,
      category: "identity",
      prompt: "Cinematic detective",
      referenceAssets: [],
    });

    expect(preview.status).toBe("unavailable");
    expect(preview.previewAssetId).toBe(character.previewAssetId);
    expect(previewListener).toHaveBeenCalledOnce();
    expect(generation.status).toBe("unavailable");
    expect(generation.generatedAssets).toEqual([]);
    expect(generation.previewAssets).toEqual([]);
    expect(generation.warnings).toHaveLength(1);
    expect(generation.errors).toEqual([]);
    expect(isUuid(generation.jobId)).toBe(true);
  });

  it("creates every canonical character field and never stores filenames as identity", () => {
    const character = new CharacterService(
      new InMemoryCharacterRepository(),
    ).create({
      ...scope,
      displayName: "Schema Test",
    });
    const expectedFields = [
      "characterId",
      "projectId",
      "productionId",
      "displayName",
      "role",
      "identityType",
      "age",
      "apparentAge",
      "heightCm",
      "bodyType",
      "skinTone",
      "genderPresentation",
      "physicalProfileVersion",
      "speciesId",
      "typeId",
      "styleProfileId",
      "identityId",
      "faceId",
      "hairId",
      "skinId",
      "eyesId",
      "beardId",
      "bodyId",
      "agePresetId",
      "expressionId",
      "wardrobeIds",
      "accessoryIds",
      "rigId",
      "skeletonId",
      "materialIds",
      "textureIds",
      "animationIds",
      "voiceId",
      "uploadedAssets",
      "generatedAssets",
      "previewAssetId",
      "compatibilityProfileId",
      "pipelineStatus",
      "readinessStatus",
      "validationIssues",
      "validatedVersion",
      "validatedAt",
      "version",
      "createdAt",
      "updatedAt",
    ].sort();

    expect(Object.keys(character).sort()).toEqual(expectedFields);
    expect(
      Object.values(character)
        .flatMap((value) => (Array.isArray(value) ? value : [value]))
        .filter((value): value is string => typeof value === "string"),
    ).not.toContainEqual(expect.stringMatching(/\.(png|jpe?g|glb|fbx)$/iu));
  });
});
