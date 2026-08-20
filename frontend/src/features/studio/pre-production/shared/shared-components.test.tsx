import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import {
  ActionCards,
  ActiveProducerPanel,
  AssetSelectionSection,
  DeferredActionNotice,
  DomainAssetGrid,
  DomainEditorTabs,
  FilterPills,
  DomainSelectionRail,
  PreProductionWorkspace,
  SuggestionsPanel,
} from ".";

describe("shared Pre-Production presentation components", () => {
  it("preserves the canonical workspace regions without additional DOM wrappers", () => {
    const { container } = render(
      <PreProductionWorkspace
        sourcePanel={<div data-testid="source" />}
        preview={<div data-testid="preview" />}
        selectionRail={<div data-testid="rail" />}
        editorTabs={<div data-testid="tabs" />}
        editorContent={<div data-testid="content" />}
        editorLabel="Environment editor"
      />,
    );

    const top = container.querySelector(".workspace-top");
    const editor = container.querySelector(".lower-editor");
    expect(top?.children).toHaveLength(3);
    expect(editor).toHaveAttribute("aria-label", "Environment editor");
    expect(editor?.querySelector(".editor-scroll")).toContainElement(
      screen.getByTestId("content"),
    );
  });

  it("keeps selection, tabs and asset actions controlled by typed callbacks", () => {
    const onSelectRail = vi.fn();
    const onTabChange = vi.fn();
    const onSelectAsset = vi.fn();
    const railItem = {
      id: "setup-1",
      primaryText: "Setup One",
      secondaryText: "Primary",
      thumbnail: <span aria-hidden="true" />,
    };
    const asset = { id: "asset-1", name: "Asset One" };

    render(
      <>
        <DomainSelectionRail
          label="Setups"
          items={[railItem]}
          selectedId="setup-1"
          addLabel="Add Setup"
          onSelect={onSelectRail}
          onAdd={vi.fn()}
        />
        <DomainEditorTabs
          activeTab="identity"
          label="Domain editor"
          tabs={[{ id: "identity", label: "Identity" }]}
          onChange={onTabChange}
        />
        <DomainAssetGrid
          title="ASSETS"
          titleId="asset-title"
          items={[asset]}
          selectedId="asset-1"
          getId={(item) => item.id}
          getItemClassName={() => "species-card"}
          getLabel={(item) => item.name}
          renderMedia={() => <span aria-hidden="true" />}
          onSelect={onSelectAsset}
          emptyMessage="No assets available."
        />
      </>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Setup One, Primary" }));
    fireEvent.click(screen.getByRole("tab", { name: "Identity" }));
    fireEvent.click(screen.getByRole("button", { name: "Asset One" }));

    expect(onSelectRail).toHaveBeenCalledWith(railItem);
    expect(onTabChange).toHaveBeenCalledWith("identity");
    expect(onSelectAsset).toHaveBeenCalledWith(asset);
  });

  it("renders shared sections and suggestions from presentation data only", () => {
    const onApply = vi.fn();
    render(
      <>
        <AssetSelectionSection title="STYLE" titleId="style-title">
          <span>Selection content</span>
        </AssetSelectionSection>
        <SuggestionsPanel
          suggestions={[
            { id: "suggestion-1", title: "Suggestion", body: "Description" },
          ]}
          appliedIds={[]}
          renderMedia={() => <span aria-hidden="true" />}
          onApply={onApply}
          onViewAll={vi.fn()}
          onGenerateMore={vi.fn()}
        />
      </>,
    );

    expect(screen.getByRole("heading", { name: "STYLE" })).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: "Apply" }));
    expect(onApply).toHaveBeenCalledWith("suggestion-1");
  });

  it("keeps single selection border-only and multi selection membership explicit", () => {
    const asset = { id: "asset-1", name: "Asset One" };
    const { container, rerender } = render(
      <DomainAssetGrid
        title="ASSETS"
        titleId="asset-state-title"
        items={[asset]}
        selectedId="asset-1"
        getId={(item) => item.id}
        getItemClassName={() => "species-card"}
        getLabel={(item) => item.name}
        renderMedia={() => <span aria-hidden="true" />}
        onSelect={vi.fn()}
        emptyMessage="No assets."
      />,
    );

    expect(container.querySelector(".is-selected")).toBeInTheDocument();
    expect(container.querySelector(".selection-check")).not.toBeInTheDocument();

    rerender(
      <DomainAssetGrid
        title="ASSETS"
        titleId="asset-state-title"
        items={[asset]}
        selectedId="asset-1"
        selectionMode="multiple"
        getId={(item) => item.id}
        getItemClassName={() => "species-card"}
        getLabel={(item) => item.name}
        renderMedia={() => <span aria-hidden="true" />}
        onSelect={vi.fn()}
        emptyMessage="No assets."
      />,
    );

    expect(container.querySelector(".selection-check")).toBeInTheDocument();
  });

  it("renders controlled filters, typed action states and an honest deferred notice", () => {
    const onFilterChange = vi.fn();
    const onActivate = vi.fn();
    render(
      <>
        <FilterPills
          label="Asset filters"
          value="all"
          items={[
            { id: "all", label: "All" },
            { id: "human", label: "Human" },
          ]}
          onChange={onFilterChange}
        />
        <ActionCards
          className="action-cards"
          actions={[
            {
              id: "upload",
              label: "Upload",
              description: "Upload Your Own",
              icon: <span aria-hidden="true" />,
              status: "deferred",
            },
          ]}
          onActivate={onActivate}
        />
        <DeferredActionNotice action="asset-upload" />
      </>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Human" }));
    fireEvent.click(
      screen.getByRole("button", { name: "UploadUpload Your Own" }),
    );
    expect(onFilterChange).toHaveBeenCalledWith("human");
    expect(onActivate).toHaveBeenCalledWith(
      expect.objectContaining({ id: "upload", status: "deferred" }),
    );
    expect(screen.getByRole("status")).toHaveTextContent(
      "Upload pipeline is not yet connected",
    );
  });

  it("renders the assigned producer and uses Sophia for the BUILD fallback", () => {
    const onDeferred = vi.fn();
    const { rerender } = render(
      <ActiveProducerPanel
        profile={{
          producerProfileId: "producer-1",
          displayName: "Custom Producer",
          roleLabel: "AI Director",
          status: "active",
        }}
        context={{ domain: "characters", projectId: "project-1" }}
        onDeferredConversation={onDeferred}
      />,
    );

    expect(screen.getByText("Custom Producer")).toBeVisible();
    expect(screen.getByText("AI Director")).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: "Ask Custom" }));
    expect(onDeferred).toHaveBeenCalledOnce();

    rerender(
      <ActiveProducerPanel
        context={{ domain: "characters", projectId: "project-1" }}
        onDeferredConversation={onDeferred}
      />,
    );
    expect(screen.getByText("Sophia")).toBeVisible();
    expect(screen.getByText("AI Producer")).toBeVisible();
    expect(screen.getByRole("button", { name: "Ask Sophia" })).toBeVisible();
  });
});
