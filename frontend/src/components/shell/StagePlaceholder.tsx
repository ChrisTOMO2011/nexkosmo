import { CircleDashed } from "lucide-react";
import {
  WORKFLOW_STAGE_DEFINITIONS,
  type WorkflowStage,
} from "../../app/workflow";
import { Panel } from "../ui";

type StagePlaceholderProps = {
  stage: WorkflowStage;
};

export function StagePlaceholder({ stage }: StagePlaceholderProps) {
  const definition = WORKFLOW_STAGE_DEFINITIONS.find(
    (candidate) => candidate.id === stage,
  );

  if (!definition) return null;

  return (
    <Panel className="stage-placeholder" aria-labelledby="stage-title">
      <span className="stage-placeholder__eyebrow">
        <CircleDashed aria-hidden="true" /> Canonical shell placeholder
      </span>
      <h1 id="stage-title">{definition.label}</h1>
      <p>{definition.description}</p>
      <div className="stage-placeholder__notice" role="status">
        This route is reserved for a later migration slice. No stage operations,
        persistence, or intelligence are connected here.
      </div>
    </Panel>
  );
}

