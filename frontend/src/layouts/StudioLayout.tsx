import type { ReactNode } from "react";
import type { WorkflowStage } from "../app/workflow";
import { TopNavigation } from "../components/shell/TopNavigation";

type StudioLayoutProps = {
  activeStage: WorkflowStage;
  projectId: string;
  children: ReactNode;
};

export function StudioLayout({
  activeStage,
  projectId,
  children,
}: StudioLayoutProps) {
  return (
    <div className="studio-shell">
      <a className="skip-link" href="#main-content">
        Skip to workspace
      </a>
      <TopNavigation activeStage={activeStage} projectId={projectId} />
      <main className="page-container" id="main-content">
        {children}
      </main>
    </div>
  );
}

