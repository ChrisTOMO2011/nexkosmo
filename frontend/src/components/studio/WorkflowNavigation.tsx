import { ChevronRight } from "lucide-react";
import {
  workflowHref,
  workflowStages,
  type WorkflowStageId,
} from "../../features/studio/config/navigation";

type WorkflowNavigationProps = {
  activeStage: WorkflowStageId;
  projectId: string;
  characterId?: string;
};

export function WorkflowNavigation({
  activeStage,
  projectId,
  characterId,
}: WorkflowNavigationProps) {
  return (
    <nav className="workflow-navigation" aria-label="Production workflow">
      {workflowStages.map((stage, index) => (
        <div className="workflow-step-wrap" key={stage.id}>
          <a
            className={`workflow-step ${activeStage === stage.id ? "is-active" : ""}`}
            aria-current={activeStage === stage.id ? "step" : undefined}
            href={workflowHref(projectId, stage.id, characterId)}
          >
            <span className="workflow-number">{index + 1}</span>
            <span className="workflow-label">{stage.label}</span>
          </a>
          {index < workflowStages.length - 1 && (
            <ChevronRight className="workflow-chevron" aria-hidden="true" />
          )}
        </div>
      ))}
    </nav>
  );
}
