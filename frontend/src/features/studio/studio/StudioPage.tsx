import { WorkflowScaffoldPage } from "../shared/WorkflowScaffoldPage";

export function StudioPage({ projectId }: { projectId: string }) {
  return <WorkflowScaffoldPage projectId={projectId} stage="studio" />;
}
