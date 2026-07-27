import { ChevronRight } from "lucide-react";
import { workflowStages } from "./pre-production/data";

type WorkflowNavigationProps = {
  activeStage: number;
  onChange: (stage: number) => void;
};

export function WorkflowNavigation({
  activeStage,
  onChange,
}: WorkflowNavigationProps) {
  return (
    <nav className="workflow-navigation" aria-label="Production workflow">
      {workflowStages.map((stage, index) => (
        <div className="workflow-step-wrap" key={stage}>
          <button
            className={`workflow-step ${activeStage === index ? "is-active" : ""}`}
            type="button"
            aria-current={activeStage === index ? "step" : undefined}
            onClick={() => onChange(index)}
          >
            <span className="workflow-number">{index + 1}</span>
            <span className="workflow-label">{stage}</span>
          </button>
          {index < workflowStages.length - 1 && (
            <ChevronRight className="workflow-chevron" aria-hidden="true" />
          )}
        </div>
      ))}
    </nav>
  );
}
