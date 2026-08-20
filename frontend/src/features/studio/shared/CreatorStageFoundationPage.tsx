import {
  BookCheck,
  FileText,
  Gauge,
  History,
  Image,
  Layers3,
  Lightbulb,
  MessageSquare,
  ShieldCheck,
  Sparkles,
  TriangleAlert,
} from "lucide-react";
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
import { workflowHref, type WorkflowStageId } from "../config/navigation";

type FoundationStage = Extract<WorkflowStageId, "idea" | "shape" | "ready">;

const stageContent = {
  idea: {
    title: "IDEA",
    eyebrow: "CREATIVE FOUNDATION",
    description:
      "Establish the production intent, audience, format, references and first creative direction with your Producer.",
    next: "discover" as const,
    navigation: [
      { label: "Creative Brief", icon: Lightbulb },
      { label: "References", icon: Image },
      { label: "Format & Audience", icon: Layers3 },
      { label: "Producer Direction", icon: Sparkles },
    ],
  },
  shape: {
    title: "SHAPE",
    eyebrow: "SCRIPT WORKSPACE",
    description:
      "Discovery material and uploaded screenplays remain connected views of the same story.",
    next: "build" as const,
    navigation: [
      { label: "Script Workspace", icon: FileText },
      { label: "Scene Structure", icon: Layers3 },
      { label: "Dialogue", icon: MessageSquare },
      { label: "Revisions", icon: History },
    ],
  },
  ready: {
    title: "READY",
    eyebrow: "PRODUCTION READINESS",
    description:
      "Validate canon, continuity, assets, rights, unresolved decisions and production risks.",
    next: "production" as const,
    navigation: [
      { label: "Readiness Overview", icon: Gauge },
      { label: "Canon & Continuity", icon: BookCheck },
      { label: "Assets & Rights", icon: ShieldCheck },
      { label: "Risks & Decisions", icon: TriangleAlert },
    ],
  },
} as const;

export function CreatorStageFoundationPage({
  projectId,
  stage,
}: {
  projectId: string;
  stage: FoundationStage;
}) {
  const content = stageContent[stage];
  const [activeItem, setActiveItem] = useState<string>(
    content.navigation[0].label,
  );
  const [inspectorOpen, setInspectorOpen] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");

  return (
    <StudioLayout
      activeStage={stage}
      projectId={projectId}
      leftSidebar={
        <LeftSidebar
          items={content.navigation}
          activeItem={activeItem}
          sectionLabel={`${content.title} sections`}
          onNavigate={(label) => {
            setActiveItem(label);
            setStatusMessage(`${label} selected.`);
          }}
          onPlaceholder={setStatusMessage}
        />
      }
      rightSidebar={
        <RightSidebar
          open={inspectorOpen}
          title={`${content.title} inspector`}
          onClose={() => setInspectorOpen(false)}
        >
          <InspectorPanel title="Inspector" className="properties-card">
            <p className="scaffold-placeholder-copy">
              Context for the selected {content.title.toLowerCase()} item will
              appear here.
            </p>
            <LoadingSkeleton lines={4} label={`${content.title} inspector`} />
          </InspectorPanel>
          <Panel className="ai-suggestions" title="Sophia">
            <p className="scaffold-placeholder-copy">
              Producer guidance remains connected to the project and its
              canonical Brain state.
            </p>
          </Panel>
        </RightSidebar>
      }
      bottomActionBar={
        <BottomActionBar
          primaryLabel={`Next: ${content.next.toUpperCase()}`}
          secondaryLabel={
            stage === "idea"
              ? "Review Production"
              : stage === "shape"
                ? "Preview Scene"
                : "Review Status"
          }
          onSecondary={() =>
            setStatusMessage(
              stage === "idea"
                ? "Production foundation selected."
                : stage === "shape"
                  ? "Scene preview remains connected to the Movie Map."
                  : "Production-readiness status selected.",
            )
          }
          onPrimary={() => navigateInApp(workflowHref(projectId, content.next))}
        />
      }
      rightSidebarLabel={`Open ${content.title.toLowerCase()} inspector`}
      onOpenRightSidebar={() => setInspectorOpen(true)}
      onPlaceholder={setStatusMessage}
      statusMessage={statusMessage}
      workspaceClassName="studio-workspace--scaffold"
    >
      <section className="workflow-scaffold" aria-labelledby={`${stage}-page-title`}>
        <header className="workflow-scaffold__heading">
          <p>THE LAST DAWN / {content.eyebrow}</p>
          <h1 id={`${stage}-page-title`}>{content.title}</h1>
          <span>{content.description}</span>
        </header>
        <div className="workflow-scaffold__grid">
          <Panel
            className="workflow-scaffold__primary"
            title={content.navigation[0].label}
            description={content.description}
          >
            <LoadingSkeleton lines={6} label={`${content.title} workspace`} />
          </Panel>
          <Panel
            className="workflow-scaffold__secondary"
            title="Project context"
            description="The Movie Map, script, assets and decisions share one project state."
          >
            <LoadingSkeleton lines={5} label="Project context" />
          </Panel>
          <Panel
            className="workflow-scaffold__timeline"
            title={
              stage === "idea"
                ? "Producer direction"
                : stage === "shape"
                  ? "Movie Map connection"
                  : "Readiness checks"
            }
            description={
              stage === "idea"
                ? "The selected AI Producer remains with the Director across the workflow."
                : stage === "shape"
                  ? "Approved Discovery moments stay connected to screenplay scenes."
                  : "Checks remain traceable to the canonical project state."
            }
          >
            <LoadingSkeleton lines={3} label={`${content.title} status`} />
          </Panel>
        </div>
      </section>
    </StudioLayout>
  );
}
