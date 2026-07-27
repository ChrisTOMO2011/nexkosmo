import { WorkflowScaffoldPage } from "../shared/WorkflowScaffoldPage";

export function RenderPage({ projectId }: { projectId: string }) {
  return <WorkflowScaffoldPage projectId={projectId} stage="render" />;
}
