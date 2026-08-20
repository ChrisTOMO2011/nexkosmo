import {
  WORKFLOW_STAGE_DEFINITIONS,
  workflowHref,
  type WorkflowStage,
} from "../../app/workflow";

type WorkflowNavigationProps = {
  activeStage: WorkflowStage;
  projectId: string;
};

export function WorkflowNavigation({
  activeStage,
  projectId,
}: WorkflowNavigationProps) {
  return (
    <nav className="workflow-navigation" aria-label="Creator workflow">
      <ol>
        {WORKFLOW_STAGE_DEFINITIONS.map((stage, index) => (
          <li key={stage.id}>
            <a
              className={activeStage === stage.id ? "is-active" : undefined}
              aria-current={activeStage === stage.id ? "page" : undefined}
              href={workflowHref(projectId, stage.id)}
            >
              <span className="workflow-navigation__marker" aria-hidden="true">
                {index + 1}
              </span>
              <span>{stage.label}</span>
            </a>
          </li>
        ))}
      </ol>
    </nav>
  );
}

