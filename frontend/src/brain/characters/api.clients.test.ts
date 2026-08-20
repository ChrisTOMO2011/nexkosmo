import { describe, expect, it, vi } from "vitest";
import {
  canonicalEntityId,
  CharacterApiError,
  HttpCharacterDataGateway,
} from "./api.clients";
import { speciesSeedIds } from "./asset.manifest";

const characterResponse = {
  character_id: "51000001-0000-4000-8000-000000000001",
  project_id: "51000001-0000-4000-8000-000000000002",
  production_id: "51000001-0000-4000-8000-000000000003",
  display_name: "Christopher",
  role: "Lead",
  species_id: speciesSeedIds.human,
  type_id: null,
  identity_id: null,
  face_id: null,
  hair_id: null,
  skin_id: null,
  eyes_id: null,
  beard_id: null,
  body_id: null,
  age_preset_id: null,
  expression_id: null,
  wardrobe_ids: [],
  accessory_ids: [],
  rig_id: null,
  skeleton_id: null,
  material_ids: [],
  texture_ids: [],
  animation_ids: [],
  voice_id: null,
  uploaded_asset_ids: [],
  generated_asset_ids: [],
  preview_asset_id: null,
  compatibility_profile_id: "52000001-0000-4000-8000-000000000001",
  pipeline_status: "draft",
  downstream_status: [],
  version: 4,
  created_at: "2026-07-28T00:00:00Z",
  updated_at: "2026-07-28T00:00:00Z",
};

describe("production character API adapter", () => {
  it("maps snake_case contracts and canonicalizes external project IDs", async () => {
    const fetcher = vi.fn(async () =>
      Response.json({ items: [characterResponse], limit: 200, offset: 0 }),
    );
    const gateway = new HttpCharacterDataGateway(
      "https://api.example.test/api/v1",
      fetcher as typeof fetch,
    );
    const characters = await gateway.listByProject("the-last-dawn");

    expect(characters[0]).toMatchObject({
      characterId: characterResponse.character_id,
      displayName: "Christopher",
      speciesId: speciesSeedIds.human,
      version: 4,
    });
    expect(fetcher).toHaveBeenCalledWith(
      expect.stringContaining(
        `/projects/${canonicalEntityId("the-last-dawn")}/characters`,
      ),
      expect.any(Object),
    );
  });

  it("sends expected versions, snake_case bodies, and idempotency keys", async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce(Response.json(characterResponse))
      .mockResolvedValueOnce(
        Response.json({
          character: {
            ...characterResponse,
            species_id: speciesSeedIds.goblin,
            version: 5,
          },
          change_summary: { cleared_fields: ["hair_id"] },
        }),
      );
    const gateway = new HttpCharacterDataGateway(
      "https://api.example.test/api/v1",
      fetcher as typeof fetch,
    );
    await gateway.updateSelections(
      characterResponse.character_id,
      { speciesId: speciesSeedIds.goblin },
      "mutation-key",
    );

    const [, request] = fetcher.mock.calls[1];
    expect(request.headers).toMatchObject({
      "Content-Type": "application/json",
      "Idempotency-Key": "mutation-key",
    });
    expect(JSON.parse(request.body as string)).toEqual({
      species_id: speciesSeedIds.goblin,
      expected_version: 4,
    });
  });

  it("surfaces production API failures without local-data fallback", async () => {
    const fetcher = vi.fn(async () =>
      Response.json(
        {
          detail: "Expected character version 3, found 4.",
          code: "concurrency_conflict",
        },
        { status: 409 },
      ),
    );
    const gateway = new HttpCharacterDataGateway(
      "https://api.example.test/api/v1",
      fetcher as typeof fetch,
    );

    await expect(
      gateway.getCharacter(characterResponse.character_id),
    ).rejects.toMatchObject({
      status: 409,
      code: "concurrency_conflict",
      retryable: false,
    } satisfies Partial<CharacterApiError>);
    expect(fetcher).toHaveBeenCalledOnce();
  });
});
