import { Bell, ChevronDown, CircleHelp, Sparkles } from "lucide-react";
import type { WorkflowStageId } from "../../features/studio/config/navigation";
import { Button, Tooltip } from "../ui";
import { WorkflowNavigation } from "./WorkflowNavigation";

type TopNavigationProps = {
  activeStage: WorkflowStageId;
  projectId: string;
  characterId?: string;
  onPlaceholder: (message: string) => void;
};

export function TopNavigation({
  activeStage,
  projectId,
  characterId,
  onPlaceholder,
}: TopNavigationProps) {
  return (
    <header className="studio-topbar">
      <a className="brand" href="/" aria-label="Nexkosmo Studio home">
        <span className="brand-mark" aria-hidden="true">
          <i />
          <i />
          <i />
          <i />
        </span>
        <span className="brand-copy">
          <strong>NEXKOSMO</strong>
          <small>STUDIO</small>
        </span>
      </a>

      <WorkflowNavigation
        activeStage={activeStage}
        projectId={projectId}
        characterId={characterId}
      />

      <div className="topbar-actions">
        <Button
          className="ai-director-button"
          leadingIcon={<Sparkles aria-hidden="true" />}
          onClick={() => onPlaceholder("AI Director is ready for integration.")}
        >
          <span>AI Director</span>
        </Button>
        <Tooltip content="Help">
          <Button
            className="icon-button"
            size="icon"
            aria-label="Help"
            onClick={() => onPlaceholder("Help centre placeholder opened.")}
          >
            <CircleHelp aria-hidden="true" />
          </Button>
        </Tooltip>
        <Tooltip content="Notifications">
          <Button
            className="icon-button notification-button"
            size="icon"
            aria-label="Notifications, one unread"
            onClick={() => onPlaceholder("No new production alerts.")}
          >
            <Bell aria-hidden="true" />
            <span className="notification-dot" />
          </Button>
        </Tooltip>
        <Button className="profile-button" aria-label="Open user menu">
          <span className="profile-avatar avatar-chris" aria-hidden="true" />
          <ChevronDown aria-hidden="true" />
        </Button>
      </div>
    </header>
  );
}
