import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import {
  CharacterApiError,
  characterPipelineService,
} from "../brain/characters";
import { AppRoutes } from "./App";

describe("Nexkosmo landing route", () => {
  it("reconnects the cinematic home at the root route", () => {
    window.history.replaceState({}, "", "/");

    render(<AppRoutes />);

    expect(screen.getByRole("heading", { name: "Nexkosmo" })).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Open Nexkosmo Studio" }),
    ).toHaveAttribute("href", "/studio");
  });
});

describe("Nexkosmo Discovery route", () => {
  it("renders the story discovery experience with the approved brand", () => {
    window.history.replaceState({}, "", "/discovery");

    render(<AppRoutes />);

    expect(
      screen.getByRole("heading", { name: "Let’s discover your story." }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("navigation", { name: "Story development progress" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Nexkosmo home" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Search" })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Open Nexkosmo Brain" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Untitled Movie" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Open menu" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Add anything" })).toBeInTheDocument();
  });

  it("opens Build this moment inside the Discovery workflow", async () => {
    const user = userEvent.setup();
    window.history.replaceState(
      {},
      "",
      "/discovery?projectId=the-last-dawn&characterId=christopher",
    );
    render(<AppRoutes />);

    await user.click(screen.getAllByRole("button", { name: "Build this moment" })[0]);

    expect(
      await screen.findByRole("region", { name: "Current story moment" }),
    ).toBeInTheDocument();
    expect(window.location.pathname).toBe("/discovery/moments/1");
    expect(screen.getByRole("button", { name: "Back to Movie Map" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "DISCOVER" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("button", { name: "Search" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Open Nexkosmo Brain" })).toBeInTheDocument();
  });
});

function renderCharacterRoute() {
  window.history.replaceState(
    {},
    "",
    "/studio/projects/the-last-dawn/pre-production/characters/christopher",
  );
  return render(<AppRoutes />);
}

describe("Nexkosmo character identity route", () => {
  it("renders the complete character identity workspace", () => {
    renderCharacterRoute();

    expect(
      screen.getByRole("heading", { name: "Christopher", level: 1 }),
    ).toBeInTheDocument();
    expect(screen.getByText("Camera Gear")).toBeInTheDocument();
    expect(screen.getByText("CGI Studio")).toBeInTheDocument();
    expect(
      screen.getByRole("tab", { name: "Identity" }),
    ).toHaveAttribute("aria-selected", "true");
    expect(screen.getAllByText("Upload").length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("AI Generate").length).toBeGreaterThanOrEqual(2);
    expect(screen.queryByText("None")).not.toBeInTheDocument();
  });

  it("supports character, style, slider and honest suggestion interactions", async () => {
    const user = userEvent.setup();
    renderCharacterRoute();

    await user.click(
      await screen.findByRole("button", { name: "Sarah, Co-Lead" }),
    );
    expect(
      screen.getByRole("button", { name: "Sarah, Co-Lead" }),
    ).toHaveAttribute("aria-pressed", "true");

    await user.click(screen.getByRole("button", { name: "Cartoon" }));
    expect(screen.getByRole("button", { name: "Cartoon" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );

    const age = screen.getByRole("slider", { name: "Age" });
    fireEvent.change(age, { target: { value: "42" } });
    expect(age).toHaveValue("42");

    await user.click(screen.getAllByRole("button", { name: "Apply" })[0]);
    expect(
      screen.getByText(
        "This curated preset is not mapped to a Character command yet. No Character selection was changed.",
      ),
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Applied" })).not.toBeInTheDocument();
  });

  it("keeps a delayed physical save scoped to the character that initiated it", async () => {
    const user = userEvent.setup();
    renderCharacterRoute();
    const sarah = await screen.findByRole("button", {
      name: "Sarah, Co-Lead",
    });
    const age = screen.getByRole("slider", { name: "Age" });

    fireEvent.change(age, { target: { value: "61" } });
    await user.click(sarah);
    const selectedCharacterAge = age.getAttribute("value");

    await new Promise((resolve) => window.setTimeout(resolve, 450));

    expect(sarah).toHaveAttribute("aria-pressed", "true");
    expect(age).toHaveAttribute("value", selectedCharacterAge);
  });

  it("uses one border-only selection for single-choice groups and checks for multi-select membership", async () => {
    const user = userEvent.setup();
    const { container } = renderCharacterRoute();
    await screen.findByRole("button", { name: "Sarah, Co-Lead" });

    const faceButtons = screen.getAllByRole("button", {
      name: /Select face variant/u,
    });
    expect(
      faceButtons.filter((button) => button.getAttribute("aria-pressed") === "true"),
    ).toHaveLength(1);
    expect(
      faceButtons.find((button) => button.getAttribute("aria-pressed") === "true")
        ?.querySelector(".selection-check"),
    ).toBeNull();

    const styleCards = Array.from(
      container.querySelectorAll<HTMLButtonElement>(".style-card"),
    );
    expect(
      styleCards.filter((button) => button.getAttribute("aria-pressed") === "true"),
    ).toHaveLength(1);
    expect(container.querySelector(".style-card .selection-check")).toBeNull();
    const previousStyle = styleCards.find(
      (button) => button.getAttribute("aria-pressed") === "true",
    );
    const nextStyle = styleCards.find((button) => button !== previousStyle);
    await user.click(nextStyle!);
    await waitFor(() => expect(nextStyle).toHaveAttribute("aria-pressed", "true"));
    expect(previousStyle).toHaveAttribute("aria-pressed", "false");
    expect(previousStyle).not.toHaveClass("is-selected");

    const speciesCards = Array.from(
      container.querySelectorAll<HTMLButtonElement>(".species-card"),
    );
    expect(
      speciesCards.filter((button) => button.getAttribute("aria-pressed") === "true"),
    ).toHaveLength(1);

    const aviator = await screen.findByRole("button", { name: "Aviator" });
    await user.click(aviator);
    await waitFor(() => expect(aviator).toHaveAttribute("aria-pressed", "true"));
    expect(aviator.querySelector(".selection-check")).toBeInTheDocument();
    expect(aviator).toHaveAttribute("data-selection-mode", "multiple");
  });

  it("switches accessory categories without mutation and persists cross-category membership", async () => {
    const user = userEvent.setup();
    const updateSpy = vi.spyOn(
      characterPipelineService,
      "updateSelectionsInSource",
    );
    const firstRender = renderCharacterRoute();
    await screen.findByRole("button", { name: "Aviator" });

    const initialMutationCount = updateSpy.mock.calls.length;
    for (const tab of [
      "Hats",
      "Facial Hair",
      "Scars & Marks",
      "Earrings & Jewellery",
      "Glasses",
    ]) {
      await user.click(screen.getByRole("tab", { name: tab }));
      expect(screen.getByRole("tab", { name: tab })).toHaveAttribute(
        "aria-selected",
        "true",
      );
    }
    expect(updateSpy).toHaveBeenCalledTimes(initialMutationCount);

    const aviator = screen.getByRole("button", { name: "Aviator" });
    if (aviator.getAttribute("aria-pressed") !== "true") {
      await user.click(aviator);
      await waitFor(() => expect(aviator).toHaveAttribute("aria-pressed", "true"));
    }
    await user.click(screen.getByRole("tab", { name: "Hats" }));
    const fedora = await screen.findByRole("button", { name: "Fedora" });
    if (fedora.getAttribute("aria-pressed") !== "true") {
      await user.click(fedora);
      await waitFor(() => expect(fedora).toHaveAttribute("aria-pressed", "true"));
    }
    await user.click(screen.getByRole("tab", { name: "Earrings & Jewellery" }));
    const stud = await screen.findByRole("button", { name: "Stud" });
    if (stud.getAttribute("aria-pressed") !== "true") {
      await user.click(stud);
      await waitFor(() => expect(stud).toHaveAttribute("aria-pressed", "true"));
    }

    firstRender.unmount();
    renderCharacterRoute();
    await screen.findByRole("button", { name: "Aviator" });
    expect(screen.getByRole("button", { name: "Aviator" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    await user.click(screen.getByRole("tab", { name: "Hats" }));
    expect(await screen.findByRole("button", { name: "Fedora" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    await user.click(screen.getByRole("tab", { name: "Earrings & Jewellery" }));
    expect(await screen.findByRole("button", { name: "Stud" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    await user.click(screen.getByRole("tab", { name: "Hats" }));
    const persistedFedora = await screen.findByRole("button", { name: "Fedora" });
    await user.click(persistedFedora);
    await waitFor(() => expect(persistedFedora).toHaveAttribute("aria-pressed", "false"));
    await user.click(screen.getByRole("tab", { name: "Glasses" }));
    expect(screen.getByRole("button", { name: "Aviator" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    await user.click(screen.getByRole("tab", { name: "Earrings & Jewellery" }));
    expect(screen.getByRole("button", { name: "Stud" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    updateSpy.mockRestore();
  });

  it("rolls back a failed optimistic accessory toggle", async () => {
    const user = userEvent.setup();
    renderCharacterRoute();
    await screen.findByRole("button", { name: "Aviator" });
    await user.click(screen.getByRole("tab", { name: "Masks" }));
    const mask = await screen.findByRole("button", { name: "Half Mask" });
    const initiallySelected = mask.getAttribute("aria-pressed");
    const updateSpy = vi
      .spyOn(characterPipelineService, "updateSelectionsInSource")
      .mockRejectedValueOnce(
        new CharacterApiError("Accessory update failed.", 500, "api_error", true),
      );

    await user.click(mask);
    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent("Accessory update failed."),
    );
    expect(mask).toHaveAttribute("aria-pressed", initiallySelected);
    updateSpy.mockRestore();
  });

  it("reloads authoritative accessories after a version conflict", async () => {
    const user = userEvent.setup();
    const updateSpy = vi
      .spyOn(characterPipelineService, "updateSelectionsInSource")
      .mockRejectedValueOnce(
        new CharacterApiError(
          "Expected character version 8, found 9.",
          409,
          "concurrency_conflict",
          false,
        ),
      );
    const getSpy = vi.spyOn(characterPipelineService.gateway, "getCharacter");
    renderCharacterRoute();
    await screen.findByRole("button", { name: "Aviator" });
    await user.click(screen.getByRole("tab", { name: "Scars & Marks" }));
    const scar = await screen.findByRole("button", { name: "Brow Scar" });
    const authoritativeMembership = scar.getAttribute("aria-pressed");

    await user.click(scar);
    await waitFor(() =>
      expect(
        screen.getByText(
          "This character changed elsewhere. The authoritative Character state has been reloaded.",
        ),
      ).toBeInTheDocument(),
    );
    expect(getSpy).toHaveBeenCalled();
    expect(scar).toHaveAttribute("aria-pressed", authoritativeMembership);
    updateSpy.mockRestore();
    getSpy.mockRestore();
  });

  it("keeps every populated Character asset tab single-select and border-only", async () => {
    const user = userEvent.setup();
    const { container } = renderCharacterRoute();
    await screen.findByRole("button", { name: "Sarah, Co-Lead" });

    for (const tabName of [
      "Face",
      "Hair",
      "Skin",
      "Eyes",
      "Beard",
      "Age",
      "Expression",
    ]) {
      await user.click(screen.getByRole("tab", { name: tabName }));
      await screen.findByRole("heading", {
        name: `${tabName.toLocaleUpperCase()} PRESETS`,
      });
      await waitFor(() =>
        expect(
          container.querySelector(".character-asset-grid") ??
            container.querySelector(".character-asset-editor [role='status']"),
        ).toBeInTheDocument(),
      );
      const cards = Array.from(
        container.querySelectorAll<HTMLButtonElement>(
          ".character-asset-grid button",
        ),
      );
      if (cards.length === 0) {
        expect(
          screen.getByText(
            `No compatible ${tabName.toLocaleLowerCase()} presets are available.`,
          ),
        ).toBeVisible();
        continue;
      }
      const initiallySelected = cards.filter(
        (button) => button.getAttribute("aria-pressed") === "true",
      );
      if (initiallySelected.length === 0) {
        await user.click(cards[0]);
      }
      await waitFor(() =>
        expect(
          cards.filter(
            (button) => button.getAttribute("aria-pressed") === "true",
          ),
        ).toHaveLength(1),
      );
      expect(
        container.querySelector(".character-asset-grid .selection-check"),
      ).toBeNull();
    }
  });

  it("keeps upload, generation and producer interactions explicitly deferred", async () => {
    const user = userEvent.setup();
    renderCharacterRoute();
    await screen.findByRole("button", { name: "Sarah, Co-Lead" });

    await user.click(
      screen.getByRole("button", { name: /Drag & drop face image here/u }),
    );
    expect(
      screen.getByText(
        "Upload pipeline is not yet connected. This feature will be available in the Asset Upload and Ingestion phase.",
      ),
    ).toBeInTheDocument();
    expect(screen.queryByAltText("Uploaded identity source")).not.toBeInTheDocument();

    const speciesSection = screen
      .getByRole("heading", { name: "SPECIES / TYPE" })
      .closest("section");
    expect(speciesSection).not.toBeNull();
    await user.click(
      within(speciesSection!).getByRole("button", {
        name: "AI GenerateGenerate with AI",
      }),
    );
    expect(
      screen.getByText(
        "AI generation is not yet connected. This feature will be available in the AI Character Generation phase.",
      ),
    ).toBeInTheDocument();

    expect(screen.getByText("Sophia")).toBeVisible();
    expect(screen.getByText("AI Producer")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Ask Sophia" }));
    expect(
      screen.getByText(
        "Producer conversation is not yet connected. No conversation or message thread was created.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "CURATED SUGGESTIONS" }),
    ).toBeVisible();
    expect(screen.queryByText("AI SUGGESTIONS")).not.toBeInTheDocument();
  });

  it("rolls back a failed optimistic style selection", async () => {
    const user = userEvent.setup();
    const updateSpy = vi
      .spyOn(characterPipelineService, "updateSelectionsInSource")
      .mockRejectedValueOnce(
        new CharacterApiError("Style update failed.", 500, "api_error", true),
      );
    const { container } = renderCharacterRoute();
    await screen.findByRole("button", { name: "Sarah, Co-Lead" });
    const cards = Array.from(
      container.querySelectorAll<HTMLButtonElement>(".style-card"),
    );
    const selected = cards.find(
      (button) => button.getAttribute("aria-pressed") === "true",
    );
    const target = cards.find((button) => button !== selected);
    expect(selected).toBeDefined();
    expect(target).toBeDefined();

    await user.click(target!);
    await waitFor(() => expect(selected).toHaveAttribute("aria-pressed", "true"));
    expect(target).toHaveAttribute("aria-pressed", "false");
    updateSpy.mockRestore();
  });

  it("reloads authoritative Character state after a version conflict", async () => {
    const user = userEvent.setup();
    const updateSpy = vi
      .spyOn(characterPipelineService, "updateSelectionsInSource")
      .mockRejectedValueOnce(
        new CharacterApiError(
          "Expected character version 3, found 4.",
          409,
          "concurrency_conflict",
          false,
        ),
      );
    const getSpy = vi.spyOn(characterPipelineService.gateway, "getCharacter");
    const { container } = renderCharacterRoute();
    await screen.findByRole("button", { name: "Sarah, Co-Lead" });
    const cards = Array.from(
      container.querySelectorAll<HTMLButtonElement>(".style-card"),
    );
    const selected = cards.find(
      (button) => button.getAttribute("aria-pressed") === "true",
    );
    const target = cards.find((button) => button !== selected);

    await user.click(target!);
    await waitFor(() =>
      expect(
        screen.getByText(
          "This character changed elsewhere. The authoritative Character state has been reloaded.",
        ),
      ).toBeInTheDocument(),
    );
    expect(getSpy).toHaveBeenCalled();
    expect(selected).toHaveAttribute("aria-pressed", "true");
    updateSpy.mockRestore();
    getSpy.mockRestore();
  });

  it("changes species filters without issuing a Character mutation", async () => {
    const user = userEvent.setup();
    const mutationSpy = vi.spyOn(
      characterPipelineService,
      "changeSpeciesInSource",
    );
    const { container } = renderCharacterRoute();
    await screen.findByRole("button", { name: "Sarah, Co-Lead" });

    await user.click(screen.getByRole("button", { name: "Elf" }));
    expect(
      container.querySelector(".filter-row button[aria-pressed='true']"),
    ).toHaveTextContent("Elf");
    expect(
      Array.from(container.querySelectorAll(".species-card strong")).map(
        (item) => item.textContent,
      ),
    ).toEqual(["Elf"]);
    expect(mutationSpy).not.toHaveBeenCalled();
    mutationSpy.mockRestore();
  });

  it("rolls back an optimistic species selection when the mutation fails", async () => {
    const user = userEvent.setup();
    const mutationSpy = vi
      .spyOn(characterPipelineService, "changeSpeciesInSource")
      .mockRejectedValueOnce(
        new CharacterApiError("Species update failed.", 500, "api_error", true),
      );
    const { container } = renderCharacterRoute();
    await screen.findByRole("button", { name: "Sarah, Co-Lead" });
    await user.click(screen.getByRole("button", { name: "Robot" }));
    const robotCard = container.querySelector<HTMLButtonElement>(
      ".species-card[data-species-key='robot']",
    );
    expect(robotCard).not.toBeNull();
    await user.click(robotCard!);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Species update failed. Try the action again.",
    );
    await user.click(screen.getByRole("button", { name: "All" }));
    expect(
      container.querySelector(".species-card[data-species-key='human']"),
    ).toHaveAttribute("aria-pressed", "true");
    expect(
      container.querySelector(".species-card[data-species-key='robot']"),
    ).toHaveAttribute("aria-pressed", "false");
    mutationSpy.mockRestore();
  });

  it("reloads the authoritative species after a species version conflict", async () => {
    const user = userEvent.setup();
    const mutationSpy = vi
      .spyOn(characterPipelineService, "changeSpeciesInSource")
      .mockRejectedValueOnce(
        new CharacterApiError(
          "Expected character version 4, found 5.",
          409,
          "concurrency_conflict",
          false,
        ),
      );
    const getSpy = vi.spyOn(characterPipelineService.gateway, "getCharacter");
    const { container } = renderCharacterRoute();
    await screen.findByRole("button", { name: "Sarah, Co-Lead" });
    await user.click(screen.getByRole("button", { name: "Robot" }));
    await user.click(
      container.querySelector<HTMLButtonElement>(
        ".species-card[data-species-key='robot']",
      )!,
    );

    await screen.findByText(
      "This character changed elsewhere. The authoritative Character state has been reloaded.",
    );
    expect(getSpy).toHaveBeenCalled();
    expect(
      container.querySelector(".filter-row button[aria-pressed='true']"),
    ).toHaveTextContent("Human");
    expect(
      container.querySelector(".species-card[data-species-key='human']"),
    ).toHaveAttribute("aria-pressed", "true");
    mutationSpy.mockRestore();
    getSpy.mockRestore();
  });

  it("reconciles supported tabs and compatible assets after species selection", async () => {
    const user = userEvent.setup();
    const tabsSpy = vi.spyOn(
      characterPipelineService.gateway,
      "getSupportedTabs",
    );
    const assetsSpy = vi.spyOn(
      characterPipelineService,
      "loadCompatibleAssetsFromSource",
    );
    const { container } = renderCharacterRoute();
    await screen.findByRole("button", { name: "Sarah, Co-Lead" });
    const initialTabCalls = tabsSpy.mock.calls.length;
    const initialAssetCalls = assetsSpy.mock.calls.length;
    await user.click(screen.getByRole("button", { name: "Robot" }));
    await user.click(
      container.querySelector<HTMLButtonElement>(
        ".species-card[data-species-key='robot']",
      )!,
    );

    await screen.findByText(/Robot compatibility profile saved\./u);
    await waitFor(() => {
      expect(tabsSpy.mock.calls.length).toBeGreaterThan(initialTabCalls);
      expect(assetsSpy.mock.calls.length).toBeGreaterThan(initialAssetCalls);
    });
    expect(screen.queryByRole("tab", { name: "Hair" })).not.toBeInTheDocument();
    expect(screen.queryByRole("tab", { name: "Beard" })).not.toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Identity" })).toHaveAttribute(
      "aria-selected",
      "true",
    );
    expect(
      container.querySelectorAll(".species-card[aria-pressed='true']"),
    ).toHaveLength(1);
    expect(container.querySelector(".species-card .selection-check")).toBeNull();
    tabsSpy.mockRestore();
    assetsSpy.mockRestore();
  });

  it("restores persisted character selections after a page reload", async () => {
    const user = userEvent.setup();
    const firstRender = renderCharacterRoute();
    await screen.findByRole("button", { name: "Sarah, Co-Lead" });
    await user.click(screen.getByRole("button", { name: "Elf" }));
    const elfCard = firstRender.container.querySelector<HTMLButtonElement>(
      ".species-card[data-species-key='elf']",
    );
    expect(elfCard).not.toBeNull();
    await user.click(elfCard!);
    await waitFor(() =>
      expect(
        screen.getByText(/Elf compatibility profile saved\./u),
      ).toBeInTheDocument(),
    );
    firstRender.unmount();

    const secondRender = renderCharacterRoute();
    await screen.findByRole("button", { name: "Sarah, Co-Lead" });
    await waitFor(() =>
      expect(
        secondRender.container.querySelector(
          ".species-card[data-species-key='elf']",
        ),
      ).toHaveAttribute("aria-pressed", "true"),
    );
  });
});

describe("Nexkosmo workflow foundations", () => {
  it("moves between workflow stages without reloading the application", async () => {
    const user = userEvent.setup();
    window.history.replaceState(
      {},
      "",
      "/discovery?projectId=the-last-dawn&characterId=christopher",
    );

    render(<AppRoutes />);
    await user.click(screen.getByRole("link", { name: "SHAPE" }));

    expect(
      await screen.findByRole("heading", { name: "SHAPE", level: 1 }),
    ).toBeInTheDocument();
    expect(window.location.pathname).toBe(
      "/studio/projects/the-last-dawn/script",
    );
    expect(screen.getByText("Your AI Producer")).toBeInTheDocument();
  });

  it("renders the canonical IDEA workflow route", () => {
    window.history.replaceState(
      {},
      "",
      "/studio/projects/the-last-dawn/idea",
    );

    render(<AppRoutes />);

    expect(
      screen.getByRole("heading", {
        name: "What do you want to create?",
        level: 1,
      }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "IDEA" })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });

  it.each([
    ["script", "SHAPE"],
  ])("renders the canonical %s workflow route", (route, label) => {
    window.history.replaceState(
      {},
      "",
      `/studio/projects/the-last-dawn/${route}`,
    );

    render(<AppRoutes />);

    expect(
      screen.getByRole("heading", { name: label, level: 1 }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: label })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });

  it("renders the canonical READY workflow route", () => {
    window.history.replaceState(
      {},
      "",
      "/studio/projects/the-last-dawn/ready",
    );

    render(<AppRoutes />);

    expect(
      screen.getByRole("heading", {
        name: "Ready to bring it to life?",
        level: 1,
      }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "READY" })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });

  it.each([
    ["set", "SET"],
    ["render", "RENDER"],
  ])("renders the shared shell for the %s route", (route, label) => {
    window.history.replaceState(
      {},
      "",
      `/studio/projects/the-last-dawn/${route}`,
    );

    render(<AppRoutes />);

    expect(
      screen.getByRole("heading", { name: label, level: 1 }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "PRODUCTION" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByText("Primary workspace")).toBeInTheDocument();
    expect(screen.getByText("Inspector")).toBeInTheDocument();
  });

  it("renders the canonical PRODUCTION workflow route", () => {
    window.history.replaceState(
      {},
      "",
      "/studio/projects/the-last-dawn/studio",
    );

    render(<AppRoutes />);

    expect(
      screen.getByRole("heading", {
        name: "We're making your movie.",
        level: 1,
      }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "PRODUCTION" })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });
});
