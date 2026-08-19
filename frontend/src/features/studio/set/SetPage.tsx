import { WorkflowScaffoldPage } from "../shared/WorkflowScaffoldPage";

export function SetPage({ projectId }: { projectId: string }) {
  return <WorkflowScaffoldPage projectId={projectId} stage="set" />;
}
