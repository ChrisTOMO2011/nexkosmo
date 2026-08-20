import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { describe, expect, it, vi } from "vitest";
import type { ApiSpecies } from "../../../brain/characters";
import {
  AccessorySelector,
  type AccessoryAssetItem,
} from "./AccessorySelector";
import { accessoryTabs } from "./data";
import {
  ALL_SPECIES_FILTER_ID,
  SpeciesSelector,
  type SpeciesFilterId,
} from "./SpeciesSelector";

const deferred = vi.fn();
const placeholder = vi.fn();

const speciesIds = {
  human: "20000001-0000-4000-8000-000000000001",
  elf: "20000002-0000-4000-8000-000000000002",
  goblin: "20000003-0000-4000-8000-000000000003",
  orc: "20000004-0000-4000-8000-000000000004",
  robot: "20000005-0000-4000-8000-000000000005",
  dragon: "20000006-0000-4000-8000-000000000006",
  alien: "20000007-0000-4000-8000-000000000007",
  monkey: "20000008-0000-4000-8000-000000000008",
  demon: "20000009-0000-4000-8000-000000000009",
} as const;

function speciesDefinition(
  key: keyof typeof speciesIds,
  name: string,
  enabled = true,
): ApiSpecies {
  return {
    speciesId: speciesIds[key],
    key,
    name,
    category: "test",
    enabled,
    capabilities: [],
    supportedTabs: ["Identity"],
    compatibilityProfileId: `profile:${key}`,
    minAge: 0,
    maxAge: 100,
    minHeightCm: 50,
    maxHeightCm: 300,
    surfaceControlLabel: "Skin Tone",
    version: 1,
  };
}

const speciesRegistry = [
  speciesDefinition("human", "Human"),
  speciesDefinition("elf", "Elf"),
  speciesDefinition("orc", "Orc"),
  speciesDefinition("robot", "Robot"),
  speciesDefinition("dragon", "Dragon"),
  speciesDefinition("alien", "Alien"),
  speciesDefinition("monkey", "Monkey"),
  speciesDefinition("demon", "Demon"),
  speciesDefinition("goblin", "Goblin"),
];

function SpeciesHarness({
  initialFilterId = speciesIds.human,
  selectedSpeciesId = speciesIds.human,
  onSpeciesChange = vi.fn(),
}: {
  initialFilterId?: SpeciesFilterId;
  selectedSpeciesId?: string;
  onSpeciesChange?: (species: ApiSpecies) => void;
}) {
  const [activeFilterId, setActiveFilterId] =
    useState<SpeciesFilterId>(initialFilterId);
  return (
    <SpeciesSelector
      activeFilterId={activeFilterId}
      selectedSpeciesId={selectedSpeciesId}
      species={speciesRegistry}
      onFilterChange={setActiveFilterId}
      onSpeciesChange={onSpeciesChange}
      onPlaceholder={placeholder}
      onDeferredAction={deferred}
    />
  );
}

function accessory(
  assetId: string,
  name: string,
  status = "available",
): AccessoryAssetItem {
  return { assetId, name, status, profileMetadata: {} };
}

const categoryAssets: Record<string, readonly AccessoryAssetItem[]> = {
  Glasses: [accessory("glasses:aviator", "Aviator")],
  Hats: [accessory("hats:fedora", "Fedora")],
  "Facial Hair": [accessory("facial-hair:goatee", "Goatee")],
  "Smoke & Pipes": [accessory("smoke-pipes:cigar", "Cigar")],
  "Pimples & Skin": [accessory("pimples-skin:freckles", "Light Freckles")],
  "Scars & Marks": [accessory("scars-marks:brow", "Brow Scar")],
  "Earrings & Jewellery": [accessory("jewellery:stud", "Stud")],
  Masks: [accessory("masks:half", "Half Mask")],
  More: [accessory("more:other", "Other Accessory")],
};

function AccessoryHarness({
  selectedIds = [],
  onAccessoryChange = vi.fn(),
}: {
  selectedIds?: readonly string[];
  onAccessoryChange?: (item: AccessoryAssetItem) => void;
}) {
  const [activeTab, setActiveTab] = useState("Glasses");
  return (
    <AccessorySelector
      activeTab={activeTab}
      selectedAccessoryIds={selectedIds}
      onTabChange={setActiveTab}
      onAccessoryChange={onAccessoryChange}
      onPlaceholder={placeholder}
      onDeferredAction={deferred}
      items={categoryAssets[activeTab]}
    />
  );
}

describe("Character identity filters", () => {
  it.each([
    ["Human", speciesIds.human],
    ["Elf", speciesIds.elf],
    ["Orc", speciesIds.orc],
    ["Robot", speciesIds.robot],
    ["Dragon", speciesIds.dragon],
    ["Alien", speciesIds.alien],
  ])(
    "shows only the %s species card without mutating the Character",
    (label, filterId) => {
      const onSpeciesChange = vi.fn();
      const { container } = render(
        <SpeciesHarness
          initialFilterId={filterId}
          onSpeciesChange={onSpeciesChange}
        />,
      );

      expect(
        Array.from(container.querySelectorAll(".species-card strong")).map(
          (item) => item.textContent,
        ),
      ).toEqual([label]);
      expect(onSpeciesChange).not.toHaveBeenCalled();
    },
  );

  it("shows every enabled species for All and only selects on a card click", () => {
    const onSpeciesChange = vi.fn();
    const { container } = render(
      <SpeciesHarness
        initialFilterId={ALL_SPECIES_FILTER_ID}
        onSpeciesChange={onSpeciesChange}
      />,
    );

    const cards = Array.from(
      container.querySelectorAll<HTMLButtonElement>(".species-card"),
    );
    expect(cards).toHaveLength(speciesRegistry.length);
    expect(onSpeciesChange).not.toHaveBeenCalled();
    fireEvent.click(cards.find((card) => card.textContent === "Elf")!);
    expect(onSpeciesChange).toHaveBeenCalledWith(
      expect.objectContaining({ speciesId: speciesIds.elf, key: "elf" }),
    );
  });

  it("excludes disabled species definitions from filters and the All grid", () => {
    const { container } = render(
      <SpeciesSelector
        activeFilterId={ALL_SPECIES_FILTER_ID}
        selectedSpeciesId={speciesIds.human}
        species={[
          ...speciesRegistry,
          speciesDefinition("goblin", "Disabled Goblin", false),
        ]}
        onFilterChange={vi.fn()}
        onSpeciesChange={vi.fn()}
        onPlaceholder={placeholder}
        onDeferredAction={deferred}
      />,
    );

    expect(container).not.toHaveTextContent("Disabled Goblin");
    expect(
      container.querySelectorAll(".species-card[data-species-key='goblin']"),
    ).toHaveLength(1);
  });

  it("uses canonical IDs for filter changes and reveals only additional species under More", async () => {
    const user = userEvent.setup();
    const { container } = render(
      <SpeciesHarness initialFilterId={speciesIds.human} />,
    );

    await user.click(screen.getByRole("button", { name: "Elf" }));
    expect(
      container.querySelector(".filter-row button[aria-pressed='true']"),
    ).toHaveTextContent("Elf");
    expect(
      Array.from(container.querySelectorAll(".species-card strong")).map(
        (item) => item.textContent,
      ),
    ).toEqual(["Elf"]);

    await user.click(screen.getByRole("button", { name: "More" }));
    expect(
      Array.from(container.querySelectorAll(".species-card strong")).map(
        (item) => item.textContent,
      ),
    ).toEqual(["Monkey", "Demon", "Goblin"]);
  });

  it("supports arrow-key navigation across species filters", () => {
    render(<SpeciesHarness initialFilterId={ALL_SPECIES_FILTER_ID} />);
    const allFilter = screen.getByRole("button", { name: "All" });
    allFilter.focus();
    fireEvent.keyDown(allFilter, { key: "ArrowRight" });

    const humanMatches = screen.getAllByRole("button", { name: "Human" });
    const humanFilter = humanMatches.find((item) =>
      item.closest("[aria-label='Species filters']"),
    );
    expect(humanFilter).toHaveAttribute("aria-pressed", "true");
    expect(humanFilter).toHaveFocus();
  });

  it("keeps selection, filter focus, and checkmark presentation independent", () => {
    const { container } = render(
      <SpeciesHarness
        initialFilterId={ALL_SPECIES_FILTER_ID}
        selectedSpeciesId={speciesIds.human}
      />,
    );
    const selectedCards = Array.from(
      container.querySelectorAll<HTMLButtonElement>(
        ".species-card[aria-pressed='true']",
      ),
    );
    expect(selectedCards).toHaveLength(1);
    expect(selectedCards[0]).toHaveAttribute("data-species-id", speciesIds.human);
    expect(selectedCards[0]).toHaveClass("is-selected");
    expect(selectedCards[0].querySelector(".selection-check")).toBeNull();
  });

  it("activates a focused species card from the keyboard", async () => {
    const user = userEvent.setup();
    const onSpeciesChange = vi.fn();
    render(
      <SpeciesHarness
        initialFilterId={speciesIds.elf}
        onSpeciesChange={onSpeciesChange}
      />,
    );

    const elfCards = screen.getAllByRole("button", { name: "Elf" });
    const elfCard = elfCards.find((item) => item.classList.contains("species-card"));
    expect(elfCard).toBeDefined();
    elfCard!.focus();
    await user.keyboard("{Enter}");

    expect(onSpeciesChange).toHaveBeenCalledWith(
      expect.objectContaining({ speciesId: speciesIds.elf }),
    );
  });

  it("switches every accessory category and renders only its canonical subset", async () => {
    const user = userEvent.setup();
    render(<AccessoryHarness />);

    for (const tab of accessoryTabs) {
      await user.click(screen.getByRole("tab", { name: tab }));
      expect(screen.getByRole("tab", { name: tab })).toHaveAttribute(
        "aria-selected",
        "true",
      );
      expect(screen.getByRole("button", { name: categoryAssets[tab][0].name })).toBeVisible();
      for (const otherTab of accessoryTabs.filter((item) => item !== tab)) {
        expect(
          screen.queryByRole("button", { name: categoryAssets[otherTab][0].name }),
        ).not.toBeInTheDocument();
      }
    }
  });

  it("supports arrow-key category navigation", () => {
    render(<AccessoryHarness />);
    const glassesTab = screen.getByRole("tab", { name: "Glasses" });
    glassesTab.focus();
    fireEvent.keyDown(glassesTab, { key: "ArrowRight" });

    expect(screen.getByRole("tab", { name: "Hats" })).toHaveAttribute(
      "aria-selected",
      "true",
    );
    expect(screen.getByRole("tab", { name: "Hats" })).toHaveFocus();
    expect(screen.getByRole("button", { name: "Fedora" })).toBeVisible();
  });

  it("uses UUID membership independently of the active category", async () => {
    const user = userEvent.setup();
    const selectedIds = ["glasses:aviator", "hats:fedora", "jewellery:stud"];
    const onAccessoryChange = vi.fn();
    render(
      <AccessoryHarness
        selectedIds={selectedIds}
        onAccessoryChange={onAccessoryChange}
      />,
    );

    const aviator = screen.getByRole("button", { name: "Aviator" });
    expect(aviator).toHaveAttribute("data-asset-id", "glasses:aviator");
    expect(aviator).toHaveAttribute("aria-pressed", "true");
    expect(aviator.querySelector(".selection-check")).toBeInTheDocument();
    expect(aviator).not.toHaveClass("is-selected");
    await user.click(aviator);
    expect(onAccessoryChange).toHaveBeenCalledWith(categoryAssets.Glasses[0]);

    await user.click(screen.getByRole("tab", { name: "Hats" }));
    expect(screen.getByRole("button", { name: "Fedora" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    await user.click(screen.getByRole("tab", { name: "Earrings & Jewellery" }));
    expect(screen.getByRole("button", { name: "Stud" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
  });

  it("disables unsupported assets and keeps deferred actions honest", async () => {
    const user = userEvent.setup();
    render(
      <AccessorySelector
        activeTab="Masks"
        selectedAccessoryIds={[]}
        onTabChange={vi.fn()}
        onAccessoryChange={vi.fn()}
        onPlaceholder={placeholder}
        onDeferredAction={deferred}
        items={[accessory("mask:unsupported", "Restricted Mask", "unsupported")]}
      />,
    );

    expect(screen.getByRole("button", { name: "Restricted Mask" })).toBeDisabled();
    await user.click(screen.getByRole("button", { name: "Upload" }));
    expect(deferred).toHaveBeenCalledWith("asset-upload");
    await user.click(screen.getByRole("button", { name: "AI Generate" }));
    expect(deferred).toHaveBeenCalledWith("character-generation");
  });
});
