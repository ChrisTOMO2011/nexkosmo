import type { ReactNode } from "react";
import { DomainEditorContent } from "./DomainEditorContent";

type PreProductionWorkspaceProps = {
  sourcePanel: ReactNode;
  preview: ReactNode;
  selectionRail: ReactNode;
  editorTabs: ReactNode;
  editorContent: ReactNode;
  editorLabel: string;
};

export function PreProductionWorkspace({
  sourcePanel,
  preview,
  selectionRail,
  editorTabs,
  editorContent,
  editorLabel,
}: PreProductionWorkspaceProps) {
  return (
    <>
      <section className="workspace-top">
        {sourcePanel}
        {preview}
        {selectionRail}
      </section>

      <section className="lower-editor" aria-label={editorLabel}>
        {editorTabs}
        <DomainEditorContent>{editorContent}</DomainEditorContent>
      </section>
    </>
  );
}
