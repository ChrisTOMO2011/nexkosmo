import { WorkflowScaffoldPage } from "../shared/WorkflowScaffoldPage";

export function ReviewPage({ projectId }: { projectId: string }) {
  return <WorkflowScaffoldPage projectId={projectId} stage="review" />;
}
