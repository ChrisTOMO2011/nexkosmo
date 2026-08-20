import { SlidersHorizontal } from "lucide-react";
import type { ReactNode } from "react";
import type { WorkflowStageId } from "../features/studio/config/navigation";
import { TopNavigation } from "../components/studio";
import { Button, Toast } from "../components/ui";

type StudioLayoutProps = {
  activeStage: WorkflowStageId;
  projectId: string;
  characterId?: string;
  variant?: "default" | "character-identity";
  leftSidebar: ReactNode;
  rightSidebar?: ReactNode;
  bottomActionBar: ReactNode;
  rightSidebarLabel?: string;
  onOpenRightSidebar?: () => void;
  onPlaceholder: (message: string) => void;
  statusMessage: string;
  statusNotice?: ReactNode;
  workspaceClassName?: string;
  children: ReactNode;
};

export function StudioLayout({
  activeStage,
  projectId,
  characterId,
  variant = "default",
  leftSidebar,
  rightSidebar,
  bottomActionBar,
  rightSidebarLabel = "Open inspector",
  onOpenRightSidebar,
  onPlaceholder,
  statusMessage,
  statusNotice,
  workspaceClassName = "",
  children,
}: StudioLayoutProps) {
  return (
    <div
      className={`nexkosmo-studio ${
        variant === "default" ? "" : `nexkosmo-studio--${variant}`
      }`.trim()}
    >
      <TopNavigation
        activeStage={activeStage}
        projectId={projectId}
        characterId={characterId}
        onPlaceholder={onPlaceholder}
      />
      <div
        className={`studio-shell ${rightSidebar ? "" : "studio-shell--without-inspector"}`}
      >
        {leftSidebar}
        <main className={`studio-workspace ${workspaceClassName}`.trim()}>
          {children}
        </main>
        {rightSidebar}
        {rightSidebar && onOpenRightSidebar && (
          <Button
            className="properties-toggle"
            size="icon"
            aria-label={rightSidebarLabel}
            onClick={onOpenRightSidebar}
          >
            <SlidersHorizontal aria-hidden="true" />
          </Button>
        )}
      </div>
      {bottomActionBar}
      {statusNotice ?? <Toast key={statusMessage} message={statusMessage} />}
    </div>
  );
}
