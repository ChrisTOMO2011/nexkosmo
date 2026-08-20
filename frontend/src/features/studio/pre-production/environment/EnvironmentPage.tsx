import {
  Box,
  Building2,
  CloudRain,
  Clock3,
  CloudUpload,
  Hexagon,
  Info,
  Layers3,
  Leaf,
  Map,
  Mountain,
  Palette,
  Pencil,
  Sparkles,
  SlidersHorizontal,
  SunMedium,
} from "lucide-react";
import { useState } from "react";
import type { Environment, EnvironmentType } from "../../../../brain/environments";
import { BottomActionBar, LeftSidebar, RightSidebar } from "../../../../components/studio";
import { Button, Dropdown, PropertyField, Slider, UploadArea } from "../../../../components/ui";
import { StudioLayout } from "../../../../layouts/StudioLayout";
import { navigateInApp } from "../../../../app/navigation";
import { preProductionNavigation } from "../../config/navigation";
import {
  ActionCards,
  ActiveProducerPanel,
  DeferredActionNotice,
  DomainAssetGrid,
  DomainEditorTabs,
  DomainInspectorPanel,
  DomainPreviewCarousel,
  DomainSelectionRail,
  DomainSourcePanel,
  DomainStatusNotice,
  FilterPills,
  PreProductionWorkspace,
  SuggestionsPanel,
} from "../shared";
import {
  environmentMultiCategories,
  environmentTitleCase as titleCase,
} from "./environment-workspace.config";
import { useEnvironmentWorkspaceController } from "./useEnvironmentWorkspaceController";

type EnvironmentPageProps = {
  projectId: string;
  environmentId?: string;
};

const tabIcons = [
  Map,
  Mountain,
  Building2,
  Leaf,
  CloudRain,
  Clock3,
  SunMedium,
  Palette,
  SlidersHorizontal,
];

export function EnvironmentPage({ projectId, environmentId }: EnvironmentPageProps) {
  const controller = useEnvironmentWorkspaceController({ projectId, environmentId });
  const {
    ownership,
    producer,
    types,
    environments,
    selected,
    selectedId,
    selectedType,
    readiness,
    supportedTabs,
    category,
    assets,
    filterItems,
    selectedAssetIds,
    activeTab,
    activeFilter,
    previewSlide,
    propertiesOpen,
    pending,
    deferredAction,
    status,
    setStatus,
    setPropertiesOpen,
    setPreviewSlide,
    setActiveTab,
    setActiveFilter,
    showDeferred,
    createEnvironment,
    selectEnvironment,
    updateIdentity,
    updateProperties,
    changeType,
    selectAsset,
    validateReadiness,
  } = controller;
  const tabs = supportedTabs.map((tab, index) => {
    const Icon = tabIcons[index] ?? Layers3;
    return { id: tab, label: tab, icon: <Icon aria-hidden="true" /> };
  });

  return (
    <StudioLayout
      activeStage="build"
      projectId={projectId}
      variant="character-identity"
      leftSidebar={
        <LeftSidebar
          items={preProductionNavigation}
          activeItem="Environment"
          sectionLabel="Pre-production sections"
          onNavigate={(label) => {
            if (label === "Characters") {
              navigateInApp(
                `/studio/projects/${projectId}/pre-production/characters/christopher`,
              );
            } else if (label !== "Environment") {
              setStatus(`${label} has not started.`);
            }
          }}
          onPlaceholder={setStatus}
          producerPanel={
            <ActiveProducerPanel
              profile={producer}
              context={{
                domain: "environment",
                projectId,
                productionId: ownership?.productionId,
                entityId: selectedId,
                activeTab,
                readinessStatus: readiness?.readinessStatus,
                details: {
                  environmentType: selectedType?.key ?? "unselected",
                  timeOfDay: selected?.timeOfDay ?? "unselected",
                  weatherProfileId: selected?.weatherProfileId ?? "unselected",
                  blockingIssueCount: String(readiness?.blockingIssues.length ?? 0),
                },
              }}
              onDeferredConversation={() => showDeferred("producer-conversation")}
            />
          }
        />
      }
      rightSidebar={
        <RightSidebar
          open={propertiesOpen}
          title="Environment properties"
          onClose={() => setPropertiesOpen(false)}
        >
          <EnvironmentInspector
            environment={selected}
            types={types}
            pending={pending}
            readinessStatus={readiness?.readinessStatus}
            onStatus={setStatus}
            onIdentity={(values) => void updateIdentity(values)}
            onUpdate={(values) => void updateProperties(values)}
            onValidate={() => void validateReadiness()}
          />
        </RightSidebar>
      }
      bottomActionBar={
        <BottomActionBar
          sceneName={selected?.displayName ?? "ENVIRONMENT PACKAGE"}
          primaryLabel="Next: READY"
          primaryDisabled={readiness?.readinessStatus !== "ready_for_scene"}
          onSecondary={() => setStatus("Environment preview rendering is deferred.")}
          onPrimary={() => navigateInApp(`/studio/projects/${projectId}/ready`)}
        />
      }
      rightSidebarLabel="Open Environment properties"
      onOpenRightSidebar={() => setPropertiesOpen(true)}
      onPlaceholder={setStatus}
      statusMessage={status}
      statusNotice={
        deferredAction ? (
          <DeferredActionNotice key={status} action={deferredAction} />
        ) : (
          <DomainStatusNotice key={status} message={status} />
        )
      }
    >
      <PreProductionWorkspace
        sourcePanel={
          <DomainSourcePanel
            title="ENVIRONMENT SOURCE"
            titleId="environment-source-title"
            titleAdornment={<Info aria-hidden="true" />}
            heading={
              <div className="character-heading">
                <p className="breadcrumb">
                  ENVIRONMENTS <span>›</span>{" "}
                  {selected?.displayName.toUpperCase() ?? "NEW PACKAGE"}
                </p>
                <h1>
                  {selected?.displayName ?? "Environment"}
                  <button
                    type="button"
                    aria-label="Edit Environment name"
                    onClick={() => setPropertiesOpen(true)}
                  >
                    <Pencil aria-hidden="true" />
                  </button>
                </h1>
                <p className="character-role">Pre-Production Environment</p>
                <div className="identity-tags">
                  <span>{selectedType?.name ?? "Unselected"}</span>
                  <span>{selected ? titleCase(selected.interiorExterior) : "Package"}</span>
                </div>
              </div>
            }
            source={
              <UploadArea
                className="upload-dropzone"
                label="Upload environment reference"
                helperText="JPG, PNG up to 10MB"
                onActivate={() => {
                  showDeferred("asset-upload");
                  return false;
                }}
                onFile={() => showDeferred("asset-upload")}
                preview={
                  <>
                    <CloudUpload aria-hidden="true" />
                    <strong>Drag &amp; drop environment image here</strong>
                    <span>or click to upload</span>
                    <small>JPG, PNG up to 10MB</small>
                  </>
                }
              />
            }
            variants={
              <div
                className="face-thumbnails environment-source-variants"
                aria-label="Environment source variants"
              >
                {[0, 1, 2, 3].map((index) => (
                  <button
                    key={index}
                    type="button"
                    className={`face-thumb environment-variant environment-variant-${index + 1} ${previewSlide === index ? "is-selected" : ""}`}
                    aria-label={`Select environment variant ${index + 1}`}
                    aria-pressed={previewSlide === index}
                    onClick={() => setPreviewSlide(index)}
                  />
                ))}
              </div>
            }
            primaryAction={
              <Button
                className="generate-button"
                leadingIcon={<Sparkles aria-hidden="true" />}
                onClick={() => showDeferred("character-generation")}
              >
                Generate with AI
              </Button>
            }
          />
        }
        preview={
          <DomainPreviewCarousel
            items={[0, 1, 2, 3, 4]}
            activeIndex={previewSlide}
            label="Environment cinematic preview"
            modes={[
              {
                id: "lit",
                label: "Lit",
                icon: <Hexagon aria-hidden="true" />,
                onSelect: () => setStatus("Lit viewport mode selected."),
              },
              {
                id: "wireframe",
                label: "Wireframe",
                icon: <Box aria-hidden="true" />,
                onSelect: () =>
                  setStatus("Wireframe viewport is a non-processing display placeholder."),
              },
            ]}
            onChange={setPreviewSlide}
            onPrevious={() => setPreviewSlide((previewSlide + 4) % 5)}
            onNext={() => setPreviewSlide((previewSlide + 1) % 5)}
            onExpand={() => setStatus("Fullscreen Environment preview is deferred.")}
            getPreviewClassName={(_, index) =>
              `preview-image environment-preview environment-preview-${index}`
            }
            renderPreviewContent={() => (
              <>
                <div className="environment-preview-label">
                  <span>{selectedType?.name ?? "Environment"}</span>
                  <strong>{selected?.displayName ?? "Create an Environment package"}</strong>
                </div>
                <div className="preview-shade" />
              </>
            )}
          />
        }
        selectionRail={
          <DomainSelectionRail
            label="Environment packages"
            items={environments.map((item, index) => ({
              id: item.environmentId,
              primaryText: item.displayName,
              secondaryText:
                types.find((type) => type.environmentTypeId === item.environmentTypeId)?.name ??
                "Environment",
              thumbnail: (
                <span
                  className={`environment-rail-thumb environment-rail-thumb-${(index % 4) + 1}`}
                  aria-hidden="true"
                />
              ),
            }))}
            selectedId={selectedId}
            addLabel="Add Environment"
            onSelect={(item) => selectEnvironment(item.id)}
            onAdd={() => void createEnvironment()}
          />
        }
        editorTabs={
          <DomainEditorTabs
            className="editor-tabs environment-editor-tabs"
            activeTab={activeTab}
            tabs={tabs}
            label="Environment editor"
            onChange={setActiveTab}
          />
        }
        editorLabel={`${activeTab} Environment editor`}
        editorContent={
          selected ? (
            activeTab === "Identity" ? (
              <EnvironmentIdentityEditor
                environment={selected}
                types={types}
                pending={pending}
                onChangeType={(typeId) => void changeType(typeId)}
                onStatus={setStatus}
              />
            ) : activeTab === "Time" ? (
              <TimeEditor
                environment={selected}
                onSelect={(time) => void updateProperties({ time_of_day: time })}
              />
            ) : (
              <div className="environment-asset-editor">
                <FilterPills
                  items={filterItems}
                  value={activeFilter}
                  label={`${activeTab} filters`}
                  onChange={setActiveFilter}
                />
                <DomainAssetGrid
                  title={`${activeTab.toUpperCase()} ASSETS`}
                  titleId="environment-assets-title"
                  items={assets}
                  selectedId={
                    environmentMultiCategories.has(category ?? "")
                      ? undefined
                      : selectedAssetIds[0]
                  }
                  selectedIds={
                    environmentMultiCategories.has(category ?? "")
                      ? selectedAssetIds
                      : undefined
                  }
                  selectionMode={
                    environmentMultiCategories.has(category ?? "") ? "multiple" : "single"
                  }
                  getId={(asset) => asset.assetId}
                  getLabel={(asset) => asset.name}
                  getItemClassName={(asset) =>
                    `accessory-card environment-asset-card environment-${asset.subcategory}`
                  }
                  renderMedia={(asset) => (
                    <span
                      className="environment-asset-media"
                      data-subcategory={asset.subcategory}
                      aria-hidden="true"
                    />
                  )}
                  getStatus={(asset) =>
                    asset.status === "development-placeholder" ? "deferred" : "available"
                  }
                  emptyMessage={`No compatible ${activeTab.toLowerCase()} assets are available for this Environment type.`}
                  onSelect={(asset) => void selectAsset(asset)}
                />
              </div>
            )
          ) : (
            <EmptyEnvironmentEditor onCreate={() => void createEnvironment()} />
          )
        }
      />
    </StudioLayout>
  );
}

function EnvironmentIdentityEditor({
  environment,
  types,
  pending,
  onChangeType,
  onStatus,
}: {
  environment: Environment;
  types: readonly EnvironmentType[];
  pending: boolean;
  onChangeType: (typeId: string) => void;
  onStatus: (message: string) => void;
}) {
  const [filter, setFilter] = useState("all");
  const visible =
    filter === "all"
      ? types.slice(0, 10)
      : types.filter((type) => type.environmentTypeId === filter);
  return (
    <div className="identity-editor environment-identity-editor">
      <section className="style-selector selector-section">
        <h3>STYLE</h3>
        <ActionCards
          className="identity-action-cards"
          actions={[
            {
              id: "upload",
              label: "Upload",
              description: "Upload Your Own",
              icon: <CloudUpload aria-hidden="true" />,
              status: "deferred",
            },
            {
              id: "generate",
              label: "AI Generate",
              description: "Generate with AI",
              icon: <Sparkles aria-hidden="true" />,
              status: "deferred",
            },
          ]}
          onActivate={() =>
            onStatus("Environment source actions are deferred; no asset was created.")
          }
        />
      </section>
      <section className="species-selector selector-section">
        <h3>ENVIRONMENT TYPE</h3>
        <FilterPills
          items={[
            { id: "all", label: "All" },
            ...types.slice(0, 6).map((type) => ({
              id: type.environmentTypeId,
              label: type.name,
            })),
          ]}
          value={filter}
          label="Environment type filters"
          onChange={setFilter}
        />
        <DomainAssetGrid
          title=""
          titleId="environment-type-grid-title"
          items={visible}
          selectedId={environment.environmentTypeId}
          getId={(type) => type.environmentTypeId}
          getLabel={(type) => type.name}
          getItemClassName={(type) =>
            `species-card environment-type-card environment-type-${type.key}`
          }
          renderMedia={(type) => (
            <span className="environment-type-media" data-type={type.key} aria-hidden="true" />
          )}
          onSelect={(type) => !pending && onChangeType(type.environmentTypeId)}
          emptyMessage="No Environment type matches this filter."
        />
      </section>
    </div>
  );
}

function TimeEditor({
  environment,
  onSelect,
}: {
  environment: Environment;
  onSelect: (time: string) => void;
}) {
  const times = ["dawn", "day", "golden-hour", "dusk", "night"];
  return (
    <DomainAssetGrid
      title="TIME OF DAY"
      titleId="environment-time-title"
      items={times}
      selectedId={environment.timeOfDay}
      getId={(value) => value}
      getLabel={titleCase}
      getItemClassName={(value) =>
        `accessory-card environment-time-card environment-time-${value}`
      }
      renderMedia={(value) => (
        <span className="environment-asset-media" data-subcategory={value} aria-hidden="true" />
      )}
      onSelect={onSelect}
      emptyMessage="No time-of-day presets are available."
    />
  );
}

function EnvironmentInspector({
  environment,
  types,
  pending,
  readinessStatus,
  onIdentity,
  onUpdate,
  onStatus,
  onValidate,
}: {
  environment?: Environment;
  types: readonly EnvironmentType[];
  pending: boolean;
  readinessStatus?: string;
  onIdentity: (values: { display_name?: string; description?: string }) => void;
  onUpdate: (values: Record<string, string | number>) => void;
  onStatus: (message: string) => void;
  onValidate: () => void;
}) {
  if (!environment) {
    return (
      <DomainInspectorPanel
        tabs={[
          { id: "properties", label: "PROPERTIES" },
          { id: "transform", label: "TRANSFORM" },
        ]}
        activeTab="properties"
        onTabChange={() => onStatus("Transform is deferred.")}
      >
        <p className="empty-inspector">Create an Environment package to edit its properties.</p>
      </DomainInspectorPanel>
    );
  }
  return (
    <>
      <DomainInspectorPanel
        tabs={[
          { id: "properties", label: "PROPERTIES" },
          { id: "transform", label: "TRANSFORM" },
        ]}
        activeTab="properties"
        onTabChange={() => onStatus("Transform is deferred.")}
      >
        <div className="property-form">
          <PropertyField label="Environment Name">
            <input
              key={`${environment.environmentId}:${environment.version}:name`}
              defaultValue={environment.displayName}
              aria-label="Environment Name"
              disabled={pending}
              onBlur={(event) =>
                event.target.value !== environment.displayName &&
                onIdentity({ display_name: event.target.value })
              }
            />
          </PropertyField>
          <PropertyField label="Environment Type">
            <Dropdown
              className="select-wrap"
              label="Environment Type"
              value={environment.environmentTypeId}
              disabled
              options={types.map((type) => ({
                label: type.name,
                value: type.environmentTypeId,
              }))}
            />
          </PropertyField>
          <PropertyField label="Location">
            <Dropdown
              className="select-wrap"
              label="Location"
              value={environment.locationType}
              disabled={pending}
              options={[
                "room",
                "corridor",
                "street",
                "plaza",
                "building",
                "landscape",
                "vehicle-interior",
                "spacecraft-interior",
                "abstract-environment",
                "custom",
              ].map((value) => ({ label: titleCase(value), value }))}
              onChange={(event) => onUpdate({ location_type: event.target.value })}
            />
          </PropertyField>
          <PropertyField label="Interior / Exterior">
            <Dropdown
              className="select-wrap"
              label="Interior / Exterior"
              value={environment.interiorExterior}
              disabled={pending}
              options={["interior", "exterior", "mixed", "virtual", "studio-stage"].map(
                (value) => ({ label: titleCase(value), value }),
              )}
              onChange={(event) => onUpdate({ interior_exterior: event.target.value })}
            />
          </PropertyField>
          <PropertyField label="Biome">
            <input
              key={`${environment.environmentId}:${environment.version}:biome`}
              defaultValue={environment.biome}
              aria-label="Biome"
              disabled={pending}
              onBlur={(event) =>
                event.target.value !== environment.biome && onUpdate({ biome: event.target.value })
              }
            />
          </PropertyField>
          <PropertyField label="Climate">
            <input
              key={`${environment.environmentId}:${environment.version}:climate`}
              defaultValue={environment.climateProfile}
              aria-label="Climate"
              disabled={pending}
              onBlur={(event) =>
                event.target.value !== environment.climateProfile &&
                onUpdate({ climate_profile: event.target.value })
              }
            />
          </PropertyField>
          <PropertyField label="Time of Day">
            <Dropdown
              className="select-wrap"
              label="Time of Day"
              value={environment.timeOfDay}
              disabled={pending}
              options={["dawn", "day", "golden-hour", "dusk", "night"].map((value) => ({
                label: titleCase(value),
                value,
              }))}
              onChange={(event) => onUpdate({ time_of_day: event.target.value })}
            />
          </PropertyField>
          <Slider
            label="Scale"
            min={1}
            max={1000}
            value={environment.scale}
            formatValue={(value) => `${value}%`}
            onChange={(value) => onUpdate({ scale: value })}
          />
          <PropertyField label="Navigation Constraints">
            <textarea
              key={`${environment.environmentId}:${environment.version}:navigation`}
              defaultValue={environment.navigationConstraints}
              aria-label="Navigation Constraints"
              disabled={pending}
              onBlur={(event) =>
                event.target.value !== environment.navigationConstraints &&
                onUpdate({ navigation_constraints: event.target.value })
              }
            />
          </PropertyField>
          <PropertyField label="Camera Access Constraints">
            <textarea
              key={`${environment.environmentId}:${environment.version}:camera`}
              defaultValue={environment.cameraAccessConstraints}
              aria-label="Camera Access Constraints"
              disabled={pending}
              onBlur={(event) =>
                event.target.value !== environment.cameraAccessConstraints &&
                onUpdate({ camera_access_constraints: event.target.value })
              }
            />
          </PropertyField>
          <Button
            className="advanced-settings-button"
            disabled={pending}
            onClick={onValidate}
          >
            Validate Readiness · {titleCase(readinessStatus ?? "not-validated")}
          </Button>
        </div>
      </DomainInspectorPanel>
      <SuggestionsPanel
        suggestions={[
          {
            id: "weather",
            title: "Weather continuity",
            body: "Check the selected weather against the planned scene.",
          },
          {
            id: "camera",
            title: "Camera access",
            body: "Confirm the package leaves space for planned camera movement.",
          },
          {
            id: "materials",
            title: "Material pass",
            body: "Review material selections before Set.",
          },
        ]}
        appliedIds={[]}
        renderMedia={(item) => (
          <span
            className={`environment-suggestion environment-suggestion-${item.id}`}
            aria-hidden="true"
          />
        )}
        onApply={() => onStatus("Suggestion application is deferred; no package data changed.")}
        onViewAll={() => onStatus("Curated Environment suggestions are shown in full.")}
        onGenerateMore={() => onStatus("AI suggestion generation is deferred.")}
        title="SUGGESTIONS"
        eyebrow="CURATED"
        generateLabel="Generate More with AI"
      />
    </>
  );
}

function EmptyEnvironmentEditor({ onCreate }: { onCreate: () => void }) {
  return (
    <section className="empty-environment">
      <Map aria-hidden="true" />
      <h2>Create an Environment package</h2>
      <p>Environment selections are saved to the canonical project and production.</p>
      <Button onClick={onCreate}>Add Environment</Button>
    </section>
  );
}
