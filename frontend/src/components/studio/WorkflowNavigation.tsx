import {
  workflowHref,
  workflowStages,
  type WorkflowStageId,
} from "../../features/studio/config/navigation";

type WorkflowNavigationProps = {
  activeStage: WorkflowStageId;
  projectId: string;
  characterId?: string;
  className?: string;
  ariaLabel?: string;
};

export function WorkflowNavigation({
  activeStage,
  projectId,
  characterId,
  className = "",
  ariaLabel = "Creator workflow",
}: WorkflowNavigationProps) {
  return (
    <nav
      className={`module-navigation creator-workflow-navigation ${className}`.trim()}
      aria-label={ariaLabel}
    >
      {workflowStages.map((stage, index) => (
          <a
            className={`module-button ${activeStage === stage.id ? "is-active" : ""}`}
            aria-current={activeStage === stage.id ? "page" : undefined}
            aria-label={stage.label}
            href={workflowHref(projectId, stage.id, characterId)}
            key={stage.id}
          >
            <span className="creator-stage-dot" aria-hidden="true">
              {index + 1}
            </span>
            <span className="creator-stage-label">{stage.label}</span>
          </a>
      ))}
    </nav>
  );
}
