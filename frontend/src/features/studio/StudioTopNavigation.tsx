import {
  Bell,
  ChevronDown,
  CircleHelp,
  Sparkles,
} from "lucide-react";
import { WorkflowNavigation } from "./WorkflowNavigation";

type StudioTopNavigationProps = {
  activeStage: number;
  onStageChange: (stage: number) => void;
  onPlaceholder: (message: string) => void;
};

export function StudioTopNavigation({
  activeStage,
  onStageChange,
  onPlaceholder,
}: StudioTopNavigationProps) {
  return (
    <header className="studio-topbar">
      <a className="brand" href="/" aria-label="Nexkosmo Studio home">
        <span className="brand-mark" aria-hidden="true">
          <i />
          <i />
        </span>
        <span className="brand-copy">
          <strong>NEXKOSMO</strong>
          <small>STUDIO</small>
        </span>
      </a>

      <WorkflowNavigation activeStage={activeStage} onChange={onStageChange} />

      <div className="topbar-actions">
        <button
          className="ai-director-button"
          type="button"
          onClick={() => onPlaceholder("AI Director is ready for integration.")}
        >
          <Sparkles aria-hidden="true" />
          <span>AI Director</span>
        </button>
        <button
          className="icon-button"
          type="button"
          aria-label="Help"
          onClick={() => onPlaceholder("Help centre placeholder opened.")}
        >
          <CircleHelp aria-hidden="true" />
        </button>
        <button
          className="icon-button notification-button"
          type="button"
          aria-label="Notifications, one unread"
          onClick={() => onPlaceholder("No new production alerts.")}
        >
          <Bell aria-hidden="true" />
          <span className="notification-dot" />
        </button>
        <button className="profile-button" type="button" aria-label="Open user menu">
          <span className="profile-avatar avatar-chris" aria-hidden="true" />
          <ChevronDown aria-hidden="true" />
        </button>
      </div>
    </header>
  );
}
