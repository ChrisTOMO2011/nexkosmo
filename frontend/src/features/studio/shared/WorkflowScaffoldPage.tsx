import { useState } from "react";
import {
  BottomActionBar,
  InspectorPanel,
  LeftSidebar,
  RightSidebar,
} from "../../../components/studio";
import { LoadingSkeleton, Panel } from "../../../components/ui";
import { StudioLayout } from "../../../layouts/StudioLayout";
import { navigateInApp } from "../../../app/navigation";
import {
  productionWorkspaceHref,
  workflowScaffoldNavigation,
  type ProductionWorkspaceId,
} from "../config/navigation";

type WorkflowScaffoldPageProps = {
  projectId: string;
  stage: ProductionWorkspaceId;
};

const nextStage: Record<ProductionWorkspaceId, ProductionWorkspaceId | null> = {
  set: "studio",
  studio: "render",
  render: null,
};

export function WorkflowScaffoldPage({
  projectId,
  stage,
}: WorkflowScaffoldPageProps) {
  const stageLabel = stage.toUpperCase();
  const navigation = workflowScaffoldNavigation[stage];
  const [activeItem, setActiveItem] = useState(navigation[0].label);
  const [inspectorOpen, setInspectorOpen] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");

  const followingStage = nextStage[stage];
  const followingLabel = followingStage?.toUpperCase();

  function showStatus(message: string) {
    setStatusMessage(message);
  }

  return (
    <StudioLayout
      activeStage="production"
      projectId={projectId}
      leftSidebar={
        <LeftSidebar
          items={navigation}
          activeItem={activeItem}
          sectionLabel={`${stageLabel} sections`}
          onNavigate={(label) => {
            setActiveItem(label);
            showStatus(`${label} is a layout placeholder.`);
          }}
          onPlaceholder={showStatus}
        />
      }
      rightSidebar={
        <RightSidebar
          open={inspectorOpen}
          title={`${stageLabel} inspector`}
          onClose={() => setInspectorOpen(false)}
        >
          <InspectorPanel title="Inspector" className="properties-card">
            <p className="scaffold-placeholder-copy">
              Properties for the selected item will appear here.
            </p>
            <LoadingSkeleton lines={4} label="Inspector placeholder" />
          </InspectorPanel>
          <Panel className="ai-suggestions" title="Workflow panel">
            <p className="scaffold-placeholder-copy">
              Stage-specific tools will be introduced when this workflow is
              implemented.
            </p>
            <LoadingSkeleton lines={3} label="Workflow tools placeholder" />
          </Panel>
        </RightSidebar>
      }
      bottomActionBar={
        <BottomActionBar
          primaryLabel={followingLabel ? `Next: ${followingLabel}` : "Render ready"}
          secondaryLabel="Preview Scene"
          onSecondary={() => showStatus("Scene preview is not implemented yet.")}
          onPrimary={() => {
            if (followingStage) {
              navigateInApp(productionWorkspaceHref(projectId, followingStage));
            } else {
              showStatus("Render actions will be implemented in the Render workflow.");
            }
          }}
        />
      }
      rightSidebarLabel={`Open ${stageLabel.toLowerCase()} inspector`}
      onOpenRightSidebar={() => setInspectorOpen(true)}
      onPlaceholder={showStatus}
      statusMessage={statusMessage}
      workspaceClassName="studio-workspace--scaffold"
    >
      <section className="workflow-scaffold" aria-labelledby="workflow-page-title">
        <header className="workflow-scaffold__heading">
          <p>THE LAST DAWN / {stageLabel}</p>
          <h1 id="workflow-page-title">{stageLabel}</h1>
          <span>Workspace foundation</span>
        </header>
        <div className="workflow-scaffold__grid">
          <Panel
            className="workflow-scaffold__primary"
            title="Primary workspace"
            description={`${stageLabel} tools will be implemented here without changing the shared Studio shell.`}
          >
            <LoadingSkeleton lines={6} label={`${stageLabel} workspace placeholder`} />
          </Panel>
          <Panel
            className="workflow-scaffold__secondary"
            title="Supporting panel"
            description="Reserved for stage-specific context and controls."
          >
            <LoadingSkeleton lines={5} label="Supporting panel placeholder" />
          </Panel>
          <Panel
            className="workflow-scaffold__timeline"
            title="Workflow area"
            description="Reserved for the stage's primary sequence or asset surface."
          >
            <LoadingSkeleton lines={3} label="Workflow area placeholder" />
          </Panel>
        </div>
      </section>
    </StudioLayout>
  );
}
