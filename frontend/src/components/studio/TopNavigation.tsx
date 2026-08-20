import approvedLogoSymbol from "../../assets/branding/nexkosmo-approved-symbol.jpeg";
import type { WorkflowStageId } from "../../features/studio/config/navigation";
import { StudioHeaderUtilities } from "./StudioHeaderUtilities";
import { WorkflowNavigation } from "./WorkflowNavigation";
import { Brain, Camera, ChevronDown, Menu } from "lucide-react";

type TopNavigationProps = {
  activeStage: WorkflowStageId;
  projectId: string;
  characterId?: string;
  onPlaceholder: (message: string) => void;
  ariaLabel?: string;
};

export function TopNavigation({
  activeStage,
  projectId,
  characterId,
  onPlaceholder,
  ariaLabel = "Creator workflow",
}: TopNavigationProps) {
  return (
    <header className="studio-topbar discovery-header creator-header">
      <a className="discovery-brand creator-brand" href="/" aria-label="Nexkosmo home">
        <img
          src={approvedLogoSymbol}
          alt=""
          width="1280"
          height="1280"
        />
        <span aria-hidden="true">
          <strong>NEXKOSMO</strong>
          <small>Your AI Producer</small>
        </span>
      </a>

      <WorkflowNavigation
        activeStage={activeStage}
        projectId={projectId}
        characterId={characterId}
        className="discovery-progress"
        ariaLabel={ariaLabel}
      />

      <div
        className="discovery-utilities creator-utilities"
        aria-label="Global tools"
      >
        <StudioHeaderUtilities onAction={onPlaceholder} />
        <button
          className="discovery-brain"
          type="button"
          aria-label="Open Nexkosmo Brain"
          title="Nexkosmo Brain"
          onClick={() => onPlaceholder("Nexkosmo Brain opened.")}
        >
          <Brain aria-hidden="true" />
        </button>
        <button
          className="discovery-project"
          type="button"
          aria-label="Untitled Movie"
          onClick={() => onPlaceholder("Project menu opened.")}
        >
          <Camera aria-hidden="true" /> Untitled Movie{" "}
          <ChevronDown aria-hidden="true" />
        </button>
        <button
          type="button"
          aria-label="Open menu"
          onClick={() => onPlaceholder("Menu opened.")}
        >
          <Menu aria-hidden="true" />
        </button>
      </div>
    </header>
  );
}
